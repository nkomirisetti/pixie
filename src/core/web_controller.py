import threading
import os
from flask import Flask, render_template, jsonify, request
import logging

# Configure Flask logging to suppress standard output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Resolve paths relative to this file (works on both Mac and Pi)
_CORE_DIR = os.path.dirname(os.path.abspath(__file__))       # src/core
_SRC_DIR = os.path.dirname(_CORE_DIR)                        # src
_TEMPLATE_DIR = os.path.join(_SRC_DIR, 'web', 'templates')
_STATIC_DIR = os.path.join(_SRC_DIR, 'web', 'static')


class WebController:
    """
    Unified web server for Pixie.
    - Always serves the Remote UI (app switcher)
    - In emulator mode, also serves the matrix emulator with WebSocket push
    """
    def __init__(self, app_manager, port=5000, emulator_display=None):
        self.app_manager = app_manager
        self.port = port
        self.emulator_display = emulator_display

        self.app = Flask(__name__, template_folder=_TEMPLATE_DIR, static_folder=_STATIC_DIR)
        self.socketio = None

        # Remote control routes (always available)
        self.app.add_url_rule('/', 'remote', self.remote)
        self.app.add_url_rule('/api/status', 'get_status', self.get_status, methods=['GET'])
        self.app.add_url_rule('/api/switch', 'switch_app', self.switch_app, methods=['POST'])

        # Emulator routes (only in emulator mode)
        if self.emulator_display is not None:
            self._setup_emulator()

        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

        url = f"http://127.0.0.1:{self.port}" if emulator_display else f"http://0.0.0.0:{self.port}"
        print(f"Web Controller started at {url}")
        if emulator_display:
            print(f"  Emulator:  {url}/emulator")
            print(f"  Remote:    {url}/")

    def _setup_emulator(self):
        """Add emulator routes and WebSocket support."""
        from flask_socketio import SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        self.emulator_display.set_socketio(self.socketio)
        self.app.add_url_rule('/emulator', 'emulator', self.emulator)
        self.app.add_url_rule('/matrix_data', 'matrix_data', self.matrix_data)

    def _run_server(self):
        try:
            if self.socketio:
                # Use SocketIO's run method for WebSocket support
                self.socketio.run(self.app, host='0.0.0.0', port=self.port,
                                  debug=False, use_reloader=False, log_output=False,
                                  allow_unsafe_werkzeug=True)
            else:
                self.app.run(host='0.0.0.0', port=self.port,
                             debug=False, use_reloader=False, load_dotenv=False)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error starting Web Controller on port {self.port}: {e}")

    # --- Remote routes ---

    def remote(self):
        return render_template('remote.html')

    def get_status(self):
        return jsonify({
            "current_app": self.app_manager.active_app_name,
            "available_apps": list(self.app_manager.apps.keys())
        })

    def switch_app(self):
        data = request.json
        if not data or 'app' not in data:
            return jsonify({"error": "Missing 'app' in payload"}), 400

        app_name = data['app']
        if app_name not in self.app_manager.apps:
            return jsonify({"error": f"App '{app_name}' not found"}), 404

        self.app_manager.switch_to(app_name)
        return jsonify({"status": "ok", "current_app": app_name})

    # --- Emulator routes ---

    def emulator(self):
        return render_template('index.html', width=self.emulator_display.width,
                               height=self.emulator_display.height)

    def matrix_data(self):
        """HTTP fallback for emulator data."""
        return jsonify(self.emulator_display.get_matrix_data())
