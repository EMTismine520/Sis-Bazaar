from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
import sys
import webbrowser

ROOT = Path(__file__).resolve().parent / "web"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    url = f"http://127.0.0.1:{port}/"
    print(f"肥鹅美食街网页版本: {url}")
    print("手机访问时把 127.0.0.1 换成电脑局域网 IP；按 Ctrl+C 停止。")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    server.serve_forever()
