"""調べ用：HPのリンクを押した直後に何が出るか（転送の途中のページ）を見る。投稿はしない。"""
import re, sys, urllib.request, urllib.error
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NoRedir)
def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "ja-JP", "Accept": "text/html"})
    try:
        r = op.open(req, timeout=20); return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")
_, _, hp = get(sys.argv[1])
seen = {}
for h in re.findall(r'href="(https?://[^"]+)"', hp):
    h = h.replace("&amp;", "&"); host = h.split("/")[2]
    if host not in seen and "fonts.g" not in host: seen[host] = h
for host, u in seen.items():
    for hop in range(4):
        try: st, hd, body = get(u)
        except Exception as e: print(f'[{host}] ERR {str(e)[:80]}'); break
        loc = hd.get("Location") or hd.get("location")
        t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S)
        print(f"[{host}] hop{hop} {st} len={len(body)} title={(t.group(1).strip() if t else '')[:50]} loc={(loc or '')[:90]}")
        if st == 200 and hop > 0 or (st == 200 and len(body) < 20000):
            print("   head:", re.sub(r"\s+", " ", body[:700]))
        if not loc: break
        u = loc if loc.startswith("http") else "/".join(u.split("/")[:3]) + loc
