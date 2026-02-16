import logging
import os
from logging.handlers import RotatingFileHandler

# Singleton logger for the entire Pixie application
_logger = None


def get_logger():
    """Get the shared Pixie logger. Creates it on first call."""
    global _logger
    if _logger is not None:
        return _logger

    _logger = logging.getLogger('pixie')
    _logger.setLevel(logging.DEBUG)

    # Console handler (INFO and above)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(message)s'))
    _logger.addHandler(console)

    # File handler (rotating, all levels)
    log_path = os.path.expanduser('~/pixie.log')
    try:
        file_handler = RotatingFileHandler(
            log_path, maxBytes=1_000_000, backupCount=3
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        _logger.addHandler(file_handler)
    except Exception:
        _logger.warning(f"Could not create log file at {log_path}")

    return _logger
