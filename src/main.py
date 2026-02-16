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
    parser.add_argument('--app', type=str, help='Initial app to start (clock, weather)')
    args = parser.parse_args()

    display: DisplayInterface

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
