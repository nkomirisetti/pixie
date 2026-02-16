import argparse
import time
import sys
import os


def main():
    parser = argparse.ArgumentParser(description='Pixie Display Controller')
    parser.add_argument('--emulator', action='store_true', help='Run in web emulator mode')
    parser.add_argument('--app', type=str, help='Initial app to start (clock, weather)')
    parser.add_argument('--dev', action='store_true', help='Enable dev mode with auto-reload on file changes')
    args = parser.parse_args()

    # Dev mode: wrap in a file-watching restart loop
    if args.dev:
        _run_with_reload(args)
        return

    _run_app(args)


def _run_app(args):
    """Normal application startup with top-level error handling."""
    from src.core.logger import get_logger
    log = get_logger()

    try:
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

        clock = ClockApp(display)
        weather = WeatherApp(display)

        app_manager.register_app("clock", clock)
        app_manager.register_app("weather", weather)

        # --- Web Controller Setup (unified server) ---
        from src.core.web_controller import WebController
        controller_port = 5002 if args.emulator else 5000
        emulator_display = display if args.emulator else None
        controller = WebController(app_manager, port=controller_port, emulator_display=emulator_display)

        # Set default app
        if args.app and args.app in app_manager.apps:
            app_manager.switch_to(args.app)
        else:
            app_manager.switch_to("clock")

        # Run loop
        log.info("Starting Pixie OS...")
        app_manager.run_loop(fps=30)

    except KeyboardInterrupt:
        log.info("Pixie shutdown by user.")
    except Exception as e:
        log.critical(f"Fatal startup error: {e}", exc_info=True)
        # Try to show error on display if possible
        try:
            display.clear()
            for x in range(64):
                for y in range(64):
                    if (x + y) % 4 == 0:
                        display.set_pixel(x, y, 255, 0, 0)
            display.update()
        except Exception:
            pass
        sys.exit(1)


def _run_with_reload(args):
    """Run with file-watching auto-reload for development."""
    import subprocess

    print("🔄 Dev mode: watching src/ for changes...")

    # Build the command to run without --dev (to avoid infinite recursion)
    cmd = [sys.executable, '-u', __file__, '--emulator']
    if args.app:
        cmd.extend(['--app', args.app])

    while True:
        process = subprocess.Popen(cmd)
        try:
            # Wait for file changes
            _wait_for_changes('src/')
            print("\n🔄 File change detected, restarting...")
            process.terminate()
            process.wait(timeout=5)
        except KeyboardInterrupt:
            process.terminate()
            process.wait(timeout=5)
            print("\nDev mode stopped.")
            break


def _wait_for_changes(watch_dir):
    """Block until a .py or .html file changes in watch_dir."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        import threading

        changed = threading.Event()

        class Handler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path.endswith(('.py', '.html', '.css', '.js')):
                    changed.set()

        observer = Observer()
        observer.schedule(Handler(), watch_dir, recursive=True)
        observer.start()
        changed.wait()  # Block until a file changes
        observer.stop()
    except ImportError:
        # Fallback: simple polling if watchdog isn't installed
        import hashlib

        def hash_dir(d):
            h = hashlib.md5()
            for root, _, files in os.walk(d):
                for f in sorted(files):
                    if f.endswith(('.py', '.html', '.css', '.js')):
                        path = os.path.join(root, f)
                        h.update(os.path.getmtime(path).__str__().encode())
            return h.hexdigest()

        snapshot = hash_dir(watch_dir)
        while True:
            time.sleep(1)
            if hash_dir(watch_dir) != snapshot:
                return


if __name__ == "__main__":
    main()
