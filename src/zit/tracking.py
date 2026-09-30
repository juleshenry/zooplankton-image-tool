"""
Links per-frame entity detections into trajectories and renders them.
"""
import colorsys
import csv
from dataclasses import dataclass, field
from typing import List, Sequence, Tuple

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

# (x, y, area) of one detected entity in one frame
Detection = Tuple[float, float, float]


@dataclass
class Track:
    track_id: int
    # (frame_number, x, y, area) in time order
    points: List[Tuple[int, float, float, float]] = field(default_factory=list)
    missed: int = 0

    @property
    def last_xy(self) -> Tuple[float, float]:
        _, x, y, _ = self.points[-1]
        return x, y

    def path_length(self) -> float:
        xy = np.array([(x, y) for _, x, y, _ in self.points])
        if len(xy) < 2:
            return 0.0
        return float(np.linalg.norm(np.diff(xy, axis=0), axis=1).sum())

    def straightness(self) -> float:
        """Net displacement over path length: ~1 for a swimmer, ~0 for jitter."""
        length = self.path_length()
        if length == 0:
            return 0.0
        _, x0, y0, _ = self.points[0]
        _, x1, y1, _ = self.points[-1]
        return float(np.hypot(x1 - x0, y1 - y0)) / length


def link_detections(
    frame_numbers: Sequence[int],
    detections: Sequence[Sequence[Detection]],
    max_jump: float = 50.0,
    max_gap: int = 2,
) -> List[Track]:
    """
    Joins detections across frames into tracks by optimal nearest-centroid
    assignment. A detection farther than `max_jump` pixels from every live
    track starts a new one; a track that goes unmatched for more than
    `max_gap` consecutive frames is closed.
    """
    tracks: List[Track] = []
    active: List[Track] = []

    for frame_no, dets in zip(frame_numbers, detections):
        matched_dets = set()
        matched_tracks = set()

        if active and dets:
            track_xy = np.array([t.last_xy for t in active])
            det_xy = np.array([(x, y) for x, y, _ in dets])
            cost = np.linalg.norm(track_xy[:, None, :] - det_xy[None, :, :], axis=2)
            rows, cols = linear_sum_assignment(cost)
            for r, c in zip(rows, cols):
                if cost[r, c] <= max_jump:
                    x, y, area = dets[c]
                    active[r].points.append((frame_no, x, y, area))
                    active[r].missed = 0
                    matched_tracks.add(r)
                    matched_dets.add(c)

        for i, t in enumerate(active):
            if i not in matched_tracks:
                t.missed += 1
        active = [t for t in active if t.missed <= max_gap]

        for c, (x, y, area) in enumerate(dets):
            if c not in matched_dets:
                t = Track(track_id=len(tracks), points=[(frame_no, x, y, area)])
                tracks.append(t)
                active.append(t)

    return tracks


def filter_tracks(
    tracks: Sequence[Track], min_points: int = 4, min_straightness: float = 0.7
) -> List[Track]:
    """
    Keeps tracks that look like directed swimming. Flickering noise (sediment,
    sensor speckle) gets linked into short zig-zag tracks that fail one test or both.
    """
    return [
        t for t in tracks
        if len(t.points) >= min_points and t.straightness() >= min_straightness
    ]


def track_color(track_id: int) -> Tuple[int, int, int]:
    """Distinct, saturated BGR color per track (golden-ratio hue stepping)."""
    hue = (track_id * 0.618033988749895) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 1.0)
    return int(b * 255), int(g * 255), int(r * 255)


def draw_trails(img: np.ndarray, tracks: Sequence[Track]) -> np.ndarray:
    """Draws each track's path with a dot at every sighting and an arrowhead at the end."""
    out = img.copy()
    thickness = max(1, round(min(img.shape[:2]) / 300))
    for t in tracks:
        if len(t.points) < 2:
            continue
        color = track_color(t.track_id)
        pts = np.array([(x, y) for _, x, y, _ in t.points], dtype=np.int32)
        cv2.polylines(out, [pts], False, color, thickness, cv2.LINE_AA)
        for p in pts[:-1]:
            cv2.circle(out, tuple(int(v) for v in p), thickness + 1, color, -1, cv2.LINE_AA)
        cv2.arrowedLine(
            out, tuple(int(v) for v in pts[-2]), tuple(int(v) for v in pts[-1]),
            color, thickness, cv2.LINE_AA, tipLength=0.3,
        )
    return out


def write_tracks_csv(path: str, tracks: Sequence[Track]):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["track_id", "frame", "x", "y", "area"])
        for t in tracks:
            for frame_no, x, y, area in t.points:
                writer.writerow([t.track_id, frame_no, f"{x:.1f}", f"{y:.1f}", f"{area:.1f}"])
