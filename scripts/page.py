"""燈のプロフィール用ページ（うさぎ│LIFE NOTES）を作る。lit.link の代わり。

毎晩、schedule/*.json の「もう出た投稿」から1枚のページを作り、site/index.html に書く。
・今週行ける場所・新しいお店・今だけのお得：投稿の見出しと ◇ の行と公式ページのURL。
・AIが比べた（PR）：PRの投稿。楽天のリンクは作る直前に楽天で「販売中・同じ商品か」を確かめた物だけ載せる。
  楽天のキーがないとき（見本づくり）は、楽天の商品ページURLをそのまま置き、見本と分かるようにする。
・期限（until）を過ぎた投稿は「終わった」へ。7日より古い投稿は載せない。

使い方：python scripts/page.py [--now 2026-10-24T09:00]
"""
import glob
import html
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import JST, URL_RE, load_json, now_jst, path  # noqa: E402

DAYS = 7
ODEKAKE = {"おでかけ", "イルミネーション", "温泉", "紅葉", "無料", "イベント", "週末旅", "旅行"}
SHOP = {"グルメ", "カフェ", "新店"}
DEAL = {"お得情報", "お得"}
SECTIONS = [
    ("odekake", "今週のおでかけ", "公式ページで日時と料金を確かめた物だけを載せています"),
    ("shop", "できたばかりのお店", "開いたばかりのお店と、はじめて出るお店"),
    ("deal", "今だけのお得", "期間のあるお得。終わる日を先に書いています"),
    ("pr", "AIが選んだ物", "3つ以上を数字で比べて、1つだけ選んだ物です"),
]
SHOW_GO = 3  # おでかけは最初の3件だけ見せ、残りはたたむ（商品とのバランス）
SEASON_I = {"spring": 0, "summer": 1, "autumn": 2, "winter": 3}


def period(now):
    """seasons.json から今日の時期を選ぶ（from が今日以前でいちばん新しい物。年の初めは前の年の最後の時期）。"""
    ps = sorted((load_json(path("seasons.json"), {}) or {}).get("periods", []), key=lambda x: x["from"])
    today = f"{now.month:02d}-{now.day:02d}"
    past = [x for x in ps if x["from"] <= today]
    return (past or ps)[-1] if ps else {"name": "", "season": "autumn", "cats": []}


def cats(now):
    """紹介商品の項目（ページの並び順）：宿 → 時期の項目 → 暮らしの物 → 楽天のお得。時期が変わると自動で入れ替わる。"""
    mid = [(c["key"], c["en"], c["name"], c["lead"], tuple(c.get("words", ()))) for c in period(now).get("cats", [])]
    return ([("stay", "STAY", "週末の宿", "口コミ1,000件以上・評価4.5以上の宿だけ", ()),
             ("book", "BOOKING", "旅と贈り物の予約", "宿とツアー、体験、お花の定期便", ())] + mid
            + [("life", "DAILY", "暮らしの物", "すぐ使う小物と消耗品", ()),
               ("sale", "SALE", "楽天のお得", "楽天のセールとポイントアップ。終わる日を先に書いています", ())])


def _lines(text):
    return [ln.strip() for ln in text.split("\n") if ln.strip()]


def _title(text):
    t = _lines(text)[0]
    t = t.strip("【】")
    return t


def _bullets(text):
    return [ln[1:].strip() for ln in _lines(text) if ln.startswith("◇")][:6]


def _line_with(text, key):
    for ln in _lines(text):
        if key in ln:
            return ln
    return ""


def _official(post):
    if post.get("_url"):
        return post["_url"]
    for t in post["threads"][1:]:
        for u in URL_RE.findall(t):
            if "{{" not in u:
                return u.rstrip("）)」。、")
    return ""


def _resolve(link, texts):
    """PRのリンクを楽天で確かめる。キーがないときは見本として商品ページのURLを返す。"""
    if not os.environ.get("RAKUTEN_APP_ID"):
        if link.get("type") == "ichiba":
            return {"ok": True, "link": link["url"], "sample": True}
        if link.get("type") == "travel":
            return {"ok": True, "link": f"https://travel.rakuten.co.jp/HOTEL/{int(link['hotelNo'])}/", "sample": True}
        return {"ok": False}
    allowed = ["ichiba", "travel"]
    if ((load_json(path("config.json"), {}) or {}).get("page") or {}).get("amazon"):
        allowed.append("amazon")  # Amazonアソシエイトにこのページのアドレスを登録した後だけ（config.json の page.amazon）
    if link.get("type") not in allowed:
        return {"ok": False, "why": "このページのアドレスを登録した広告だけ載せる（A8は未登録）"}
    from book import resolve_link  # 予約係と同じ確かめ方
    try:
        return resolve_link(link, texts)
    except Exception as e:  # 楽天につながらない日は載せない
        return {"ok": False, "why": str(e)[:80]}


def collect(now):
    since = (now - timedelta(days=DAYS)).date()
    items = {k: [] for k, _, _ in SECTIONS}
    ended = []
    seen = set()
    pr_urls = set()
    cs = cats(now)
    for f in sorted(glob.glob(path("schedule", "*.json")), reverse=True):
        day = os.path.basename(f)[:-5]
        if not re.match(r"\d{4}-\d{2}-\d{2}$", day):
            continue
        d = datetime.fromisoformat(day).date()
        if d < since:
            continue
        data = load_json(f, {}) or {}
        # 公式ページを「付け忘れ」の別の投稿で出した日は、そのURLを元の投稿のカードに付ける
        for fu in [q for q in data.get("posts", []) if "付け忘れ" in q["threads"][0]]:
            for q in data.get("posts", []):
                if q is not fu and q.get("topic") == fu.get("topic") and not q.get("link") and not _official(q):
                    q["_url"] = _official(fu)
        for p in sorted(data.get("posts", []), key=lambda p: p.get("slot", ""), reverse=True):
            due = datetime.fromisoformat(f"{day}T{p['slot']}").replace(tzinfo=JST)
            if due > now and not (p.get("link") and d == now.date()):
                continue  # PRは当日分を朝から載せる（リンクはこの場で楽天に確かめる）
            text = p["threads"][0]
            if "付け忘れ" in text:
                continue
            title = _title(text)
            if title in seen:
                continue
            seen.add(title)
            entry = {"day": f"{d.month}/{d.day}", "year": d.year, "title": title, "bullets": _bullets(text),
                     "reason": _line_with(text, "選んだ理由").replace("選んだ理由：", ""),
                     "source": _line_with(text, "より（"), "url": _official(p)}
            until = p.get("ends") or p.get("until")  # ends＝催し・お得が終わる時刻（夜の回が書く）。過ぎたらページから外す
            if until and datetime.fromisoformat(until).replace(tzinfo=JST) < now:
                ended.append(entry)
                continue
            link = p.get("link")
            if link:
                r = _resolve(link, list(p["x"]) + list(p["threads"]))
                if not r.get("ok"):
                    continue
                pr_urls.add(link.get("url", ""))
                entry["expect"] = link.get("expect", "")
                entry["url"] = r["link"]
                entry["sample"] = r.get("sample", False)
                entry["image"] = r.get("image", "")
                entry["amazon"] = link.get("type") == "amazon"
                entry["cat"] = "stay" if link.get("type") == "travel" else _cat(_text(entry) + " " + entry["expect"], cs)
                items["pr"].append(entry)
                continue
            topic = p.get("topic", "")
            if topic in DEAL and _rakuten_page(entry["url"]):  # 楽天のセールは楽天アフィリエイトのリンクにする
                entry["url"] = _rakuten_afl(entry["url"])
                entry["cat"] = "sale"
                items["pr"].append(entry)
                continue
            key = "odekake" if topic in ODEKAKE else "shop" if topic in SHOP else "deal" if topic in DEAL else ""
            if key:  # リンクのない比べ（電気代など）はページに載せない
                entry["kind"] = key
                items[key].append(entry)
    items["pick"] = _room_picks(now, since, skip=pr_urls)
    items["a8"] = _a8_items()
    return items, ended


def _rakuten_page(url):
    host = urllib.parse.urlparse(url or "").hostname or ""
    return host == "rakuten.co.jp" or host.endswith(".rakuten.co.jp")


def _rakuten_afl(url):
    aid = os.environ.get("RAKUTEN_AFFILIATE_ID")
    if not aid:
        return url  # 見本（キーのない手元）はそのまま
    enc = urllib.parse.quote(url, safe="")
    return f"https://hb.afl.rakuten.co.jp/hgc/{aid}/?pc={enc}&m={enc}"


def _cat(text, cs):
    for key, _, _, _, words in cs:  # 宿とセールは言葉を持たないので当たらない
        if any(w in text for w in words):
            return key
    return "life"


A8_NOTE = {  # 広告主ごとの一言（A8の案内に書いてある事だけ）
    "nta.co.jp": "JR＋宿泊のセットや国内ツアーを、まとめて予約できます",
    "kkday.com": "国内と海外の体験・チケットを予約できます",
    "hitohana.tokyo": "色が選べるお花の定期便",
    "andplants.jp": "観葉植物のお店のお花の定期便",
}


def _a8_items():
    """汐がリンク帳に書いた「A8ページ」のリンク（このページのサイトで取った物）。夜の回が data/a8-page.json に写す。
    開いて広告主のページに着いた物だけ載せる。"""
    out = []
    for it in (load_json(path("data", "a8-page.json"), {}) or {}).get("items", []):
        url, host = it.get("url", ""), it.get("host", "")
        if not url:
            continue
        if os.environ.get("RAKUTEN_APP_ID"):  # 機械の上だけで確かめる（手元の見本はそのまま）
            from lib import a8_link
            try:
                if not a8_link(url, host).get("ok"):
                    continue
            except Exception:
                continue
        raw = it.get("name", "")
        m = re.search(r"【([^】]+)】", raw)
        rest = re.sub(r"【[^】]*】", " ", raw).replace("！", "、").strip(" 、")
        name = m.group(1) if m else raw
        if m and rest and re.search(r"オフ|OFF|プレゼント|無料|％|%|円", m.group(1)):  # 【】が宣伝文のときは残りを名前にする
            name = rest
        note = next((v for k, v in A8_NOTE.items() if host.endswith(k)), "") or (rest if m else "")
        out.append({"name": name, "url": url, "note": note})
    return out


def _short(name, n=34):
    name = re.sub(r"【[^】]*】|［[^］]*］|\[[^\]]*\]", "", name or "").strip()
    return name if len(name) <= n else name[:n].rstrip() + "…"


def _room_picks(now, since, skip=(), limit=24):
    """ROOM台本の商品（毎晩、燈が比べて選んだ3品）を、新しい順に最大24品。楽天で販売中を確かめた物だけ。"""
    out, seen = [], set()
    for f in sorted(glob.glob(path("schedule", "*.json")), reverse=True):
        day = os.path.basename(f)[:-5]
        if not re.match(r"\d{4}-\d{2}-\d{2}$", day):
            continue
        d = datetime.fromisoformat(day).date()
        if d < since or d > now.date():
            continue
        for it in (load_json(f, {}) or {}).get("room", []):
            url = it.get("url", "")
            if not url or url in seen or url in skip:  # 上の「AIが比べた」と同じ物は出さない
                continue
            seen.add(url)
            r = _resolve({"type": "ichiba", "url": url, "expect": it.get("expect", "")}, [it.get("comment", "")])
            if not r.get("ok"):
                continue
            lines = [ln.strip() for ln in (it.get("comment") or "").split("\n") if ln.strip() and not ln.startswith("#")]
            out.append({"day": f"{d.month}/{d.day}", "name": _short(r.get("name")) or it.get("expect", ""),
                        "expect": it.get("expect", ""), "price": r.get("price"), "count": r.get("reviewCount"),
                        "avg": r.get("reviewAverage"), "lines": lines[:3], "url": r["link"],
                        "sample": r.get("sample", False), "image": r.get("image", "")})
            out[-1]["cat"] = _cat(" ".join([out[-1]["name"], out[-1]["expect"]] + lines[:1]), cats(now))
            if len(out) >= limit:
                return out
    return out


def esc(s):
    return html.escape(s or "", quote=True)


WEEK = "月火水木金土日"
ROW_RE = re.compile(r"^(?P<name>[^：:]+)[：:](?P<rest>.*)$")
# 地名 → 都府県（左の色の線とタブに使う）
PLACE = [("東京", "東京"), ("高円寺", "東京"), ("池袋", "東京"), ("銀座", "東京"), ("渋谷", "東京"), ("新宿", "東京"),
         ("上野", "東京"), ("二子玉川", "東京"), ("芝公園", "東京"), ("お台場", "東京"), ("豊洲", "東京"), ("浅草", "東京"),
         ("横浜", "神奈川"), ("神奈川", "神奈川"), ("川崎", "神奈川"), ("鎌倉", "神奈川"), ("箱根", "神奈川"),
         ("埼玉", "埼玉"), ("千葉", "千葉"), ("舞浜", "千葉"),
         ("茨城", "茨城"), ("水戸", "茨城"), ("ひたち海浜", "茨城"), ("栃木", "栃木"), ("日光", "栃木"), ("あしかが", "栃木"),
         ("足利", "栃木"), ("宇都宮", "栃木"), ("那須", "栃木"), ("群馬", "群馬"), ("草津", "群馬"), ("高崎", "群馬"),
         ("大阪", "大阪"), ("梅田", "大阪"), ("なんば", "大阪"), ("難波", "大阪"), ("天王寺", "大阪"), ("福島", "大阪"),
         ("京都", "京都"), ("嵐山", "京都"), ("神戸", "兵庫"), ("兵庫", "兵庫"), ("有馬", "兵庫"), ("城崎", "兵庫"),
         ("姫路", "兵庫"), ("奈良", "奈良"), ("和歌山", "和歌山"), ("高野山", "和歌山"), ("滋賀", "滋賀"), ("琵琶湖", "滋賀")]
KANTO = {"東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"}
REGION_COLOR = {"関東": "#5D7FA3", "関西": "#C27A63"}  # しぼりこみは「関東・関西」の2つ（10/24 オーナー「東京、大阪、兵庫は変だ」）


def region(pref):
    return "関東" if pref in KANTO else "関西" if pref else ""


PREF_ORDER = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬", "大阪", "京都", "兵庫", "奈良", "和歌山", "滋賀"]
PREF_COLOR = {"東京": "#5D7FA3", "神奈川": "#4E8B86", "埼玉": "#9A8657", "千葉": "#C2964A", "茨城": "#7E8F6A",
              "栃木": "#A0705F", "群馬": "#6C7FA0", "大阪": "#C27A63",
              "京都": "#8E7BA6", "兵庫": "#4F6A8A", "奈良": "#6F8F5F", "和歌山": "#B5788A", "滋賀": "#5F9A9A"}
DATE_HEAD = re.compile(r"^((?:今日|明日|あす)?\s*\d{1,2}/\d{1,2}[^、,]{0,14}?(?:から|まで)?)[、,]\s*")
BLOCKS = {  # 章の英語名
    "odekake": "GO OUT", "shop": "NEW OPEN", "deal": "LIMITED", "pr": "AI PICK", "ended": "ARCHIVE",
}


def _text(e):
    return e["title"] + " " + " ".join(e["bullets"])


def _pref(e):
    t = _text(e)
    best = None
    for word, pref in PLACE:
        i = t.find(word)
        if i >= 0 and (best is None or i < best[0]):
            best = (i, pref)
    return best[1] if best else ""


def _cut(x, marks, n=13):
    """長い言葉を、助詞（marks）のすぐあとで2つに分ける。前後とも3文字以上残る所だけ。"""
    if len(x) <= n:
        return [x]
    for i in range(len(x) - 3, 2, -1):
        if x[i - 1] in marks:
            return _cut(x[:i], marks, n) + _cut(x[i:], marks, n)
    return _cut(x, "でのと", n) if marks == "はが" else [x]


def phr(text):
    """見出しを言葉の切れ目（、・空白、長い所は「は」「が」のあと）で区切り、
    言葉の途中で改行しないようにする（月のページと同じ作り）。"""
    parts = []
    for x in re.findall(r"[^、，・ 　]+[、，・]?[ 　]?", text or ""):
        parts += _cut(x, "はが")
    return "".join(f'<span class="nwp{" sp" if x[-1] in " 　" else ""}">{esc(x.strip())}</span>'
                   for x in parts if x.strip()) or esc(text)


def _wd(text, year):
    """「10/29」のような日付に曜日を足す（10/29（木））。すでに曜日があれば足さない。"""
    def add(m):
        try:
            d = datetime(year, int(m.group(1)), int(m.group(2)))
        except ValueError:
            return m.group(0)
        return f"{m.group(0)}（{WEEK[d.weekday()]}）"
    return re.sub(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?![\d/（(])", add, text)


def _split_title(title):
    """「10/24・25、高円寺フェスなど…」→（日付の部分, 残り）。"""
    m = DATE_HEAD.match(title)
    if m:
        return m.group(1).strip(), title[m.end():].strip()
    return "", title


def _free(e):
    """「無料」の印。行くこと自体が無料と書いてある物だけ（「未就学児は無料」「登録は無料」「無料送迎」では付けない）。"""
    if e.get("kind") == "deal":
        return ""
    t = _text(e)
    if "入場無料" in t:
        return "入場無料"
    if re.search(r"参加費は無料|観覧無料|見学無料|入園無料|入館無料|無料で(見|入|参加|楽し)", t) or "無料" in e["title"]:
        return "無料"
    return ""


def _rows(e):
    """「名前：6,293件・4.52」のような行を比べ表の行にする。読めない行があれば None。"""
    rows = []
    for b in e["bullets"]:
        m = ROW_RE.match(b)
        if not m:
            return None
        rest = m.group("rest")
        cnt = re.search(r"([\d,]+)件", rest)
        avg = re.search(r"(?<![\d,])([1-5]\.\d{1,2})(?!\d)", rest)
        if not cnt or not avg:
            return None
        note = re.split(r"[。、]", rest, maxsplit=1)
        note = note[1].strip() if len(note) > 1 else ""
        rows.append({"name": m.group("name").strip(), "count": int(cnt.group(1).replace(",", "")),
                     "avg": avg.group(1), "note": note})
    if len(rows) < 2:
        return None
    exp = e.get("expect") or ""
    for r in rows:
        if (exp and exp in r["name"]) or r["name"].split(" ")[-1] in e["title"]:
            r["pick"] = True
            break
    return rows


ARROW = ('<svg class="arw" viewBox="0 0 24 12" aria-hidden="true"><path d="M1 6H22M17.5 1.8 22 6l-4.5 4.2" fill="none" '
         'stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/></svg>')
OUT = ('<svg class="out" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 9 9 3M4.2 3H9v4.8" fill="none" '
       'stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/></svg>')


MEDIA = ("walkerplus.com", "iko-yo.net", "pretty-online.jp", "voyvoi.com", "storm.mg", "prtimes.jp", "jorudan.co.jp",
         "jalan.net", "tabelog.com", "timeout.jp", "fashion-press.net", "yahoo.co.jp", "note.com", "enjoytokyo.jp")


def link_label(url):
    """カードの下の言葉。施設・主催・役所のページは「公式ページ」、ニュースや情報サイトは「紹介記事」（10/24 オーナー「もっと正確に」）。"""
    host = (urllib.parse.urlparse(url or "").hostname or "").lower()
    return "紹介記事" if any(host == m or host.endswith("." + m) for m in MEDIA) else "公式ページ"


def spot(e):
    pref = _pref(e)
    color = PREF_COLOR.get(pref, "#A07E66")
    when, name = _split_title(e["title"].replace("AIが比べた", "", 1).strip("、 "))
    when = _wd(when, e["year"]) if when else _wd(e["day"], e["year"]) + "調べ"
    free = _free(e)
    tag = f'<span class="tg">・{esc(free)}</span>' if free else ""
    pl = f'<span class="pl">{esc(pref)}</span>' if pref else ""
    if not e.get("url"):  # リンクのないカードは載せない（押しても何も開かないため）
        return ""
    href = esc(e["url"])
    label = f"{link_label(e['url'])}{OUT}"
    return (f'<a class="card it" data-pref="{esc(region(pref))}" data-free="{1 if free else 0}" style="--pc:{color}" href="{href}" '
            f'target="_blank" rel="noopener"><div class="d">{pl}<span class="when">{esc(when)}</span>{tag}</div>'
            f'<div class="t">{phr(name)}</div>'
            f'<div class="mp">{label}</div>{ARROW}</a>')


def _img(e):
    u = e.get("image") or ""
    if not u.startswith("https://"):
        return ""
    return f'<img class="ph" src="{esc(u)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">'


def compare(e):
    """AIが比べたPR：選んだ1つと理由と「詳しく」だけを見せ、比べた表はたたんでおく。"""
    rows = _rows(e) or []
    title = e["title"].replace("AIが比べた", "", 1).strip("、 ")
    chosen = next((r for r in rows if r.get("pick")), None)
    if chosen:
        head = (f'<div class="cho">{_img(e)}<div class="tx"><span class="lb">選んだのは</span><b>{phr(chosen["name"])}</b>'
                f'<span class="sc">★ {esc(chosen["avg"])}<i>｜</i>レビュー {chosen["count"]:,}件</span></div></div>')
    else:
        head = ""
    if rows:
        top = max(r["count"] for r in rows) or 1
        trs = "".join(
            f'<div class="row{" on" if r.get("pick") else ""}"><div class="nm">{esc(r["name"])}</div>'
            f'<div class="nu"><span class="av">★ {esc(r["avg"])}</span><span class="ct">{r["count"]:,}件</span></div>'
            f'<div class="br"><i style="width:{max(3, round(r["count"] / top * 100))}%"></i></div></div>' for r in rows)
        table = f'<details class="fold"><summary>比べた{len(rows)}つを見る</summary><div class="tbl">{trs}</div></details>'
    else:
        table = ""
    reason = f'<p class="why">{esc(e["reason"])}</p>' if e.get("reason") else ""
    btn = f'<a class="buy" href="{esc(e["url"])}" target="_blank" rel="sponsored noopener">詳しく{ARROW}</a>'
    sample = '<p class="smp">見本：本番は楽天で販売中を確かめたPRリンクになります</p>' if e.get("sample") else ""
    return (f'<article class="card cmp"><div class="d"><span class="prm">PR</span><span class="when">{esc(e["day"])}　AIが比べた{"・Amazon" if e.get("amazon") else ""}</span></div>'
            f'<div class="t">{phr(title)}</div>{head}{reason}{table}<div class="ft2">{btn}</div>{sample}</article>')


def pick(e):
    meta = []
    if e.get("avg"):
        meta.append(f'<span class="av">★ {esc(str(e["avg"]))}</span>')
    if e.get("count"):
        meta.append(f'<span class="ct">レビュー {int(e["count"]):,}件</span>')
    if e.get("price"):
        meta.append(f'<span class="yen">税込 {int(e["price"]):,}円</span>')
    lis = f'<p class="why">{esc(e["lines"][0])}</p>' if e["lines"] else ""
    sample = '<p class="smp">見本：本番は楽天で販売中を確かめたPRリンクになります</p>' if e.get("sample") else ""
    return (f'<article class="card cmp pk2"><div class="d"><span class="prm">PR</span><span class="when">{esc(e["day"])}　AIが選んだ</span></div>'
            f'<div class="cho">{_img(e)}<div class="tx"><span class="lb">選んだのは</span><b>{phr(e["name"])}</b>'
            f'<div class="meta">{"".join(meta)}</div></div></div>{lis}'
            f'<div class="ft2">'
            f'<a class="buy" href="{esc(e["url"])}" target="_blank" rel="sponsored noopener">詳しく{ARROW}</a></div>{sample}</article>')


def sale(e):
    when, name = _split_title(e["title"].replace("AIが比べた", "", 1).strip("、 "))
    when = _wd(when, e["year"]) if when else _wd(e["day"], e["year"]) + "調べ"
    btn = f'<a class="buy" href="{esc(e["url"])}" target="_blank" rel="sponsored noopener">詳しく{ARROW}</a>'
    return (f'<article class="card cmp"><div class="d"><span class="prm">PR</span><span class="when">{esc(when)}</span></div>'
            f'<div class="t">{phr(name)}</div><div class="ft2">{btn}</div></article>')


def a8card(e):
    note = f'<p class="why">{esc(e["note"])}</p>' if e.get("note") else ""
    btn = f'<a class="buy" href="{esc(e["url"])}" target="_blank" rel="sponsored noopener">詳しく{ARROW}</a>'
    return (f'<article class="card cmp"><div class="d"><span class="prm">PR</span><span class="when">予約・申し込み</span></div>'
            f'<div class="t">{phr(e["name"])}</div>{note}<div class="ft2">{btn}</div></article>')


def _season(now):
    """表紙の季節：時期（seasons.json）の季節で、色・春夏秋冬の印・見出しを切り替える。"""
    pe = period(now)
    sea = pe.get("season", "autumn")
    i = SEASON_I.get(sea, 2)
    year = now.year - (1 if now.month <= 2 and sea == "winter" else 0)
    return i, sea, f"{sea.upper()} {year}", pe.get("name") or f'{"春夏秋冬"[i]}のおでかけ'


def _year_ring(cur):
    gs = []
    for i, (x, ch) in enumerate(zip((81, 107, 133, 159), "春夏秋冬")):
        cls = "yp" if i < cur else "yn" if i == cur else "yx"
        ring = f'<path class="ring" d="M{x} 3l11 11-11 11-11-11z"/>' if i == cur else ""
        gs.append(f'<g class="{cls}">{ring}<path class="dm" d="M{x} 8.5l5.5 5.5-5.5 5.5-5.5-5.5z"/>'
                  f'<text x="{x}" y="39">{ch}</text></g>')
    return ('<svg class="yr" viewBox="0 0 240 44" aria-hidden="true"><g class="ln"><path d="M46 14h18M176 14h18"/></g>'
            '<g class="dt"><circle cx="38" cy="14" r="1.3"/><circle cx="202" cy="14" r="1.3"/>'
            '<circle cx="29" cy="14" r="1" opacity=".7"/><circle cx="211" cy="14" r="1" opacity=".7"/>'
            '<circle cx="21" cy="14" r=".8" opacity=".45"/><circle cx="219" cy="14" r=".8" opacity=".45"/></g>'
            + "".join(gs) + "</svg>")


def render(items, ended, now, cfg):
    p = cfg.get("page", {})
    sns = [("Instagram", "@ai_usagichan1", "https://www.instagram.com/ai_usagichan1/"),
           ("Threads", "@ai_usagichan1", "https://www.threads.com/@ai_usagichan1"),
           ("X", "@ai_usagichan", "https://x.com/ai_usagichan")]
    follow = "".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(n)}<span>{esc(h)}</span></a>' for n, h, u in sns)
    if p.get("room_url"):
        follow += (f'<a class="co" href="{esc(p["room_url"])}" target="_blank" rel="noopener">楽天ROOM'
                   f'<span>AIが比べて選んだ物を、まとめて置いています</span></a>')
    spots = [e for e in items["odekake"] + items["shop"] if e.get("url")]  # おでかけはおでかけとお店だけ。お得は別の欄
    deals = [e for e in items["deal"] if e.get("url")]
    regs = [x for x in REGION_COLOR if any(region(_pref(e)) == x for e in spots)]
    tabs = '<button class="on" data-p="">すべて</button>' + "".join(
        f'<button data-p="{esc(x)}" style="--pc:{REGION_COLOR[x]}">{esc(x)}</button>' for x in regs)
    cs = cats(now)
    goods = {k: [] for k, *_ in cs}
    for e in items["pr"]:
        goods.get(e.get("cat"), goods["life"]).append(sale(e) if e.get("cat") == "sale" else compare(e))
    for e in items.get("pick", []):
        goods.get(e.get("cat"), goods["life"]).append(pick(e))
    goods["book"] += [a8card(e) for e in items.get("a8", [])]
    blocks, nav = [], []
    if spots:  # いちばん上はおでかけ。数を絞って、残りはたたむ
        cards = [spot(e) for e in spots]
        more = ""
        if len(cards) > SHOW_GO:
            more = (f'<details class="fold more"><summary>ほかのおでかけ{len(cards) - SHOW_GO}件を見る</summary>'
                    f'{"".join(cards[SHOW_GO:])}</details>')
        nav.append(f'<a class="g" href="#odekake"><span><i>GO OUT</i>おでかけ</span><b>{len(spots)}</b></a>')
        blocks.append(f'<section class="blk go" id="odekake"><div class="wk"><span class="en2">GO OUT</span>'
                      f'<span class="jp2">今週のおでかけ</span></div><p class="lead">公式ページで日時と料金を確かめた物だけ</p>'
                      f'<div class="seg" role="group" aria-label="しぼりこみ"><button class="on" data-f="0">すべて</button><button data-f="1">無料だけ</button></div>'
                      f'<nav class="flt" aria-label="地域">{tabs}</nav>'
                      f'{"".join(cards[:SHOW_GO])}{more}<p class="none">この地域は、これから増やしていきます</p></section>')
    if deals:  # 期間のあるお得（無印良品週間など）は、おでかけの下に別の欄で
        nav.append(f'<a href="#deal"><span><i>DEAL</i>今だけのお得</span><b>{len(deals)}</b></a>')
        blocks.append('<section class="blk" id="deal"><div class="wk"><span class="en2">DEAL</span>'
                      '<span class="jp2">今だけのお得</span></div><p class="lead">期間のあるお得。終わる日を先に書いています</p>'
                      + "".join(spot(e) for e in deals) + '</section>')
    for key, en, name, lead, _ in cs:
        if not goods[key]:
            continue
        nav.append(f'<a href="#{key}"><span><i>{en}</i>{esc(name)}</span><b>{len(goods[key])}</b></a>')
        blocks.append(f'<section class="blk" id="{key}"><div class="wk"><span class="en2">{en}</span>'
                      f'<span class="jp2">{esc(name)}</span></div><p class="lead">{esc(lead)}</p>{"".join(goods[key])}</section>')
    cur, sea, sea_en, sea_jp = _season(now)
    return TEMPLATE.format(
        nav="".join(nav), blocks="".join(blocks), follow=follow, ring=_year_ring(cur), sea_en=sea_en, sea_jp=sea_jp, sea=sea,
        n_pr=sum(len(v) for v in goods.values()),
        pr_note=("このページには楽天アフィリエイトとAmazonアソシエイトの広告（PR）があります。<br>"
                 "Amazonのアソシエイトとして、当サイトは適格販売により収入を得ています。"
                 if any(e.get("amazon") for e in items["pr"]) else
                 "このページにはアフィリエイト広告（PR）があります" if items.get("a8") else
                 "このページには楽天アフィリエイトの広告（PR）があります"),
        updated=f"{now.month}/{now.day}（{WEEK[now.weekday()]}）{now:%H:%M}")


TEMPLATE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>うさぎ│LIFE NOTES</title>
<meta name="description" content="関東・関西で、今日から・新しく・無料で行ける場所と、AIが数字で比べた物を毎日。">
<meta property="og:title" content="うさぎ│LIFE NOTES">
<meta property="og:description" content="おでかけ先と宿と、AIが比べて選んだ物を毎日更新。">
<meta property="og:image" content="https://usagi-life-notes.pages.dev/logo.png">
<meta property="og:url" content="https://usagi-life-notes.pages.dev/">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#FAF8F5">
<link rel="icon" href="logo.png"><link rel="apple-touch-icon" href="logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Jost:wght@300;400;500&display=swap">
<style>
/* 紙の手帳のような生成りの地に、白い紙を重ねる。色はロゴの茶と、地域ごとの淡い色だけ */
:root{{
  color-scheme:light;
  --bg:#FAF8F5; --paper:#FFFFFF; --ink:#2B2622; --sub:#6B6058; --mute:#8C7B6E; --line:#E6DED4; --line2:#D6CCC1;
  --brown:#A07E66; --brown2:#8C6A55; --free:#5E8A4A; --pr:#B5643F; --acc:#A07E66;
  --c1:rgba(242,214,194,.6); --c2:rgba(205,224,236,.65); --c3:rgba(214,228,205,.65); --c4:rgba(240,214,218,.65);
  --min:"Shippori Mincho","Hiragino Mincho ProN","Yu Mincho",serif;
  --go:"Zen Kaku Gothic New","Hiragino Sans","Noto Sans JP",sans-serif;
  --en:"Jost","Futura","Avenir Next",sans-serif;
}}
/* 季節の色（seasons.json の時期で body の class が変わる） */
.s-winter{{--acc:#71849B;--c1:rgba(208,222,238,.75);--c2:rgba(228,222,242,.7);--c3:rgba(222,232,242,.85);--c4:rgba(242,224,230,.6)}}
.s-spring{{--acc:#BF8792;--c1:rgba(246,214,222,.65);--c2:rgba(250,236,200,.65);--c3:rgba(214,232,206,.65);--c4:rgba(214,226,240,.6)}}
.s-summer{{--acc:#4F8C99;--c1:rgba(200,232,236,.7);--c2:rgba(210,226,246,.7);--c3:rgba(250,240,196,.6);--c4:rgba(214,238,222,.6)}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%;scroll-behavior:smooth}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:400 14px/1.7 var(--go)}}
a{{color:inherit;text-decoration:none}}
a:focus-visible,button:focus-visible{{outline:1px solid var(--brown);outline-offset:3px}}
.wrap{{max-width:460px;margin:0 auto;padding-block:0 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}

/* 表紙 */
.head{{position:relative;isolation:isolate;overflow:hidden;text-align:center;margin:0 calc(-1 * max(16px,env(safe-area-inset-left,0px)));padding:40px 16px 26px}}
.head .blob{{position:absolute;border-radius:50%;filter:blur(2px);z-index:-1}}
.b1{{width:170px;height:170px;left:-48px;top:24px;background:var(--c1)}}
.b2{{width:120px;height:120px;right:-22px;top:18px;background:var(--c2)}}
.b3{{width:104px;height:104px;right:34px;bottom:-30px;background:var(--c3)}}
.b4{{width:64px;height:64px;left:-12px;bottom:6px;background:var(--c4)}}
.s-winter .head:after{{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;opacity:.55;
  background-image:radial-gradient(circle,#B9C8DA 1.1px,transparent 1.6px),radial-gradient(circle,#CBD6E4 .9px,transparent 1.4px);
  background-size:46px 52px,31px 37px;background-position:8px 12px,22px 30px;-webkit-mask-image:linear-gradient(#000,transparent 75%);mask-image:linear-gradient(#000,transparent 75%)}}
.head img{{width:88px;height:88px;display:block;margin:0 auto;border-radius:50%;background:#fff}}
.en{{font:300 10px/1 var(--en);letter-spacing:.5em;color:var(--brown);margin:16px 0 0;padding-left:.5em}}
.sub{{font-size:12.5px;line-height:1.95;color:var(--sub);margin:14px 0 0}}
.sea{{display:flex;align-items:center;justify-content:center;gap:10px;margin:20px 0 0;font:400 11px/1 var(--en);letter-spacing:.32em;color:var(--brown)}}
.sea:before,.sea:after{{content:"";flex:0 0 34px;height:1px;background:var(--brown)}}
.sea b{{font:600 13px/1 var(--min);letter-spacing:.12em;color:var(--brown2)}}
.yr{{display:block;width:240px;height:44px;margin:18px auto 0}}
.yr .ln path{{fill:none;stroke:var(--brown);stroke-width:1;stroke-linecap:round}}
.yr .dt circle{{fill:var(--brown)}}
.yr text{{font:9.5px var(--min);letter-spacing:.1em;fill:var(--brown);text-anchor:middle}}
.yr .dm{{fill:none;stroke:var(--brown);stroke-width:1}}
.yr .yp .dm{{fill:var(--brown);fill-opacity:.4;stroke-opacity:.5}} .yr .yp text{{fill-opacity:.55}}
.yr .yn .dm{{fill:var(--brown)}} .yr .yn text{{font-weight:700}}
.yr .ring{{fill:none;stroke:var(--brown);stroke-width:.8}}

/* 切り替え */
.seg{{display:flex;justify-content:center;margin:22px 0 0}}
.seg button{{font:700 12.5px/1 var(--go);letter-spacing:.12em;color:var(--mute);background:#fff;border:1px solid #D9CFC4;padding:9px 18px;cursor:pointer;margin-left:-1px}}
.seg button.on{{background:var(--ink);border-color:var(--ink);color:#fff}}
.flt{{display:flex;flex-wrap:wrap;justify-content:center;gap:0 20px;border-top:1px solid #DDD3C8;border-bottom:1px solid #DDD3C8;padding:10px 0;margin:12px 0 14px}}
.flt button{{font:700 13px/1 var(--go);letter-spacing:.06em;color:var(--pc,var(--mute));background:none;border:0;border-bottom:1px solid transparent;padding:6px 0;cursor:pointer}}
.flt button.on{{color:var(--pc,var(--ink));border-bottom-color:var(--pc,var(--ink))}}
.cnt{{display:flex;justify-content:center;margin:0 0 26px}}
.cnt span{{font-size:12px;color:var(--sub);padding:0 12px;letter-spacing:.06em}}
.cnt span+span{{border-left:1px solid var(--line2)}}
.cnt b{{font:600 17px/1 var(--min);color:var(--ink);margin:0 3px}}
.pr-note{{font-size:11px;line-height:1.8;color:var(--mute);text-align:center;margin:0 0 20px}}
.cats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin:24px 0 10px}}
.cats a{{display:flex;align-items:center;justify-content:space-between;gap:8px;background:#fff;border:1px solid var(--line);border-left:3px solid var(--acc);padding:11px 14px 12px;font:700 13.5px/1.3 var(--go);letter-spacing:.06em;transition:background .2s}}
.cats a:hover{{background:color-mix(in srgb,var(--acc) 5%,#fff)}}
.cats a span{{display:flex;flex-direction:column;gap:5px}}
.cats a i{{font:400 9px/1 var(--en);font-style:normal;letter-spacing:.28em;color:var(--acc)}}
.cats a b{{font:400 18px/1 var(--en);color:var(--acc)}}
.cats a.g{{border-left-color:#5D7FA3}} .cats a.g i,.cats a.g b{{color:#5D7FA3}}
.go .seg{{margin:4px 0 0}}
.more{{margin:4px 0 12px}} .more summary{{display:block;width:max-content;margin:0 auto 12px}}

/* 章 */
.blk{{background:var(--paper);border:1px solid #ECE5DC;border-top:3px solid var(--acc);padding:22px 14px 12px;margin-bottom:18px;scroll-margin-top:12px}}
.blk.hid{{display:none}}
.wk{{display:flex;flex-direction:column;gap:6px;margin:0 0 6px}}
.en2{{font:400 10px/1 var(--en);letter-spacing:.36em;color:var(--acc)}}
.jp2{{font:600 18px/1.4 var(--min);letter-spacing:.08em}}
.lead{{font-size:11.5px;color:var(--mute);margin:0 0 14px}}
.none{{display:none;font-size:12px;color:var(--mute);text-align:center;margin:4px 0 12px}}
.blk.empty .none{{display:block}}

/* おでかけのカード */
.card{{display:block;position:relative;background:#fff;border:1px solid var(--line);margin-bottom:12px;padding:12px 42px 38px 14px;box-shadow:inset 3px 0 0 var(--pc,var(--brown));transition:background .2s}}
a.card:hover{{background:color-mix(in srgb,var(--pc,var(--brown)) 4%,#fff)}}
.card[hidden]{{display:none}}
.d{{display:flex;flex-wrap:wrap;align-items:center;gap:2px 0;font-size:12px;line-height:1.5;letter-spacing:.02em;color:#8A6E5C}}
.pl{{font-weight:700;letter-spacing:.12em;color:var(--pc);margin-right:8px}}
.pl:before{{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--pc);margin-right:5px;vertical-align:1px}}
.pl:after{{content:"";display:inline-block;width:1px;height:9px;background:var(--line2);margin-left:8px;vertical-align:-1px}}
.tg{{font-size:11px;letter-spacing:.12em;color:var(--free);margin-left:8px}}
.t{{font:700 15px/1.4 var(--go);letter-spacing:0;margin:3px 0 2px}}
.nwp{{display:inline-block}} .nwp.sp{{margin-right:.3em}}
.m{{list-style:none;margin:6px 0 0;padding:0;display:grid;gap:2px}}
.m li{{font-size:12px;line-height:1.7;color:var(--sub);padding-left:11px;position:relative}}
.m li:before{{content:"";position:absolute;left:0;top:.8em;width:4px;height:1px;background:var(--line2)}}
.mp{{position:absolute;left:14px;bottom:12px;display:inline-flex;align-items:center;gap:3px;font-size:11.5px;font-weight:500;letter-spacing:.14em;color:#5B514A;border-bottom:1px solid #CFC5BA;padding-bottom:1px}}
.out{{width:9px;height:9px}}
.arw{{position:absolute;right:14px;top:50%;width:22px;height:11px;transform:translateY(-50%);color:#A99C90;transition:transform .2s}}
a.card:hover .arw{{transform:translate(3px,-50%)}}

/* AIが比べた */
.cmp{{padding:14px 16px 16px;box-shadow:none}}
.prm{{font:500 9.5px/1 var(--en);letter-spacing:.14em;color:var(--pr);border:1px solid var(--pr);padding:3px 6px 2px;margin-right:8px}}
.cmp .t{{margin-top:8px}}
.tbl{{margin:10px 0 0;border-top:1px solid var(--line)}}
.row{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;padding:10px 0 9px;border-bottom:1px solid var(--line)}}
.nm{{font-size:13px;font-weight:500;min-width:0}}
.nt{{display:block;font-size:11px;font-weight:400;color:var(--mute)}}
.nu{{display:flex;gap:12px;align-items:baseline;white-space:nowrap}}
.av{{font:400 13px/1 var(--en);letter-spacing:.02em;color:var(--brown2)}}
.ct{{font:300 12px/1 var(--en);color:var(--mute);min-width:4.4em;text-align:right;font-variant-numeric:tabular-nums}}
.br{{grid-column:1/-1;height:2px;background:#F2EDE7}}
.br i{{display:block;height:100%;background:#D9CDC1}}
.row.on .nm{{font-weight:700}} .row.on .ct{{color:var(--ink);font-weight:400}}
.row.on .br i{{background:var(--brown)}}
.pk{{display:inline-block;font-size:9.5px;font-weight:700;letter-spacing:.12em;color:#fff;background:var(--brown);padding:1px 6px;margin-right:6px;vertical-align:1px}}
.cap{{font-size:10.5px;color:var(--mute);margin:6px 0 0;letter-spacing:.04em}}
.why{{margin:14px 0 0;padding:12px 0 0;border-top:1px solid var(--line)}}
.why span{{font:400 10px/1 var(--en);letter-spacing:.3em;color:var(--brown)}}
.why span:before{{content:"WHY  ·  ";}}
.why p{{margin:6px 0 0;font-size:13px;line-height:1.85}}
.ft2{{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 12px;margin-top:14px}}
.src{{flex:1 1 11em;font-size:10.5px;color:var(--mute);margin:0;letter-spacing:.02em}}
.cmp .mp{{position:static}}
.buy{{display:inline-flex;align-items:center;gap:12px;background:var(--ink);color:#fff;font:500 13px/1 var(--go);letter-spacing:.2em;padding:13px 18px 13px 22px}}
.buy .arw{{position:static;transform:none;color:#fff;width:20px}}
.buy:hover .arw{{transform:translateX(3px)}}
.cho{{margin:10px 0 0;padding:10px 12px;background:#FAF6F1;display:flex;align-items:center;gap:12px}}
.cho .tx{{display:grid;gap:2px;min-width:0}}
.cho .ph{{flex:0 0 76px;width:76px;height:76px;object-fit:contain;background:#fff;border:1px solid var(--line)}}
.cho .meta{{margin:2px 0 0}}
.cho .lb{{font:400 10px/1.4 var(--en);letter-spacing:.2em;color:var(--brown)}}
.cho b{{font-size:14.5px;line-height:1.5}}
.cho .sc{{font:400 12px/1.4 var(--en);color:var(--sub)}} .cho .sc i{{font-style:normal;color:var(--line2);margin:0 6px}}
.cmp .why,.pk2 .why{{margin:10px 0 0;padding:0;border:0;font-size:12.5px;line-height:1.8;color:var(--sub)}}
.fold{{margin:10px 0 0}}
.fold summary{{cursor:pointer;list-style:none;font-size:11.5px;letter-spacing:.12em;color:#5B514A;display:inline-block;border-bottom:1px solid #CFC5BA}}
.fold summary::-webkit-details-marker{{display:none}}
.fold summary:after{{content:" ＋";color:var(--brown)}} .fold[open] summary:after{{content:" −"}}
.ft2{{justify-content:flex-end}}
.meta{{display:flex;flex-wrap:wrap;gap:4px 14px;align-items:baseline;margin:4px 0 0}}
.meta .ct{{min-width:0;text-align:left}}
.yen{{font:400 12.5px/1 var(--en);color:var(--ink);letter-spacing:.02em}}
.pk2 .m{{margin-top:10px}}
.smp{{font-size:10px;color:var(--mute);text-align:right;margin:8px 0 0}}

.tip,.ft,.lead{{text-wrap:balance}}
.past{{list-style:none;margin:6px 0 4px;padding:0;font-size:12px;line-height:2;color:#5B514A}}
.tip{{border-top:1px solid var(--line);margin:10px 0 0;padding:12px 2px 2px;font-size:11.5px;line-height:1.8;color:var(--sub);text-align:center}}

/* FOLLOW */
.sns{{margin-top:36px;text-align:center}}
.sns h2{{display:flex;align-items:center;justify-content:center;gap:14px;font:400 10.5px/1 var(--en);letter-spacing:.42em;color:var(--mute);margin:0 0 16px}}
.sns h2:before,.sns h2:after{{content:"";width:40px;height:1px;background:var(--line2)}}
.sns a{{display:block;border:1px solid var(--ink);padding:14px;margin:0 0 10px;font:500 13px/1.5 var(--go);letter-spacing:.1em}}
.sns a span{{font:400 12px var(--en);color:var(--mute);margin-left:8px;letter-spacing:.06em}}
.sns a.co{{background:#5B5450;border-color:#5B5450;color:#fff}}
.sns a.co span{{display:block;margin:4px 0 0;color:#E9E1D8;font-family:var(--go)}}
.ft{{text-align:center;font-size:10.5px;letter-spacing:.06em;color:var(--mute);margin-top:28px;line-height:1.9}}
#totop{{position:fixed;right:max(16px,env(safe-area-inset-right,0px));bottom:calc(20px + env(safe-area-inset-bottom,0px));width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.94);border:1px solid #CFC4B8;box-shadow:0 2px 8px rgba(60,45,35,.12);display:flex;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity .3s;cursor:pointer;padding:0}}
#totop.on{{opacity:1;pointer-events:auto}}
.fade{{opacity:1;transform:none;transition:opacity .7s ease,transform .7s ease}}
.js .fade:not(.in){{opacity:0;transform:translateY(10px)}}
@media (prefers-reduced-motion:reduce){{.js .fade:not(.in){{opacity:1;transform:none}}.card,.arw,#totop{{transition:none}}}}
</style></head>
<body class="s-{sea}"><div class="wrap">
<header class="head">
<span class="blob b1"></span><span class="blob b2"></span><span class="blob b3"></span><span class="blob b4"></span>
<img src="logo.png" alt="うさぎ│LIFE NOTES" width="88" height="88">
<h1 class="en">USAGI LIFE NOTES</h1>
<p class="sub">おでかけ先と、泊まる宿と、あると助かる物。<br>AIが毎日しらべて、数字で比べて選んでいます</p>
<div class="sea"><span>{sea_en}</span><b>{sea_jp}</b></div>
{ring}
</header>
<nav class="cats" aria-label="項目">{nav}</nav>
<p class="pr-note">{pr_note}</p>
{blocks}
<p class="tip">出かける前・買う前に、公式ページと楽天のページで<br>最新の情報を確かめてください。</p>
<div class="sns"><h2>FOLLOW</h2>{follow}</div>
<p class="ft">うさぎ│LIFE NOTES ｜ 毎日更新（最終 {updated}）<br>7日より前の投稿は、外しています</p>
</div>
<button id="totop" aria-label="上にもどる"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="#4A403A" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 13V3M3.5 7.5 8 3l4.5 4.5"/></svg></button>
<script>
(function(){{
var d=document.documentElement;d.classList.add("js");
var pref="",free=false;
function apply(){{
  document.querySelectorAll(".blk").forEach(function(b){{
    var cs=b.querySelectorAll(".card.it");if(!cs.length)return;var k=0;
    cs.forEach(function(c){{var ok=(!pref||!c.dataset.pref||c.dataset.pref===pref)&&(!free||c.dataset.free==="1");c.hidden=!ok;if(ok)k++;}});
    b.classList.toggle("empty",!k);
  }});
}}
document.querySelectorAll(".flt button").forEach(function(x){{x.addEventListener("click",function(){{
  document.querySelectorAll(".flt button").forEach(function(y){{y.classList.toggle("on",y===x);}});pref=x.dataset.p;apply();}});}});
document.querySelectorAll(".seg button").forEach(function(x){{x.addEventListener("click",function(){{
  document.querySelectorAll(".seg button").forEach(function(y){{y.classList.toggle("on",y===x);}});free=x.dataset.f==="1";apply();}});}});
var F="";try{{F=new URLSearchParams(location.search).get("f")||"";if(F)sessionStorage.setItem("f",F);else F=sessionStorage.getItem("f")||"";}}catch(e){{}}
document.addEventListener("click",function(ev){{
  var a=ev.target.closest&&ev.target.closest("a.buy");if(!a||!navigator.sendBeacon)return;
  var c=a.closest(".card")||a,t=c.querySelector(".t,.cho b"),sec=a.closest("section[id]");
  var k=(t?t.textContent:a.textContent).replace(/\\s+/g,"").slice(0,30);
  var sk="buy"+(sec?"-"+sec.id:"");
  try{{navigator.sendBeacon("/c?f="+encodeURIComponent(F||"direct")+"&s="+encodeURIComponent(sk.slice(0,16))+"&k="+encodeURIComponent(k));}}catch(e){{}}
}});
var t=document.getElementById("totop");
addEventListener("scroll",function(){{t.classList.toggle("on",scrollY>600);}},{{passive:true}});
t.addEventListener("click",function(){{scrollTo({{top:0,behavior:"smooth"}});}});
if("IntersectionObserver" in window){{var io=new IntersectionObserver(function(es){{es.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add("in");io.unobserve(e.target);}}}});}},{{rootMargin:"0px 0px -8% 0px"}});
  document.querySelectorAll(".blk").forEach(function(b,i){{b.classList.add("fade");if(i<1)b.classList.add("in");io.observe(b);}});}}
}})();
</script>
</body></html>
"""


def main():
    now = now_jst()
    if "--now" in sys.argv:
        now = datetime.fromisoformat(sys.argv[sys.argv.index("--now") + 1]).replace(tzinfo=JST)
    cfg = load_json(path("config.json"), {}) or {}
    items, ended = collect(now)
    out = path("site", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render(items, ended, now, cfg))
    print(json.dumps({k: len(v) for k, v in items.items()} | {"ended": len(ended)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
