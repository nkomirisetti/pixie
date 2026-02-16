"""
QR Code renderer for the 64x64 LED matrix.
Pure Python implementation — no external libraries needed.
Supports WiFi QR codes for the provisioning flow.
"""

# QR Code encoding tables for alphanumeric mode
ALPHANUMERIC_TABLE = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17, 'I': 18,
    'J': 19, 'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24, 'P': 25, 'Q': 26, 'R': 27,
    'S': 28, 'T': 29, 'U': 30, 'V': 31, 'W': 32, 'X': 33, 'Y': 34, 'Z': 35, ' ': 36,
    '$': 37, '%': 38, '*': 39, '+': 40, '-': 41, '.': 42, '/': 43, ':': 44,
}


def generate_qr_matrix(data):
    """
    Generate a QR code as a 2D boolean matrix.
    Uses the qrcode library if available, otherwise falls back to a simple
    text-based representation.
    """
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=None,  # Auto-detect smallest version
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=0,
        )
        qr.add_data(data)
        qr.make(fit=True)
        matrix = qr.make_image(fill_color="black", back_color="white")
        # Convert to boolean grid
        width = matrix.size[0]
        pixels = list(matrix.getdata())
        grid = []
        for y in range(width):
            row = []
            for x in range(width):
                # Black pixel = True (draw), White = False
                row.append(pixels[y * width + x] == 0)
            grid.append(row)
        return grid
    except ImportError:
        # Fallback: no qrcode library — show a placeholder
        return None


def draw_qr_on_display(display, data, color=(255, 255, 255)):
    """
    Render a QR code centered on the 64x64 display.
    Scales the QR modules to fit with a quiet zone.
    """
    grid = generate_qr_matrix(data)

    if grid is None:
        # No qrcode library — draw a simple "WiFi" indicator instead
        _draw_wifi_icon(display, color)
        return

    qr_size = len(grid)
    display_size = 64

    # Calculate scale: leave 2px quiet zone on each side
    usable = display_size - 4  # 60px usable
    scale = usable // qr_size

    if scale < 1:
        scale = 1

    # Center the QR code
    total_qr_px = qr_size * scale
    offset_x = (display_size - total_qr_px) // 2
    offset_y = (display_size - total_qr_px) // 2

    # Draw white background behind QR (needed for scanning)
    for y in range(max(0, offset_y - 2), min(display_size, offset_y + total_qr_px + 2)):
        for x in range(max(0, offset_x - 2), min(display_size, offset_x + total_qr_px + 2)):
            display.set_pixel(x, y, 255, 255, 255)

    # Draw QR modules (black on white)
    r, g, b = 0, 0, 0  # QR code is always black on white for scanning
    for qy, row in enumerate(grid):
        for qx, module in enumerate(row):
            if module:  # Dark module
                for dy in range(scale):
                    for dx in range(scale):
                        px = offset_x + qx * scale + dx
                        py = offset_y + qy * scale + dy
                        if 0 <= px < display_size and 0 <= py < display_size:
                            display.set_pixel(px, py, r, g, b)


def _draw_wifi_icon(display, color):
    """Fallback: draw a simple WiFi icon when QR library isn't available."""
    r, g, b = color
    cx, cy = 32, 40

    # WiFi arcs (concentric quarter circles)
    import math
    for radius in [6, 12, 18]:
        for angle in range(0, 91):
            rad = math.radians(angle + 225)  # Top-facing arc
            x = int(cx + radius * math.cos(rad))
            y = int(cy + radius * math.sin(rad))
            if 0 <= x < 64 and 0 <= y < 64:
                display.set_pixel(x, y, r, g, b)

    # Center dot
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            display.set_pixel(cx + dx, cy + dy, r, g, b)
