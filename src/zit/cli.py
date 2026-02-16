import argparse
import sys
from .core import Zit

def main():
    parser = argparse.ArgumentParser(description="ZIT: Zooplankton Image Tool")
    parser.add_argument("--input", "-i", type=str, help="Input video path")
    parser.add_argument("--output", "-o", type=str, default="frames/basic", help="Output folder for frames")
    parser.add_argument("--interval", type=int, default=1, help="Interval in seconds for frame capture")
    parser.add_argument("--epsilon", type=float, default=20.0, help="Composite epsilon")
    parser.add_argument("--noise", type=float, default=50.0, help="Noise delta")
    parser.add_argument("--composite", action="store_true", help="Perform composition after capture")
    parser.add_argument("--out-file", type=str, default="composited.png", help="Output file name for composition")
    parser.add_argument("--skip", type=int, nargs=2, metavar=("START", "END"), help="Start and end frames to skip to")

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    z = Zit(
        input_video=args.input,
        output_folder=args.output,
        interval=args.interval,
        composite_epsilon=args.epsilon,
        noise_delta=args.noise
    )

    print(f"Capturing frames from {args.input}...")
    z.capture_frames()

    if args.composite:
        print(f"Creating composite: {args.out_file}...")
        skip_tuple = tuple(args.skip) if args.skip else None
        z.composite_from_frames(args.out_file, skip=skip_tuple)
        print("Done.")

if __name__ == "__main__":
    main()
