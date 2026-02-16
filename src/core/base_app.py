from abc import ABC, abstractmethod
import time

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
        print(f"App {self.__class__.__name__} started.")

    def stop(self):
        """Called when the app becomes inactive."""
        self.is_active = False
        print(f"App {self.__class__.__name__} stopped.")

    @abstractmethod
    def update(self):
        """Called every frame to update application logic."""
        pass

    @abstractmethod
    def draw(self):
        """Called every frame to render to the display."""
        pass
