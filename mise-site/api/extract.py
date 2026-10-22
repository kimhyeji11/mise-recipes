from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
import ipaddress, json, re, socket

MAX_BYTES = 5 * 1024 * 1024

def check_public_url(url):
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname or p.username or p.password:
        raise ValueError("http 또는 https 형식의 공개 웹사이트 주소를 입력해주세요.")
    try:
        addresses = {x[4][0] for x in socket.getaddrinfo(p.hostname, p.port or (443 if p.scheme == "https" else 80))}
        if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):
            raise ValueError("공개 웹사이트 주소만 가져올 수 있어요.")
    except socket.gaierror as e:
        raise ValueError("사이트 주소를 찾을 수 없어요.") from e

class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def find_recipe(value):
    if isinstance(value, list):
        for item in value:
            found = find_recipe(item)
            if found: return found
    elif isinstance(value, dict):
        typ = value.get("@type", [])
        if typ == "Recipe" or isinstance(typ, list) and "Recipe" in typ: return value
        for key in ("@graph", "mainEntity", "itemListElement"):
            found = find_recipe(value.get(key))
            if found: return found
    return None

def get_recipe(url):
    check_public_url(url)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; MiseRecipeImporter/1.0)", "Accept": "text/html,application/xhtml+xml"})
    with build_opener(SafeRedirect()).open(req, timeout=12) as response:
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES: raise ValueError("페이지가 너무 커서 읽을 수 없어요.")
        charset = response.headers.get_content_charset() or "utf-8"
    html = data.decode(charset, errors="replace")
    blocks = re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script\s*>', html, re.I | re.S)
    for block in blocks:
        try:
            recipe = find_recipe(json.loads(block.strip()))
            if recipe:
                return {"title": recipe.get("name", ""), "description": recipe.get("description", ""),
                    "servings": recipe.get("recipeYield", ""), "totalTime": recipe.get("totalTime") or recipe.get("cookTime") or recipe.get("prepTime", ""),
                    "image": recipe.get("image", ""), "ingredients": recipe.get("recipeIngredient", []),
                    "steps": recipe.get("recipeInstructions", [])}
        except (json.JSONDecodeError, TypeError):
            continue
    raise ValueError("사이트가 레시피 정보를 자동으로 제공하지 않아요. 링크를 저장하고 내용을 직접 입력해주세요.")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/extract":
            self.send_error(404); return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > 8192: raise ValueError("요청이 너무 커요.")
            payload = json.loads(self.rfile.read(size))
            result = {"ok": True, "recipe": get_recipe(str(payload.get("url", "")))}
            status = 200
        except Exception as e:
            result = {"ok": False, "error": str(e)}; status = 400
        body = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)
