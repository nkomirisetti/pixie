# Pixie Roadmap: Path to Production

## Phase 1: Core Application Framework ✅
- [x] App Manager with hot-switching
- [x] App Interface (`start()`, `update()`, `draw()`)
- [x] Clock & Weather apps
- [ ] Config Manager (persist settings to disk)

## Phase 2: Remote Control & API ✅
- [x] REST API (`/api/status`, `/api/switch`)
- [x] Mobile-responsive web remote (`remote.html`)
- [x] Systemd service for auto-start on boot
- [ ] Service Integration (send data to apps, e.g., "Set Text to 'Hello'")

## Phase 2.5: Production Hardening 🔧
**Goal:** Make the device reliable enough to hand to a non-technical user.

### Security
- [ ] Web API authentication (PIN or API key)
- [ ] Change default SSH credentials or disable password auth
- [ ] HTTPS support (self-signed cert)

### Reliability
- [ ] SD card resilience (read-only overlay filesystem)
- [ ] Graceful error handling in all apps (network down, API failures)
- [ ] Watchdog timer to recover from hard hangs
- [ ] Graceful shutdown on power loss

### OTA Updates
- [ ] "Check for updates" button in web UI
- [ ] Auto-update mechanism (pull from GitHub releases)
- [ ] Version display in web UI

### Hardware Controls
- [ ] Brightness control (manual via web UI)
- [ ] Auto-dimming (time-based schedule or light sensor)
- [ ] Display on/off schedule (sleep mode)

### User Configuration
- [ ] Timezone selection (first-run + settings)
- [ ] Location setting (for Weather, Transit)
- [ ] Device naming (avoid multi-device hostname collisions)
- [ ] Factory reset (physical button combo)

## Phase 3: WiFi Provisioning 📡
**Goal:** Seamless out-of-box WiFi setup.
- [ ] AP mode fallback ("Pixie-Setup" network)
- [ ] Captive portal for WiFi credential entry
- [ ] QR code on matrix linking to setup page
- [ ] mDNS / device discovery for Android compatibility

## Phase 4: Advanced Features ✨
- [ ] Weather App (OpenWeatherMap integration)
- [ ] Spotify / Now Playing (album art, progress bar)
- [ ] Pixel Pet (Tamagotchi-style state machine)
- [ ] Transit Tracker (NYC MTA integration)
- [ ] Custom text/image display via API
- [ ] Notification relay (phone → matrix)

## Phase 5: Polish & Ship 🚀
- [ ] App Store-style browsable app catalog in web UI
- [ ] Usage analytics (optional, anonymized)
- [ ] Documentation & user guide
- [ ] Packaging & enclosure design
- [ ] Production SD card image creation
