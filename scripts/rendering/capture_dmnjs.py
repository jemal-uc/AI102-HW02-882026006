import http.server
import socketserver
import subprocess
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_PNG = ROOT / "tests" / "validation-evidence" / "dmnjs_drd_verify.png"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, format, *args):
        pass

with socketserver.TCPServer(("127.0.0.1", 0), QuietHandler) as httpd:
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    url = f"http://127.0.0.1:{port}/scripts/rendering/render_dmnjs.html"
    cmd = [
        EDGE,
        "--headless",
        "--disable-gpu",
        f"--screenshot={OUT_PNG}",
        "--window-size=1800,960",
        "--virtual-time-budget=4000",
        url,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    httpd.shutdown()
    print("Exit:", res.returncode, "Exists:", OUT_PNG.exists(), "Size:", OUT_PNG.stat().st_size if OUT_PNG.exists() else 0)
