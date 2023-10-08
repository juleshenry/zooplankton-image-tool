import cv2
import os
import numpy as np
from scipy.spatial import distance as dist
from PIL import Image

class Zit:

    def __init__(self, input_video, output_folder, interval):
        self.input_video = input_video
        self.output_folder = output_folder
        self.interval = interval

    def capture_frames(self):
        cap = cv2.VideoCapture(self.input_video)
        frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        frame_number = 0
        os.makedirs(self.output_folder, exist_ok=True)
        while 1:
            ret, frame = cap.read()
            if not ret:
                break
            # x=frame_number % (frame_rate * self.interval) == 0
            # if x:print(x)
            if frame_number % (frame_rate * self.interval) == 0:
                frame_path = os.path.join(output_folder, f"frame_{frame_number}.jpg")
                cv2.imwrite(frame_path, frame)
                print(f"Saved frame {frame_number}")
            frame_number += 1
        cap.release()
        cv2.destroyAllWindows()

    def pathjoin(self, x):
        return os.path.join(self.output_folder, x)
    
    def multiply_concat(self, a, b, debug:bool = False):
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
        blended = cv2.multiply(foreground, background, scale=1/255.0)

        # Display the result
        if debug:
            cv2.imshow('Blended Image', blended)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        # Save the result
        cv2.imwrite(self.pathjoin('x.jpg'), blended)

    def composify(self, a,b,debug=False):

        a = self.pathjoin(a)
        b = self.pathjoin(b)
        foreground = cv2.imread(b)
        background = cv2.imread(a)

        # Resize the images to the same dimensions if necessary
        height, width = background.shape[:2]
        # foreground = cv2.resize(foreground, (width, height))

            # Composite the images (foreground on top of background)
        composite = cv2.addWeighted(foreground, 1, background, 1, 0)

        # Display the result
        if debug:
            cv2.imshow('Composite Image', composite)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        # Save the result
        cv2.imwrite(out:=self.pathjoin('composite.png'), composite)
        return out

    def replace_different_pixels(self, bgp, olp, output_path):
        # Open the background and overlay images
        background = Image.open(bgp)
        overlay = Image.open(olp)

        # Ensure that overlay has the same size as background
        overlay = overlay.resize(background.size)

        # Get pixel data
        background_data = background.load()
        overlay_data = overlay.load()

        # Iterate over each pixel
        for x in range(background.width):
            for y in range(background.height):
                bg_pixel = background_data[x, y][:3]
                overlay_pixel = overlay_data[x, y][:3]
                # Compare RGB values
                if dist.euclidean(bg_pixel,overlay_pixel) < 50:
                    # If pixels are different, replace background pixel with overlay pixel
                    background_data[x, y] = (*overlay_pixel, 255)

        # Save the result
        background.save(output_path, 'PNG')
        return output_path

# Usage example
if __name__=='__main__':
    input_video = './samples/flowe.mp4'
    output_folder = 'red_bud_simple'
    interval_seconds = 5
    z = Zit(input_video, output_folder, interval_seconds)
    out_initial = 'composite.png'
    frames = sorted(os.listdir(z.output_folder))
    init_b, init_o = frames[:2]
    init_b, init_o = z.pathjoin(init_b), z.pathjoin(init_o)
    out_name = ""
    for i, f in enumerate(frames[:-1]):
        if i:
            f = z.pathjoin(f)
            out_name = z.replace_different_pixels(f,out_name,out_name)
        else:
            out_name = z.replace_different_pixels(init_b,init_o,out_initial)