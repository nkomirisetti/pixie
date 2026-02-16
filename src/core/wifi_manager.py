import subprocess
import json
import re
from src.core.logger import get_logger

log = get_logger()

AP_CONNECTION_NAME = "pixie-hotspot"
AP_IP = "192.168.4.1"
AP_PREFIX = 24


class WifiManager:
    """
    Manages WiFi connections using NetworkManager (nmcli).
    Handles AP mode for provisioning and STA mode for normal operation.
    """

    def __init__(self):
        self._device = "wlan0"
        self._device_id = self._get_device_id()
        self.ap_ssid = f"Pixie-{self._device_id}"

    def _run(self, cmd, check=True):
        """Run a shell command and return stdout."""
        log.debug(f"nmcli: {cmd}")
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            if check and result.returncode != 0:
                log.error(f"Command failed: {cmd}\nstderr: {result.stderr.strip()}")
            return result
        except subprocess.TimeoutExpired:
            log.error(f"Command timed out: {cmd}")
            return None

    def _get_device_id(self):
        """Get last 4 chars of wlan0 MAC for unique device naming."""
        result = self._run(f"nmcli -t -f GENERAL.HWADDR device show {self._device}")
        if result and result.returncode == 0:
            # Output: GENERAL.HWADDR:XX:XX:XX:XX:XX:XX
            mac = result.stdout.strip().split(":")
            # Take last 4 hex chars (last 2 octets, no colons)
            return "".join(mac[-2:]).upper()
        return "0000"

    # --- Connection Status ---

    def is_connected(self):
        """Check if wlan0 has an active WiFi (non-AP) connection."""
        result = self._run(
            f"nmcli -t -f TYPE,STATE,NAME connection show --active"
        )
        if result and result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split(":")
                if len(parts) >= 3:
                    conn_type, state, name = parts[0], parts[1], ":".join(parts[2:])
                    if conn_type == "802-11-wireless" and name != AP_CONNECTION_NAME:
                        return True
        return False

    def get_current_network(self):
        """Return the SSID of the currently connected WiFi, or None."""
        result = self._run(
            f"nmcli -t -f active,ssid dev wifi list ifname {self._device}"
        )
        if result and result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.startswith("yes:"):
                    return line.split(":", 1)[1]
        return None

    def get_ip_address(self):
        """Return the current IP address of wlan0, or None."""
        result = self._run(
            f"nmcli -t -f IP4.ADDRESS device show {self._device}"
        )
        if result and result.returncode == 0:
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", result.stdout)
            if match:
                return match.group(1)
        return None

    # --- WiFi Scanning ---

    def scan_networks(self):
        """Scan for visible WiFi networks. Returns list of dicts."""
        # Trigger a fresh scan
        self._run(f"nmcli dev wifi rescan ifname {self._device}", check=False)

        result = self._run(
            f"nmcli -t -f SSID,SIGNAL,SECURITY,FREQ dev wifi list ifname {self._device}"
        )
        if not result or result.returncode != 0:
            return []

        networks = {}
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split(":")
            if len(parts) >= 3:
                ssid = parts[0]
                if not ssid or ssid == self.ap_ssid:
                    continue  # Skip empty and our own AP
                signal = int(parts[1]) if parts[1].isdigit() else 0
                security = parts[2] if len(parts) > 2 else ""

                # Keep strongest signal if duplicate SSIDs
                if ssid not in networks or signal > networks[ssid]["signal"]:
                    networks[ssid] = {
                        "ssid": ssid,
                        "signal": signal,
                        "secure": bool(security and security != "--"),
                    }

        # Sort by signal strength (strongest first)
        return sorted(networks.values(), key=lambda n: n["signal"], reverse=True)

    # --- Connect to Network ---

    def connect(self, ssid, password=None):
        """
        Connect to a WiFi network. Returns (success, message).
        Saves the connection for auto-reconnect on future boots.
        """
        log.info(f"Attempting to connect to '{ssid}'...")

        # First, stop AP if running
        self.stop_ap()

        # Try connecting
        if password:
            cmd = (
                f"nmcli dev wifi connect '{ssid}' "
                f"password '{password}' ifname {self._device}"
            )
        else:
            cmd = f"nmcli dev wifi connect '{ssid}' ifname {self._device}"

        result = self._run(cmd)

        if result and result.returncode == 0:
            ip = self.get_ip_address()
            log.info(f"Connected to '{ssid}' with IP {ip}")
            return True, ip or "Connected"
        else:
            error = result.stderr.strip() if result else "Command failed"
            log.error(f"Failed to connect to '{ssid}': {error}")
            # Restart AP so user can try again
            self.start_ap()
            return False, self._parse_error(error)

    def _parse_error(self, error):
        """Convert nmcli error to user-friendly message."""
        if "Secrets were required" in error or "secret" in error.lower():
            return "Incorrect password"
        if "No network with SSID" in error:
            return "Network not found"
        if "timeout" in error.lower():
            return "Connection timed out"
        return "Connection failed — please try again"

    # --- Saved Networks ---

    def get_saved_networks(self):
        """Return list of saved WiFi connections."""
        result = self._run("nmcli -t -f NAME,TYPE connection show")
        if not result or result.returncode != 0:
            return []

        saved = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 2 and parts[1] == "802-11-wireless":
                name = parts[0]
                if name != AP_CONNECTION_NAME:
                    saved.append(name)
        return saved

    def forget_network(self, name):
        """Delete a saved WiFi connection."""
        result = self._run(f"nmcli connection delete '{name}'")
        if result and result.returncode == 0:
            log.info(f"Forgot network: {name}")
            return True
        return False

    # --- AP Mode ---

    def start_ap(self):
        """Create a WiFi hotspot for provisioning."""
        log.info(f"Starting AP mode: {self.ap_ssid}")

        # Remove old hotspot connection if it exists
        self._run(f"nmcli connection delete '{AP_CONNECTION_NAME}'", check=False)

        # Create hotspot
        result = self._run(
            f"nmcli connection add type wifi ifname {self._device} "
            f"con-name '{AP_CONNECTION_NAME}' "
            f"autoconnect no "
            f"ssid '{self.ap_ssid}' "
            f"-- "
            f"wifi.mode ap "
            f"wifi.band bg "
            f"ipv4.method shared "
            f"ipv4.addresses {AP_IP}/{AP_PREFIX}"
        )

        if not result or result.returncode != 0:
            log.error("Failed to create AP connection")
            return False

        # Activate it
        result = self._run(f"nmcli connection up '{AP_CONNECTION_NAME}'")
        if result and result.returncode == 0:
            log.info(f"AP active: {self.ap_ssid} on {AP_IP}")
            self._setup_captive_dns()
            return True

        log.error("Failed to activate AP")
        return False

    def stop_ap(self):
        """Stop the hotspot and return to normal WiFi."""
        log.info("Stopping AP mode...")
        self._teardown_captive_dns()
        self._run(f"nmcli connection down '{AP_CONNECTION_NAME}'", check=False)
        self._run(f"nmcli connection delete '{AP_CONNECTION_NAME}'", check=False)

    def _setup_captive_dns(self):
        """Configure dnsmasq to redirect all DNS to our AP for captive portal."""
        try:
            conf = f"address=/#/{AP_IP}\n"
            conf_path = "/tmp/pixie-captive-dns.conf"
            with open(conf_path, "w") as f:
                f.write(conf)
            # NM's dnsmasq reads conf.d, but we can also use iptables redirect
            # For simplicity, we'll rely on NM's shared mode which already sets up
            # DHCP with dnsmasq. We add a redirect rule for captive portal detection.
            self._run(
                f"sudo iptables -t nat -A PREROUTING -i {self._device} "
                f"-p tcp --dport 80 -j DNAT --to-destination {AP_IP}:80",
                check=False,
            )
            log.debug("Captive portal DNS redirect configured")
        except Exception as e:
            log.warning(f"Could not set up captive DNS redirect: {e}")

    def _teardown_captive_dns(self):
        """Remove captive portal DNS redirect rules."""
        self._run(
            f"sudo iptables -t nat -D PREROUTING -i {self._device} "
            f"-p tcp --dport 80 -j DNAT --to-destination {AP_IP}:80",
            check=False,
        )

    # --- WiFi QR Code ---

    def get_wifi_qr_string(self):
        """Return the WiFi QR code string for the AP network."""
        return f"WIFI:S:{self.ap_ssid};T:nopass;;"
