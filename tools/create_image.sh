#!/bin/bash
# ============================================================
# Pixie Golden Image Creator
# Creates a compressed .img file from a configured Pi's SD card.
#
# Usage:
#   ./tools/create_image.sh <sd-card-device> [output-file]
#
# Example:
#   ./tools/create_image.sh /dev/disk4 pixie-v1.0.img
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "Usage: $0 <sd-card-device> [output-file]"
    echo ""
    echo "  sd-card-device  e.g. /dev/disk4 (macOS) or /dev/sdb (Linux)"
    echo "  output-file     Output image filename (default: pixie-golden.img)"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

DISK="$1"
OUTPUT="${2:-pixie-golden.img}"

echo -e "${YELLOW}Creating golden image from ${DISK}...${NC}"
echo "This may take a while depending on the SD card size."

# Unmount disk
if [[ "$OSTYPE" == "darwin"* ]]; then
    diskutil unmountDisk "$DISK" 2>/dev/null || true
    RDISK="${DISK/disk/rdisk}"
    echo -e "${YELLOW}Reading from ${RDISK}...${NC}"
    sudo dd if="$RDISK" of="$OUTPUT" bs=4m status=progress
else
    sudo umount "${DISK}"* 2>/dev/null || true
    echo -e "${YELLOW}Reading from ${DISK}...${NC}"
    sudo dd if="$DISK" of="$OUTPUT" bs=4M status=progress
fi

sync

# Compress the image
echo -e "${YELLOW}Compressing image...${NC}"
gzip -k "$OUTPUT"
COMPRESSED="${OUTPUT}.gz"

ORIG_SIZE=$(du -h "$OUTPUT" | cut -f1)
COMP_SIZE=$(du -h "$COMPRESSED" | cut -f1)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Golden image created!${NC}"
echo -e "${GREEN}  Raw:        ${OUTPUT} (${ORIG_SIZE})${NC}"
echo -e "${GREEN}  Compressed: ${COMPRESSED} (${COMP_SIZE})${NC}"
echo -e "${GREEN}  ${NC}"
echo -e "${GREEN}  Flash to new cards with:${NC}"
echo -e "${GREEN}  ./tools/flash.sh /dev/diskN ${OUTPUT}${NC}"
echo -e "${GREEN}========================================${NC}"
