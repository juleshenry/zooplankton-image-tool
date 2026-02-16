import os
import sys
import shutil
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Add src to sys.path to allow imports
sys.path.append(os.getcwd())
from src.zit.core import Zit

def create_grid(video_path, output_grid_path):
    video_name = os.path.basename(video_path)
    # Sweeping Noise Delta and Composite Epsilon (5x5 grid)
    noise_deltas = [0, 50, 100, 150, 200]
    epsilons = [0, 20, 40, 60, 80]
    
    # Fix interval to 1 second for the sweep
    fixed_interval = 1
    
    temp_base = f"temp_sweep_{video_name.replace('.', '_')}"
    os.makedirs(temp_base, exist_ok=True)
    
    # Capture frames once per video since interval is fixed
    frames_dir = os.path.join(temp_base, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    z = Zit(
        input_video=video_path,
        output_folder=frames_dir,
        interval=fixed_interval
    )
    print(f"Capturing frames for {video_name}...")
    z.capture_frames()
    
    composites = {} # (noise, epsilon) -> path
    
    for i, epsilon in enumerate(epsilons):
        for j, noise in enumerate(noise_deltas):
            z.composite_epsilon = float(epsilon)
            z.noise_delta = float(noise)
            out_file = os.path.join(temp_base, f"comp_e{epsilon}_n{noise}.png")
            print(f"Creating composite {video_name} | Epsilon {epsilon} | Noise {noise}...")
            z.composite_from_frames(out_file, use_entities=True)
            if os.path.exists(out_file):
                composites[(epsilon, noise)] = out_file

    if not composites:
        print(f"No composites created for {video_name}")
        return

    # Create the grid
    sample_img = Image.open(next(iter(composites.values())))
    w, h = sample_img.size
    
    # Scale down images for the grid
    scale = 0.5
    sw, sh = int(w * scale), int(h * scale)
    
    margin_left = 180
    margin_top = 100
    grid_w = sw * len(noise_deltas) + margin_left
    grid_h = sh * len(epsilons) + margin_top
    
    grid_img = Image.new("RGB", (grid_w, grid_h), (255, 255, 255))
    draw = ImageDraw.Draw(grid_img)
    
    try:
        # Common paths for Helvetica on macOS
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except:
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()

    for i, epsilon in enumerate(epsilons):
        y = i * sh + margin_top
        draw.text((10, y + sh // 2 - 12), f"Thresh: {epsilon}", fill=(0, 0, 0), font=font)
        for j, noise in enumerate(noise_deltas):
            x = j * sw + margin_left
            if i == 0:
                draw.text((x + sw // 2 - 40, 10), f"MinArea: {noise}", fill=(0, 0, 0), font=font)
            
            img_path = composites.get((epsilon, noise))
            if img_path:
                img = Image.open(img_path).resize((sw, sh), Image.Resampling.LANCZOS)
                grid_img.paste(img, (x, y))

    grid_img.save(output_grid_path)
    print(f"Saved sweep grid to {output_grid_path}")

    # Cleanup temporary files
    shutil.rmtree(temp_base)
    print(f"Cleaned up {temp_base}")

def main():
    video_dir = "videos"
    if not os.path.exists(video_dir):
        print(f"Directory {video_dir} not found.")
        return
    videos = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".mp4")]
    
    for video in videos:
        grid_name = f"sweep_grid_{os.path.basename(video)}.png"
        create_grid(video, grid_name)

if __name__ == "__main__":
    main()
