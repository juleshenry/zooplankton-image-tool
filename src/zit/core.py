r"""
                                             ▁▁▅▆▆▆▅▁▁                                              
                                            ▂▅▅ ▃▃▃▂▅▅▃                                             
                                            ▄▆ ▅███▆▁▅▇                                             
                                            ▅▆ █████▁▄▇                                             
                               ▂▃▃▃▂▁       ▃▅▄▁▄▅▄▁▄▅▄      ▃▄▄▄▂                                  
                               █▇▂▆█▄▁       ▁▂▅▅▅▅▅▂▁     ▁▃█▃▁▅█                                  
                               ██▂ ▂▆▇▁▁                  ▁▇▄▃▂▄▇█                                  
                               ▃██▅▁▂▄▅█▃▁              ▁▂▅█  ▆██▄                                  
                                 ▅██▆▄▃▃▅█▃            ▅▆▄▂▄███▇▄                                   
                                  ▂▂▄▇▇█▃▅▆▅          ▅▅▅▅▇█▇▄▃▁                                    
                                      ▁▃█▆▇▅▅▆▇▇▇▇▇▇▇▇▅▅▇▆▃▂                                        
                                      ▂▅██▅▃      ▁▂▅████▅                                          
                                      ▄█▂▁▁ ▁▃▃▂▃▃▃▂▁▁▇███▄                                         
                                      ▄▇  ▁▄▄▂▂▂▂▅█▆▄▁▃▇██▆                                         
                                      ▄▇ ▃▅▂▂▄▄▄▄▂ ▂▅█▁▇██▆                                         
                                      ▄▇ ▇▃▃██████▄ ▂█▃▇██▆                                         
                                      ▄█▆█▃▃▇████▇▃ ▂█████▆                                         
                                      ▄█▄▆▆▃▂▄██▄▁ ▃▇█████▆                                         
                                      ▄██▆▆▇▆▃▃▃▃▆██▆█████▆                                         
                                      ▄██▁ ▂▅▄▄▄█▅▄▄▅█████▆                                         
                                      ▄▇▁▇▇▄▂▂▂▂▂▁▅███████▆                                         
                                      ▄▇▃▅▅▆██▆▆▆▆▄▂█▆████▆                                         
                                      ▅██▃▁▁▃▃ ▁▁▁▃▆▇▁████▆                                         
                                    ▁▂▆███▆▅▅▅▄▅█▇▆▇ ▆████▆▂                                        
                                 ▁▄▅▆▃▅▇██▃▁▁▂▆▁▁▂▃▁ ███▇▆▇█▃▃▁                                     
                               ▂▆▅▂▂▄▆▇███▄▁  ▁▁▄▂ ▁▃█████▄▄▄█▇▄                                    
                               ▄█▇▆██▇▅▆███▆▄▄▅▅▇▇▆▆███▃▃▇█████▄                                    
                               ▁▄▄▄▄▂▁▃▇▃█████████████▆█▄▁▁▁▁▁▁                                     
                                    ▁▅▅▁▂█████████████▂▆▇▆▁                                         
                                    ▅▆▂▂███████████████▃▄▇▇                                         
                                  ▃▆▄▃▆██▅▁         ▂▅▆█▆▄▆█▅                                       
                                  ▆▅▅██▇▃              ▄██▇█▆                                       
                                  ▃██▆▃                  ▂▄▄▂                                       

                                 ________  ___  _________   
                                 |\_____  \|\  \|\___   ___\ 
                                  \|___/  /\ \  \|___ \  \_| 
                                      /  / /\ \  \   \ \  \  
                                     /  /_/__\ \  \   \ \  \ 
                                    |\________\ \__\   \ \__\
                                     \|_______|\|__|    \|__|
                            
                            
                              Zooplankton Imaging Tool by Julian Henry                          
                                 
"""

import cv2
import os
import numpy as np
from PIL import Image
from typing import Optional, Tuple

from .tracking import draw_trails, filter_tracks, link_detections, write_tracks_csv


class Zit:
    def __init__(
        self,
        input_video: str,
        output_folder: str,
        interval: float,
        composite_epsilon: float = 20.0,
        noise_delta: float = 50.0,
    ):
        self.input_video = input_video
        self.output_folder = output_folder
        self.interval = interval
        self.composite_epsilon = composite_epsilon
        self.noise_delta = noise_delta

    @staticmethod
    def clear_folder(folder_path: str):
        """
        Removes previously captured frame_<n>.jpg files from a folder,
        leaving any other files untouched.
        """
        if not os.path.exists(folder_path):
            return
        for filename in os.listdir(folder_path):
            if not (filename.startswith("frame_") and filename.endswith(".jpg")):
                continue
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def capture_frames(self):
        self.clear_folder(self.output_folder)
        cap = cv2.VideoCapture(self.input_video)
        if not cap.isOpened():
            print(f"Error: Could not open video {self.input_video}")
            return

        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        if not frame_rate or frame_rate <= 0:
            frame_rate = 30 # Default if unknown
        # Sample every `step` frames; sub-second intervals are allowed down to every frame
        step = max(1, round(frame_rate * self.interval))

        frame_number = 0
        os.makedirs(self.output_folder, exist_ok=True)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_number % step == 0:
                frame_path = os.path.join(self.output_folder, f"frame_{frame_number}.jpg")
                cv2.imwrite(frame_path, frame)
                print(f"Saved frame {frame_number}")
            frame_number += 1
        cap.release()

    def pathjoin(self, x: str) -> str:
        return os.path.join(self.output_folder, x)

    def multiply_concat(self, a_path: str, b_path: str, debug: bool = False):
        a = self.pathjoin(a_path)
        b = self.pathjoin(b_path)
        foreground = cv2.imread(b)
        background = cv2.imread(a)
        
        if foreground is None or background is None:
            print("Error loading images for multiply_concat")
            return

        height, width = foreground.shape[:2]
        background = cv2.resize(background, (width, height))
        blended = cv2.multiply(foreground, background, scale=1 / 255.0)

        if debug:
            cv2.imshow("Blended Image", blended)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        cv2.imwrite(self.pathjoin("x.jpg"), blended)

    @staticmethod
    def get_avg_pix(img: Image.Image) -> Tuple[float, float, float]:
        img_arr = np.array(img.convert("RGB"))
        avg = np.mean(img_arr, axis=(0, 1))
        return tuple(avg)

    def replace_different_pixels(self, bgp: str, olp: str, output_path: str) -> str:
        background = Image.open(bgp).convert("RGB")
        overlay = Image.open(olp).resize(background.size).convert("RGB")

        bg_arr = np.array(background)
        ol_arr = np.array(overlay)

        bg_arr = self._apply_composite(bg_arr, ol_arr)

        result = Image.fromarray(bg_arr)
        result.save(output_path, "PNG")
        return output_path

    def _apply_composite(self, bg_arr: np.ndarray, ol_arr: np.ndarray) -> np.ndarray:
        avg_pixel = np.mean(ol_arr, axis=(0, 1))

        # Vectorized Euclidean distance calculation
        # Distance between overlay pixels and the average color
        dist_to_avg = np.linalg.norm(ol_arr.astype(float) - avg_pixel, axis=2)
        
        # Distance between background and overlay pixels
        dist_bg_ol = np.linalg.norm(bg_arr.astype(float) - ol_arr.astype(float), axis=2)

        # Apply mask: (overlay not noise) AND (difference > epsilon)
        mask = (dist_to_avg >= self.noise_delta) & (dist_bg_ol > self.composite_epsilon)
        
        # Update background where mask is True
        bg_arr[mask] = ol_arr[mask]
        return bg_arr

    @staticmethod
    def frame_match(frame_name: str) -> int:
        try:
            return int(frame_name.split("_")[1].split(".")[0])
        except (IndexError, ValueError):
            return -1

    def filter_files_by_range(self, file_list, start_frame_name, end_frame_name):
        start_frame = self.frame_match(start_frame_name)
        end_frame = self.frame_match(end_frame_name)
        return [
            filename
            for filename in file_list
            if start_frame <= self.frame_match(filename) <= end_frame
        ]

    def composite_from_frames(
        self,
        out_file: str,
        skip: Optional[Tuple[int, int]] = None,
        use_entities: bool = False,
        trails: bool = False,
        tracks_csv: Optional[str] = None,
        max_jump: float = 50.0,
        min_track_points: int = 4,
        min_straightness: float = 0.7,
        track_merge: float = 0.0,
    ):
        """
        Composites the captured frames into `out_file`. With `use_entities`,
        detected animals can also be linked into tracks: `trails` draws their
        paths onto the composite and `tracks_csv` writes the per-frame positions.
        """
        frames = sorted([f for f in os.listdir(self.output_folder) if f.startswith("frame_") and f.endswith(".jpg")], key=self.frame_match)
        if not frames:
            print("No frames found to composite.")
            return

        if skip:
            start, end = skip
            frames = self.filter_files_by_range(
                frames,
                f"frame_{start}.jpg",
                f"frame_{end}.jpg",
            )
        
        if len(frames) < 2:
            print("Not enough frames for composition.")
            return

        if use_entities:
            self._entity_composite(
                frames, out_file, trails, tracks_csv, max_jump, min_track_points, min_straightness,
                track_merge,
            )
            return
        if trails or tracks_csv:
            print("Tracking requires entity recognition (--entities); skipping trails/tracks.")

        bg_img = Image.open(self.pathjoin(frames[0])).convert("RGB")
        bg_arr = np.array(bg_img)
        
        for frame_name in frames[1:]:
            ol_img = Image.open(self.pathjoin(frame_name)).resize(bg_img.size).convert("RGB")
            ol_arr = np.array(ol_img)
            bg_arr = self._apply_composite(bg_arr, ol_arr)
            
        result = Image.fromarray(bg_arr)
        result.save(out_file, "PNG")

    @staticmethod
    def _merged_detections(frame_mask: np.ndarray, merge: float, min_frac: float = 0.005):
        """
        Fuses nearby foreground fragments into whole-animal blobs for tracking.
        Large animals (birds, mammals) break into many pieces under MOG2; closing
        with a kernel `merge` * the frame's short side rejoins them. Blobs under
        `min_frac` of the frame are dropped as leftover speckle.
        """
        ks = max(3, int(min(frame_mask.shape) * merge)) | 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ks, ks))
        merged = cv2.morphologyEx(frame_mask, cv2.MORPH_CLOSE, kernel)
        n, _, stats, centroids = cv2.connectedComponentsWithStats(merged)
        min_area = frame_mask.size * min_frac
        return [
            (float(centroids[i][0]), float(centroids[i][1]), float(stats[i, cv2.CC_STAT_AREA]))
            for i in range(1, n)
            if stats[i, cv2.CC_STAT_AREA] >= min_area
        ]

    def _entity_composite(
        self, frames, out_file, trails=False, tracks_csv=None, max_jump=50.0,
        min_track_points=4, min_straightness=0.7, track_merge=0.0,
    ):
        # Use MOG2 background subtractor for better motion detection and ghosting prevention
        backSub = cv2.createBackgroundSubtractorMOG2(history=len(frames), varThreshold=self.composite_epsilon, detectShadows=True)
        
        # Training pass: identify background and motion
        images = []
        frame_numbers = []
        for frame_name in frames:
            img = cv2.imread(self.pathjoin(frame_name))
            if img is not None:
                images.append(img)
                frame_numbers.append(self.frame_match(frame_name))
                backSub.apply(img)
        
        if not images:
            return

        # Use the computed background as base
        background = backSub.getBackgroundImage()
        if background is None:
            # Fallback to median if MOG2 fails to produce a clean background
            background = np.median(np.stack(images[:min(len(images), 50)]), axis=0).astype(np.uint8)
            
        result_arr = background.copy()
        detections = []
        
        # Persistence mask to filter out static objects that MOG2 might still flag
        # We only want "proper animals in motion"
        for img in images:
            # Learning rate 0 to keep the background static during the drawing phase
            fgMask = backSub.apply(img, learningRate=0)
            
            # Shadows are usually marked as 127, foreground as 255. 
            # We only want the high-confidence foreground.
            _, fgMask = cv2.threshold(fgMask, 200, 255, cv2.THRESH_BINARY)
            
            # Clean up mask to remove speckles and bridge gaps in animals
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel)
            fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_CLOSE, kernel)
            fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_DILATE, kernel)
            
            # Find contours to isolate entities
            contours, _ = cv2.findContours(fgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            frame_mask = np.zeros_like(fgMask)
            frame_dets = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > self.noise_delta:
                    # Filter by aspect ratio to avoid picking up scan lines or frame artifacts
                    x, y, w, h = cv2.boundingRect(cnt)
                    aspect_ratio = float(w) / h
                    # Proper animals are usually somewhat contained, not 100x longer than wide
                    if 0.05 < aspect_ratio < 20:
                        cv2.drawContours(frame_mask, [cnt], -1, 255, -1)
                        m = cv2.moments(cnt)
                        if m["m00"] > 0:
                            frame_dets.append((m["m10"] / m["m00"], m["m01"] / m["m00"], area))
                        else:
                            frame_dets.append((x + w / 2, y + h / 2, area))
            if track_merge > 0:
                frame_dets = self._merged_detections(frame_mask, track_merge)
            detections.append(frame_dets)
            
            # Temporal order: newer entities overwrite older ones at the same location
            result_arr[frame_mask == 255] = img[frame_mask == 255]

        if trails or tracks_csv:
            tracks = link_detections(frame_numbers, detections, max_jump=max_jump)
            tracks = filter_tracks(tracks, min_track_points, min_straightness)
            print(f"Tracked {len(tracks)} swimming entities across {len(images)} frames.")
            if trails:
                result_arr = draw_trails(result_arr, tracks)
            if tracks_csv:
                write_tracks_csv(tracks_csv, tracks)
                print(f"Wrote tracks to {tracks_csv}")

        cv2.imwrite(out_file, result_arr)
