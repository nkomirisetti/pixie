from src.core.display_interface import DisplayInterface
from src.core.matrix_buffer import MatrixBuffer


class WebMatrixAdapter(DisplayInterface):
    """
    Adapter that holds a pixel buffer for the web emulator.
    The actual serving is done by WebController when in emulator mode.
    """
    def __init__(self, width=64, height=64):
        self.width = width
        self.height = height
        self.buffer = MatrixBuffer(width, height)
        self._socketio = None  # Set by WebController

    def set_socketio(self, socketio):
        """Called by WebController to enable WebSocket frame push."""
        self._socketio = socketio

    def set_pixel(self, x, y, r, g, b):
        self.buffer.set_pixel(x, y, r, g, b)

    def fill(self, r, g, b):
        self.buffer.fill(r, g, b)

    def clear(self):
        self.buffer.clear()

    def update(self):
        """Push the current frame to connected browsers via WebSocket."""
        if self._socketio:
            self._socketio.emit('frame', self.buffer.get_buffer())

    def get_matrix_data(self):
        """Return buffer data (used by WebController for HTTP fallback)."""
        return self.buffer.get_buffer()
