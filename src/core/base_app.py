from abc import ABC, abstractmethod


class BaseApp(ABC):
    """
    Base class for all Pixie applications.
    """
    def __init__(self, display, config=None):
        self.display = display
        self.config = config or {}
        self.is_active = False

    def start(self):
        """Called when the app becomes active."""
        self.is_active = True

    def stop(self):
        """Called when the app becomes inactive."""
        self.is_active = False

    @abstractmethod
    def update(self):
        """Called every frame to update application logic."""
        pass

    @abstractmethod
    def draw(self):
        """Called every frame to render to the display."""
        pass

    def draw_error(self, message="ERR"):
        """
        Draw a simple error indicator on the display.
        Red border with a red '!' in the center.
        Can be called by AppManager when an app crashes.
        """
        d = self.display
        w, h = 64, 64

        # Red border
        for x in range(w):
            d.set_pixel(x, 0, 255, 0, 0)
            d.set_pixel(x, 1, 255, 0, 0)
            d.set_pixel(x, h - 1, 255, 0, 0)
            d.set_pixel(x, h - 2, 255, 0, 0)
        for y in range(h):
            d.set_pixel(0, y, 255, 0, 0)
            d.set_pixel(1, y, 255, 0, 0)
            d.set_pixel(w - 1, y, 255, 0, 0)
            d.set_pixel(w - 2, y, 255, 0, 0)

        # Exclamation mark in center (red on black)
        cx = w // 2
        # Vertical bar of !
        for y in range(20, 38):
            d.set_pixel(cx, y, 255, 50, 50)
            d.set_pixel(cx - 1, y, 255, 50, 50)
        # Dot of !
        for dy in range(42, 45):
            d.set_pixel(cx, dy, 255, 50, 50)
            d.set_pixel(cx - 1, dy, 255, 50, 50)
