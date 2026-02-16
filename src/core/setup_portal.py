import threading
from flask import Flask, render_template, jsonify, request
import logging
import os

from src.core.logger import get_logger

log = get_logger()

# Suppress Flask/Werkzeug logs
werkzeug_log = logging.getLogger('werkzeug')
werkzeug_log.setLevel(logging.ERROR)

_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TEMPLATE_DIR = os.path.join(_SRC_DIR, 'web', 'templates')
_STATIC_DIR = os.path.join(_SRC_DIR, 'web', 'static')


class SetupPortal:
    """
    Captive portal served during WiFi provisioning (AP mode).
    Runs on port 80 for captive portal auto-detection.
    """

    def __init__(self, wifi_manager):
        self.wifi = wifi_manager
        self._connected = threading.Event()
        self._result_ip = None

        self.app = Flask(__name__, template_folder=_TEMPLATE_DIR, static_folder=_STATIC_DIR)

        # Routes
        self.app.add_url_rule('/', 'setup', self.setup_page)
        self.app.add_url_rule('/api/scan', 'scan', self.scan, methods=['GET'])
        self.app.add_url_rule('/api/connect', 'connect', self.connect, methods=['POST'])
        self.app.add_url_rule('/api/status', 'status', self.portal_status, methods=['GET'])
        self.app.add_url_rule('/api/saved', 'saved', self.saved_networks, methods=['GET'])
        self.app.add_url_rule('/api/forget', 'forget', self.forget_network, methods=['POST'])

        # Captive portal detection endpoints — return redirect to setup page
        # Android checks /generate_204, Apple checks /hotspot-detect.html
        self.app.add_url_rule('/generate_204', 'captive_android', self._captive_redirect)
        self.app.add_url_rule('/hotspot-detect.html', 'captive_apple', self._captive_redirect)
        self.app.add_url_rule('/connecttest.txt', 'captive_ms', self._captive_redirect)
        # Catch-all for any other captive portal checks
        self.app.add_url_rule('/redirect', 'captive_generic', self._captive_redirect)

    def _captive_redirect(self):
        """Redirect captive portal detection to our setup page."""
        from flask import redirect
        return redirect('/')

    # --- Portal Pages ---

    def setup_page(self):
        return render_template('setup.html', ap_ssid=self.wifi.ap_ssid)

    # --- API Endpoints ---

    def scan(self):
        """Return list of visible WiFi networks."""
        try:
            networks = self.wifi.scan_networks()
            return jsonify({"networks": networks})
        except Exception as e:
            log.error(f"Scan error: {e}")
            return jsonify({"networks": [], "error": str(e)})

    def connect(self):
        """Attempt to connect to a WiFi network."""
        data = request.json
        if not data or 'ssid' not in data:
            return jsonify({"success": False, "message": "Missing SSID"}), 400

        ssid = data['ssid']
        password = data.get('password', '')

        success, message = self.wifi.connect(ssid, password if password else None)

        if success:
            self._result_ip = message
            # Signal that we're connected — but delay so client gets the response
            threading.Timer(3.0, self._connected.set).start()

        return jsonify({"success": success, "message": message})

    def portal_status(self):
        """Return current provisioning status."""
        return jsonify({
            "ap_ssid": self.wifi.ap_ssid,
            "connected": self.wifi.is_connected(),
            "current_network": self.wifi.get_current_network(),
            "ip": self.wifi.get_ip_address(),
        })

    def saved_networks(self):
        """Return list of saved WiFi connections."""
        return jsonify({"networks": self.wifi.get_saved_networks()})

    def forget_network(self):
        """Delete a saved WiFi connection."""
        data = request.json
        if not data or 'name' not in data:
            return jsonify({"success": False}), 400
        success = self.wifi.forget_network(data['name'])
        return jsonify({"success": success})

    # --- Run ---

    def run_until_connected(self, port=80):
        """
        Start the portal server and block until WiFi is configured.
        Returns the IP address of the new connection.
        """
        log.info(f"Setup portal starting on port {port}...")

        server_thread = threading.Thread(
            target=lambda: self.app.run(
                host='0.0.0.0', port=port,
                debug=False, use_reloader=False, load_dotenv=False
            ),
            daemon=True
        )
        server_thread.start()
        log.info(f"Setup portal ready at http://192.168.4.1:{port}/")

        # Block until WiFi is configured
        self._connected.wait()
        log.info(f"WiFi configured! IP: {self._result_ip}")
        return self._result_ip
