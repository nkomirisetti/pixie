import threading
from flask import Flask, render_template, jsonify, request
import logging

# Configure Flask logging to suppress standard output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class WebController:
    """
    Control Server that exposes an API to control the AppManager.
    """
    def __init__(self, app_manager, port=5000):
        self.app_manager = app_manager
        self.port = port
        self.app = Flask(__name__, template_folder='../web/templates', static_folder='../web/static')
        
        # Define routes
        self.app.add_url_rule('/', 'remote', self.remote)
        self.app.add_url_rule('/api/status', 'get_status', self.get_status, methods=['GET'])
        self.app.add_url_rule('/api/switch', 'switch_app', self.switch_app, methods=['POST'])

        # Start Flask in a separate thread
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"Web Controller started at http://0.0.0.0:{self.port}")

    def _run_server(self):
        try:
            # Run Flask server securely (disable debug to avoid thread issues)
            self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        except OSError as e:
            print(f"Error starting Web Controller on port {self.port}: {e}")
            print("Try running with a different port if needed.")

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
