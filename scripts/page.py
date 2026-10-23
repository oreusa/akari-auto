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


def card(e):
    tag = '<span class="tag">PR</span>' if not e.get("noad") and e.get("reason") else ""
    lis = "".join(f"<li>{esc(b)}</li>" for b in e["bullets"])
    reason = f'<p class="reason"><b>選んだ理由</b>{esc(e["reason"])}</p>' if e.get("reason") else ""
    if e.get("url"):
        is_pr = not e.get("noad") and e.get("reason")
        label = "楽天で見る" if is_pr else "公式ページ"
        rel = "sponsored noopener" if is_pr else "noopener"
        btn = f'<a class="btn{" pr" if is_pr else ""}" href="{esc(e["url"])}" target="_blank" rel="{rel}">{label} →</a>'
    else:
        btn = ""
    sample = '<p class="sample">見本：本番は楽天のPRリンクになります</p>' if e.get("sample") else ""
    src = f'<p class="src">{esc(e["source"])}</p>' if e.get("source") else ""
    return (f'<article class="card"><div class="meta"><span class="day">{esc(e["day"])}</span>{tag}</div>'
            f'<h3>{esc(e["title"])}</h3><ul>{lis}</ul>{reason}{src}{btn}{sample}</article>')


def render(items, ended, now, cfg):
    p = cfg.get("page", {})
    links = [("楽天ROOM", p.get("room_url")), ("Threads", "https://www.threads.com/@ai_usagichan1"),
             ("X", "https://x.com/ai_usagichan"), ("インスタ", "https://www.instagram.com/ai_usagichan1/")]
    follow = "".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(n)}</a>' for n, u in links if u)
    secs = []
    for key, name, lead in SECTIONS:
        if not items[key]:
            continue
        cards = "".join(card(e) for e in items[key])
        secs.append(f'<section id="{key}"><h2>{esc(name)}</h2><p class="lead">{esc(lead)}</p>{cards}</section>')
    if ended:
        li = "".join(f"<li>{esc(e['day'])} {esc(e['title'])}</li>" for e in ended)
        secs.append(f'<section id="ended"><h2>終わったおでかけ</h2><ul class="ended">{li}</ul></section>')
    nav = "".join(f'<a href="#{k}">{esc(n)}</a>' for k, n, _ in SECTIONS if items[k])
    updated = f"{now.month}/{now.day} {now:%H:%M}"
    return TEMPLATE.format(nav=nav, sections="".join(secs), follow=follow, updated=updated)


TEMPLATE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>うさぎ│LIFE NOTES</title>
<meta name="description" content="首都圏・関西で今日から・新しく・無料で行ける場所と、AIが数字で比べた物。">
<meta property="og:title" content="うさぎ│LIFE NOTES">
<meta property="og:image" content="logo.png">
<meta name="twitter:card" content="summary">
<style>
:root{{--bg:#fbf8f3;--card:#fff;--ink:#2b2622;--sub:#776d64;--line:#ece4d8;--accent:#c8763a;--pr:#bf3b2f;--chip:#f3ece2}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1c1a18;--card:#262320;--ink:#f1ebe3;--sub:#b3a89c;--line:#3a3530;--accent:#e39a5f;--pr:#ef7a6c;--chip:#302c28;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#1c1a18;--card:#262320;--ink:#f1ebe3;--sub:#b3a89c;--line:#3a3530;--accent:#e39a5f;--pr:#ef7a6c;--chip:#302c28;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.7 -apple-system,"Hiragino Sans","Noto Sans JP",sans-serif}}
.wrap{{max-width:640px;margin:0 auto;padding-block:24px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
header{{text-align:center}}
header img{{width:120px;height:120px;border-radius:50%;object-fit:cover;border:1px solid var(--line)}}
.brand{{letter-spacing:.2em;font-size:12px;color:var(--sub);margin:8px 0 0}}
h1{{font-size:22px;margin:4px 0 6px}}
.intro{{color:var(--sub);font-size:14px;margin:0}}
.notice{{background:var(--chip);border-radius:8px;padding:8px 12px;font-size:12px;color:var(--sub);margin:16px 0}}
nav{{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:12px 0 4px}}
nav a{{font-size:13px;color:var(--ink);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:4px 12px;background:var(--card)}}
h2{{font-size:18px;margin:32px 0 2px;border-left:4px solid var(--accent);padding-left:10px}}
.lead{{color:var(--sub);font-size:13px;margin:0 0 12px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:0 0 12px}}
.meta{{display:flex;gap:8px;align-items:center;font-size:12px;color:var(--sub)}}
.tag{{color:var(--pr);border:1px solid var(--pr);border-radius:4px;padding:0 6px;font-weight:700}}
h3{{font-size:16px;margin:4px 0 6px;line-height:1.5}}
ul{{margin:0;padding-left:1.1em}} li{{margin:2px 0;font-size:14px}}
.reason{{margin:10px 0 0;font-size:14px;background:var(--chip);border-radius:8px;padding:8px 10px}}
.reason b{{display:block;font-size:12px;color:var(--accent)}}
.src{{font-size:12px;color:var(--sub);margin:8px 0 0}}
.sample{{font-size:11px;color:var(--sub);margin:4px 0 0}}
.btn{{display:inline-block;margin-top:10px;font-size:14px;font-weight:700;color:var(--accent);text-decoration:none}}
.btn.pr{{background:var(--pr);color:#fff;border-radius:8px;padding:8px 14px}}
.ended li{{color:var(--sub)}}
footer{{margin-top:36px;text-align:center}}
.follow{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0}}
.follow a{{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px;color:var(--ink);text-decoration:none;font-weight:700}}
.small{{font-size:12px;color:var(--sub)}}
</style></head>
<body><div class="wrap">
<header>
<img src="logo.png" alt="うさぎ│LIFE NOTES のロゴ">
<p class="brand">USAGI LIFE NOTES</p>
<h1>あしたから行ける・AIが比べた</h1>
<p class="intro">首都圏・関西で「今日から・新しく・無料で」行ける場所を、AIが毎日調べて載せています。</p>
</header>
<p class="notice">このページはPR（楽天アフィリエイト）を含みます。値段や日時は変わることがあるので、出かける前・買う前に公式ページで確かめてください。</p>
<nav>{nav}</nav>
{sections}
<footer>
<h2 style="text-align:left">FOLLOW</h2>
<div class="follow">{follow}</div>
<p class="small">毎日更新（最終 {updated}）。7日より前の投稿は外しています。</p>
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
