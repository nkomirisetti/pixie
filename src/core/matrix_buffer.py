class MatrixBuffer:
    """
    Holds the state of the matrix pixels.
    """
    def __init__(self, width=64, height=64):
        self.width = width
        self.height = height
        # Initialize buffer with (0, 0, 0)
        self.buffer = [[(0, 0, 0) for _ in range(height)] for _ in range(width)]

    def set_pixel(self, x, y, r, g, b):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[x][y] = (r, g, b)

    def get_pixel(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.buffer[x][y]
        return (0, 0, 0)

    def fill(self, r, g, b):
        for x in range(self.width):
            for y in range(self.height):
                self.buffer[x][y] = (r, g, b)

    def clear(self):
        self.fill(0, 0, 0)

    def get_buffer(self):
        return self.buffer
