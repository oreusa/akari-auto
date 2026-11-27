"""11/27 年末年始の2枚（/hatsuuri 初売り・福袋、/nenmatsu ごみ・役所）。関西 tools/shin/lists.py・関東 scripts/shin_kanto_lists.py から同じ形で呼ぶ。
元のデータは夜が公式から集めた行（関西 tools/nenmatsu/*.tsv・関東 data/nenmatsu/*.tsv。もとは project-files kanri/nenmatsu）。
「未確認」「不明」「未照合」「要確認」の区切りは書かず、全部消えた欄は「公式で確認」（カードの公式リンクへ）。"""
import hashlib, os, re

NG = re.compile(r"未確認|不明|未照合|要確認|確認中")
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
