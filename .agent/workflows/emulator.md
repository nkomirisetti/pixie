---
description: Run Pixie locally in emulator mode for development
---

# Run Emulator

This workflow starts Pixie in emulator mode on the local Mac. No Pi required.

## Ports
- **5001**: Matrix emulator (visual pixel grid) — open in browser
- **5002**: Pixie Remote (app switcher UI)

## Steps

// turbo-all

1. Start the emulator:
```bash
cd /Users/nikhilkomirisetti/projects/Pixie && python3 run_pixie.py --emulator
```

2. Open the emulator in the browser (navigate to http://127.0.0.1:5001)

3. Open the remote in the browser (navigate to http://127.0.0.1:5002)
