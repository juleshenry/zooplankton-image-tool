import cv2
import os

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

            if frame_number % (frame_rate * self.interval) == 0:
                frame_path = os.path.join(output_folder, f"frame_{frame_number}.jpg")
                cv2.imwrite(frame_path, frame)
                print(f"Saved frame {frame_number}")
            frame_number += 1
        cap.release()
        cv2.destroyAllWindows()

# Usage example
if __name__=='__main__':
    a,b,c=1,2,3
    input_video = './samples/red_bud_isle_simple.mp4'
    output_folder = 'red_bud_simple'
    interval_seconds = 1
    z = Zit(input_video, output_folder, interval_seconds)
    z.capture_frames()
