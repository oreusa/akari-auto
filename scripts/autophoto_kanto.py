#!/usr/bin/env python3
"""11/21 オーナー「お出かけ先とか全部写真取得できるように。より良い写真を選べるように」
関東には毎朝ひとりでに写真を付ける仕組みが無かった（六義園・新宿御苑・高尾山も写真なし）→ 関西（usagi tools/mihon/autophoto.py）と同じ形。
site/assets/mihon.json（mihon.py の出力）で写真の無い催しについて：
  ① 催しの名前そのもの（六義園など、名前が場所の物）→ ② 会場の名前（vr）の順に、ウィキデータで日本の同じ名前の項目を探し、
  その場所のコモンズの分類から 文字の点＋見た目の点（色・くっきり・季節・夜）で一番の1枚（scripts/photo_best.py）。点が低ければ代表の写真。
  → site/assets/ph（大・s・t）＋ data/venue_photos.json（auto:1）。試した物は data/auto_tried.json に残し30日は試さない。1日 AUTO_V 件まで。
このあと mihon.py をもう1回走らせると写真が入る。"""
import os, re, sys, json, hashlib, datetime, io
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
os.environ.setdefault("PW", "1200")
import photo_best as B
PH = os.path.join(R, "site", "assets", "ph")
def lj(p, d):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return d
def sj(p, o): json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
k = lambda s: re.sub(r"\s+", "", s or "")
T = datetime.date.today().isoformat(); today = datetime.date.today()
M = lj(os.path.join(R, "site", "assets", "mihon.json"), {})
VPF = os.path.join(R, "data", "venue_photos.json"); VP = lj(VPF, {})
TRF = os.path.join(R, "data", "auto_tried.json"); TR = lj(TRF, {})
def fresh(key): return key in TR and (today - datetime.date.fromisoformat(TR[key])).days < 30

def save(url, name):
    from PIL import Image
    im = Image.open(io.BytesIO(B.get(url))).convert("RGB")
    f = hashlib.md5(name.encode()).hexdigest()[:8] + ".webp"
    for d in ("", "s", "t"): os.makedirs(os.path.join(PH, d), exist_ok=True)
    im.thumbnail((1200, 1200)); im.save(os.path.join(PH, f), "WEBP", quality=80)
    s = im.copy(); s.thumbnail((480, 480)); s.save(os.path.join(PH, "s", f), "WEBP", quality=76)
    w, h = im.size; s0 = min(w, h); im.crop(((w - s0) // 2, (h - s0) // 2, (w - s0) // 2 + s0, (h - s0) // 2 + s0)).resize((200, 200)).save(os.path.join(PH, "t", f), "WEBP", quality=74)
    return f

def pick(q, theme):
    e = B.entity(q); lab = (e or {}).get("label", "")
    if not e or not lab or not (k(q) in k(lab) or k(lab) in k(q)): return None
    c = None
    if e.get("cat"):
        try:
            _, cs = B.best(q, theme)
            if cs and cs[0]["score"] >= 70: c = cs[0]
        except Exception as ex: print("ERR best", q, ex)
    if not c and e.get("p18"):
        t = "File:" + e["p18"]; ii = (B.info([t]).get(t) or {}).get("ii") or {}
        md = ii.get("extmetadata", {}); lic = md.get("LicenseShortName", {}).get("value", "")
        if any(lic.startswith(x) for x in B.OK) and ii.get("width", 0) >= 800 and ii.get("width", 0) >= ii.get("height", 1):
            c = {"thumb": ii.get("thumburl"), "page": ii.get("descriptionurl"), "license": lic, "artist": re.sub(r"<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip(), "title": t}
    return c

n, got = 0, 0
LIM = int(os.environ.get("AUTO_V", "25"))
for key, o in M.items():
    if o.get("im") or n >= LIM: continue
    name = o.get("n", ""); th = B.theme_of(name)
    qs = []
    nm = re.sub(r"20\d\d(-20\d\d)?|第\d+回|（[^）]*）|\([^)]*\)", "", name).strip()
    qs.append(nm)
    if o.get("vr") and not re.search(r"[区市町村]$|周辺|エリア|参加店|駅前", o["vr"]): qs.append(o["vr"])
    for q in dict.fromkeys(x for x in qs if x and len(x) >= 2):
        if q in VP or fresh(q): continue
        n += 1; TR[q] = T
        try:
            c = pick(q, th)
            if not c: print("写真なし", q); continue
            vk = name if q == nm else q   # 名前で当てた時は催しの名前で残す（mihon.py は名前を先に見る）
            f = save(c["thumb"], "venue:" + vk)
            VP[vk] = {"img": f, "cr": f'{(c.get("artist") or "撮影者")[:40]}（{c["license"]}・Wikimedia Commons）', "page": c["page"], "auto": 1, "d": T}
            got += 1; print("写真", vk, "←", c["title"][:60], c.get("score", ""), c.get("why", ""))
            break
        except Exception as ex:
            print("ERR", q, ex)
sj(VPF, VP); sj(TRF, TR)
print(f"関東の自動の写真: 試した {n} / 付いた {got} / 写真の表 {len(VP)}")
