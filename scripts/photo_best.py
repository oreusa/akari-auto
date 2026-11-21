"""11/18 月：「行きたくなる写真」を選ぶ（cover.py の次の版）。
11/18 owner「TANOSU より完全に劣ってる」→ 並べて分かった元：うちの写真は建物の外観・駅・駐車場＝記録写真。
その場所のコモンズの分類（ウィキデータ P373）の中から、写真を全部見て点数を付けて上位3枚を残す。
  ＋ 秀逸な画像・高品質な画像・価値ある画像（コモンズの人が選んだ印）
  ＋ 催しの季節・時間に合う（紅葉なら autumn/紅葉/November…、夜なら night/illumination…）
  − 季節違い（紅葉の催しに桜・雪）、記録写真の言葉（駅・駐車場・看板・地図・案内板・内部…）
使い方: python3 tools/photo/best.py <一覧.tsv> <保存先>   一覧＝「名前<TAB>探す言葉1|言葉2」（cover.py と同じ）
結果: 保存先/best.json（1件に候補3つ）と NNN-0.jpg NNN-1.jpg NNN-2.jpg。最後は目で見て決める。"""
import json, math, os, re, sys, time, urllib.parse, urllib.request
PW = int(os.environ.get("PW", "640"))
OK = ("CC0", "Public domain", "CC BY 2.0", "CC BY 2.1", "CC BY 2.5", "CC BY 3.0", "CC BY 4.0", "CC BY-SA 2.0", "CC BY-SA 2.1", "CC BY-SA 2.5", "CC BY-SA 3.0", "CC BY-SA 4.0")
UA = {"User-Agent": "TownNotePhotoBot/1.0 (https://kansai.townnote.app/)"}
API = "https://commons.wikimedia.org/w/api.php?"


def get(u):
    for i in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
        except Exception:
            if i == 2: raise
            time.sleep(3)


def js(u):
    return json.loads(get(u))


SEASON = {
    "autumn": (r"autumn|fall|momiji|koyo|kōyō|紅葉|もみじ|maple|foliage|november|11月|秋", r"cherry|sakura|桜|spring|snow|雪|winter|hydrangea|紫陽花|plum|梅|summer|夏"),
    "night": (r"night|illumination|illuminated|light[- ]?up|ライトアップ|イルミ|夜|夜景|evening|dusk|lantern|灯", r""),
    "flower": (r"rose|バラ|薔薇|flower|花|cosmos|コスモス", r"snow|雪"),
}
BAD = r"station|parking|駐車|signboard|sign\b|看板|案内|map\b|地図|plaque|monument stone|碑|interior|内部|toilet|bus\b|バス停|ticket|切符|aerial|空撮|construction|工事|under renovation|logo|poster|leaflet|document|panorama of city|exterior of the building|office"
GOOD = r"garden|庭園|pond|池|pagoda|塔|temple|寺|shrine|神社|castle|城|view|景|landscape|reflection|lake|湖|mountain|山"


def theme_of(name):
    if re.search(r"紅葉|もみじ|モミジ|錦秋|秋の", name): return "autumn"
    if re.search(r"イルミ|ライトアップ|夜|光|ナイト|NIGHT|灯|ルミナ", name): return "night"
    if re.search(r"バラ|ローズ|コスモス|花", name): return "flower"
    return ""


def entity(q):
    """日本(P17=Q17)のウィキデータの項目で、写真の分類(P373)か代表の写真(P18)がある物"""
    hits = js("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"action": "wbsearchentities", "format": "json", "language": "ja", "uselang": "ja", "type": "item", "limit": 5, "search": q})).get("search", [])
    if not hits: return None
    ents = js("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"action": "wbgetentities", "format": "json", "ids": "|".join(h["id"] for h in hits), "props": "claims|labels", "languages": "ja"})).get("entities", {})
    for h in hits:
        c = ents.get(h["id"], {}).get("claims", {})
        if not any(x["mainsnak"].get("datavalue", {}).get("value", {}).get("id") == "Q17" for x in c.get("P17", [])): continue
        cat = c["P373"][0]["mainsnak"]["datavalue"]["value"] if "P373" in c else ""
        p18 = c["P18"][0]["mainsnak"]["datavalue"]["value"] if "P18" in c else ""
        if cat or p18:
            return {"id": h["id"], "label": h.get("label", ""), "cat": cat, "p18": p18}
    return None


def members(cat, depth=1, limit=400):
    """分類とその下の分類（1段）のファイル名"""
    files, cats, seen = [], ["Category:" + cat], set()
    for d in range(depth + 1):
        nxt = []
        for c in cats:
            if c in seen: continue
            seen.add(c); cont = {}
            while True:
                p = {"action": "query", "format": "json", "list": "categorymembers", "cmtitle": c, "cmtype": "file|subcat", "cmlimit": 500, **cont}
                d0 = js(API + urllib.parse.urlencode(p))
                for m in d0.get("query", {}).get("categorymembers", []):
                    if m["ns"] == 6: files.append(m["title"])
                    elif m["ns"] == 14: nxt.append(m["title"])
                if "continue" not in d0 or len(files) > limit: break
                cont = d0["continue"]
            if len(files) > limit: break
        cats = nxt[:25]
        if len(files) > limit: break
    return list(dict.fromkeys(f for f in files if re.search(r"\.(jpe?g|png|webp|tiff?)$", f, re.I)))[:limit]


def info(titles):
    out = {}
    for i in range(0, len(titles), 50):
        p = {"action": "query", "format": "json", "titles": "|".join(titles[i:i + 50]), "prop": "imageinfo|categories", "iiprop": "url|extmetadata|size", "iiurlwidth": PW, "cllimit": "max"}
        cont = {}
        while True:
            d = js(API + urllib.parse.urlencode({**p, **cont}))
            for pg in d.get("query", {}).get("pages", {}).values():
                o = out.setdefault(pg["title"], {"cats": []})
                if pg.get("imageinfo"): o["ii"] = pg["imageinfo"][0]
                o["cats"] += [c["title"] for c in pg.get("categories", [])]
            if "continue" not in d: break
            cont = d["continue"]
        time.sleep(0.3)
    return out


def score(title, o, theme):
    ii = o.get("ii") or {}
    m = ii.get("extmetadata", {})
    lic = m.get("LicenseShortName", {}).get("value", "")
    if not any(lic.startswith(x) for x in OK): return None
    w, h = ii.get("width", 0), ii.get("height", 1)
    if w < h * 1.2 or w < 1600: return None
    cats = " ".join(o["cats"])
    text = (title + " " + cats + " " + re.sub(r"<[^>]+>", " ", m.get("ImageDescription", {}).get("value", ""))).lower()
    s, why = math.log10(w * h) * 4, []
    if "Featured pictures" in cats: s += 50; why.append("秀逸")
    if "Quality images" in cats: s += 35; why.append("高品質")
    if "Valued images" in cats: s += 20; why.append("価値")
    if theme:
        good, bad = SEASON[theme]
        if re.search(good, text, re.I): s += 30; why.append("季節が合う")
        elif theme in ("autumn", "night"): s -= 15
        if bad and re.search(bad, text, re.I): s -= 45; why.append("季節違い")
    if re.search(BAD, text, re.I): s -= 40; why.append("記録写真")
    if re.search(GOOD, text, re.I): s += 6
    art = re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()
    return {"title": title, "page": ii.get("descriptionurl"), "thumb": ii.get("thumburl"), "license": lic, "artist": art[:80], "w": w, "h": h, "score": round(s, 1), "why": why}


def visual(url, theme):
    """11/21 オーナー「より良い写真を選べるように」→ 文字（題・分類）の点に、写真そのものの見た目の点を足す。
    小さい写真（幅240）で ①色の鮮やかさ ②くっきり（輪郭の強さ）③明るさのほどよさ ④季節・時間に合う色
    （紅葉＝赤・橙・黄の多さ／夜＝暗い地に明るい光）⑤くもり空（上の3分の1が白っぽく色が無い）を減点。PIL だけで量る。"""
    try:
        from PIL import Image, ImageFilter, ImageStat
        import io
        im = Image.open(io.BytesIO(get(url))).convert("RGB"); im.thumbnail((240, 240))
    except Exception:
        return 0, []
    w, h = im.size; hsv = im.convert("HSV"); px = list(hsv.getdata()); n = len(px) or 1
    L = im.convert("L"); lm = ImageStat.Stat(L).mean[0]
    sat = sum(p[1] for p in px) / n / 255
    edge = ImageStat.Stat(L.filter(ImageFilter.FIND_EDGES)).mean[0]
    s, why = 0.0, []
    s += max(-10, min(14, (sat - .22) * 60))                    # 色の鮮やかさ（灰色っぽい写真は下げる）
    s += max(-12, min(10, (edge - 9) * 1.2))                     # くっきり（ぼやけ・のっぺりは下げる）
    if theme == "night":
        hi = sum(1 for v in L.getdata() if v > 215) / n
        if lm < 95 and hi > .01: s += 18; why.append("夜の光")
        elif lm > 130: s -= 18; why.append("昼の写真")
    else:
        if lm < 60: s -= 14; why.append("暗い")
        elif lm > 205: s -= 10; why.append("白飛び")
        top = [p for i, p in enumerate(px) if i < n // 3]
        if top and sum(1 for p in top if p[1] < 30 and p[2] > 170) / len(top) > .55: s -= 10; why.append("くもり空")
    if theme == "autumn":
        warm = sum(1 for p in px if (p[0] < 32 or p[0] > 240) and p[1] > 110 and p[2] > 70) / n
        if warm > .18: s += 22; why.append("紅葉の色")
        elif warm < .05: s -= 18; why.append("紅葉が写っていない")
    if sat > .3 and edge > 12: why.append("鮮やか")
    return round(s, 1), why


def best(q, theme):
    e = entity(q)
    if not e: return None, []
    titles = members(e["cat"]) if e["cat"] else []
    if e["p18"]: titles.append("File:" + e["p18"])
    titles = list(dict.fromkeys(titles))
    if not titles: return e, []
    inf = info(titles)
    cand = [r for r in (score(t, inf[t], theme) for t in inf) if r]
    if e["p18"]:
        for r in cand:
            if r["title"] == "File:" + e["p18"]: r["score"] += 8; r["why"].append("代表の写真")
    cand.sort(key=lambda r: -r["score"])
    # 11/21 文字の点の上位12枚だけ、写真の見た目でも点を付けて並べ直す（呼び出しを増やしすぎない）
    for r in cand[:12]:
        v, vw = visual(r["thumb"], theme); r["score"] = round(r["score"] + v, 1); r["vis"] = v; r["why"] += vw
    cand = sorted(cand[:12], key=lambda r: -r["score"]) + cand[12:]
    return e, cand[:3]


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    res = []
    for i, ln in enumerate(open(src, encoding="utf-8")):
        if "\t" not in ln: continue
        name, qs = ln.rstrip("\n").split("\t")
        th = theme_of(name); e, cand = None, []
        for q in [x for x in qs.split("|") if x]:
            try: e, cand = best(q, th)
            except Exception as ex: print("ERR", q, ex)
            if cand: break
        for k, r in enumerate(cand):
            fn = f"{i:03d}-{k}.jpg"
            try: open(os.path.join(out, fn), "wb").write(get(r["thumb"])); r["file"] = fn
            except Exception as ex: print("ERR img", ex)
        res.append({"name": name, "theme": th, "entity": e, "cand": cand})
        print(i, name, th, "→", [(r["title"][5:40], r["score"], r["why"]) for r in cand])
    json.dump(res, open(os.path.join(out, "best.json"), "w"), ensure_ascii=False, indent=1)
    print("候補あり", sum(1 for r in res if r["cand"]), "/", len(res))
