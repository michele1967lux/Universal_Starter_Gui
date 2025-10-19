#!/usr/bin/env python3
"""
Example server script for testing Universal Starter GUI.
This script runs a simple HTTP server that stays alive.
"""

import time
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f"""
        <html>
        <head><title>Example Server</title></head>
        <body>
            <h1>Universal Starter GUI - Example Server</h1>
            <p>Server is running!</p>
            <p>Current time: {datetime.datetime.now()}</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        # Custom log format
        print(f"[{datetime.datetime.now()}] {format % args}")


def main():
    port = 8080
    server = HTTPServer(('localhost', port), SimpleHandler)
    print(f"Example server started on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.shutdown()


if __name__ == "__main__":
    main()
