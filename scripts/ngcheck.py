"""お客さんの画面に出してはいけない言葉が、作ったページに無いか調べる（11/9 オーナー「なんか対策ないの」）。
見つかったら 1 で終わる（page.yml ではここで止まり、本番に出さない）。言葉は ngwords.json。
使い方: python3 ngcheck.py ページのフォルダ [ngwords.json]"""
import glob, json, os, re, sys
root = sys.argv[1]
wf = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "ngwords.json")
_d = json.load(open(wf))
W = [(re.compile(rx), why) for rx, why in _d["words"]]
ALLOW = _d.get("allow", [])  # 正しい言葉（イベント名など）はここに足す
SKIP = re.compile(r"mihon|preview|-try\.html|_mihon|okaimono-live|otoku|/googl[^/]*\.html$")
bad = []
for f in sorted(glob.glob(os.path.join(root, "**", "*.html"), recursive=True)):
    if SKIP.search(f):
        continue
    t = open(f, errors="ignore").read()
    if 'name="robots" content="noindex' in t and "/c/" in f:
        continue
    t = re.sub(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<!--.*?-->", " ", t, flags=re.S)
    attrs = " ".join(re.findall(r'(?:title|alt|content|aria-label|placeholder)="([^"]*)"', t))
    text = re.sub(r"<[^>]+>", " ", t) + " " + attrs
    for a in ALLOW:
        text = text.replace(a, "")
    for rx, why in W:
        for m in rx.finditer(text):
            s = text[max(0, m.start() - 20):m.end() + 20].replace("\n", " ").strip()
            bad.append(f"{os.path.relpath(f, root)}：{why}：…{s}…")
            break
# 11/9 メニューの「本当に値下がりした物」は JS の中の文だった → JS の文字（"…"・'…'）も調べる
for f in sorted(glob.glob(os.path.join(root, "assets", "*.js"))):
    if SKIP.search(f):
        continue
    t = open(f, errors="ignore").read()
    t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
    t = re.sub(r"(?m)^\s*//.*$", " ", t)
    text = " ".join(m.group(2) for m in re.finditer(r"(['\"])((?:(?!\1)[^\\\n]|\\.)*)\1", t))
    text = re.sub(r"\$\{[^}]*\}", "", text)
    for a in ALLOW:
        text = text.replace(a, "")
    for rx, why in W:
        if why == "壊れた表示":
            continue
        for m in rx.finditer(text):
            s = text[max(0, m.start() - 20):m.end() + 20].replace("\n", " ").strip()
            bad.append(f"{os.path.relpath(f, root)}：{why}：…{s}…")
            break
for b in bad[:80]:
    print("×", b)
print(f"ngcheck: {len(bad)} 件" if bad else "ngcheck: なし")
sys.exit(1 if bad else 0)
