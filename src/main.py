import argparse
import time
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.display_interface import DisplayInterface

def main():
    parser = argparse.ArgumentParser(description='Pixie Display Controller')
    parser.add_argument('--emulator', action='store_true', help='Run in web emulator mode')
    args = parser.parse_args()

    display: DisplayInterface

    if args.emulator:
        from src.adapters.web_matrix import WebMatrixAdapter
        display = WebMatrixAdapter()
    else:
        from src.adapters.real_matrix import RealMatrixAdapter
        display = RealMatrixAdapter()

    # Simple animation loop
    print("Starting animation loop...")
    x = 0
    y = 0
    dx = 1
    dy = 1
    
    try:
        while True:
            display.clear()
            
            # Draw a moving white pixel
            display.set_pixel(x, y, 255, 255, 255)
            
            # Simple bouncing logic
            x += dx
            y += dy
            
            if x <= 0 or x >= 63: dx *= -1
            if y <= 0 or y >= 63: dy *= -1
            
            display.update()
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
