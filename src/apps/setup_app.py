from src.core.base_app import BaseApp
from src.core.qr_display import draw_qr_on_display
import time


class SetupApp(BaseApp):
    """
    Display app shown during WiFi provisioning.
    Shows a QR code that connects the user's phone to the Pixie AP,
    alternating with "Connect to Pixie-XXXX" text.
    """

    def __init__(self, display, ap_ssid="Pixie", qr_data=None, config=None):
        super().__init__(display, config)
        self.ap_ssid = ap_ssid
        self.qr_data = qr_data or f"WIFI:S:{ap_ssid};T:nopass;;"
        self._show_qr = True
        self._last_toggle = time.time()
        self._toggle_interval = 5.0  # Switch between QR and text every 5s

    def update(self):
        now = time.time()
        if now - self._last_toggle > self._toggle_interval:
            self._show_qr = not self._show_qr
            self._last_toggle = now

    def draw(self):
        self.display.clear()
        if self._show_qr:
            self._draw_qr()
        else:
            self._draw_instructions()

    def _draw_qr(self):
        """Draw the WiFi QR code on the matrix."""
        draw_qr_on_display(self.display, self.qr_data)

    def _draw_instructions(self):
        """Draw simple 'SETUP' indicator with AP name."""
        d = self.display
        w, h = 64, 64

        # Pulsing blue border
        t = time.time()
        pulse = int(128 + 127 * (0.5 + 0.5 * __import__('math').sin(t * 2)))

        for x in range(w):
            d.set_pixel(x, 0, 0, 0, pulse)
            d.set_pixel(x, h - 1, 0, 0, pulse)
        for y in range(h):
            d.set_pixel(0, y, 0, 0, pulse)
            d.set_pixel(w - 1, y, 0, 0, pulse)

        # WiFi icon in center
        import math
        cx, cy = 32, 28
        for radius in [5, 10, 15]:
            for angle in range(60, 121):
                rad = math.radians(angle + 180)
                x = int(cx + radius * math.cos(rad))
                y = int(cy + radius * math.sin(rad))
                if 0 <= x < w and 0 <= y < h:
                    d.set_pixel(x, y, 100, 100, 255)

        # Dot
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                d.set_pixel(cx + dx, cy + dy, 100, 100, 255)

        # "SETUP" text using simple pixel dots at bottom
        # Draw a blinking arrow pointing at the QR
        if int(t * 2) % 2 == 0:
            for x in range(24, 40):
                d.set_pixel(x, 56, 0, 100, 255)
