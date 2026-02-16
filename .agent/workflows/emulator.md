---
description: Run Pixie locally in emulator mode for development
---

# Run Emulator

This workflow starts Pixie in emulator mode on the local Mac. No Pi required.

Everything runs on a single port (5002):
- **http://127.0.0.1:5002/** — Remote control UI (app switcher)
- **http://127.0.0.1:5002/emulator** — Matrix pixel grid (WebSocket real-time)

## Steps

// turbo-all

1. Start the emulator:
```bash
cd /Users/nikhilkomirisetti/projects/Pixie && python3 run_pixie.py --emulator
```

2. Open the emulator in the browser (navigate to http://127.0.0.1:5002/emulator)

3. Open the remote in the browser (navigate to http://127.0.0.1:5002/)

### Dev Mode (auto-reload on file changes)

```bash
cd /Users/nikhilkomirisetti/projects/Pixie && python3 run_pixie.py --emulator --dev
```
