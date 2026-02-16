import time
from src.core.base_app import BaseApp
from src.core.logger import get_logger

log = get_logger()

MAX_CONSECUTIVE_ERRORS = 3


class AppManager:
    """
    Manages the lifecycle of apps and the main event loop.
    Handles per-frame errors gracefully with auto-recovery.
    """
    def __init__(self, display):
        self.display = display
        self.apps = {}
        self.active_app_name = None
        self.active_app = None
        self._error_count = 0  # consecutive errors for active app

    def register_app(self, name, app_instance):
        if not isinstance(app_instance, BaseApp):
            raise ValueError("App instance must inherit from BaseApp")
        self.apps[name] = app_instance
        log.info(f"Registered app: {name}")

    def switch_to(self, name):
        if name not in self.apps:
            log.warning(f"App '{name}' not found.")
            return

        if self.active_app:
            try:
                self.active_app.stop()
            except Exception as e:
                log.error(f"Error stopping {self.active_app_name}: {e}")

        self.active_app_name = name
        self.active_app = self.apps[name]
        self._error_count = 0

        try:
            self.active_app.start()
            log.info(f"Switched to app: {name}")
        except Exception as e:
            log.error(f"Error starting {name}: {e}")
            self._handle_app_failure(name)

        self.display.clear()

    def _handle_app_failure(self, failed_app_name):
        """When an app exceeds max errors, switch to the next available app."""
        log.error(f"App '{failed_app_name}' failed {MAX_CONSECUTIVE_ERRORS} times, switching away.")

        # Find another app to switch to
        for name in self.apps:
            if name != failed_app_name:
                log.info(f"Falling back to app: {name}")
                self.active_app_name = name
                self.active_app = self.apps[name]
                self._error_count = 0
                try:
                    self.active_app.start()
                    return
                except Exception as e:
                    log.error(f"Fallback app '{name}' also failed: {e}")

        # All apps failed — stay on current but reset counter
        log.error("All apps failed. Showing error screen.")
        self._error_count = 0

    def run_loop(self, fps=30):
        if not self.active_app:
            log.warning("No active app to run.")
            return

        ms_per_frame = 1.0 / fps

        try:
            while True:
                start_time = time.time()

                try:
                    # Logic
                    self.active_app.update()

                    # Rendering
                    self.display.clear()
                    self.active_app.draw()
                    self.display.update()

                    # Success — reset error counter
                    if self._error_count > 0:
                        log.info(f"App '{self.active_app_name}' recovered after {self._error_count} error(s).")
                    self._error_count = 0

                except Exception as e:
                    self._error_count += 1
                    log.error(f"Frame error in '{self.active_app_name}' "
                              f"({self._error_count}/{MAX_CONSECUTIVE_ERRORS}): {e}")

                    # Show error state on display
                    try:
                        self.display.clear()
                        self.active_app.draw_error()
                        self.display.update()
                    except Exception:
                        pass  # Even error drawing failed, just skip the frame

                    if self._error_count >= MAX_CONSECUTIVE_ERRORS:
                        self._handle_app_failure(self.active_app_name)

                # Timing
                elapsed = time.time() - start_time
                sleep_time = max(0, ms_per_frame - elapsed)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            log.info("Exiting AppManager loop.")
            if self.active_app:
                try:
                    self.active_app.stop()
                except Exception:
                    pass
