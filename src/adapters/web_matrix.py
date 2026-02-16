import threading
from flask import Flask, render_template, jsonify
from src.core.display_interface import DisplayInterface
from src.core.matrix_buffer import MatrixBuffer
import time

class WebMatrixAdapter(DisplayInterface):
    """
    Adapter that serves the matrix via a Flask web server.
    """
    def __init__(self, width=64, height=64):
        self.width = width
        self.height = height
        self.buffer = MatrixBuffer(width, height)
        self.app = Flask(__name__, template_folder='../web/templates', static_folder='../web/static')
        
        # Define routes
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/matrix_data', 'matrix_data', self.get_matrix_data)

        # Start Flask in a separate thread
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"Web Emulator started at http://127.0.0.1:5001")

    def _run_server(self):
        # Run Flask server securely (disable debug to avoid thread issues)
        self.app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

    def index(self):
        return render_template('index.html', width=self.width, height=self.height)

    def get_matrix_data(self):
        # Return the buffer as a flat list for efficiency or structured JSON
        # Here we return a simple structured JSON for clarity
        return jsonify(self.buffer.get_buffer())

    def set_pixel(self, x, y, r, g, b):
        self.buffer.set_pixel(x, y, r, g, b)

    def fill(self, r, g, b):
        self.buffer.fill(r, g, b)

    def clear(self):
        self.buffer.clear()

    def update(self):
        # In a polling based web app, the client fetches data.
        # We don't need to push updates here, but we could use WebSockets later.
        pass
