#!/usr/bin/env python3
"""mise 로컬 미리보기 서버: 정적 파일 + /api/extract (Vercel 함수와 같은 코드 사용).
실행: python3 recipe-server.py  →  http://127.0.0.1:8765/index.html
"""
import os, sys, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "api"))
import extract  # noqa: E402

PORT = int(os.environ.get("PORT", "8765"))

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)
    def do_POST(self):
        extract.handler.do_POST(self)

if __name__ == "__main__":
    page = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    url = f"http://127.0.0.1:{PORT}/{page}"
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"mise 로컬 서버 실행 중: {url}  (종료: Ctrl+C)")
    try: webbrowser.open(url)
    except Exception: pass
    try: server.serve_forever()
    except KeyboardInterrupt: print("\n종료했어요.")
