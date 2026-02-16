from src.core.base_app import BaseApp

class WeatherApp(BaseApp):
    def __init__(self, display, config=None):
        super().__init__(display, config)

    def update(self):
        # Weather update logic (e.g. fetch API every 10 mins)
        pass

    def draw(self):
        # Simple representation: A sun icon (yellow circle)
        self.display.clear()
        
        # Draw a yellow sun
        cx, cy = 32, 20
        radius = 8
        for x in range(cx - radius, cx + radius):
            for y in range(cy - radius, cy + radius):
                if (x - cx)**2 + (y - cy)**2 <= radius**2:
                    self.display.set_pixel(x, y, 255, 255, 0)
        
        # Some blue "rain" or ground
        for x in range(0, 64, 4):
            self.display.set_pixel(x, 60, 0, 0, 200)
