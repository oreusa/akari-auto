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
SKIP = ("google.com/maps", "fonts.googleapis", "fonts.gstatic")
IPHONE = dict(
    user_agent=("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
                "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"),
    viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True, locale="ja-JP",
)


def words(name):
    """カードの名前から、題名に出てきそうな言葉（2文字以上）を取り出す。"""
    name = re.sub(r"[0-9０-９/／・、。「」『』（）()【】\s~〜－-]+", " ", name or "")
    return [w for w in name.split() if len(w) >= 2][:6]


async def hp_links(ctx):
    page = await ctx.new_page()
    t0 = time.time()
    await page.goto(HP + "?me=check", wait_until="load", timeout=30000)
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
            if (r.height < 44 || fs < 12) out.push({t: (e.textContent || '').trim().slice(0, 20), h: Math.round(r.height), w: Math.round(r.width), fs});
        }
        return out;
    }""")
    await page.close()
    return links, small, hp_sec


async def open_one(ctx, sem, link):
    async with sem:
        page = await ctx.new_page()
        r = {**link, "status": 0, "sec": None, "final": "", "title": "", "err": ""}
        t0 = time.time()
        try:
            resp = await page.goto(link["href"], wait_until="domcontentloaded", timeout=LIMIT)
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
    if r["err"]:
        out.append("開かない（" + ("15秒たっても開かない" if "Timeout" in r["err"] else r["err"]) + "）")
    elif r["status"] >= 400:
        out.append(f"ページがない・断られる（{r['status']}）")
    if r["sec"] and r["sec"] >= SLOW and not r["err"]:
        out.append(f"重い（{r['sec']}秒）")
    if r["final"]:
        a, b = urllib.parse.urlparse(r["href"]), urllib.parse.urlparse(r["final"])
        if a.path not in ("", "/") and b.path in ("", "/") and "rakuten" not in a.netloc:
            out.append("トップページに飛ばされる（行き先が消えた可能性）")
    if r["href"].startswith("http://"):
        out.append("http（安全でない）")
    if r["blank"]:
        out.append("新しい画面で開く（アプリ内ブラウザで止まりやすい）")
    if r["title"] and r["name"] and r["sec"] is not None and not r["err"]:
        ws = words(r["name"])
        if ws and not any(w in r["title"] for w in ws) and r["sec"] < LIMIT / 1000:
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
        sem = asyncio.Semaphore(6)
        res = await asyncio.gather(*(open_one(ctx, sem, l) for l in todo))
        await br.close()
    now = datetime.now(JST)
    bad = [(r, problems(r)) for r in res]
    bad = [(r, ps) for r, ps in bad if ps]
    secs = sorted(r["sec"] for r in res if r["sec"] is not None and not r["err"])
    med = secs[len(secs) // 2] if secs else 0
    lines = [
        "# HPのリンクの確かめ（scripts/linkcheck.py。スマホのブラウザで全部開く）", "",
        f"確かめた時刻：{now:%Y-%m-%d %H:%M}｜HP {hp_sec:.1f}秒｜リンク {len(res)}本｜開くまでの中央値 {med}秒｜直す所 {len(bad)}本", "",
        "## 直す所（集め係・夜の回は、ここに出た物を直すか消す）", "",
    ]
    if not bad:
        lines.append("- なし")
    for r, ps in sorted(bad, key=lambda x: -(x[0]["sec"] or 0)):
        lines.append(f"- {r['name'] or r['label']}（{r['part']}・{r['sec']}秒・{r['status'] or 'ERR'}）｜{'・'.join(ps)}｜{r['href']}"
                     + (f" → {r['final']}" if r["final"] and r["final"].rstrip('/') != r["href"].rstrip('/') else "")
                     + (f"｜題名：{r['title']}" if r["title"] else ""))
    lines += ["", "## 押しにくい所（縦44px未満・字12px未満。見えている物だけ）", ""]
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
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:60]))


if __name__ == "__main__":
    asyncio.run(main())
