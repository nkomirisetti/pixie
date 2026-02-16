# Pixie Roadmap: Path to Production

This document outlines the strategic roadmap to transform the Pixie prototype into a consumer-ready smart device.

## Phase 1: The Core Application Framework ("The Brain")
**Goal:** Create a robust software architecture that runs on the Pi, managing multiple "Apps" (Clock, Weather, etc.) and handling display rendering seamlessly.
- [ ] **App Manager**: A system to switch between different modes/apps without restarting the script.
- [ ] **App Interface**: A standard structure for all features (e.g., `Start()`, `Update()`, `Draw()`).
- [ ] **Basic Apps**: Implement "Digital Clock" and "Text Scroller" using this new framework.
- [ ] **Config Manager**: Save settings (e.g., default app, brightness) to disk.

## Phase 2: Remote Control & API ("The Remote")
**Goal:** Control the device from a smartphone via a local web interface (a Mobile-First Web App).
- [ ] **REST/WebSocket API**: Endpoints to change the active app, update settings, and receive status.
- [ ] **Web Dashboard**: A mobile-responsive React/Vue/HTML web app hosted on the Pi.
    - *Why Web first?* It works immediately on iOS and Android without App Store friction.
- [ ] **Service Integration**: Allow the Web UI to send data to the Pi (e.g., "Set Text to 'Hello'").

## Phase 3: Connectivity & Provisioning ("The Out-of-Box Experience")
**Goal:** Seamlessly get the device online when a user unboxes it.
- [ ] **WiFi Access Point (AP) Mode**: If WiFi fails, the Pi broadcasts a "Pixie-Setup" network.
- [ ] **Captive Portal**: Connecting to "Pixie-Setup" creates a popup to enter home WiFi credentials.
- [ ] **QR Code Feature**: Display a QR code on the matrix that links to the setup page.
    - *Note*: This is often easier and more compatible than Bluetooth for initial MVPs.

## Phase 4: Advanced Features ("The Magic")
**Goal:** Implement the rich, connected features that delight the user.
- [ ] **Weather App**: Pull data from OpenWeatherMap using the user's location.
- [ ] **Spotify/Now Playing**: Integrate with Spotify API to show album art/progress.
- [ ] **Pixel Pet**: A state-machine based "Tamagotchi" style character.
- [ ] **Transit Tracker**: NYC Subway/MTA integration.

## Recommendation
We should start with **Phase 1**. Without a solid App Manager, building individual features (like Weather or Spotify) will result in spaghetti code that is hard to merge later.
