# app.py
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess

# Run your original start script in the background
def run_main():
    subprocess.run(["bash", "start"])

threading.Thread(target=run_main, daemon=True).start()

# Minimal HTTP server for Koyeb
PORT = int(os.environ.get("PORT", 8000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Healthcheck server running on port {PORT}")
    server.serve_forever()
