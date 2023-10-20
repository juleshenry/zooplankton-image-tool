import cv2
import os
import numpy as np
from scipy.spatial import distance as dist
from PIL import Image
from typing import Optional, Tuple


class Zit:
    def __init__(
        self,
        input_video,
        output_folder,
        interval,
        composite_epsilon: Optional[float] = None,
        noise_delta: Optional[float] = None,
    ):
        self.input_video = input_video
        self.output_folder = output_folder
        self.interval = interval
        self.composite_epsilon = composite_epsilon
        self.noise_delta = noise_delta

    @staticmethod
    def clear_folder(folder_path):
        """
        Clears all files from a folder.

        Parameters:
            folder_path (str): Path to the folder to be cleared.
        """
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            os.remove(file_path)

    def capture_frames(self):
        self.clear_folder(self.output_folder)
        cap = cv2.VideoCapture(self.input_video)
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        frame_number = 0
        os.makedirs(self.output_folder, exist_ok=True)
        while 1:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_number % (frame_rate * self.interval) == 0:
                frame_path = os.path.join(output_folder, f"frame_{frame_number}.jpg")
                cv2.imwrite(frame_path, frame)
                print(f"Saved frame {frame_number}")
            frame_number += 1
        cap.release()
        cv2.destroyAllWindows()

    def pathjoin(self, x):
        return os.path.join(self.output_folder, x)

    def multiply_concat(self, a, b, debug: bool = False):
        # Load the images
        a = self.pathjoin(a)
        b = self.pathjoin(b)
        foreground = cv2.imread(b)
        background = cv2.imread(a)
        # Resize the images to the same dimensions if necessary
        # You can skip this step if your images are already the same size
        # Ensure both images have the same dimensions
        height, width = foreground.shape[:2]
        background = cv2.resize(background, (width, height))
        # Perform the Multiply blending
        blended = cv2.multiply(foreground, background, scale=1 / 255.0)

        # Display the result
        if debug:
            cv2.imshow("Blended Image", blended)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        # Save the result
        cv2.imwrite(self.pathjoin("x.jpg"), blended)

    @staticmethod
    def get_avg_pix(img, img_data) -> Tuple[float, float, float]:
        avg = [
            0,
            0,
            0,
        ]
        for x in range(img.width):
            for y in range(img.height):
                pix = img_data[x, y][:3]
                avg = [x + y for x, y in zip(pix, avg)]
        avg = [o / (img.width * img.height) for o in avg]  # normalize
        return avg

    def replace_different_pixels(self, bgp, olp, output_path):
        if not self.composite_epsilon:
            raise ValueError("Must set composite epsilon in constructor")

        # Open the background and overlay images
        print("Putting", olp, "onto", bgp)
        background = Image.open(bgp)
        overlay = Image.open(olp).resize(background.size)

        # Get pixel data
        background_data = background.load()
        overlay_data = overlay.load()
        avg_pixel = self.get_avg_pix(overlay, overlay_data)

        # Iterate over each pixel
        for x in range(background.width):
            for y in range(background.height):
                bg_pixel = background_data[x, y][:3]
                overlay_pixel = overlay_data[x, y][:3]

                # If trying to overlay something basically, average noise, do not
                if dist.euclidean(overlay_pixel, avg_pixel) < self.noise_delta:
                    continue
                # Compare RGB values
                dif = dist.euclidean(bg_pixel, overlay_pixel)
                if dif > self.composite_epsilon:
                    # If pixels are different, replace background pixel with overlay pixel
                    background_data[x, y] = (*overlay_pixel, 255)
        # Save the result
        background.save(output_path, "PNG")
        return output_path

    @staticmethod
    def frame_match(frame_name: str):
        return int(frame_name.split("_")[1].split(".")[0])

    def filter_files_by_range(self, file_list, start_frame, end_frame):
        start_frame = self.frame_match(start_frame)
        end_frame = self.frame_match(end_frame)
        return [
            filename
            for filename in file_list
            if start_frame <= self.frame_match(filename) <= end_frame
        ]

    def composite_from_frames(
        self, out_file: str, skip: Optional[Tuple[int, int]] = None
    ):
        frames = sorted(os.listdir(z.output_folder))
        if skip:
            start, end = skip
            frames = self.filter_files_by_range(
                frames,
                f"frame_{start}.jpg",
                f"frame_{end}.jpg",
            )
        init_b, init_o = frames[:2]
        init_b, init_o = self.pathjoin(init_b), self.pathjoin(init_o)
        # Initial compose
        out_name = self.replace_different_pixels(init_b, init_o, out_file)
        for next_frame in frames[2:]:
            next_frame = self.pathjoin(next_frame)
            out_name = self.replace_different_pixels(out_name, next_frame, out_name)


# Usage example
if __name__ == "__main__":
    # import argparse
    # parser = argparse.ArgumentParser(description="CSS Parser")
    # a, p = parser.parse_args()

    # print(p[0])
    # Convert video into frames
    input_video = "./samples/plankt_oct19.mp4"
    output_folder = "frames/basic"
    interval_seconds = 1
    z = Zit(
        input_video,
        output_folder,
        interval_seconds,
        composite_epsilon=20, #de jour, ymmv
        noise_delta=50, #de jour, ymmv
    )
    z.capture_frames()
    z.composite_from_frames(f"{input_video.split('/')[2].split('.')[0]}") #, skip=(0,960,))
