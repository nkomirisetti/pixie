from abc import ABC, abstractmethod

class DisplayInterface(ABC):
    """
    Abstract base class for display adapters.
    Defines the contract for drawing to a display (hardware or virtual).
    """

    @abstractmethod
    def set_pixel(self, x, y, r, g, b):
        """Sets a single pixel at (x, y) to color (r, g, b)."""
        pass

    @abstractmethod
    def fill(self, r, g, b):
        """Fills the entire display with color (r, g, b)."""
        pass

    @abstractmethod
    def clear(self):
        """Clears the display (sets all pixels to black)."""
        pass

    @abstractmethod
    def update(self):
        """Refreshes the display (if needed)."""
        pass
