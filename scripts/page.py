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
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import JST, URL_RE, load_json, now_jst, path  # noqa: E402

DAYS = 7
ODEKAKE = {"おでかけ", "イルミネーション", "温泉", "紅葉", "無料", "イベント", "週末旅", "旅行"}
SHOP = {"グルメ", "カフェ", "新店"}
DEAL = {"お得情報", "お得"}
SECTIONS = [
    ("odekake", "あしたから行ける", "今週の無料・新しいおでかけ。公式ページで確かめた物だけです。"),
    ("shop", "新しいお店", "開いたばかりのお店。"),
    ("deal", "今だけのお得", "期間のあるお得。終わる日を先に書いています。"),
    ("pr", "AIが比べた", "3つ以上を数字で比べて、1つを選んだ理由つきで載せています。"),
]


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
    if link.get("type") not in ("ichiba", "travel"):
        return {"ok": False, "why": "楽天以外はページのURL登録が済むまで載せない"}
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
    for f in sorted(glob.glob(path("schedule", "*.json")), reverse=True):
        day = os.path.basename(f)[:-5]
        if not re.match(r"\d{4}-\d{2}-\d{2}$", day):
            continue
        d = datetime.fromisoformat(day).date()
        if d < since:
            continue
        data = load_json(f, {}) or {}
        for p in sorted(data.get("posts", []), key=lambda p: p.get("slot", ""), reverse=True):
            due = datetime.fromisoformat(f"{day}T{p['slot']}").replace(tzinfo=JST)
            if due > now:
                continue
            text = p["threads"][0]
            if "付け忘れ" in text:
                continue
            title = _title(text)
            if title in seen:
                continue
            seen.add(title)
            entry = {"day": f"{d.month}/{d.day}", "title": title, "bullets": _bullets(text),
                     "reason": _line_with(text, "選んだ理由").replace("選んだ理由：", ""),
                     "source": _line_with(text, "より（"), "url": _official(p)}
            until = p.get("until")
            if until and datetime.fromisoformat(until).replace(tzinfo=JST) < now:
                ended.append(entry)
                continue
            link = p.get("link")
            if link:
                r = _resolve(link, list(p["x"]) + list(p["threads"]))
                if not r.get("ok"):
                    continue
                entry["expect"] = link.get("expect", "")
                entry["url"] = r["link"]
                entry["sample"] = r.get("sample", False)
                items["pr"].append(entry)
                continue
            topic = p.get("topic", "")
            key = "odekake" if topic in ODEKAKE else "shop" if topic in SHOP else "deal" if topic in DEAL else "pr"
            if key == "pr":
                entry["noad"] = True
            items[key].append(entry)
    return items, ended


def esc(s):
    return html.escape(s or "", quote=True)


AREAS = ["東京", "横浜", "神奈川", "埼玉", "千葉", "大阪", "京都", "神戸", "兵庫", "奈良", "和歌山", "滋賀",
         "有馬", "城崎", "高円寺", "池袋", "銀座", "渋谷", "新宿", "上野", "梅田", "なんば", "二子玉川", "芝公園"]
WEEK = "月火水木金土日"
ROW_RE = re.compile(r"^(?P<name>[^：:]+)[：:](?P<rest>.*)$")


def _area(e):
    text = e["title"] + " ".join(e["bullets"])
    for a in AREAS:
        if a in text:
            return a
    return ""


def _flags(e):
    text = e["title"] + " ".join(e["bullets"])
    out = []
    if "無料" in text:
        out.append(("free", "入場無料" if "入場無料" in text else "無料あり"))
    if re.search(r"開店|オープン|新店|初出店|1号店|2号店", text):
        out.append(("new", "NEW OPEN"))
    m = re.search(r"(\d{1,2}/\d{1,2})まで", text)
    if m:
        out.append(("until", f"{m.group(1)}まで"))
    return out


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
    pick = None
    for r in rows:
        if (exp and exp in r["name"]) or r["name"].split(" ")[-1] in e["title"]:
            pick = r
            break
    if pick:
        pick["pick"] = True
    return rows


def _flag_html(e):
    return "".join(f'<span class="flag {k}">{esc(v)}</span>' for k, v in _flags(e))


def spot(e, i):
    lis = "".join(f"<li>{esc(b)}</li>" for b in e["bullets"])
    area = _area(e)
    area_html = f'<span class="area">{esc(area)}</span>' if area else ""
    btn = (f'<a class="go" href="{esc(e["url"])}" target="_blank" rel="noopener">公式ページ<span aria-hidden="true">↗</span></a>'
           if e.get("url") else "")
    src = f'<p class="src">{esc(e["source"])}</p>' if e.get("source") else ""
    return (f'<article class="spot"><div class="stub"><span class="no">{i:02d}</span>'
            f'<span class="posted">{esc(e["day"])}</span></div>'
            f'<div class="body"><div class="tags">{area_html}{_flag_html(e)}</div>'
            f'<h3>{esc(e["title"])}</h3><ul>{lis}</ul>'
            f'<div class="foot">{src}{btn}</div></div></article>')


def compare(e):
    rows = _rows(e)
    is_pr = not e.get("noad")
    if rows:
        top = max(r["count"] for r in rows) or 1
        trs = []
        for r in rows:
            w = max(4, round(r["count"] / top * 100))
            pick = '<span class="pick">選んだ</span>' if r.get("pick") else ""
            note = f'<span class="note">{esc(r["note"])}</span>' if r["note"] else ""
            trs.append(f'<div class="row{" is-pick" if r.get("pick") else ""}"><div class="nm">{pick}{esc(r["name"])}{note}</div>'
                       f'<div class="num"><span class="avg">★{esc(r["avg"])}</span><span class="cnt">{r["count"]:,}件</span></div>'
                       f'<div class="bar"><i style="width:{w}%"></i></div></div>')
        table = f'<div class="table" role="table" aria-label="比べた結果">{"".join(trs)}</div>'
        cap = '<p class="cap">棒の長さはレビューの件数です</p>'
    else:
        table = "<ul>" + "".join(f"<li>{esc(b)}</li>" for b in e["bullets"]) + "</ul>"
        cap = ""
    reason = (f'<div class="reason"><span class="lbl">選んだ理由</span><p>{esc(e["reason"])}</p></div>'
              if e.get("reason") else "")
    if e.get("url"):
        if is_pr:
            btn = f'<a class="buy" href="{esc(e["url"])}" target="_blank" rel="sponsored noopener">楽天で見る<span aria-hidden="true">→</span></a>'
        else:
            btn = f'<a class="go" href="{esc(e["url"])}" target="_blank" rel="noopener">公式ページ<span aria-hidden="true">↗</span></a>'
    else:
        btn = ""
    sample = '<p class="sample">見本：本番は楽天で販売中を確かめたPRリンクになります</p>' if e.get("sample") else ""
    pr = '<span class="prmark">PR</span>' if is_pr else ""
    src = f'<p class="src">{esc(e["source"])}</p>' if e.get("source") else ""
    title = e["title"].replace("AIが比べた", "", 1).strip("、 ")
    return (f'<article class="cmp"><div class="cmp-head"><span class="eyebrow">AIが比べた</span>{pr}'
            f'<span class="posted">{esc(e["day"])}</span></div><h3>{esc(title)}</h3>{table}{cap}{reason}'
            f'<div class="foot">{src}{btn}</div>{sample}</article>')


def render(items, ended, now, cfg):
    p = cfg.get("page", {})
    links = [("楽天ROOM", "ROOM", p.get("room_url")), ("Threads", "@ai_usagichan1", "https://www.threads.com/@ai_usagichan1"),
             ("X", "@ai_usagichan", "https://x.com/ai_usagichan"),
             ("Instagram", "@ai_usagichan1", "https://www.instagram.com/ai_usagichan1/")]
    follow = "".join(f'<a{' class="room"' if n == "楽天ROOM" else ""} href="{esc(u)}" target="_blank" rel="noopener"><span class="sn">{esc(n)}</span>'
                     f'<span class="sh">{esc(h)}</span><span aria-hidden="true" class="ar">↗</span></a>'
                     for n, h, u in links if u)
    en = {"odekake": "GO OUT", "shop": "NEW SHOPS", "deal": "LIMITED", "pr": "COMPARED"}
    secs = []
    for key, name, lead in SECTIONS:
        if not items[key]:
            continue
        if key == "pr":
            cards = "".join(compare(e) for e in items[key])
        else:
            cards = "".join(spot(e, i + 1) for i, e in enumerate(items[key]))
        secs.append(f'<section class="sec" id="{key}"><header class="sec-head"><span class="en">{en[key]}</span>'
                    f'<h2>{esc(name)}</h2><span class="count">{len(items[key])}件</span></header>'
                    f'<p class="lead">{esc(lead)}</p><div class="list">{cards}</div></section>')
    if ended:
        li = "".join(f"<li><span>{esc(e['day'])}</span>{esc(e['title'])}</li>" for e in ended)
        secs.append(f'<section class="sec" id="ended"><header class="sec-head"><span class="en">ENDED</span>'
                    f'<h2>終わったおでかけ</h2></header><ul class="ended">{li}</ul></section>')
    nav = "".join(f'<a href="#{k}">{esc(n)}<span>{len(items[k])}</span></a>' for k, n, _ in SECTIONS if items[k])
    free = sum(1 for k in ("odekake", "shop", "deal") for e in items[k] if any(f[0] == "free" for f in _flags(e)))
    stats = (f'<div class="stat"><b>{len(items["odekake"])}</b><span>行ける場所</span></div>'
             f'<div class="stat"><b>{free}</b><span>無料あり</span></div>'
             f'<div class="stat"><b>{len(items["pr"])}</b><span>比べた物</span></div>')
    return TEMPLATE.format(nav=nav, sections="".join(secs), follow=follow, stats=stats,
                           md=f"{now.month}.{now.day:02d}", wd=WEEK[now.weekday()],
                           updated=f"{now.month}/{now.day}（{WEEK[now.weekday()]}）{now:%H:%M}")


TEMPLATE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>うさぎ│LIFE NOTES</title>
<meta name="description" content="首都圏・関西で、今日から・新しく・無料で行ける場所と、AIが数字で比べた物を毎日。">
<meta property="og:title" content="うさぎ│LIFE NOTES">
<meta property="og:description" content="今週行ける場所と、AIが比べた物を毎日更新。">
<meta property="og:image" content="logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" href="logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@500;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Cormorant+Garamond:ital,wght@0,500;1,500&display=swap">
<style>
/* 夕方から夜に変わる空の色（ラベンダー）と、ロゴのピーチ。紙の手帳のように、余白と細い線で区切る */
:root{{
  --paper:#f7f5f9; --sheet:#fffefe; --ink:#2d2733; --sub:#71687a; --hair:#e4dee9;
  --lav:#8f80c4; --lav-soft:#ece8f6; --peach:#e3946b; --peach-soft:#fbeadf; --pr:#c4553f;
  --f-disp:"Shippori Mincho B1","Hiragino Mincho ProN","Yu Mincho",serif;
  --f-body:"Zen Kaku Gothic New","Hiragino Sans","Noto Sans JP",system-ui,sans-serif;
  --f-latin:"Cormorant Garamond","Times New Roman",serif;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{
  --paper:#15131b; --sheet:#1e1b26; --ink:#efeaf4; --sub:#a59db0; --hair:#2f2a3a;
  --lav:#b7aaf0; --lav-soft:#2a2540; --peach:#f0aa82; --peach-soft:#3a2a24; --pr:#f08a74; color-scheme:dark}}}}
:root[data-theme="dark"]{{
  --paper:#15131b; --sheet:#1e1b26; --ink:#efeaf4; --sub:#a59db0; --hair:#2f2a3a;
  --lav:#b7aaf0; --lav-soft:#2a2540; --peach:#f0aa82; --peach-soft:#3a2a24; --pr:#f08a74; color-scheme:dark}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
body{{margin:0;background:var(--paper);color:var(--ink);font:400 15px/1.8 var(--f-body);letter-spacing:.02em;font-feature-settings:"palt" 1}}
a{{color:inherit}}
a:focus-visible{{outline:2px solid var(--lav);outline-offset:3px;border-radius:6px}}
.wrap{{max-width:680px;margin:0 auto;padding-block:28px 56px;padding-left:max(18px,env(safe-area-inset-left,0px));padding-right:max(18px,env(safe-area-inset-right,0px))}}

/* 表紙 */
.cover{{display:grid;grid-template-columns:auto 1fr;gap:18px;align-items:center;padding-bottom:22px;border-bottom:1px solid var(--hair)}}
.cover img{{width:88px;height:88px;border-radius:50%;background:var(--sheet);border:1px solid var(--hair);display:block}}
.brand{{font:500 13px/1 var(--f-latin);letter-spacing:.32em;color:var(--sub);margin:0 0 6px}}
.brand i{{color:var(--lav);font-style:italic}}
.issue{{display:flex;align-items:baseline;gap:10px;margin:0}}
.issue b{{font:500 44px/1 var(--f-latin);letter-spacing:.02em;font-variant-numeric:lining-nums}}
.issue span{{font:500 13px/1 var(--f-body);color:var(--sub);border:1px solid var(--hair);border-radius:999px;padding:4px 9px}}
.headline{{font:700 clamp(26px,7vw,34px)/1.45 var(--f-disp);letter-spacing:.06em;margin:24px 0 10px;text-wrap:balance}}
.headline span{{display:inline-block}}
.headline em{{font-style:normal;background:linear-gradient(transparent 62%,var(--peach-soft) 62%)}}
.intro{{color:var(--sub);margin:0;max-width:34em}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);margin:22px 0 0;border-top:1px solid var(--hair);border-bottom:1px solid var(--hair)}}
.stat{{padding:12px 0 10px;text-align:center}}
.stat+.stat{{border-left:1px solid var(--hair)}}
.stat b{{display:block;font:500 30px/1.1 var(--f-latin);font-variant-numeric:tabular-nums lining-nums}}
.stat span{{font-size:11px;color:var(--sub);letter-spacing:.12em}}
.notice{{font-size:11.5px;line-height:1.7;color:var(--sub);margin:14px 0 0}}
.notice b{{color:var(--pr);font-weight:700;margin-right:6px}}

/* 目次（ストーリーのリンクから #odekake などで飛べる） */
.toc{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;margin:22px calc(-1 * max(18px,env(safe-area-inset-left,0px))) 0;background:color-mix(in srgb,var(--paper) 88%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--hair)}}
.toc-in{{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;padding:10px max(18px,env(safe-area-inset-left,0px))}}
.toc-in::-webkit-scrollbar{{display:none}}
.toc a{{flex:none;text-decoration:none;font-size:13px;font-weight:500;padding:6px 12px;border-radius:999px;border:1px solid var(--hair);background:var(--sheet);display:flex;gap:6px;align-items:center}}
.toc a span{{font:500 13px/1 var(--f-latin);color:var(--lav)}}

/* 章 */
.sec{{margin-top:44px;scroll-margin-top:64px}}
.sec-head{{display:grid;grid-template-columns:1fr auto;align-items:end;gap:2px 12px}}
.sec-head .en{{grid-column:1/-1;font:italic 500 15px/1 var(--f-latin);letter-spacing:.24em;color:var(--lav)}}
.sec-head h2{{font:700 24px/1.4 var(--f-disp);letter-spacing:.08em;margin:0;text-wrap:balance}}
.sec-head .count{{font-size:12px;color:var(--sub);padding-bottom:6px}}
.lead{{font-size:13px;color:var(--sub);margin:6px 0 16px;padding-bottom:14px;border-bottom:1px solid var(--hair)}}
.list{{display:grid;gap:14px}}

/* 行ける場所：切符の半券の形 */
.spot{{display:grid;grid-template-columns:58px minmax(0,1fr);background:var(--sheet);border:1px solid var(--hair);border-radius:14px;overflow:hidden}}
.stub{{display:flex;flex-direction:column;align-items:center;justify-content:flex-start;gap:4px;padding:16px 0;border-right:1px dashed var(--hair);background:var(--lav-soft)}}
.stub .no{{font:500 24px/1 var(--f-latin);color:var(--lav);font-variant-numeric:lining-nums}}
.posted{{font-size:10.5px;color:var(--sub);letter-spacing:.06em}}
.body{{padding:14px 16px 14px;min-width:0}}
.tags{{display:flex;flex-wrap:wrap;gap:6px;min-height:0}}
.tags:empty{{display:none}}
.area,.flag{{font-size:11px;font-weight:700;letter-spacing:.06em;padding:2px 8px;border-radius:4px}}
.area{{background:var(--paper);color:var(--ink);border:1px solid var(--hair)}}
.flag.free{{background:var(--peach-soft);color:var(--pr)}}
.flag.new{{background:var(--lav-soft);color:var(--lav);font-family:var(--f-latin);letter-spacing:.14em}}
.flag.until{{border:1px solid var(--hair);color:var(--sub)}}
.spot h3,.cmp h3{{font:700 17px/1.55 var(--f-disp);letter-spacing:.04em;margin:8px 0 6px;text-wrap:balance}}
.spot ul,.cmp ul{{margin:0;padding:0;list-style:none;display:grid;gap:3px}}
.spot li,.cmp ul li{{font-size:13.5px;line-height:1.7;padding-left:14px;position:relative}}
.spot li::before,.cmp ul li::before{{content:"";position:absolute;left:2px;top:.75em;width:5px;height:5px;border-radius:50%;background:var(--peach)}}
.foot{{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 12px;margin-top:12px;padding-top:10px;border-top:1px solid var(--hair)}}
.src{{font-size:11px;color:var(--sub);margin:0;flex:1 1 12em}}
.go{{font-size:13px;font-weight:700;text-decoration:none;color:var(--lav);display:inline-flex;gap:4px;align-items:center;white-space:nowrap}}
.go:hover{{text-decoration:underline;text-underline-offset:3px}}

/* AIが比べた：表のように並べる */
.cmp{{background:var(--sheet);border:1px solid var(--hair);border-radius:14px;padding:16px 16px 14px}}
.cmp-head{{display:flex;align-items:center;gap:8px}}
.eyebrow{{font-size:11px;font-weight:700;letter-spacing:.2em;color:var(--lav)}}
.prmark{{font-size:10px;font-weight:700;letter-spacing:.1em;color:var(--pr);border:1px solid var(--pr);border-radius:3px;padding:0 5px;line-height:1.6}}
.cmp-head .posted{{margin-left:auto}}
.table{{display:grid;gap:0;margin-top:6px;border-top:1px solid var(--hair)}}
.row{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 12px;padding:9px 0 10px;border-bottom:1px solid var(--hair)}}
.nm{{font-size:13.5px;font-weight:500;min-width:0}}
.nm .note{{display:block;font-size:11.5px;font-weight:400;color:var(--sub)}}
.num{{display:flex;gap:10px;align-items:baseline;font-variant-numeric:tabular-nums;white-space:nowrap}}
.avg{{font:500 15px/1 var(--f-latin)}}
.cnt{{font-size:12px;color:var(--sub);min-width:5.2em;text-align:right}}
.bar{{grid-column:1/-1;height:4px;border-radius:2px;background:var(--paper)}}
.bar i{{display:block;height:100%;border-radius:2px;background:var(--hair)}}
.row.is-pick .bar i{{background:var(--peach)}}
.row.is-pick .nm{{font-weight:700}}
.row.is-pick .cnt{{color:var(--ink);font-weight:700}}
.pick{{display:inline-block;font-size:10px;font-weight:700;color:#fff;background:var(--peach);border-radius:3px;padding:0 6px;margin-right:6px;vertical-align:2px;letter-spacing:.08em}}
.cap{{font-size:11px;color:var(--sub);margin:6px 0 0}}
.reason{{margin-top:12px;padding:12px 14px;border-radius:10px;background:var(--lav-soft)}}
.reason .lbl{{font-size:11px;font-weight:700;letter-spacing:.16em;color:var(--lav)}}
.reason p{{margin:2px 0 0;font-size:13.5px}}
.buy{{display:inline-flex;align-items:center;gap:8px;text-decoration:none;font-size:14px;font-weight:700;color:#fff;background:var(--pr);border-radius:999px;padding:9px 18px;white-space:nowrap;transition:transform .15s}}
.buy:hover{{transform:translateY(-1px)}}
@media (prefers-reduced-motion:reduce){{.buy{{transition:none}}.buy:hover{{transform:none}}}}
.sample{{font-size:10.5px;color:var(--sub);margin:8px 0 0;text-align:right}}

.ended{{list-style:none;margin:0;padding:0;display:grid;gap:6px}}
.ended li{{font-size:13px;color:var(--sub);text-decoration:line-through;text-decoration-color:var(--hair)}}
.ended span{{display:inline-block;min-width:3.4em;text-decoration:none}}

/* 終わり */
.end{{margin-top:56px;padding-top:28px;border-top:1px solid var(--hair);text-align:center}}
.end .en{{font:italic 500 15px/1 var(--f-latin);letter-spacing:.24em;color:var(--lav)}}
.end h2{{font:700 20px/1.5 var(--f-disp);letter-spacing:.08em;margin:6px 0 16px}}
.follow{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;text-align:left}}
.follow a{{display:grid;grid-template-columns:1fr auto;gap:0 8px;text-decoration:none;background:var(--sheet);border:1px solid var(--hair);border-radius:12px;padding:12px 14px}}
.follow a.room{{grid-column:1/-1;background:var(--peach-soft);border-color:transparent}}
.sn{{font-weight:700;font-size:14px}}
.sh{{grid-row:2;font-size:11.5px;color:var(--sub)}}
.ar{{grid-row:1/3;grid-column:2;align-self:center;color:var(--lav)}}
.colophon{{font-size:11px;color:var(--sub);margin:22px 0 0;line-height:1.9}}
.colophon .moon{{display:inline-block;width:10px;height:10px;border-radius:50%;box-shadow:-3px 1px 0 0 var(--peach);transform:translate(3px,1px);margin-right:4px}}
</style></head>
<body><div class="wrap">
<header class="cover">
<img src="logo.png" alt="うさぎ│LIFE NOTES" width="88" height="88">
<div><p class="brand">USAGI <i>Life</i> NOTES</p><p class="issue"><b>{md}</b><span>{wd}曜日号</span></p></div>
</header>
<h1 class="headline"><span>今週の<em>行き先</em>が、</span><span>いちばん早く分かる。</span></h1>
<p class="intro">首都圏と関西で「今日から・新しく・無料で」行ける場所を、AIが毎日調べて書き足しています。買う物は、3つ以上を数字で比べてから1つだけ。</p>
<div class="stats">{stats}</div>
<p class="notice"><b>PR</b>このページは楽天アフィリエイトの広告を含みます。日時や値段は変わることがあるので、出かける前・買う前に公式ページで確かめてください。</p>
<nav class="toc" aria-label="目次"><div class="toc-in">{nav}</div></nav>
{sections}
<footer class="end">
<span class="en">FOLLOW</span>
<h2>毎日の続きは、こちらで</h2>
<div class="follow">{follow}</div>
<p class="colophon"><span class="moon" aria-hidden="true"></span>最終更新 {updated}<br>7日より前の投稿は外しています</p>
</footer>
</div></body></html>
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
