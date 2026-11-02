"""HPのリンクを、スマホのブラウザと同じ形で全部開いて確かめる（notes/linkcheck.md）。

10/27 オーナー「リンク押したら重いし開かないのある」「リンク先とか、使いにくさとか、月は初めから気を使ってる」。
・リンク先：開けるか・何秒かかるか・行き先がトップに飛んでいないか・題名がカードの名前と合うか
・押しやすさ：押す所が小さすぎないか（縦44px未満）・字が小さすぎないか（12px未満）
"""
import asyncio
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime, timedelta, timezone

from playwright.async_api import async_playwright

HP = os.environ.get("HP_URL", "https://usagi-life-notes.pages.dev/")
OUT = os.path.join(os.path.dirname(__file__), "..", "notes", "linkcheck.md")
SLOW = 5.0
LIMIT = 15000
JST = timezone(timedelta(hours=9))
SKIP = ("google.com/maps", "fonts.googleapis", "fonts.gstatic",
        # SNS・ROOMはロボットを断るだけで、人のスマホでは開く（確かめても意味がない）
        "instagram.com", "ig.me/", "x.com/", "threads.net", "threads.com", "room.rakuten.co.jp")
BOT = ("Just a moment", "しばらくお待ちください", "Attention Required")  # ロボット避けの画面（人は開ける）
SHOP = ("hb.afl.rakuten", "px.a8.net", "amazon.", "amzn.")  # 売り場：重さは相手のページの重さ（燈が直せない）
IPHONE = dict(
    user_agent=("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
                "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"),
    viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True, locale="ja-JP",
)


def _norm(t):
    return re.sub(r"[\W_0-9０-９]+", "", (t or "").lower())


def same(name, title):
    """カードの名前と行き先の題名が合っているか（名前の2文字ずつが題名に3割以上ある）。"""
    n, t = _norm(name), _norm(title)
    grams = {n[i:i + 2] for i in range(len(n) - 1)}
    return not grams or sum(g in t for g in grams) / len(grams) >= 0.3


async def hp_links(ctx):
    # 11/2 LIFE NOTE：リストは /odekake と /okaimono の2枚に分けた。両方を開く
    L, SM, sec0 = [], [], None
    for path in ("odekake", "okaimono"):
        links, small, sec = await _one(ctx, HP.rstrip("/") + "/" + path)
        L += links; SM += small; sec0 = sec if sec0 is None else sec0
    return L, SM, sec0


async def _one(ctx, url):
    page = await ctx.new_page()
    t0 = time.time()
    await page.goto(url + "?me=check", wait_until="load", timeout=30000)
    hp_sec = time.time() - t0
    # 隠れているタブ・欄も含めて、全部のリンクを取る
    links = await page.evaluate("""() => [...document.querySelectorAll('a[href^="http"]')].map(a => {
        const c = a.closest('.card, article, section');
        const t = c ? (c.querySelector('.t, .cho b, h2, h3') || {}).textContent || '' : '';
        const sec = a.closest('section[id]');
        return {href: a.href, label: (a.textContent || '').trim().slice(0, 30), name: t.trim().slice(0, 60),
                part: sec ? sec.id : '', blank: a.target === '_blank'};
    })""")
    # 押しやすさ：見えている押す所の大きさと字の大きさ
    small = await page.evaluate("""() => {
        const out = [];
        for (const e of document.querySelectorAll('a, button')) {
            const r = e.getBoundingClientRect();
            if (!r.width || !r.height) continue;
            const fs = parseFloat(getComputedStyle(e).fontSize);
            if (e.classList.contains('go') && e.closest('.card')) continue;  // カード全体が押せる（:after）
            if (r.height < 44 || fs < 12) out.push({t: (e.textContent || '').trim().slice(0, 20), h: Math.round(r.height), w: Math.round(r.width), fs});
        }
        return out;
    }""")
    await page.close()
    return links, small, hp_sec


def target(href):
    """売り場のリンクは、相手の商品ページを直接開く。アフィリエイトの入口（hb.afl・px.a8）を
    ロボットが開くと「クリック」に数えられ、売れた帳の数字がにごる（10/31 月）。"""
    u = urllib.parse.urlparse(href)
    if "hb.afl.rakuten" in u.netloc:
        q = urllib.parse.parse_qs(u.query)
        return (q.get("m") or q.get("pc") or [None])[0]
    if "px.a8.net" in u.netloc:
        return None  # 行き先がURLに書いていない。開かない
    if "amazon." in u.netloc and "tag=" in u.query:
        q = [(k, v) for k, v in urllib.parse.parse_qsl(u.query) if k != "tag"]
        return u._replace(query=urllib.parse.urlencode(q)).geturl()
    return href


async def open_one(ctx, sem, link):
    async with sem:
        page = await ctx.new_page()
        r = {**link, "status": 0, "sec": None, "final": "", "title": "", "err": ""}
        t0 = time.time()
        url = target(link["href"])
        if not url:  # A8：開かずに正常あつかい（押されたことにしない）
            await page.close()
            r.update(status=200, sec=0.0, title="（A8は開かない）")
            return r
        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=LIMIT)
            r["sec"] = round(time.time() - t0, 1)
            r["status"] = resp.status if resp else 0
            r["final"] = page.url
            r["title"] = (await page.title())[:60]
        except Exception as e:  # 15秒で開かない・つながらない
            r["sec"] = round(time.time() - t0, 1)
            r["err"] = str(e).split("\n")[0][:80]
        await page.close()
        return r


def problems(r):
    out = []
    shop = any(k in r["href"] for k in SHOP)
    bot = any(k in r["title"] for k in BOT)
    if r["err"]:
        out.append("開かない（" + ("15秒たっても開かない" if "Timeout" in r["err"] else r["err"]) + "）")
    elif r["status"] >= 400 and not bot:
        out.append(f"ページがない・断られる（{r['status']}）")
    if r["sec"] and r["sec"] >= SLOW and not r["err"] and not shop:
        out.append(f"重い（{r['sec']}秒）")
    a = urllib.parse.urlparse(r["href"])
    if r["final"]:
        b = urllib.parse.urlparse(r["final"])
        if a.path not in ("", "/") and b.path in ("", "/") and "rakuten" not in a.netloc:
            out.append("トップページに飛ばされる（行き先が消えた可能性）")
    # 催しだけのサイト（やきいもフェス等）は題名が合うのでよい。施設のトップ（科博・六本木ヒルズ等）だけ出す
    if r["part"] == "odekake" and a.path in ("", "/") and not a.query and not (r["title"] and same(r["name"], r["title"])):
        out.append("公式のトップページ（催しのページに替える）")
    if r["href"].startswith("http://"):
        out.append("http（安全でない）")
    if r["blank"]:
        out.append("新しい画面で開く（アプリ内ブラウザで止まりやすい）")
    if r["title"] and r["name"] and not r["err"] and not shop and not bot and not same(r["name"], r["title"]):
        out.append("題名がカードの名前と合わない（中身を見て確かめる）")
    return out


async def main():
    async with async_playwright() as p:
        exe = os.environ.get("CHROMIUM")
        br = await (p.chromium.launch(executable_path=exe) if exe else p.chromium.launch())
        ctx = await br.new_context(**IPHONE)
        links, small, hp_sec = await hp_links(ctx)
        seen, todo = set(), []
        for l in links:
            if any(s in l["href"] for s in SKIP) or l["href"] in seen:
                continue
            seen.add(l["href"])
            todo.append(l)
        # 載せる前の確かめで止まっている物も、ブラウザで開いてみる（簡単な開き方だけ断るページを戻すため）
        import json
        try:
            held = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "link-ok.json"), encoding="utf-8"))
        except (OSError, ValueError):
            held = {}
        for u, v in held.items():
            if not v.get("ok") and u not in seen:
                seen.add(u)
                todo.append({"href": u, "label": "載せる前に止めた物", "name": "", "part": "hold", "blank": False})
        sem = asyncio.Semaphore(6)
        res = await asyncio.gather(*(open_one(ctx, sem, l) for l in todo))
        await br.close()
    now = datetime.now(JST)
    bad = [(r, problems(r)) for r in res]
    bad = [(r, ps) for r, ps in bad if ps]
    shop_secs = sorted(r["sec"] for r in res if r["sec"] and not r["err"] and any(k in r["href"] for k in SHOP))
    bots = [r for r in res if any(k in r["title"] for k in BOT)]
    secs = sorted(r["sec"] for r in res if r["sec"] is not None and not r["err"])
    med = secs[len(secs) // 2] if secs else 0
    lines = [
        "# HPのリンクの確かめ（scripts/linkcheck.py。スマホのブラウザで全部開く）", "",
        f"確かめた時刻：{now:%Y-%m-%d %H:%M}｜HP {hp_sec:.1f}秒｜リンク {len(res)}本｜開くまでの中央値 {med}秒｜直す所 {len(bad)}本", "",
        f"売り場（楽天・A8）{len(shop_secs)}本の中央値 {shop_secs[len(shop_secs) // 2] if shop_secs else 0}秒（相手のページの重さ。燈は直せない）"
        f"｜ロボット避けの画面 {len(bots)}本（人のスマホでは開く）", "",
        "## 直す所（集め係・夜の回は、ここに出た物を直すか消す。投稿済みの物は data/link-fix.json で差し替え）", "",
    ]
    if not bad:
        lines.append("- なし")
    for r, ps in sorted(bad, key=lambda x: -(x[0]["sec"] or 0)):
        lines.append(f"- {r['name'] or r['label']}（{r['part']}・{r['sec']}秒・{r['status'] or 'ERR'}）｜{'・'.join(ps)}｜{r['href']}"
                     + (f" → {r['final']}" if r["final"] and r["final"].rstrip('/') != r["href"].rstrip('/') else "")
                     + (f"｜題名：{r['title']}" if r["title"] else ""))
    lines += ["", "## 押しにくい所（参考。月と同じ大きさなら直さない。10/27 オーナー「月と同じなら不備なし」）", ""]
    if not small:
        lines.append("- なし")
    seen_s = set()
    for s in small:
        key = (s["t"], s["h"], s["fs"])
        if key in seen_s:
            continue
        seen_s.add(key)
        lines.append(f"- 「{s['t']}」 高さ{s['h']}px・幅{s['w']}px・字{s['fs']}px")
    lines += ["", "## 全部のリンク（遅い順）", "", "秒｜状態｜欄｜名前｜行き先"]
    for r in sorted(res, key=lambda x: -(x["sec"] or 0)):
        lines.append(f"{r['sec']}｜{r['status'] or 'ERR'}｜{r['part']}｜{r['name'] or r['label']}｜{r['href']}")
    # ブラウザで開けた結果を、HPの「載せる前の確かめ」（page.py の gate）にも渡す。ロボットを断るだけのページもこちらで通る
    import json
    okp = os.path.join(os.path.dirname(__file__), "..", "data", "link-ok.json")
    try:
        book = json.load(open(okp, encoding="utf-8"))
    except (OSError, ValueError):
        book = {}
    for r in res:
        good = not r["err"] and (r["status"] < 400 or r["status"] in (401, 403, 429))
        book[r["href"]] = {"ok": good, "why": r["err"][:60] or ("" if r["status"] < 400 else str(r["status"])),
                           "sec": r["sec"], "at": now.date().isoformat(), "by": "browser"}
    with open(okp, "w", encoding="utf-8") as f:
        json.dump(book, f, ensure_ascii=False, indent=1, sort_keys=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:60]))


if __name__ == "__main__":
    asyncio.run(main())
