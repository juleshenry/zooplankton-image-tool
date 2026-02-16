import cv2
import os
import numpy as np
from scipy.spatial import distance as dist
from PIL import Image
from typing import Optional, Tuple


class Zit:
    def __init__(
        self,
        input_video: str,
        output_folder: str,
        interval: int,
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
        Clears all files from a folder.
        """
        if not os.path.exists(folder_path):
            return
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def capture_frames(self):
        self.clear_folder(self.output_folder)
        cap = cv2.VideoCapture(self.input_video)
        if not cap.isOpened():
            print(f"Error: Could not open video {self.input_video}")
            return

        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        if frame_rate == 0:
            frame_rate = 30 # Default if unknown

        frame_number = 0
        os.makedirs(self.output_folder, exist_ok=True)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_number % (frame_rate * self.interval) == 0:
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
    def get_avg_pix(img: Image.Image, img_data) -> Tuple[float, float, float]:
        avg = [0.0, 0.0, 0.0]
        for x in range(img.width):
            for y in range(img.height):
                pix = img_data[x, y][:3]
                avg[0] += pix[0]
                avg[1] += pix[1]
                avg[2] += pix[2]
        total_pixels = img.width * img.height
        return (avg[0] / total_pixels, avg[1] / total_pixels, avg[2] / total_pixels)

    def replace_different_pixels(self, bgp: str, olp: str, output_path: str) -> str:
        print("Putting", olp, "onto", bgp)
        background = Image.open(bgp).convert("RGB")
        overlay = Image.open(olp).resize(background.size).convert("RGB")

        background_data = background.load()
        overlay_data = overlay.load()
        avg_pixel = self.get_avg_pix(overlay, overlay_data)

        for x in range(background.width):
            for y in range(background.height):
                bg_pixel = background_data[x, y]
                overlay_pixel = overlay_data[x, y]

                if dist.euclidean(overlay_pixel, avg_pixel) < self.noise_delta:
                    continue
                
                dif = dist.euclidean(bg_pixel, overlay_pixel)
                if dif > self.composite_epsilon:
                    background_data[x, y] = overlay_pixel
        
        background.save(output_path, "PNG")
        return output_path

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
        self, out_file: str, skip: Optional[Tuple[int, int]] = None
    ):
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

        init_b = self.pathjoin(frames[0])
        init_o = self.pathjoin(frames[1])
        
        out_name = self.replace_different_pixels(init_b, init_o, out_file)
        for next_frame in frames[2:]:
            next_frame_path = self.pathjoin(next_frame)
            out_name = self.replace_different_pixels(out_name, next_frame_path, out_name)
