import csv

import cv2
import numpy as np

from zit.core import Zit
from zit.tracking import Track, draw_trails, filter_tracks, link_detections, track_color


def test_link_detections_follows_two_crossing_paths():
    # One entity moves right along y=10, another moves left along y=40.
    frames = [0, 30, 60, 90]
    dets = [
        [(10.0, 10.0, 50.0), (90.0, 40.0, 60.0)],
        [(30.0, 10.0, 50.0), (70.0, 40.0, 60.0)],
        [(50.0, 40.0, 60.0), (50.0, 10.0, 50.0)],  # order swapped on purpose
        [(70.0, 10.0, 50.0), (30.0, 40.0, 60.0)],
    ]

    tracks = link_detections(frames, dets, max_jump=30)

    assert len(tracks) == 2
    for t in tracks:
        ys = {y for _, _, y, _ in t.points}
        assert len(ys) == 1
        assert [f for f, *_ in t.points] == frames
        assert t.path_length() == 60.0


def test_link_detections_splits_on_large_jump():
    tracks = link_detections([0, 1], [[(0.0, 0.0, 1.0)], [(100.0, 0.0, 1.0)]], max_jump=50)
    assert len(tracks) == 2


def test_link_detections_bridges_short_gap_then_closes():
    dets = [[(0.0, 0.0, 1.0)], [], [(5.0, 0.0, 1.0)], [], [], [], [(10.0, 0.0, 1.0)]]
    tracks = link_detections(list(range(len(dets))), dets, max_jump=20, max_gap=2)

    assert [len(t.points) for t in tracks] == [2, 1]


def test_filter_tracks_drops_jitter_and_short_tracks():
    straight = Track(0, [(i, i * 10.0, 0.0, 1.0) for i in range(5)])
    zigzag = Track(1, [(i, (i % 2) * 10.0, 0.0, 1.0) for i in range(5)])
    short = Track(2, [(i, i * 10.0, 0.0, 1.0) for i in range(2)])

    assert filter_tracks([straight, zigzag, short]) == [straight]


def test_track_colors_are_distinct():
    assert len({track_color(i) for i in range(8)}) == 8


def test_draw_trails():
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    single = Track(0, [(0, 5.0, 5.0, 1.0)])
    assert draw_trails(img, [single]).max() == 0

    path = Track(1, [(0, 5.0, 25.0, 1.0), (1, 20.0, 25.0, 1.0), (2, 40.0, 25.0, 1.0)])
    out = draw_trails(img, [path])
    assert out[25].max() > 0
    assert img.max() == 0  # input untouched


def test_entity_composite_writes_trails_and_tracks(tmp_path):
    z = Zit(input_video="", output_folder=str(tmp_path), interval=1,
            composite_epsilon=16.0, noise_delta=20.0)
    for i in range(10):
        frame = np.full((80, 160, 3), 40, dtype=np.uint8)
        x = 5 + i * 14
        frame[15:25, x : x + 10] = 220          # swims right
        frame[55:65, 145 - i * 14 : 155 - i * 14] = 220  # swims left
        cv2.imwrite(str(tmp_path / f"frame_{i * 30}.jpg"), frame)

    out_file = str(tmp_path / "out.png")
    csv_file = str(tmp_path / "tracks.csv")
    z.composite_from_frames(out_file, use_entities=True, trails=True,
                            tracks_csv=csv_file, max_jump=30)

    with open(csv_file) as f:
        rows = list(csv.DictReader(f))
    by_track = {}
    for r in rows:
        by_track.setdefault(r["track_id"], []).append(r)
    long_tracks = list(by_track.values())
    assert len(long_tracks) == 2
    assert all(len(v) >= 5 for v in long_tracks)
    assert {r["frame"] for r in long_tracks[0]} <= {str(i * 30) for i in range(10)}

    result = cv2.imread(out_file)
    # Trails are colored, while the grayscale scene is not.
    b, g, r = cv2.split(result.astype(int))
    assert (np.abs(b - r) + np.abs(g - r)).max() > 100


def test_track_merge_joins_fragmented_large_animal(tmp_path):
    # A big striped "animal" crosses the frame. Its stripes are separate
    # foreground blobs, so without merging each stripe gets its own track.
    z = Zit(input_video="", output_folder=str(tmp_path), interval=1,
            composite_epsilon=16.0, noise_delta=20.0)
    for i in range(10):
        frame = np.full((200, 400, 3), 40, dtype=np.uint8)
        x = 10 + i * 35
        for s in range(4):
            frame[60:140, x + s * 12 : x + s * 12 + 6] = 220
        cv2.imwrite(str(tmp_path / f"frame_{i}.jpg"), frame)

    def n_tracks(merge):
        csv_file = str(tmp_path / f"tracks_{merge}.csv")
        z.composite_from_frames(str(tmp_path / "out.png"), use_entities=True,
                                tracks_csv=csv_file, max_jump=60, track_merge=merge)
        with open(csv_file) as f:
            return len({r["track_id"] for r in csv.DictReader(f)})

    assert n_tracks(0) > 1
    assert n_tracks(0.1) == 1
