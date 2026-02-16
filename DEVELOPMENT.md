# Pixie Developer Guide

## Architecture

Pixie is a smart LED matrix display (64×64 RGB) running on a Raspberry Pi Zero 2 W. The software follows a clean adapter pattern:

```
run_pixie.py                    # Entry point
├── src/core/app_manager.py     # Game loop: update() → draw() → display.update()
├── src/core/base_app.py        # Abstract base class for apps
├── src/core/web_controller.py  # Unified Flask+SocketIO server (remote + emulator)
├── src/core/display_interface.py  # Abstract display interface
├── src/core/matrix_buffer.py   # 64×64 pixel buffer
├── src/adapters/
│   ├── real_matrix.py          # Pi hardware (rgbmatrix library)
│   └── web_matrix.py           # Browser emulator (buffer + SocketIO emit)
├── src/apps/
│   ├── clock_app.py            # Digital clock
│   └── weather_app.py          # Weather display
└── src/web/templates/
    ├── index.html              # Emulator UI (WebSocket canvas)
    └── remote.html             # Remote control UI
```

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run locally (no Pi needed)
python3 run_pixie.py --emulator

# Dev mode (auto-restart on file changes)
python3 run_pixie.py --emulator --dev
```

Then open:
- **http://127.0.0.1:5002/** — Remote control (switch apps)
- **http://127.0.0.1:5002/emulator** — Matrix emulator (live pixel view)

## Adding a New App

1. Create `src/apps/my_app.py`:
```python
from src.core.base_app import BaseApp

class MyApp(BaseApp):
    def update(self):
        pass  # Logic runs every frame

    def draw(self):
        # Draw to self.display (64x64 grid)
        self.display.set_pixel(32, 32, 255, 0, 0)  # Red pixel at center
```

2. Register it in `run_pixie.py`:
```python
from src.apps.my_app import MyApp
my_app = MyApp(display)
app_manager.register_app("my_app", my_app)
```

The web remote auto-discovers registered apps.

## Display API

```python
display.set_pixel(x, y, r, g, b)  # Set one pixel (0-255 RGB)
display.fill(r, g, b)              # Fill entire display
display.clear()                     # Set all pixels to black
display.update()                    # Push frame to display/browser
```

Coordinates: `(0,0)` is top-left, `(63,63)` is bottom-right.

## Deploying to Pi

```bash
# One-command deploy (rsync + restart service)
# See .agent/workflows/deploy.md

# Manual steps:
sshpass -p "pixie" rsync -avz --exclude='.git' --exclude='__pycache__' \
  -e ssh ./ pi@pixie1.local:pixie/
sshpass -p "pixie" ssh pi@pixie1.local "sudo systemctl restart pixie"
```

**Pi details:** Host `pixie1.local`, user `pi`, password `pixie`, project at `/home/pi/pixie`

## Pi-Specific Notes

- The `rgbmatrix` library requires **root** to access GPIO. The systemd service runs as root.
- `drop_privileges = False` must stay set in `real_matrix.py` or the web server loses file access.
- `load_dotenv=False` is required in Flask's `app.run()` on the Pi.
- The systemd service (`pixie.service`) auto-starts on boot and restarts on crash.

## Web Server Architecture

A single `WebController` Flask+SocketIO server handles everything:
- On Pi: serves the remote UI on port **5000**
- In emulator: serves remote + emulator on port **5002**, pushes frames via WebSocket

The emulator is opt-in: `WebController(app_manager, port=5002, emulator_display=display)`
