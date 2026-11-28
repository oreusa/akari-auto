"""11/27 年末年始の2枚（/hatsuuri 初売り・福袋、/nenmatsu ごみ・役所）。関西 tools/shin/lists.py・関東 scripts/shin_kanto_lists.py から同じ形で呼ぶ。
元のデータは夜が公式から集めた行（関西 tools/nenmatsu/*.tsv・関東 data/nenmatsu/*.tsv。もとは project-files kanri/nenmatsu）。
「未確認」「不明」「未照合」「要確認」の区切りは書かず、全部消えた欄は「公式で確認」（カードの公式リンクへ）。"""
import datetime, hashlib, os, re

NG = re.compile(r"未確認|不明|未照合|要確認|確認中|断定|リンク先|を使用")
RAKUTEN_XMAS = "https://hb.afl.rakuten.co.jp/hgc/58b50f43.00cd84ff.58b50f44.4872e82d/?pc=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F%25E3%2582%25AF%25E3%2583%25AA%25E3%2582%25B9%25E3%2583%259E%25E3%2582%25B9%2520%25E3%2582%25AE%25E3%2583%2595%25E3%2583%2588%2F"
RAKUTEN = "https://hb.afl.rakuten.co.jp/hgc/58b50f43.00cd84ff.58b50f44.4872e82d/?pc=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F%25E7%25A6%258F%25E8%25A2%258B%25202027%2F"


def clean(v):
    out, cut = [], False
    for s in re.split(r"。", (v or "").strip()):
        s = s.strip()
        if not s: continue
        if NG.search(s):
            cut = True
            cs = [c for c in re.split(r"、", s) if c.strip() and not NG.search(c)]
            if cs: out.append("、".join(cs))
        else: out.append(s)
    t = "。".join(out)
    if not t: return "公式で確認"
    return t + ("（ほかは公式で確認）" if cut else "")


def _rows(path, region):
    if not os.path.exists(path): return []
    rr = [l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")]
    return [r for r in rr if len(r) >= 8 and r[0] == region]


def _pf(x): return re.sub(r"(都|府|県)$", "", x)


def hatsuuri(path, region):
    its = []
    for _, pf, n, ganjitsu, hatsu, fuku, close, urls in (r[:8] for r in _rows(path, region)):
        us = urls.split()
        it = {"t": n, "p": _pf(pf), "a": pf, "k": "uri", "u": us[0] if us else "", "ub": "公式の案内を見る", "id": hashlib.sha1(n.encode()).hexdigest()[:6],
              "rows": [["元日・1/2", clean(ganjitsu)], ["初売り", clean(hatsu)], ["福袋", clean(fuku)], ["閉店時刻", clean(close)]],
              "d": "元日〜初売り", "mq": f"{n} {pf}"}
        if clean(fuku).startswith("あり"): it["bg"] = "福袋あり"
        it["hk"] = "／".join(f"{a} {b}" for a, b in it["rows"][:2] if b != "公式で確認") or "元日・初売りは公式で確認"
        its.append(it)
    return its


def gomi(path, region):
    its = []
    for _, pf, n, sh, sodai, mochi, yaku, urls in (r[:8] for r in _rows(path, region)):
        us = urls.split()
        its.append({"t": n, "p": _pf(pf), "a": pf, "k": "gomi", "u": us[0] if us else "", "ub": "市の公式の案内を見る", "id": hashlib.sha1(n.encode()).hexdigest()[:6],
                    "rows": [["ごみの収集", clean(sh)], ["粗大ごみ", clean(sodai)], ["持ち込み", clean(mochi)], ["役所の休み", clean(yaku)]],
                    "d": "年末年始", "mq": f"{n}役所 {pf}"})
        its[-1]["hk"] = ("ごみ " + clean(sh)) if clean(sh) != "公式で確認" else ("役所の休み " + clean(yaku))
    return its


def _md(t, today):
    """「11/27〜12/25」などから (始まり, 終わり) の日付。年は今日に近い方（1〜5月は次の年）"""
    t = re.sub(r"(\d{1,2})[/月](\d{1,2})日?〜(\d{1,2})(?![/月\d])", lambda m: f"{m.group(1)}/{m.group(2)}〜{m.group(1)}/{m.group(3)}", t or "")  # 12/18〜20 → 12/18〜12/20
    mm = re.findall(r"(\d{1,2})[/月](\d{1,2})", t)
    if not mm: return "", ""
    def d(m, dd):
        m, dd = int(m), int(dd); y = today.year + (1 if m < 6 and today.month >= 6 else 0)
        try: return datetime.date(y, m, dd).isoformat()
        except ValueError: return ""
    return d(*mm[0]), d(*mm[-1])


def christmas(path, region, today=None):
    """列：地域・都府県・名前・場所・期間・時間・入場料・見どころ・公式URL。終わった行は出さない"""
    today = today or datetime.date.today(); td = today.isoformat(); its = []
    if not os.path.exists(path): return its
    for r in (l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")):
        if len(r) < 9 or r[0] != region: continue
        _, pf, n, place, per, tm, fee, mie, urls = r[:9]
        st, en = _md(per, today)
        if en and en < td: continue
        us = urls.split(); fe = clean(fee)
        it = {"t": n, "p": _pf(pf), "a": pf, "v": place, "k": "xmas", "u": us[0] if us else "", "ub": "公式の案内を見る", "id": hashlib.sha1(n.encode()).hexdigest()[:6],
              "rows": [["期間", clean(per)], ["時間", clean(tm)], ["入場料", fe], ["見どころ", clean(mie)]], "mq": f"{place or n} {pf}"}
        if st and en: it.update({"s": st, "e": en})
        else: it["d"] = clean(per)
        it["hk"] = "／".join(x for x in (clean(tm) if clean(tm) != "公式で確認" else "", fe if fe != "公式で確認" else "") if x) or clean(mie)
        if fe.startswith("無料"): it["f"] = 1
        its.append(it)
    return its


def toshikoshi(path, region, today=None):
    """列：地域・都府県・名前・場所・12/31の時間・人数と料金・2026年か例年か・公式URL。1/2になったら全部消す"""
    today = today or datetime.date.today(); its = []
    if today.month == 1 and today.day >= 2: return its
    if not os.path.exists(path): return its
    end = datetime.date(today.year + (1 if today.month >= 6 else 0), 1, 1).isoformat()
    for r in (l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")):
        if len(r) < 8 or r[0] != region: continue
        _, pf, n, place, tm, ppl, yr, urls = r[:8]
        us = urls.split(); rei = "2026" not in yr
        it = {"t": n, "p": _pf(pf), "a": pf, "v": place, "k": "toshi", "u": us[0] if us else "", "ub": "公式の案内を見る", "id": hashlib.sha1(n.encode()).hexdigest()[:6],
              "rows": [["12/31の時間", clean(tm)], ["人数・料金", clean(ppl)], ["案内", "例年の案内（2026年の案内が出たら書き換えます）" if rei else "2026年の案内"]],
              "bg": "例年の案内" if rei else "2026年の案内", "bgc": "off" if rei else "", "d": "12/31〜元日", "e": end, "mq": f"{place or n} {pf}"}
        it["hk"] = clean(tm) if clean(tm) != "公式で確認" else clean(ppl)
        its.append(it)
    return its


def kawaru(path, region, today=None):
    """11/28 月：道と電車・バスが変わる日（夜の【夜 変わる日】）。列：地域・都府県・市区・何が・いつ・どう変わる・ひとこと・公式URL。
    書いてある一番遅い日の14日後まで出す（「◯◯ いつから」で検索する人の入口）"""
    today = today or datetime.date.today(); its = []
    if not os.path.exists(path): return its
    for r in (l.rstrip("\n").split("\t") for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")):
        if len(r) < 8 or r[0] != region: continue
        _, pf, city, n, when, how, tip, urls = r[:8]
        ds = [datetime.date(int(a), int(b), int(c)) for a, b, c in re.findall(r"(20\d\d)/(\d{1,2})/(\d{1,2})", when)]
        if not ds: continue
        if max(ds) + datetime.timedelta(days=14) < today: continue
        us = urls.split()
        it = {"t": n, "p": _pf(pf), "a": pf, "v": city, "k": "kawa", "u": us[0] if us else "", "ub": "公式のお知らせを見る", "id": hashlib.sha1(n.encode()).hexdigest()[:6],
              "rows": [["いつ", clean(when)], ["どう変わる", clean(how)], ["使う人へ", clean(tip)]],
              "d": when, "s": min(ds).isoformat(), "e": (max(ds) + datetime.timedelta(days=14)).isoformat(), "mq": f"{pf}{city} {n}", "hk": clean(when)}
        its.append(it)
    its.sort(key=lambda x: x["s"])
    return its


def pages2(region, site, cpath, tpath):
    """12月の2枚：/christmas と /toshikoshi。5件未満なら作らない（夜の行が入るまで出さない）"""
    out = []
    c = christmas(cpath, region)
    if len(c) >= 5:
        out.append(("christmas", "/christmas", f"{region}のクリスマスマーケット・クリスマスの催し2026｜期間・時間・入場料（{len(c)}か所）｜{site}",
                    f"{region}のクリスマスマーケットとクリスマスの催し{len(c)}か所の、期間・時間・入場料・見どころを、各主催の公式ページからまとめました。終わった催しは自動で外します。",
                    {"h1": f"{region}のクリスマス", "sub": f"マーケットと催し 2026・{len(c)}か所", "K": {"xmas": ["クリスマス", "#2E6B4F"]}, "cnt": "か所", "unit": "か所", "view": "list",
                     "note": "期間・時間・入場料は各主催の公式の案内です。確かめられていない所は「公式で確認」です。",
                     "pr": {"h": "クリスマスの準備に", "t": "楽天市場のクリスマスギフトを見る", "u": RAKUTEN_XMAS, "n": "楽天市場の検索ページです（広告・PR）。"}}, c))
    t = toshikoshi(tpath, region)
    if len(t) >= 5:
        n26 = sum(1 for x in t if x["bgc"] == "")
        out.append(("toshikoshi", "/toshikoshi", f"{region}の除夜の鐘・年越しカウントダウン2026-2027｜12/31の時間・人数・料金（{len(t)}か所）｜{site}",
                    f"{region}の除夜の鐘と年越しカウントダウン{len(t)}か所の、大晦日の時間・つける人数や料金を、各寺社・主催の公式ページからまとめました。",
                    {"h1": f"{region}の除夜の鐘・年越し", "sub": f"2026-2027・大晦日・{len(t)}か所", "dl": f"2026年の案内が出た所 <b>{n26}</b>か所",
                     "K": {"toshi": ["年越し", "#3B4B7A"]}, "cnt": "か所", "unit": "か所", "view": "list",
                     "note": "2026年の案内がまだの所は例年の案内を載せ、出たら書き換えます。"}, t))
    k = kawaru(os.path.join(os.path.dirname(tpath), "kawaru.tsv"), region)
    if len(k) >= 5:
        out.append(("kawaru", "/kawaru", f"{region}の道と電車・バスが変わる日 2026-2027｜新しい改札・乗り場の変更・路線の廃止・通行止め（{len(k)}件）｜{site}",
                    f"{region}で、これから変わる駅の改札・バスの乗り場や路線・道路の規制{len(k)}件を、鉄道会社・バス会社・国や市の公式のお知らせからまとめました。いつから、どう変わるかを1件ずつ。",
                    {"h1": f"{region}の道と電車が変わる日", "sub": f"駅・バス・道路・{len(k)}件", "K": {"kawa": ["変わる日", "#3E6A8A"]}, "cnt": "件", "unit": "件", "view": "list",
                     "note": "鉄道会社・バス会社・国や市の公式のお知らせです。変わることがあるので、使う前に公式のお知らせを確かめてください。"}, k))
    return out


def pages(region, site, hpath, gpath):
    """[(name, url, title, desc, page, items)]。5件未満のページは作らない"""
    out = []
    h = hatsuuri(hpath, region)
    if len(h) >= 5:
        out.append(("hatsuuri", "/hatsuuri", f"{region}の初売り・福袋2027｜百貨店の元日休み・初売りの時間・福袋の予約（{len(h)}店）｜{site}",
                    f"{region}の百貨店・ショッピングセンター{len(h)}店の、元日の休み・初売りの日と時間・福袋の予約や抽選・閉店時刻を、各店の公式ページからまとめました。",
                    {"h1": f"{region}の初売り・福袋", "sub": f"2027年・元日から初売りまで・{len(h)}店", "K": {"uri": ["初売り", "#B5553C"]}, "cnt": "店", "unit": "店", "view": "list",
                     "note": "元日の休み・初売り・福袋は各店の公式の案内です。確かめられていない所は「公式で確認」です。",
                     "pr": {"h": "ネットで買える福袋", "t": "楽天市場の福袋2027を見る", "u": RAKUTEN, "n": "楽天市場の検索ページです（広告・PR）。"}}, h))
    g = gomi(gpath, region)
    if len(g) >= 5:
        out.append(("nenmatsu", "/nenmatsu", f"{region}の年末年始のごみ・役所2026-2027｜最終収集日・年始の開始・粗大ごみ（{len(g)}市区）｜{site}",
                    f"{region}の{len(g)}市区の、年末の最終収集日と年始の開始・粗大ごみ・持ち込み・役所の休みを、各市区の公式ページからまとめました。",
                    {"h1": f"{region}の年末年始のごみ・役所", "sub": f"2026-2027・{len(g)}市区", "K": {"gomi": ["年末年始", "#4F7A6B"]}, "cnt": "市区", "unit": "市区", "view": "list",
                     "note": "収集日は地区で違う所が多いので、自分の地区は各市区の公式の表で確かめてください。"}, g))
    return out


# ---------- 11/27 月：1件ずつのページ（/hatsuuri/<id>・/nenmatsu/<id>・/christmas/<id>・/toshikoshi/<id>） ----------
# 検索の帳面で、開店の1店ページ（「◯◯ いつ開店」に1件1ページで答える）が一番見られていた → 年末年始も「◯◯市 年末年始 ごみ」「◯◯ 初売り 2027」に1件1ページで答える。
# 関西 tools/shin/lists.py・関東 scripts/shin_kanto_lists.py から同じ形で呼ぶ。中身は一覧と同じ行（夜が公式で集めた物）だけ。
def machi_map(mdir):
    """街のページの名前 → /machi/<id>（ごみのページから「この街の家と土地の相場」へ1本）"""
    out = {}
    if not os.path.isdir(mdir): return out
    for f in os.listdir(mdir):
        if not f.endswith(".html"): continue
        try: m = re.search(r"<title>([^<｜|]*?)の地価", open(os.path.join(mdir, f), encoding="utf-8").read(3000))
        except Exception: m = None
        if m: out[m.group(1)] = "/machi/" + f[:-5]
    return out


def _e(s):
    import html as _h
    return _h.escape(str(s or ""), quote=True)


def details(name, items, region, site, machi=None, today=None):
    """一覧の行 → [(path, url, title, desc, data)]。一覧の行には it["sp"]（くわしいページ）を足す"""
    import urllib.parse as _up
    today = today or datetime.date.today()
    machi = machi or {}
    LBL = {"hatsumode": "初詣2027", "hatsuuri": "初売り・福袋2027", "nenmatsu": "年末年始のごみ・役所", "christmas": "クリスマスの催し", "toshikoshi": "除夜の鐘・年越し", "kawaru": "道と電車が変わる日"}[name]
    out = []
    for it in items:
        it["sp"] = f"/{name}/{it['id']}"
    for it in items:
        n, pf, rows = it["t"], it.get("a") or it["p"], it.get("rows", [])
        rv = {a: b for a, b in rows}
        if name == "hatsuuri":
            title = f"{n}の初売り2027はいつ？元日の営業・福袋・閉店時刻｜{pf}｜{site}"
            sub = f"{pf}・初売り2027"
            desc = f"{n}の2027年の初売り。元日・1/2：{rv.get('元日・1/2', '公式で確認')}。初売り：{rv.get('初売り', '公式で確認')}。福袋：{rv.get('福袋', '公式で確認')}。"
        elif name == "nenmatsu":
            title = f"{n}の年末年始のごみ収集2026-2027｜最終日・年始の開始・粗大ごみ・役所の休み｜{site}"
            sub = f"{pf}・年末年始のごみと役所"
            desc = f"{n}の年末年始。ごみの収集：{rv.get('ごみの収集', '公式で確認')}。役所の休み：{rv.get('役所の休み', '公式で確認')}。"
        elif name == "hatsumode":
            title = f"{n}の初詣2027｜大晦日・三が日の参拝時間・交通規制｜{it.get('a') or pf}｜{site}"
            sub = f"{it['p']}・初詣2027"
            desc = f"{n}（{it.get('a') or pf}）の初詣2027。時間：{rv.get('時間', '公式で確認')}。" + (f"車・混雑：{rv['車・混雑']}。" if rv.get('車・混雑') else "")
        elif name == "toshikoshi":
            title = f"{n} 2026-2027｜大晦日の時間・人数・料金｜{pf}｜{site}"
            sub = f"{pf}・除夜の鐘・年越し"
            desc = f"{n}（{it.get('v') or pf}）。12/31の時間：{rv.get('12/31の時間', '公式で確認')}。人数・料金：{rv.get('人数・料金', '公式で確認')}。"
        elif name == "kawaru":
            title = f"{n}はいつから？{rv.get('いつ', '')}｜{it.get('v') or pf}｜{site}"
            sub = f"{pf}{it.get('v') or ''}・変わる日"
            desc = f"{n}。いつ：{rv.get('いつ', '公式で確認')}。{rv.get('どう変わる', '')}"
        else:
            title = f"{n}｜期間・時間・入場料｜{pf}のクリスマス2026｜{site}"
            sub = f"{pf}・クリスマスの催し"
            desc = f"{n}（{it.get('v') or pf}）。期間：{rv.get('期間', '公式で確認')}。時間：{rv.get('時間', '公式で確認')}。入場料：{rv.get('入場料', '公式で確認')}。"
        desc = desc[:150]
        big = '<div class="big">' + "".join(f'<div class="w"><span>{_e(a)}</span><b>{_e(b)}</b></div>' for a, b in rows) + "</div>"
        q = _up.quote(it.get("mq") or f"{n} {pf}")
        act = ('<div class="oact">' + (f'<a class="dbtn" href="{_e(it["u"])}" target="_blank" rel="noopener" data-k="1件｜公式">{_e(it.get("ub") or "公式の案内を見る")} ↗</a>' if it.get("u") else "")
               + f'<a class="dbtn2" href="https://www.google.com/maps/search/?api=1&amp;query={q}" target="_blank" rel="noopener" data-k="1件｜地図">地図アプリで開く</a></div>')
        note = ('<p class="dnote">収集日は地区で違う所が多いので、自分の地区は市区の公式の表で確かめてください。</p>' if name == "nenmatsu" else
                '<p class="dnote">鉄道会社・バス会社・国や市の公式のお知らせをもとにしています。変わることがあるので、使う前に公式のお知らせをご確認ください。</p>' if name == "kawaru" else
                '<p class="dnote">各主催・各店の公式の案内をもとにしています。変わることがあるので、出かける前に公式の案内をご確認ください。「公式で確認」は、まだ確かめられていない所です。</p>')
        html_ = '<section class="dsec osp">' + big + act + note + "</section>"
        if name == "hatsuuri":
            html_ += (f'<section class="dsec"><h2>ネットで買える福袋</h2><div class="oact"><a class="dbtn2" href="{_e(RAKUTEN)}" target="_blank" rel="noopener sponsored" data-k="1件｜楽天 福袋">楽天市場の福袋2027を見る ↗</a></div>'
                      '<p class="dnote">楽天市場の検索ページです（広告・PR）。</p></section>')
        mk = max((k for k in machi if n.startswith(k) or (it.get("v") or "").startswith(k)), key=len, default="")
        sibs = [x for x in items if x is not it and x.get("p") == it.get("p")][:8]
        if sibs:
            html_ += (f'<section class="dsec"><h2>{_e(it["p"])}のほかの{_e({"nenmatsu": "市区", "hatsumode": "初詣", "kawaru": "変わる予定"}.get(name, LBL.split("・")[0]))}</h2><div class="drel">'
                      + "".join(f'<a href="{x["sp"]}" data-k="1件｜同じ府県">{_e(x["t"])}<small>{_e(x.get("hk", ""))[:40]}</small></a>' for x in sibs) + "</div></section>")
        rel = [(f"{region}の{LBL}（一覧）", f"/{name}")]
        if mk: rel.append((f"{mk}の家と土地の相場", machi[mk]))
        html_ += ('<section class="dsec"><h2>あわせて見る</h2><div class="drel">'
                  + "".join(f'<a href="{u}" data-k="あわせて：{_e(l)}">{_e(l)}</a>' for l, u in rel) + "</div></section>")
        out.append((f"{name}/{it['id']}", it["sp"], title, desc, {"h1": n, "sub": sub, "html": html_, "js": ""}))
    return out
