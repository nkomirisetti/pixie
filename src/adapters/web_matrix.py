from src.core.display_interface import DisplayInterface
from src.core.matrix_buffer import MatrixBuffer


class WebMatrixAdapter(DisplayInterface):
    """
    Adapter that holds a pixel buffer for the web emulator.
    The actual serving is done by WebController when in emulator mode.
    """
    def __init__(self, width=64, height=64):
        super().__init__()
        self.width = width
        self.height = height
        self.buffer = MatrixBuffer(width, height)
        self._socketio = None

    def set_socketio(self, socketio):
        """Called by WebController to enable WebSocket frame push."""
        self._socketio = socketio

    def set_brightness(self, value):
        """Set emulated brightness (0-100). Applied as alpha scaling in the browser."""
        self._brightness = max(0, min(100, int(value)))

    def set_pixel(self, x, y, r, g, b):
        # Scale by brightness for visual accuracy in emulator
        scale = self._brightness / 100.0
        self.buffer.set_pixel(x, y, int(r * scale), int(g * scale), int(b * scale))

    def fill(self, r, g, b):
        scale = self._brightness / 100.0
        self.buffer.fill(int(r * scale), int(g * scale), int(b * scale))

    def clear(self):
        self.buffer.clear()

    def update(self):
        """Push the current frame to connected browsers via WebSocket."""
        if self._socketio:
            self._socketio.emit('frame', self.buffer.get_buffer())

    def get_matrix_data(self):
        """Return buffer data (used by WebController for HTTP fallback)."""
        return self.buffer.get_buffer()
