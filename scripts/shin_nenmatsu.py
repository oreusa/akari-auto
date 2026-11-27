"""11/27 年末年始の2枚（/hatsuuri 初売り・福袋、/nenmatsu ごみ・役所）。関西 tools/shin/lists.py・関東 scripts/shin_kanto_lists.py から同じ形で呼ぶ。
元のデータは夜が公式から集めた行（関西 tools/nenmatsu/*.tsv・関東 data/nenmatsu/*.tsv。もとは project-files kanri/nenmatsu）。
「未確認」「不明」「未照合」「要確認」の区切りは書かず、全部消えた欄は「公式で確認」（カードの公式リンクへ）。"""
import datetime, hashlib, os, re

NG = re.compile(r"未確認|不明|未照合|要確認|確認中")
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
    mm = re.findall(r"(\d{1,2})[/月](\d{1,2})", t or "")
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
