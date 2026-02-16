import time
from src.core.base_app import BaseApp

class AppManager:
    """
    Manages the lifecycle of apps and the main event loop.
    """
    def __init__(self, display):
        self.display = display
        self.apps = {}
        self.active_app_name = None
        self.active_app = None

    def register_app(self, name, app_instance):
        if not isinstance(app_instance, BaseApp):
            raise ValueError("App instance must inherit from BaseApp")
        self.apps[name] = app_instance
        print(f"Registered app: {name}")

    def switch_to(self, name):
        if name not in self.apps:
            print(f"Error: App '{name}' not found.")
            return

        if self.active_app:
            self.active_app.stop()

        self.active_app_name = name
        self.active_app = self.apps[name]
        self.active_app.start()
        self.display.clear()

    def run_loop(self, fps=30):
        if not self.active_app:
            print("No active app to run.")
            return

        ms_per_frame = 1.0 / fps
        
        try:
            while True:
                start_time = time.time()
                
                # Logic
                self.active_app.update()
                
                # Rendering
                self.display.clear()
                self.active_app.draw()
                self.display.update()
                
                # Timing
                elapsed = time.time() - start_time
                sleep_time = max(0, ms_per_frame - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\nExiting AppManager loop.")
            if self.active_app:
                self.active_app.stop()
