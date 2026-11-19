"""11/19 オーナー「今日からブラックフライデー、全アフェリエイト、本気で」→ おかいものに「ブラックフライデーで安い物」。

夜（GPT）が毎朝 7:00 の回に「燈への報告」へ書く行を、月が data/bf-okaimono.json に入れる（入れ方は
python3 scripts/bf_okaimono.py ingest <燈への報告を落としたテキスト>）。page.yml では okai_v4.py の後に
python3 scripts/bf_okaimono.py が動き、/okaimono と /okaimono-<種類> の順位の上に枠を1つ足す。
  【夜 BF おかいもの】日時｜種類｜商品名｜量・入数｜いまの値段｜クーポンの文｜使える時間｜レビュー件数｜★｜URL（楽天）
  【夜 Amazon BF おかいもの】日時｜種類｜商品名｜量・入数｜いまの値段｜割引の文｜レビュー件数｜★｜URL（Amazon）
見た目は今の順位（.rkl）と同じ形。新しい色・字は足さない。11/25 2:00 を過ぎたら何も出さない（自動で消える）。
値段・クーポンの文は夜がページで見たままを出し、「何時に確かめた」を必ず添える。36時間より古い行は出さない。"""
import html
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime, timedelta, timezone

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(R, "site")
DATA = os.path.join(R, "data", "bf-okaimono.json")
JST = timezone(timedelta(hours=9))
E = html.escape
START = datetime(2026, 11, 19, 20, 0, tzinfo=JST)
END = datetime(2026, 11, 25, 1, 59, tzinfo=JST)
AMZ = os.environ.get("AMAZON_TAG", "aiusagichan-22")
AFF = os.environ.get("RAKUTEN_AFFILIATE_ID") or "58b50f43.00cd84ff.58b50f44.4872e82d"
NG = ["酒", "ビール", "ワイン", "サプリ", "医薬", "電気毛布", "ヒーター", "こたつ", "加湿器", "火災警報器", "訳あり", "枕"]

sys.path.insert(0, os.path.join(R, "scripts"))
try:
    from okai_v4 import NAME, SYN
except Exception:
    NAME, SYN = {}, {}


def kind(word):
    w = (word or "").strip()
    for k, nm in NAME.items():
        if w == nm or w in nm or nm in w:
            return k
    for s, k in SYN.items():
        if s in w:
            return k
    return ""


def ingest(path):
    """燈への報告のテキストから【夜 BF おかいもの】【夜 Amazon BF おかいもの】の行を読み、json に足す（同じURLは新しい方）。"""
    txt = open(path, encoding="utf-8-sig").read().replace("\\_", "_")
    try:
        d = json.load(open(DATA, encoding="utf-8"))
    except Exception:
        d = {"_": __doc__.splitlines()[0], "items": []}
    have = {it["url"]: it for it in d["items"]}
    n = 0
    for line in txt.splitlines():
        m = re.search(r"【夜 (Amazon )?BF おかいもの】(.*)", line)
        if not m:
            continue
        f = [x.strip() for x in m.group(2).split("｜")]
        amz = bool(m.group(1))
        need = 9 if amz else 10
        if len(f) < need:
            continue
        at = re.match(r"(\d{4})-(\d\d)-(\d\d) (\d\d):(\d\d)", f[0])
        url = re.search(r"https?://\S+", f[-1])
        if not at or not url:
            continue
        url = url.group(0).rstrip("）)。、")
        if amz and not re.match(r"https://www\.amazon\.co\.jp/", url):
            continue
        if not amz and not re.match(r"https://item\.rakuten\.co\.jp/", url):
            continue
        name = f[2]
        if any(w in name for w in NG):
            continue
        it = {"at": f"{at.group(1)}-{at.group(2)}-{at.group(3)} {at.group(4)}:{at.group(5)}", "src": "amazon" if amz else "rakuten",
              "k": kind(f[1]), "kind": f[1], "n": name, "q": f[3], "p": f[4], "cp": f[5],
              "t": "" if amz else f[6], "rc": f[-3], "av": f[-2], "url": url}
        if url in have and have[url]["at"] >= it["at"]:
            continue
        have[url] = it
        n += 1
    d["items"] = sorted(have.values(), key=lambda x: x["at"], reverse=True)[:80]
    d["updated"] = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    json.dump(d, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("bf_okaimono ingest:", n, "件足した・全部", len(d["items"]))


def link(it):
    if it["src"] == "amazon":
        u = re.sub(r"[?&]tag=[^&]*", "", it["url"])
        return u + ("&" if "?" in u else "?") + "tag=" + AMZ
    enc = urllib.parse.quote(it["url"], safe="")
    return f"https://hb.afl.rakuten.co.jp/hgc/{AFF}/?pc={enc}&m={enc}"


def block(items, title_small):
    rows = []
    for it in items:
        d = re.match(r"\d{4}-(\d\d)-(\d\d) (\d\d:\d\d)", it["at"])
        seen = f"{int(d.group(1))}/{int(d.group(2))} {d.group(3)}" if d else it["at"]
        shop = "Amazon" if it["src"] == "amazon" else "楽天"
        sub = "・".join(x for x in [it.get("cp"), it.get("t")] if x and x not in ("不明", "まだ"))
        star = f"・★{E(it['av'])}（{E(it['rc'])}件）" if it.get("av") and it["av"] != "不明" else ""
        rows.append(
            f'<li><a href="{E(link(it))}" rel="sponsored noopener" target="_blank" data-k="kp:BF {E(it.get("kind",""))}">'
            f'<div class="tx"><p class="nm">{E(it["n"])}' + (f'　<small>{E(it["q"])}</small>' if it.get("q") and it["q"] not in it["n"] else "") + '</p>'
            f'<p class="pz"><b>{E(it["p"])}</b>' + (f'　<span>{E(sub)}</span>' if sub else "") + '</p>'
            f'<p class="sh">{shop}{star}・{E(seen)} に確かめた</p></div><span class="go">見る</span></a></li>')
    return (f'<section id="bf" aria-label="ブラックフライデーで安い物"><h3>ブラックフライデーで安い物<small>{E(title_small)}</small></h3>'
            f'<ol class="rkl">{"".join(rows)}</ol>'
            '<p class="kij" style="margin:6px 16px 0">値段とクーポンは、書いてある時刻にお店のページで見た物です。クーポンは先着や時間で終わることがあるので、買う前にお店のページで確かめてください。</p></section>')


def render(now=None):
    now = now or datetime.now(JST)
    if not (START <= now <= END):
        print("bf_okaimono: 期間の外なので出さない")
        return 0
    try:
        items = json.load(open(DATA, encoding="utf-8")).get("items", [])
    except Exception:
        items = []
    fresh = []
    for it in items:
        try:
            at = datetime.strptime(it["at"], "%Y-%m-%d %H:%M").replace(tzinfo=JST)
        except Exception:
            continue
        if now - at <= timedelta(hours=36):
            fresh.append(it)
    fresh.sort(key=lambda i: (i["src"] != "rakuten", i["at"]), reverse=False)
    if not fresh:
        print("bf_okaimono: 新しい行が無いので出さない")
        return 0
    small = "11/25（水）1:59まで・楽天のクーポンなど" if not any(i["src"] == "amazon" for i in fresh) else "11/25（水）1:59まで・楽天のクーポンとAmazon"
    n = 0
    top = os.path.join(SITE, "okaimono.html")
    if os.path.exists(top):
        x = open(top, encoding="utf-8").read()
        if 'id="bf"' not in x and '<div class="my" id="v4my"' in x:
            x = x.replace('<div class="my" id="v4my"', block(fresh[:10], small) + '<div class="my" id="v4my"', 1)
            open(top, "w", encoding="utf-8").write(x)
            n += 1
    for k in {i["k"] for i in fresh if i.get("k")}:
        p = os.path.join(SITE, f"okaimono-{k}.html")
        if not os.path.exists(p):
            continue
        x = open(p, encoding="utf-8").read()
        mine = [i for i in fresh if i.get("k") == k][:5]
        if 'id="bf"' in x or '<ol class="rkl">' not in x:
            continue
        x = x.replace('<ol class="rkl">', block(mine, small) + '<h3>ふだんの最安</h3><ol class="rkl">', 1)
        open(p, "w", encoding="utf-8").write(x)
        n += 1
    print("bf_okaimono:", len(fresh), "件・", n, "ページに出した")
    return n


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "ingest":
        ingest(sys.argv[2])
    else:
        render()
