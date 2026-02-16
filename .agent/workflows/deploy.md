---
description: Deploy Pixie code to the Raspberry Pi and restart the service
---

# Deploy to Pi

This workflow deploys the current code to the Raspberry Pi and restarts the Pixie service.

**Pi Details:**
- Hostname: `pixie1.local` (IP fallback: check with `sshpass -p "pixie" ssh pi@pixie1.local "hostname -I"`)
- User: `pi`, Password: `pixie`
- Project path on Pi: `/home/pi/pixie`
- Service name: `pixie`

## Steps

// turbo-all

1. Sync all source files to the Pi:
```bash
sshpass -p "pixie" rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='.agent' --exclude='node_modules' -e ssh /Users/nikhilkomirisetti/projects/Pixie/ pi@pixie1.local:pixie/
```

2. Restart the Pixie service:
```bash
sshpass -p "pixie" ssh pi@pixie1.local "sudo systemctl restart pixie"
```

3. Wait 3 seconds, then check the service status:
```bash
sleep 3 && sshpass -p "pixie" ssh pi@pixie1.local "sudo systemctl status pixie --no-pager -l"
```

4. Verify the web server is responding:
```bash
curl -s --connect-timeout 5 http://pixie1.local:5000/api/status
```

5. If verification fails, check logs:
```bash
sshpass -p "pixie" ssh pi@pixie1.local "sudo journalctl -u pixie --no-pager -n 30"
```
