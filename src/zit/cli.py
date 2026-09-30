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

import argparse
import sys
from .core import Zit

def main():
    parser = argparse.ArgumentParser(description="ZIT: Zooplankton Image Tool")
    parser.add_argument("--input", "-i", type=str, help="Input video path")
    parser.add_argument("--output", "-o", type=str, default="frames/basic", help="Output folder for frames")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval in seconds for frame capture (fractions allowed, e.g. 0.25)")
    parser.add_argument("--epsilon", type=float, default=20.0, help="Composite epsilon")
    parser.add_argument("--noise", type=float, default=50.0, help="Noise delta")
    parser.add_argument("--composite", action="store_true", help="Perform composition after capture")
    parser.add_argument("--entities", action="store_true", help="Use entity recognition for composition")
    parser.add_argument("--out-file", type=str, default="composited.png", help="Output file name for composition")
    parser.add_argument("--trails", action="store_true", help="Draw tracked entity paths onto the composite (requires --entities)")
    parser.add_argument("--tracks-csv", type=str, help="Write tracked entity positions to this CSV (requires --entities)")
    parser.add_argument("--max-jump", type=float, default=50.0, help="Max pixels an entity may move between sampled frames and keep its track")
    parser.add_argument("--min-track-points", type=int, default=4, help="Min sightings for a track to count as a swimmer")
    parser.add_argument("--min-straightness", type=float, default=0.7, help="Min net-displacement/path-length (0-1) for a track to count as a swimmer")
    parser.add_argument("--track-merge", type=float, default=0.0, help="Fuse fragments within this fraction of the frame size before tracking; use ~0.05-0.1 for large animals (0 = off)")
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
        z.composite_from_frames(
            args.out_file,
            skip=skip_tuple,
            use_entities=args.entities,
            trails=args.trails,
            tracks_csv=args.tracks_csv,
            max_jump=args.max_jump,
            min_track_points=args.min_track_points,
            min_straightness=args.min_straightness,
            track_merge=args.track_merge,
        )
        print("Done.")

if __name__ == "__main__":
    main()
