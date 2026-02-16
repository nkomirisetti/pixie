#!/bin/bash
# ============================================================
# Pixie SD Card Flash Script
# Creates a production-ready SD card for a new Pixie device.
#
# Prerequisites:
#   - A "golden" Pixie image file (created with create_image.sh)
#   - OR a running configured Pi to rsync from
#
# Usage:
#   ./tools/flash.sh <sd-card-device> [image-file]
#
# Examples:
#   ./tools/flash.sh /dev/disk4              # Flash + provision from source
#   ./tools/flash.sh /dev/disk4 pixie.img    # Flash from image
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

usage() {
    echo "Usage: $0 <sd-card-device> [image-file]"
    echo ""
    echo "  sd-card-device  e.g. /dev/disk4 (macOS) or /dev/sdb (Linux)"
    echo "  image-file      Optional golden image to flash"
    echo ""
    echo "If no image file is given, you must have Raspberry Pi Imager installed."
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

DISK="$1"
IMAGE="${2:-}"

# Safety check
echo -e "${RED}WARNING: This will ERASE ALL DATA on ${DISK}${NC}"
echo -n "Type 'yes' to continue: "
read CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Generate unique device ID from timestamp
DEVICE_ID=$(openssl rand -hex 2 | tr '[:lower:]' '[:upper:]')
HOSTNAME="pixie-${DEVICE_ID}"

echo -e "${GREEN}Device hostname will be: ${HOSTNAME}${NC}"

# --- Step 1: Flash the image ---
if [ -n "$IMAGE" ]; then
    echo -e "${YELLOW}Flashing image: ${IMAGE}${NC}"

    # Unmount disk first
    if [[ "$OSTYPE" == "darwin"* ]]; then
        diskutil unmountDisk "$DISK" 2>/dev/null || true
        RDISK="${DISK/disk/rdisk}"
        sudo dd if="$IMAGE" of="$RDISK" bs=4m status=progress
        sync
    else
        sudo umount "${DISK}"* 2>/dev/null || true
        sudo dd if="$IMAGE" of="$DISK" bs=4M status=progress
        sync
    fi

    echo -e "${GREEN}Image flashed successfully.${NC}"
else
    echo -e "${YELLOW}No image file provided.${NC}"
    echo "Please flash Raspberry Pi OS Lite (64-bit) using Raspberry Pi Imager first."
    echo "Set username: pi, password: pixie, enable SSH, set hostname to: ${HOSTNAME}"
    echo ""
    echo "After flashing, run this script again with --provision flag."
    exit 0
fi

# --- Step 2: Mount and configure ---
echo -e "${YELLOW}Mounting and configuring...${NC}"

if [[ "$OSTYPE" == "darwin"* ]]; then
    sleep 3
    diskutil mountDisk "$DISK"
    BOOT_MOUNT="/Volumes/bootfs"
    ROOT_MOUNT="/Volumes/rootfs"
else
    sleep 2
    BOOT_MOUNT=$(mktemp -d)
    ROOT_MOUNT=$(mktemp -d)
    sudo mount "${DISK}1" "$BOOT_MOUNT"
    sudo mount "${DISK}2" "$ROOT_MOUNT"
fi

# Enable SSH
touch "${BOOT_MOUNT}/ssh"

# Set hostname
if [ -d "$ROOT_MOUNT" ]; then
    echo "$HOSTNAME" | sudo tee "${ROOT_MOUNT}/etc/hostname" > /dev/null
    sudo sed -i.bak "s/127.0.1.1.*/127.0.1.1\t${HOSTNAME}/" "${ROOT_MOUNT}/etc/hosts"
fi

# --- Step 3: Copy Pixie project ---
if [ -d "$ROOT_MOUNT/home/pi" ]; then
    echo -e "${YELLOW}Copying Pixie project files...${NC}"
    sudo mkdir -p "${ROOT_MOUNT}/home/pi/pixie"
    sudo rsync -a --exclude='.git' --exclude='__pycache__' --exclude='.agent' \
        "${PROJECT_DIR}/" "${ROOT_MOUNT}/home/pi/pixie/"
    sudo chown -R 1000:1000 "${ROOT_MOUNT}/home/pi/pixie"
fi

# --- Step 4: Create first-boot script ---
if [ -d "$ROOT_MOUNT" ]; then
    echo -e "${YELLOW}Creating first-boot provisioning script...${NC}"
    sudo tee "${ROOT_MOUNT}/home/pi/first-boot.sh" > /dev/null << 'FIRSTBOOT'
#!/bin/bash
# Pixie first-boot provisioning — runs once and deletes itself
set -e

LOG="/home/pi/first-boot.log"
exec > "$LOG" 2>&1

echo "=== Pixie First Boot ==="
echo "$(date)"

# Wait for network or proceed without
sleep 10

# Install Python dependencies
echo "Installing Python packages..."
pip3 install -r /home/pi/pixie/requirements.txt --break-system-packages || \
    python3 -m pip install -r /home/pi/pixie/requirements.txt --break-system-packages

# Install and enable the Pixie service
echo "Setting up systemd service..."
cat > /etc/systemd/system/pixie.service << 'EOF'
[Unit]
Description=Pixie Display Controller
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/pixie
ExecStart=/usr/bin/python3 /home/pi/pixie/run_pixie.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable pixie
systemctl start pixie

echo "Pixie service installed and started."

# Self-destruct
rm -f /home/pi/first-boot.sh
rm -f /etc/systemd/system/pixie-firstboot.service

echo "First boot complete!"
FIRSTBOOT
    sudo chmod +x "${ROOT_MOUNT}/home/pi/first-boot.sh"

    # Create a systemd service to run on first boot
    sudo tee "${ROOT_MOUNT}/etc/systemd/system/pixie-firstboot.service" > /dev/null << 'SVC'
[Unit]
Description=Pixie First Boot Setup
After=network-online.target
Wants=network-online.target
ConditionPathExists=/home/pi/first-boot.sh

[Service]
Type=oneshot
ExecStart=/bin/bash /home/pi/first-boot.sh
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
SVC
    # Enable the first-boot service
    if [ -d "${ROOT_MOUNT}/etc/systemd/system/multi-user.target.wants" ]; then
        sudo ln -sf /etc/systemd/system/pixie-firstboot.service \
            "${ROOT_MOUNT}/etc/systemd/system/multi-user.target.wants/pixie-firstboot.service"
    fi
fi

# --- Step 5: Unmount ---
echo -e "${YELLOW}Unmounting...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    diskutil unmountDisk "$DISK"
else
    sudo umount "$BOOT_MOUNT" "$ROOT_MOUNT"
    rmdir "$BOOT_MOUNT" "$ROOT_MOUNT"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SD card ready!${NC}"
echo -e "${GREEN}  Hostname: ${HOSTNAME}${NC}"
echo -e "${GREEN}  ${NC}"
echo -e "${GREEN}  Insert into Pi, power on, and wait.${NC}"
echo -e "${GREEN}  The Pixie-XXXX WiFi will appear.${NC}"
echo -e "${GREEN}========================================${NC}"
