"""関東の 泊まり・初詣・まちランキング・紅葉の都県ページ（関西 usagi tools/shin/lists.py と build.py と同じ形・同じ list.js / odekake.js）。
11/23 owner「関東と関西どっちも完璧にしろよ」「またhp関東だけ違うとかあったら」→ 関西にあって関東に無かった新しい形のページを、関東の数字で作る。
scripts/shin_kanto.py の main() から呼ばれる（イルミ・紅葉を作ったあと）。"""
import copy, datetime, hashlib, json, math, os, re

try:
    from yari import sell_cfg  # 関西 tools/shin/yari.py
except ImportError:
    from shin_yari import sell_cfg  # 関東 scripts/shin_yari.py

KIND = [("ie", "家と土地", "#C0532B"), ("hito", "人口", "#2E8B6E")]
ODE_NAV = lambda cur: [dict(n, **({"cur": 1} if n["href"] == cur else {})) for n in [
    {"t": "開催中", "ic": "now", "href": "/odekake"}, {"t": "今週末", "ic": "we", "href": "/odekake?w=we"},
    {"t": "いまから", "ic": "map", "href": "/ima"}, {"t": "泊まり", "ic": "inn", "href": "/tomari"}]]
ALSO = [["関東のおでかけ・イベント", "/odekake"], ["関東のイルミネーション", "/illumination"], ["関東の紅葉", "/koyo"],
        ["いまから行けるおでかけ", "/ima"], ["泊まりで行くおでかけ", "/tomari"], ["関東の初詣", "/hatsumode"], ["年末年始のごみ・役所", "/nenmatsu"], ["初売り・福袋2027", "/hatsuuri"]]
# 泊まりで行く所：大きな街の真ん中（東京駅・新宿・横浜）から25km以上（scripts/kansai_yado.py の kanto と同じ）
CENTERS, FAR_KM = [(35.6812, 139.7671), (35.6896, 139.7006), (35.4658, 139.6223)], 25


def _dist(a, b, c, d):
    r = math.pi / 180
    return 6371 * math.hypot((d - b) * r * math.cos((a + c) / 2 * r), (c - a) * r)


def _yado(R, S):
    p = os.path.join(S, "kanto-yado.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    memo = json.load(open(os.path.join(R, "data", "kanto-yado.json"), encoding="utf-8"))
    return {k: v["h"] for k, v in memo.items() if v.get("h") and v.get("ll") and min(_dist(v["ll"][0], v["ll"][1], a, b) for a, b in CENTERS) >= FAR_KM}


def pct(v):
    return ("+" if v > 0 else "±" if v == 0 else "") + f"{v:.1f}%"


def ranks(rows, key):
    """同じ値は同じ順位（1位 A・1位 B・3位 C）"""
    out, prev, rk = [], None, 0
    for i, r in enumerate(rows):
        if r[key] != prev: rk = i + 1; prev = r[key]
        out.append((rk, r))
    return out


def build(write, cfg, IT, il, ky, ICONS, KINDS, R, S, TD, PREF, FULL, SLUG):
    def YADO_PR(p, w):  # 11/27 shin_kanto.py と同じ（都県の宿・楽天トラベル1本）
        import urllib.parse as _u
        u = "https://hb.afl.rakuten.co.jp/hgc/58b50f43.00cd84ff.58b50f44.4872e82d/?pc=" + _u.quote(f"https://travel.rakuten.co.jp/yado/{SLUG[p]}/", safe="")
        return {"h": f"{p}で泊まって{w}を見る", "t": f"楽天トラベルで{FULL[p]}の宿を見る", "u": u, "n": "楽天トラベルの都県の宿の一覧です（広告・PR）。"}
    made = set()

    def ode(fname, url, title, desc, page, its, cur):
        c = cfg(cur); c["nav"] = ODE_NAV(cur)
        page.setdefault("also", [a for a in ALSO if a[1] != cur])
        write(fname, url, title, c, {"items": its, "icons": ICONS, "page": page}, "list", desc)
        made.add(url)

    # ---------- 紅葉の都県ページ（関西 /koyo-osaka などと同じ） ----------
    for p in PREF:
        nk = sum(1 for i in ky if i["p"] == p)
        if not nk: continue
        write(f"koyo-{SLUG[p]}.html", f"/koyo-{SLUG[p]}", f"{p}の紅葉2026｜見頃とライトアップ（{FULL[p]}）｜LIFE NOTE", cfg("/koyo"),
              {"items": ky, "icons": ICONS, "page": {"h1": f"{p}の紅葉", "sub": f"見頃とライトアップ・{nk}か所", "p": p, "st": "pref", "pr": YADO_PR(p, "紅葉")}}, "odekake",
              f"{FULL[p]}の紅葉の名所とライトアップ{nk}か所を、見頃の時期つきでまとめています。")
        made.add(f"/koyo-{SLUG[p]}")

    # ---------- 初詣（data/hatsumode.tsv：各寺社の公式ページで確かめた事だけ） ----------
    hp = os.path.join(R, "data", "hatsumode.tsv")
    if os.path.exists(hp):
        rows = [l.rstrip("\n").split("\t") for l in open(hp, encoding="utf-8") if l.strip() and not l.startswith("#")]
        rows = [r for r in rows if len(r) == 7]
        hm = []
        try: VP = json.load(open(os.path.join(R, "data", "venue_photos.json"), encoding="utf-8"))
        except Exception: VP = {}
        for p, n, city, tm, tr, yr, url in rows:
            it = {"t": n, "p": p, "a": city, "k": "hatsu", "u": url, "ub": "公式の案内を見る", "id": hashlib.sha1(n.encode()).hexdigest()[:6],
                  "bg": "2027年の案内" if yr == "2027年" else ("昨年の案内" if yr == "昨年" else "例年の案内"), "bgc": "" if yr == "2027年" else "off",
                  "rows": [["時間", tm]] + ([["車・混雑", tr]] if tr not in ("", "—") else []) + [["案内", "2027年の案内" if yr == "2027年" else f"{yr}の案内（2027年の案内が出たら書き換えます）"]],
                  "d": "大晦日〜三が日", "mq": f"{n} {city}"}
            v = VP.get(n) or VP.get(re.sub(r"\s+", "", n)) or {}
            if v.get("img"): it.update({"im": v["img"], "cr": v.get("cr", ""), "cu": v.get("page", "")})
            hm.append(it)
        # 11/27 月：寺社ごとの1件ページ（/hatsumode/<id>・関西と同じ）
        try:
            import shin_nenmatsu as NM0
            _dt0 = NM0.details("hatsumode", hm, "関東", "LIFE NOTE", NM0.machi_map(os.path.join(S, "machi")))
        except Exception as _e: print("初詣の1件ページは作らない", repr(_e)); _dt0 = []
        if _dt0:
            os.makedirs(os.path.join(S, "hatsumode"), exist_ok=True)
            for _pth, _u, _ti, _de, _d in _dt0:
                _c = cfg("/odekake"); _c["nav"] = [{"t": "一覧へ", "ic": "now", "href": "/hatsumode"}]
                _c["foot"] = "各寺社の公式の案内をもとにしています。出かける前に公式の案内をご確認ください。"
                write(_pth + ".html", _u, _ti, _c, _d, "doc", _de)
            for smn in ("sitemap.xml", "sitemap-all.xml"):
                _p = os.path.join(S, smn)
                if os.path.exists(_p):
                    _x = open(_p, encoding="utf-8").read(); _h = re.search(r"<loc>(https?://[^/<]+)", _x); _h = _h.group(1) if _h else "https://kanto.townnote.app"
                    _add = "".join(f"<url><loc>{_h}{_u}</loc><lastmod>{TD}</lastmod></url>\n" for _pth, _u, *_r in _dt0 if f"{_u}<" not in _x)
                    if _add: open(_p, "w", encoding="utf-8").write(_x.replace("</urlset>", _add + "</urlset>", 1))
            print("hatsumode 1件ページ", len(_dt0))
        if len(hm) >= 5:
            n27 = sum(1 for r in rows if r[5] == "2027年")
            ode("hatsumode.html", "/hatsumode", f"関東の初詣2027｜大晦日・三が日の時間と交通規制（{len(hm)}か所）｜LIFE NOTE",
                f"関東7都県の初詣{len(hm)}か所の、大晦日と三が日の参拝時間・交通規制・駐車場を、各寺社の公式ページからまとめました。",
                {"h1": "関東の初詣", "sub": f"2027年・大晦日と三が日・{len(hm)}か所", "dl": f"2027年の案内が出た所 <b>{n27}</b>か所",
                 "K": {"hatsu": ["初詣", "#A23B3B"]}, "cnt": "か所", "unit": "初詣",
                 "note": "時間と交通規制は、各寺社の公式ページの案内です。2027年の案内がまだの所は、昨年・例年の案内を載せ、出たら書き換えます。出かける前に公式で確かめてください。"}, hm, "/hatsumode")

    # ---------- 11/27 年末年始の2枚：/hatsuuri（おかいもの）・/nenmatsu（おでかけ）。中身は scripts/shin_nenmatsu.py（関西 tools/shin/nenmatsu.py と同じ） ----------
    try:
        import shin_nenmatsu as NM
        try: VP2 = json.load(open(os.path.join(R, "data", "venue_photos.json"), encoding="utf-8"))
        except Exception: VP2 = {}
        for nm_, url_, ti_, de_, pg_, its_ in NM.pages("関東", "LIFE NOTE", os.path.join(R, "data", "nenmatsu", "hatsuuri.tsv"), os.path.join(R, "data", "nenmatsu", "gomi.tsv")) + \
                NM.pages2("関東", "LIFE NOTE", os.path.join(R, "data", "nenmatsu", "christmas.tsv"), os.path.join(R, "data", "nenmatsu", "toshikoshi.tsv")):
            for it in its_:
                v = VP2.get(it["t"]) or {}
                if v.get("img"): it.update({"im": v["img"], "cr": v.get("cr", ""), "cu": v.get("page", "")})
            # 11/27 月：1件ずつのページ（/hatsuuri/<id> など・関西と同じ）。一覧の行に「くわしいページ」（sp）が付く
            try: _dt = NM.details(nm_, its_, "関東", "LIFE NOTE", NM.machi_map(os.path.join(S, "machi")))
            except Exception as _e: print("年末年始の1件ページは作らない", repr(_e)); _dt = []
            if nm_ == "hatsuuri":
                c = cfg("/okaimono"); c["menu"] = {"k": "Shopping", "items": [["初売り・福袋", "/hatsuuri", 1]]}
                c["nav"] = [{"t": "おかいもの", "ic": "yen", "href": "/okaimono"}, {"t": "初売り", "ic": "now", "href": "/hatsuuri", "cur": 1}, {"t": "年末年始", "ic": "we", "href": "/nenmatsu"}]
                pg_.setdefault("also", [["年末年始のごみ・役所", "/nenmatsu"], ["関東の初詣", "/hatsumode"], ["日用品の値段くらべ", "/okaimono"], ["お得な物", "/otoku"]])
                write(nm_ + ".html", url_, ti_, c, {"items": its_, "icons": ICONS, "page": pg_}, "list", de_)
                made.add(url_)
            else:
                pg_.setdefault("also", {"christmas": [["関東のイルミネーション", "/illumination"], ["除夜の鐘・年越し", "/toshikoshi"], ["関東のおでかけ・イベント", "/odekake"]],
                                        "toshikoshi": [["関東の初詣", "/hatsumode"], ["年末年始のごみ・役所", "/nenmatsu"], ["クリスマスの催し", "/christmas"]],
                                    "kawaru": [["関東の初詣", "/hatsumode"], ["年末年始のごみ・役所", "/nenmatsu"], ["関東のおでかけ・イベント", "/odekake"]]}.get(nm_,
                                       [["初売り・福袋2027", "/hatsuuri"], ["関東の初詣", "/hatsumode"], ["関東のおでかけ・イベント", "/odekake"]]))
                ode(nm_ + ".html", url_, ti_, de_, pg_, its_, url_)
            if _dt:
                os.makedirs(os.path.join(S, nm_), exist_ok=True)
                for _pth, _u, _ti, _de, _d in _dt:
                    _c = cfg("/okaimono" if nm_ == "hatsuuri" else "/odekake")
                    _c["nav"] = [{"t": "一覧へ", "ic": "now", "href": "/" + nm_}]
                    if nm_ == "hatsuuri": _c["menu"] = {"k": "Shopping", "items": [["初売り・福袋", "/hatsuuri", 1]]}
                    _c["foot"] = "各市区・各店・各主催の公式の案内をもとにしています。出かける前・出す前に公式の案内をご確認ください。"
                    write(_pth + ".html", _u, _ti, _c, _d, "doc", _de)
                print(nm_, "1件ページ", len(_dt))
                for smn in ("sitemap.xml", "sitemap-all.xml"):
                    _p = os.path.join(S, smn)
                    if os.path.exists(_p):
                        _x = open(_p, encoding="utf-8").read(); _h = re.search(r"<loc>(https?://[^/<]+)", _x); _h = _h.group(1) if _h else "https://kanto.townnote.app"
                        _add = "".join(f"<url><loc>{_h}{_u}</loc><lastmod>{TD}</lastmod></url>\n" for _pth, _u, *_r in _dt if f"{_u}<" not in _x)
                        if _add: open(_p, "w", encoding="utf-8").write(_x.replace("</urlset>", _add + "</urlset>", 1))
            sm = os.path.join(S, "sitemap.xml")
            if os.path.exists(sm):
                x = open(sm, encoding="utf-8").read()
                if f"/{nm_}<" not in x:
                    h = re.search(r"<loc>(https?://[^/<]+)", x); h = h.group(1) if h else "https://kanto.townnote.app"
                    open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", f"<url><loc>{h}/{nm_}</loc><lastmod>{TD}</lastmod></url></urlset>", 1))
    except Exception as e:
        print("shin_kanto_lists: 初売り・年末年始は前のまま", repr(e))

    # ---------- 泊まり（少し遠いおでかけ＋近くの評価の高い宿3軒） ----------
    try:
        Y = {re.sub(r"\s+", "", k): v for k, v in _yado(R, S).items() if v}
        tm, seen = [], set()
        for src in (IT, il, ky):
            for x in src:
                k = re.sub(r"\s+", "", x["t"])
                if k not in Y or k in seen or x["e"] < TD: continue
                seen.add(k)
                hs = []
                for h in sorted(Y[k][:3], key=lambda h: h.get("km", 99)):
                    nm = re.sub(r"\s*(<[^<>]*>|\^)\s*$", "", h.get("n", "")).strip()
                    meta = "・".join(v for v in [(f"★{h['r']:.2f}".rstrip("0").rstrip(".") + (f"（口コミ{h['rc']:,}件）" if h.get("rc") else "")) if h.get("r") else "",
                                                 "すぐそば" if h.get("km", 9) < 0.1 else f"ここから{h['km']}km"] if v)
                    hs.append([nm, h["u"], meta, f"{int(h['min']):,}円〜" if h.get("min") else ""])
                it = dict(x); it["links"] = hs; it["lh"] = "近くの宿（評価の高い順から3軒・近い順）"
                it["lnote"] = "宿は楽天トラベルの評価3.5以上・口コミ10件以上。値段は1泊の最安の目安で、日や人数で変わります。宿のリンクは広告（PR）です。"
                it["hk"] = (f"近くの宿 {len(hs)}軒・" + (hs[0][3] if hs and hs[0][3] else "")).rstrip("・")
                tm.append(it)
        if len(tm) >= 5:
            nin = sum(len(x["links"]) for x in tm)
            ode("tomari.html", "/tomari", "泊まりで行く関東のおでかけ｜近くの評価の高い宿つき｜LIFE NOTE",
                f"関東の少し遠いおでかけ{len(tm)}か所と、近くの評価の高い宿をまとめました。宿は楽天トラベルの評価と口コミの数から選んでいます。",
                {"h1": "泊まりで行くおでかけ", "sub": f"少し遠いおでかけ {len(tm)}か所と、近くの宿 {nin}軒", "K": KINDS(tm), "cnt": "か所", "unit": "宿つき",
                 "note": "東京駅・新宿・横浜から25km以上はなれた、泊まりで行きたいおでかけです。押すと近くの宿が3軒出ます。"}, tm, "/tomari")
        print("tomari", len(tm))
    except Exception as e:
        print("shin_kanto_lists: 泊まりは作らない", repr(e))

    # ---------- まちランキング（地価公示・国勢調査の公式の数字から、都県ごと・関東全体の順位） ----------
    try:
        towns = json.load(open(os.path.join(S, "assets", "towns.json"), encoding="utf-8"))
        tk = json.load(open(os.path.join(R, "scripts", "toukei_kanto.json"), encoding="utf-8"))
        jis = json.load(open(os.path.join(R, "scripts", "jis_kanto.json"), encoding="utf-8"))
        src = {s["p"]: s for s in json.load(open(os.path.join(R, "data", "kanto_chika", "sources.json"), encoding="utf-8"))}
        for t in towns:
            s_ = tk.get(jis.get(t["p"] + "|" + t["n"]) or "", {})
            if s_.get("p20") and s_.get("p25"): t["pg"] = round((s_["p25"] / s_["p20"] - 1) * 100, 1); t["pn"] = s_["p25"]
        NOTE = "※ 市区町村の平均の目安です。家ごとの値段は物件で変わります。"
        POPU = "https://www.stat.go.jp/data/kokusei/2025/index.html"
        rl = []

        def item(title, p, k, head, rows, val, extra, url, lead, ub="出どころの公式ページ"):
            rk = ranks(rows, val)
            lines = [f"{r}位 {t['n']}{('（' + t['p'] + '）') if p == '関東' else ''} {pct(t[val])}" + (f"（{t['pn']:,}人）" if val == "pg" and t.get("pn") else "") for r, t in rk]
            body = head + "\n\n" + "\n".join(lines) + ("\n\n" + extra if extra else "") + "\n\n" + NOTE
            first = rk[0][1]
            rl.append({"t": title, "p": p, "k": k, "d": lead, "body": body, "u": url, "ub": ub, "nomap": 1,
                       "id": "k" + hashlib.sha1(title.encode()).hexdigest()[:6],
                       "links": [[t["n"], "/machi/" + t["id"], "この街の家と土地の値段", ""] for _, t in rk[:6]], "lh": "出てくる街のくわしいページ", "lnote": ""})
            return first

        # 関東全体
        al = sorted([t for t in towns if t.get("r8") is not None], key=lambda t: -t["r8"])
        up = sum(1 for t in al if t["r8"] > 0); dn = sum(1 for t in al if t["r8"] < 0)
        a0 = al[0]
        item(f"関東{len(al)}の市区町村｜住宅地の上がり幅1位は{a0['n']}{pct(a0['r8'])}", "関東", "ie",
             "令和8年地価公示・住宅地の平均変動率（1月1日時点）。関東7都県の上位30", al[:30], "r8",
             f"関東{len(al)}の市区町村のうち、上がった所 {up}・下がった所 {dn}・変わらない所 {len(al) - up - dn}。", "https://www.mlit.go.jp/totikensangyo/totikensangyo_fr4_000043.html", "令和8年地価公示")
        pa = sorted([t for t in towns if t.get("pg") is not None], key=lambda t: -t["pg"])
        p0 = pa[0]
        item(f"関東の人口｜5年で増えた割合1位は{p0['n']}{pct(p0['pg'])}", "関東", "hito",
             "国勢調査の人口・2020年から2025年の増えた割合。関東7都県の上位30", pa[:30], "pg",
             f"{len(pa)}の市区町村のうち、人口が増えた所は{sum(1 for t in pa if t['pg'] > 0)}です。", POPU, "国勢調査 2025年")
        # 東京23区
        ku = sorted([t for t in towns if t["p"] == "東京" and t["n"].endswith("区") and t.get("r8") is not None], key=lambda t: -t["r8"])
        if len(ku) >= 20:
            item(f"東京23区｜住宅地の上がり幅1位は{ku[0]['n']}{pct(ku[0]['r8'])}", "東京", "ie",
                 "令和8年地価公示・東京23区の住宅地の平均変動率（1月1日時点）", ku, "r8",
                 "1年前（令和7年）の1位：" + max(ku, key=lambda t: t.get("r7") or -99)["n"] + " " + pct(max(t.get("r7") or -99 for t in ku)), src["東京"]["url"], "令和8年地価公示")
        # 都県ごと
        for p in PREF:
            ts = sorted([t for t in towns if t["p"] == p and t.get("r8") is not None], key=lambda t: -t["r8"])
            if len(ts) >= 5:
                r7 = [t for t in ts if t.get("r7") is not None]
                b7 = max(r7, key=lambda t: t["r7"]) if r7 else None
                up = sum(1 for t in ts if t["r8"] > 0); dn = sum(1 for t in ts if t["r8"] < 0)
                ex = (f"1年前（令和7年）の1位：{b7['n']} {pct(b7['r7'])}\n" if b7 else "") + f"{len(ts)}の市区町村のうち、上がった所 {up}・下がった所 {dn}・変わらない所 {len(ts) - up - dn}。"
                item(f"{FULL[p]}の住宅地｜上がり幅1位は{ts[0]['n']}{pct(ts[0]['r8'])}", p, "ie",
                     f"令和8年地価公示・{FULL[p]}の住宅地の平均変動率（1月1日時点）", ts, "r8", ex, src.get(p, {}).get("url", ""), "令和8年地価公示")
            ps = sorted([t for t in towns if t["p"] == p and t.get("pg") is not None], key=lambda t: -t["pg"])
            if len(ps) >= 5:
                item(f"{FULL[p]}の人口｜5年で増えた割合1位は{ps[0]['n']}{pct(ps[0]['pg'])}", p, "hito",
                     f"国勢調査の人口・{FULL[p]}の市区町村の2020年から2025年の増えた割合", ps, "pg",
                     f"{len(ps)}の市区町村のうち、人口が増えた所は{sum(1 for t in ps if t['pg'] > 0)}です。", POPU, "国勢調査 2025年")
        if len(rl) >= 5:
            c = copy.deepcopy(cfg("/fudosan-list"))
            c["nav"] = [{"t": "街をさがす", "ic": "find", "href": "/fudosan-list"}, {"t": "ランキング", "ic": "rank", "a": "top", "cur": 1}, {"t": "売りたい", "ic": "sell", "href": "/uru"}, {"t": "いくら？", "ic": "yen", "href": "/ikura"}]
            c["menu"] = {"k": "Home & Land", "items": [["まちランキング", "/ranking", 1]]}
            c["foot"] = "数字はどれも国・都県の公式の発表です（地価公示・国勢調査）。街の平均で、1軒ずつの値段ではありません。"
            c["sell"] = sell_cfg(1)
            write("ranking.html", "/ranking", f"関東まちランキング｜地価・人口の順位を公式の数字で（{len(rl)}本）｜LIFE NOTE", c,
                  {"items": rl, "page": {"h1": "関東まちランキング", "sub": f"地価・人口の順位を、公式の数字で・{len(rl)}本", "view": "list", "cnt": "本",
                                         "K": {k[0]: [k[1], k[2]] for k in KIND if any(x["k"] == k[0] for x in rl)},
                                         "note": "数字は国土交通省・各都県・総務省統計局の公式の発表です。押すと順位の全部と、出どころの公式ページが出ます。"}},
                  "list", f"関東の街を、住宅地の地価の動き・人口の増えた割合など公式の数字で順位にしました（{len(rl)}本）。")
            made.add("/ranking")
        print("ranking", len(rl))
    except Exception as e:
        print("shin_kanto_lists: まちランキングは作らない", repr(e))
    # 検索の機械が見つけられるように sitemap に足す（同じ住所はくり返さない）
    try:
        sm = os.path.join(S, "sitemap.xml")
        if os.path.exists(sm):
            x = open(sm, encoding="utf-8").read()
            base = (re.search(r"<loc>(https://[^/<]+)", x) or [None, "https://kanto.townnote.app"])[1]
            add = "".join(f"<url><loc>{base}{u}</loc><lastmod>{TD}</lastmod></url>" for u in sorted(made) if f"{base}{u}<" not in x)
            if add: open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", add + "</urlset>", 1))
    except Exception as e:
        print("shin_kanto_lists: sitemap は前のまま", repr(e))
    return made
