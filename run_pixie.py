import argparse
import time
import sys
import os

print("DEBUG: STARTING PIXIE ROOT MAIN V2")

from src.core.display_interface import DisplayInterface
from src.core.matrix_buffer import MatrixBuffer

def main():
    parser = argparse.ArgumentParser(description='Pixie Display Controller')
    parser.add_argument('--emulator', action='store_true', help='Run in web emulator mode')
    parser.add_argument('--app', type=str, help='Initial app to start (clock, weather)')
    args = parser.parse_args()

    # display: DisplayInterface

    if args.emulator:
        from src.adapters.web_matrix import WebMatrixAdapter
        display = WebMatrixAdapter()
    else:
        from src.adapters.real_matrix import RealMatrixAdapter
        display = RealMatrixAdapter()

    # --- App Manager Setup ---
    from src.core.app_manager import AppManager
    from src.apps.clock_app import ClockApp
    from src.apps.weather_app import WeatherApp
    
    app_manager = AppManager(display)
    
    # Register Apps
    clock = ClockApp(display)
    weather = WeatherApp(display)
    
    app_manager.register_app("clock", clock)
    app_manager.register_app("weather", weather)
    
    # --- Web Controller Setup ---
    from src.core.web_controller import WebController
    # Use port 5000 on Pi
    controller_port = 5002 if args.emulator else 5000
    controller = WebController(app_manager, port=controller_port)

    # Set default app
    if args.app and args.app in ["clock", "weather"]:
        app_manager.switch_to(args.app)
    else:
        app_manager.switch_to("clock")
    
    # Run loop
    print("Starting Pixie OS...")
    try:
        app_manager.run_loop(fps=30)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
