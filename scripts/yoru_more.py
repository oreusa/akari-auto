"""夜の【夜 1件の中身】の関東の行を data/odekake_more.json に入れる（11/27）。
使い方: python3 scripts/yoru_more.py 報告の文.txt   （燈への報告を写した文。関東の行だけ拾う）
- 名前ごとに一番新しい行を使う。1件ページ（spot_pages.py）は、ここの時間・料金・駐車場・注意を note から作った物より優先して出す
- 「不明」「未確認」「記載なし」などの言葉がある区切りは出さない（全部消えた欄は書かない）
- 「11/27の営業…」のような その日だけの言い方も出さない（古くなるため）"""
import json, os, re, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, "data", "odekake_more.json")
NG = re.compile(r"不明|未確認|記載なし|記載がない|明記なし|案内しない|確認中|わからない|分からない")
ONEDAY = re.compile(r"^\d{1,2}/\d{1,2}(の|は)")
NOPRICE = re.compile(r"\d|無料")


def clean(t, sep="、"):
    out = []
    for s in re.split(r"[。]", t or ""):
        cs = [c.strip() for c in re.split(r"、", s) if c.strip() and not NG.search(c) and not ONEDAY.match(c.strip())]
        if cs: out.append("、".join(cs))
    return sep.join(out).strip("、。 ")


def parse(line):
    f = line.strip().split("｜")
    if len(f) < 4 or not f[0].startswith("【夜 1件の中身】") or f[1] != "関東": return None
    day = f[0].replace("【夜 1件の中身】", "").strip()[:10]
    kv, src = {}, []
    for x in f[3:]:
        m = re.match(r"^(時間|料金|駐車場|休み|注意)：(.*)$", x.strip())
        if m: kv[m.group(1)] = m.group(2)
        else: src += re.findall(r"https?://\S+", x)
    r = {}
    for lb, k in (("時間", "time"), ("駐車場", "park")):
        v = clean(kv.get(lb))
        if v: r[k] = v
    v = clean(kv.get("料金"))
    if v and NOPRICE.search(v): r["price"] = v
    n = []
    h = clean(kv.get("休み"))
    if h: n.append("休み：" + h)
    c = clean(kv.get("注意"), "。")
    if c: n.append(c)
    if n: r["note"] = "。".join(n) + "。"
    if not r: return None
    r["day"] = day
    if src: r["src"] = src[0]
    return f[2].strip(), r


def main():
    t = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    try: D = json.load(open(P, encoding="utf-8"))
    except Exception: D = {"rows": {}}
    n = 0
    for ln in t.splitlines():
        p = parse(ln)
        if not p: continue
        nm, r = p
        if D["rows"].get(nm, {}).get("day", "") > r["day"]: continue
        D["rows"][nm] = r; n += 1
    json.dump(D, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(P, "a").write("\n")
    print("関東の行", n, "件を入れた →", P)


if __name__ == "__main__": main()
