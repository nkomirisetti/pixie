from src.core.display_interface import DisplayInterface

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
except ImportError:
    # Handle case where library is not installed (e.g. on Mac)
    RGBMatrix = None
    RGBMatrixOptions = None

class RealMatrixAdapter(DisplayInterface):
    """
    Adapter that drives the real RGB Matrix hardware.
    """
    def __init__(self, width=64, height=64):
        if RGBMatrix is None:
            raise ImportError("rpi-rgb-led-matrix library not found. Are you running on the Pi?")

        self.options = RGBMatrixOptions()
        self.options.rows = height
        self.options.cols = width
        self.options.chain_length = 1
        self.options.parallel = 1
        self.options.hardware_mapping = 'adafruit-hat'
        self.options.gpio_slowdown = 4 # Adjust as needed for generic panels

        self.matrix = RGBMatrix(options=self.options)
        self.canvas = self.matrix.CreateFrameCanvas()
        self.width = width
        self.height = height

    def set_pixel(self, x, y, r, g, b):
        self.canvas.SetPixel(x, y, r, g, b)

    def fill(self, r, g, b):
        self.canvas.Fill(r, g, b)

    def clear(self):
        self.canvas.Clear()

    def update(self):
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
