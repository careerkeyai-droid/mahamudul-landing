#!/usr/bin/env python3
"""
Simple local development server with hot reload support.

Usage:
  python3 devserver.py
Then open:
  http://localhost:5500
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable


HOST = "127.0.0.1"
PORT = 5500
ROOT = Path(__file__).resolve().parent
WATCHED_EXTENSIONS = {".html", ".css", ".js"}


def iter_watched_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() in WATCHED_EXTENSIONS:
            yield path


def project_version() -> str:
    latest_mtime_ns = 0
    for file_path in iter_watched_files(ROOT):
        try:
            latest_mtime_ns = max(latest_mtime_ns, file_path.stat().st_mtime_ns)
        except FileNotFoundError:
            # A file can disappear during a save; ignore transient state.
            continue
    return str(latest_mtime_ns)


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/__reload":
            payload = project_version().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        return super().do_GET()


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Serving {ROOT} at http://{HOST}:{PORT}")
    print("Hot reload is active for .html/.css/.js changes.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
