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
    ("pr", "うさぎが選んだ物", "3つ以上を数字で比べて、1つだけ選んだ物です"),
]
SHOW_GO = 5  # おでかけは地域ごとに最初の5件だけ見せ、残りは「ほかの〜件を見る」（商品とのバランス）
SEASON_I = {"spring": 0, "summer": 1, "autumn": 2, "winter": 3}


def period(now):
    """seasons.json から今日の時期を選ぶ（from が今日以前でいちばん新しい物。年の初めは前の年の最後の時期）。"""
    ps = sorted((load_json(path("seasons.json"), {}) or {}).get("periods", []), key=lambda x: x["from"])
    today = f"{now.month:02d}-{now.day:02d}"
    past = [x for x in ps if x["from"] <= today]
    return (past or ps)[-1] if ps else {"name": "", "season": "autumn", "cats": []}


def cats(now):
    """買い物の項目（タブの並び順）：時期の項目 → 日用品 → 食べ物 → グッズ・ギフト。宿・予約・セールは別の欄。
    時期が変わると時期の項目だけ自動で入れ替わる（10/24 オーナー「日用品・グッズが増えたら？分け方を綺麗に」）。"""
    mid = [(c["key"], c["en"], c["name"], c["lead"], tuple(c.get("words", ()))) for c in period(now).get("cats", [])]
    return ([("stay", "STAY", "週末の宿", "", ()), ("book", "BOOKING", "予約", "", ())] + mid
            # 11/3 オーナー「トイレットペーパーが食べ物？酷い」→「ふるさと納税」の言葉で食べ物にしない。水・炭酸水も飲み物としてここへ
            + [("food", "FOOD", "食べ物・飲み物", "", ("米", "肉", "鍋", "スープ", "麺", "お菓子", "チョコ", "スイーツ", "コーヒー", "お茶",
                                               "水 ", "ミネラルウォーター", "炭酸水", "の水", "飲料", "ドリンク", "ジュース",
                                               "カニ", "蟹", "うなぎ", "グルメ", "おせち")),
               ("gift", "GOODS", "グッズ・ギフト", "", ("ギフト", "プレゼント", "グッズ", "ぬいぐるみ", "キャラクター", "雑貨", "花束", "フラワー")),
               ("life", "DAILY", "日用品", "", ()),
               ("sale", "SALE", "楽天のお得", "", ())])


SPOT_AHEAD = 14  # HPだけのおでかけは、始まる14日前から載せる


def page_spots_ended(now):
    """HPだけのおでかけで、終わって30日以内の物（「終わったおでかけ」に1行で残す。10/26 月のやり方「終わったものは自動で消さず残す」）。"""
    out = []
    for it in (load_json(path("data", "page-spots.json"), {}) or {}).get("items", []):
        e = _dt(it.get("ends"))
        if it.get("kind") != "shop" and e and now - timedelta(days=30) <= e < now:
            out.append({"title": it.get("title", ""), "name": it.get("title", ""), "ends": it["ends"], "place": it.get("place", ""),
                        "pref_fixed": it.get("pref", ""), "bullets": [], "day": f"{now.month}/{now.day}", "year": e.year})
    return out


_HOLD = set()  # 載せる前の確かめで通らなかったURL（このページには出さない）
UA_PHONE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")


def _open_ok(url):
    """スマホと同じ形で開けるか（ページがない・15秒で開かないだけ×。重いだけの物は載せる）。"""
    import time
    import urllib.error
    import urllib.request
    import urllib.parse
    t0 = time.time()
    # 10/31 月：アフィリエイトの入口（hb.afl・px.a8）をロボットが開くとクリックに数えられる。商品ページを直接開く
    u = urllib.parse.urlparse(url)
    if "hb.afl.rakuten" in u.netloc:
        q = urllib.parse.parse_qs(u.query)
        url = (q.get("m") or q.get("pc") or [url])[0]
    elif "px.a8.net" in u.netloc:
        return {"ok": True, "why": "", "sec": 0.0}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA_PHONE, "Accept-Language": "ja"})
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read(200000)
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception as e:
        return {"ok": False, "why": str(e)[:60], "sec": round(time.time() - t0, 1)}
    sec = round(time.time() - t0, 1)
    # 403・429はロボットを断るだけのことが多く、人のスマホでは開く（関内フード等）ので載せる
    return {"ok": code < 400 or code in (401, 403, 429), "why": "" if code < 400 else f"{code}", "sec": sec}


def gate(urls, now):
    """HPに載せる前に、まだ確かめていないリンクを開いて確かめる（10/27 オーナー「HPに載せる時もまず確認」）。
    通った物は3日覚えておく（data/link-ok.json）。通らない物は毎回確かめ直し、通るまで載せない。"""
    from concurrent.futures import ThreadPoolExecutor
    fp = path("data", "link-ok.json")
    book = load_json(fp, {}) or {}
    today = now.date().isoformat()
    old = (now - timedelta(days=3)).date().isoformat()
    # 通った物は3日、ブラウザ（毎日13:30の linkcheck）で開けた物はその日のうち確かめ直さない
    todo = [u for u in set(urls) if not (book.get(u, {}).get("ok") and book[u].get("at", "") >= old)
            and not (book.get(u, {}).get("by") == "browser" and book[u].get("at") == today)]
    with ThreadPoolExecutor(8) as ex:
        for u, r in zip(todo, ex.map(_open_ok, todo)):
            if not r["ok"] and book.get(u, {}).get("ok") and book[u].get("by") == "browser" and book[u].get("at", "") >= old:
                continue  # 機械の簡単な開き方では断られても、ブラウザで開けたページは載せる（無印良品など）
            book[u] = r | {"at": today}
    book = {u: v for u, v in book.items() if v.get("at", "") >= (now - timedelta(days=14)).date().isoformat()}
    with open(fp, "w", encoding="utf-8") as fh:
        json.dump(book, fh, ensure_ascii=False, indent=1, sort_keys=True)
    _HOLD.clear()
    bad = {u for u in set(urls) if not book.get(u, {}).get("ok")}
    if len(bad) > len(set(urls)) / 2:  # 半分より多く×は、確かめる側（ネット）の不調。HPを空にしない
        print("確かめで×が多すぎるので、今回は止めずに載せる:", len(bad))
        return
    _HOLD.update(bad)
    for u in sorted(_HOLD):
        print("載せない（確かめで×）:", u, book[u].get("why"), book[u].get("sec"))


def _fix_url(url):
    """投稿のあとで開かなくなった公式ページを差し替える（data/link-fix.json。notes/linkcheck.md を見て集め係・夜の回が書く）。
    ""に差し替えた物はカードを出さない。"""
    fix = (load_json(path("data", "link-fix.json"), {}) or {}).get("fix", {})
    return fix.get(url, url) if url else url


def _page_spots(now, ended=None):
    """HPだけに載せるおでかけ（投稿しない物も、来た人が使えるように。10/24 オーナー「投稿前に入れといてもいい」）。
    夜の回が公式ページで日時・料金を確かめて data/page-spots.json に書く。終わった物・始まる14日より前の物は出さない。"""
    out = []
    for it in (load_json(path("data", "page-spots.json"), {}) or {}).get("items", []):
        try:
            if it.get("ends") and datetime.fromisoformat(it["ends"]).replace(tzinfo=JST) < now:
                continue
            if it.get("start") and datetime.fromisoformat(it["start"]).replace(tzinfo=JST) > now + timedelta(days=SPOT_AHEAD):
                continue
        except ValueError:
            continue
        if not str(it.get("url", "")).startswith("https://") or not it.get("title"):
            continue
        shop = it.get("kind") == "shop"  # 新しいお店：open（開店日）が先なら「もうすぐ」、過ぎたら「できた」。開店から30日で外す
        if shop:
            try:
                od = datetime.fromisoformat(it.get("open", "")).replace(tzinfo=JST)
            except ValueError:
                continue
            if od < now - timedelta(days=30) or od > now + timedelta(days=60):
                continue
        y = int((it.get("start") or now.isoformat())[:4])
        if ended is not None:
            continue
        out.append({"title": it["title"], "name": it["title"], "start": it.get("start", ""), "ends": it.get("ends", ""),
                    "day": f"{now.month}/{now.day}", "year": y, "bullets": [it.get("note", "")],
                    "url": _fix_url(it["url"]), "place": it.get("place", ""), "pref_fixed": it.get("pref", ""),
                    "free_fixed": bool(it.get("free")), "note": it.get("note", ""), "kind": "shop" if shop else "odekake",
                    "open": it.get("open", ""), "days": it.get("days", ""), "opennote": it.get("opennote", ""), "page": True})
    return out


# 11/9 オーナー「燈？」「本当に値下がりってタイトル変すぎ」→ 前の投稿の文をHPに出す時も、中の名前と変な言い方を直す（ngcheck で止まるため）
_SAY = [("燈が毎日記録、本当に下がった物だけのページ", "いまが買い時の日用品のページ"), ("本当に値下がりした物だけ", "いまが買い時の日用品"),
        ("本当に下がった物", "ふだんより安い物"), ("本当に値下がりした物", "ふだんより安い物"), ("本当に", "")]


def _say(s):
    for a, b in _SAY:
        s = s.replace(a, b)
    return re.sub(r"(?<!ガス)燈(?:が|は|の|も)、?", "", s)


def _lines(text):
    return [_say(ln.strip()) for ln in text.split("\n") if ln.strip()]


def _title(text):
    ls = _lines(text)
    t = ls[0]
    if t == "【関東おでかけ情報】" and len(ls) > 1:  # 9:15は毎日同じ見出しなので、2行目（いつ・どこで・何が）を名前にする
        return ls[1]
    t = t.strip("【】")
    return t


def _bullets(text):
    """◇ の行。下に1字下げた行が続くときは1つにまとめる（10/28から ◇ は名前だけ＋下げた行。HPの比べ表は「名前：件数・評価、決め手」で読む）。"""
    out = []
    for raw in text.split("\n"):
        ln = raw.strip()
        if not ln:
            continue
        if ln.startswith("◇"):
            out.append(ln[1:].strip())
        elif raw.startswith("　") and out and not ln.startswith(("※", "#")):
            out[-1] += ("、" if "：" in out[-1] else "：") + ln
    return out[:6]


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


def collect(now, light=False):
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
        old = d < since  # 7日より前の日は「終わったおでかけ」を拾うためだけに読む（月と同じく30日残す）
        if d < (now - timedelta(days=30)).date():
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
                     "but": next((ln for ln in _lines(text) if ln.startswith("ただし")), ""),
                     "source": _line_with(text, "より（"), "url": _official(p), "place": p.get("place", ""),
                     "name": p.get("name", ""), "start": p.get("start", ""), "ends": p.get("ends") or p.get("until") or ""}
            entry["url"] = _fix_url(entry["url"])
            until = p.get("ends") or p.get("until")  # ends＝催し・お得が終わる時刻（夜の回が書く）。過ぎたらページから外す
            if until and datetime.fromisoformat(until).replace(tzinfo=JST) < now:
                if p.get("topic", "") in ODEKAKE and not p.get("link"):
                    ended.append(entry)
                continue
            if old:
                continue
            link = p.get("link")
            if link and link.get("mochimono"):  # おでかけに付けた持ち物は、HPではおでかけのカードとして出す
                link = None
            if link and light:
                continue
            if link:
                r = _resolve(link, list(p["x"]) + list(p["threads"]))
                if not r.get("ok"):
                    continue
                pr_urls.add(link.get("url", ""))
                entry["expect"] = link.get("expect", "")
                entry["url"] = r["link"]
                entry["sample"] = r.get("sample", False)
                entry["image"] = r.get("image", "")
                entry["price"] = r.get("price") if isinstance(r.get("price"), (int, float)) else None
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
    if light:
        return items, ended
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

MARATHON_URL = "https://event.rakuten.co.jp/campaign/point-up/marathon/"


def sale_box():
    """11/1 月（オーナー「燈のHPも改良して…ここから稼げなきゃ終わる」）：楽天の大きなセールの前の7日と開催中だけ、
    いちばん上に「エントリー」の入口を出す。楽天は、リンクを押してから24時間のうちの買い物がまとめて紹介料の対象になるので、
    1つの商品より、みんなが必ず押すエントリーのページがいちばん効く。日程は data/sales.json（夜の回が公式で確かめる）。"""
    try:
        d = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sales.json"), encoding="utf-8"))
    except Exception:
        return ""
    now = datetime.now(JST).replace(tzinfo=None)
    wk = "月火水木金土日"
    for x in d.get("sales", []):
        try:
            st = datetime.fromisoformat(x["start"])
            en = datetime.fromisoformat(x["end"])
        except Exception:
            continue
        if not (st - timedelta(days=7) <= now <= en):
            continue
        name = html.escape(x.get("name", "楽天のセール"))
        url = html.escape(_rakuten_afl(x.get("url") or MARATHON_URL), quote=True)
        if now < st:
            left = (st.date() - now.date()).days
            when = f"{st.month}/{st.day}（{wk[st.weekday()]}）{st:%H:%M}から" + (f"・あと{left}日" if left else "・今日から")
            if x.get("note"):
                when += "（見込み）"
            # 11/4 オーナー「普通マラソン前に人って調べない？」：始まる前は、下調べ（カートに入れておく）を促す
            sub = "買う前にエントリーが必要です。始まる前に、買う物をカートに入れておくと、すぐに買えます"
        else:
            e2 = en + timedelta(minutes=1)
            when = f"開催中・{e2.month}/{e2.day}（{wk[e2.weekday()]}）{e2:%H:%M}まで"
            sub = "まだの方は、買う前にエントリーを。1,000円以上を何店で買うかでポイントが増えます"
        # 11/1 オーナー「キレそう」：赤い大きな箱が月とちがい、リストが下に押された → 月の「関連ページ」と同じ白い箱に小さくまとめる
        return (f'<section class="sbox" id="sale"><div class="sb-x"><p class="sb-t">{name}</p>'
                f'<p class="sb-w">{html.escape(when)}</p></div><a class="buy sb-go nofilt" href="{url}" rel="sponsored noopener" target="_blank">エントリー<span>→</span></a>'
                f'<p class="sb-s">{html.escape(sub)}<span>（楽天アフィリエイトの広告）</span></p></section>')
    return ""



# 11/3 日用品だと決まる言葉（ほかの言葉より先に見る。ふるさと納税のトイレットペーパーが食べ物に入っていた）
LIFE_WORDS = ("トイレットペーパー", "ティッシュ", "キッチンペーパー", "洗剤", "柔軟剤", "シャンプー", "ボディソープ", "ハンドソープ",
              "乾電池", "マスク", "ゴミ袋", "おむつ", "オムツ", "おしりふき", "モバイルバッテリー", "歯ブラシ", "ラップ")


def _cat(text, cs):
    if any(w in text for w in LIFE_WORDS) and any(k == "life" for k, *_ in cs):
        return "life"
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


def goods_store(now):
    """HPの商品の置き場 data/page-goods.json（10/26 オーナー「アフェリエイトは常に増やしていかなきゃ意味無い」）。
    予定表の page_goods は7日で消えるので、集め係と夜の回がここに足す。until（その日まで出す。季節物）を過ぎた物は出さない。
    売り切れ・値段は作るたびに楽天で確かめ直すので、売っていない物は自動で消える。"""
    out = []
    for it in (load_json(path("data", "page-goods.json"), {}) or {}).get("items", []):
        if it.get("asin") and not it.get("url"):  # 11/1 Amazon も置く（凪が確かめた物だけ）
            it = dict(it, url=f"https://www.amazon.co.jp/dp/{it['asin']}")
        if not str(it.get("url", "")).startswith("https://"):
            continue
        if it.get("until") and it["until"] < now.date().isoformat():
            continue
        out.append(it)
    return out


def _added(it, now):
    try:
        return datetime.fromisoformat(it.get("added", "")).date()
    except ValueError:
        return now.date()


def _room_picks(now, since, skip=(), limit=90):
    """ROOM台本の商品（毎晩、燈が比べて選んだ3品）と商品の置き場を、新しい順に最大60品。楽天で販売中を確かめた物だけ。"""
    out, seen = [], set()
    days = []
    for f in sorted(glob.glob(path("schedule", "*.json")), reverse=True):
        day = os.path.basename(f)[:-5]
        if not re.match(r"\d{4}-\d{2}-\d{2}$", day):
            continue
        d = datetime.fromisoformat(day).date()
        if d < since or d > now.date():
            continue
        data = load_json(f, {}) or {}
        days.append((d, data.get("room", []) + data.get("page_goods", [])))  # page_goods＝投稿しないがHPに置く物（夜の回が選ぶ）
    store = sorted(goods_store(now), key=lambda it: it.get("added", ""), reverse=True)
    # 11/1 オーナー「継続してほしいちゃんと」：凪が毎晩○にしたAmazonの商品は、人の手を待たずにHPへ（7日以内の確認だけ）
    have = {it.get("asin") for it in store if it.get("asin")}
    amz, names = [], set()
    from lib import amazon_checked
    for asin, a in sorted((amazon_checked() or {}).items(), key=lambda kv: str(kv[1].get("checkedAt", "")), reverse=True):
        nm, spec = str(a.get("name", "")), str(a.get("specs", ""))
        if asin in have or a.get("ok") is False or nm[:20] in names:  # 色違いは1つだけ
            continue
        names.add(nm[:20])
        try:
            why = f"選んだ理由：Amazonのレビュー{int(a.get('reviews') or 0):,}件で、評価は{float(a.get('stars') or 0)}でした。"
        except (TypeError, ValueError):
            continue
        amz.append({"asin": asin, "url": f"https://www.amazon.co.jp/dp/{asin}", "expect": "",
                      "comment": why + ("\n" + spec.replace("／", "、") if spec else ""), "added": str(a.get("checkedAt", ""))[:10]})
    days.insert(0, (now.date(), amz))  # Amazonは先に読む（ROOM台本で90件が埋まって出なくならないように）
    days.append((now.date(), store))
    for d, its in days:
        if its is store or its is amz:
            d = None
        for it in its:
            url = it.get("url", "")
            if not url or url in seen or url in skip:  # 上の「AIが比べた」と同じ物は出さない
                continue
            seen.add(url)
            is_amz = bool(it.get("asin"))
            if is_amz:  # 11/1 オーナー「Amazonも、hpは置けるんじゃないの？」：凪が7日以内に確かめた物だけ
                if not ((load_json(path("config.json"), {}) or {}).get("page") or {}).get("amazon"):
                    continue
                from lib import amazon_link
                try:
                    r = amazon_link(it["asin"], it.get("expect", ""), now=now, max_age_h=24 * 7)
                except Exception as e:
                    r = {"ok": False, "why": str(e)[:80]}
            else:
                r = _resolve({"type": "ichiba", "url": url, "expect": it.get("expect", "")}, [it.get("comment", "")])
            if not r.get("ok"):
                continue
            lines = [ln.strip() for ln in (it.get("comment") or "").split("\n") if ln.strip() and not ln.startswith("#")]
            dd = d or _added(it, now)
            out.append({"day": f"{dd.month}/{dd.day}", "name": _short(r.get("name")) or it.get("expect", ""),
                        "expect": it.get("expect", ""), "price": r.get("price"), "count": r.get("reviewCount"),
                        "avg": r.get("reviewAverage"), "lines": lines[:3], "url": r["link"],
                        "sample": r.get("sample", False), "image": r.get("image", ""), "amazon": is_amz})
            cs = cats(now)
            out[-1]["cat"] = (it["cat"] if it.get("cat") in {k for k, *_ in cs}
                              else _cat(" ".join([out[-1]["name"], out[-1]["expect"]] + lines[:1]), cs))
            if len(out) >= limit:
                return out
    return out


def esc(s):
    return html.escape(s or "", quote=True)


WEEK = "月火水木金土日"
ROW_RE = re.compile(r"^(?P<name>[^：:]+)[：:](?P<rest>.*)$")
# 地名 → 都府県（左の色の線とタブに使う）
# 「東京」が付くが千葉にある所は先に（10/29 東京ドイツ村が東京のカードになり、地図のピンが出なかった）
PLACE = [("東京ドイツ村", "千葉"), ("東京ディズニー", "千葉"), ("東京湾アクアライン", "千葉"), ("東京", "東京"), ("高円寺", "東京"), ("池袋", "東京"), ("銀座", "東京"), ("渋谷", "東京"), ("新宿", "東京"),
         ("上野", "東京"), ("二子玉川", "東京"), ("芝公園", "東京"), ("お台場", "東京"), ("豊洲", "東京"), ("浅草", "東京"),
         ("横浜", "神奈川"), ("神奈川", "神奈川"), ("川崎", "神奈川"), ("鎌倉", "神奈川"), ("箱根", "神奈川"),
         ("埼玉", "埼玉"), ("千葉", "千葉"), ("舞浜", "千葉"),
         ("茨城", "茨城"), ("水戸", "茨城"), ("ひたち海浜", "茨城"), ("栃木", "栃木"), ("日光", "栃木"), ("あしかが", "栃木"),
         ("足利", "栃木"), ("宇都宮", "栃木"), ("那須", "栃木"), ("群馬", "群馬"), ("草津", "群馬"), ("高崎", "群馬"),
         ("伊香保", "群馬"), ("前橋", "群馬"), ("富岡", "群馬"), ("桐生", "群馬"), ("四万温泉", "群馬"), ("水上", "群馬"),
         ("川越", "埼玉"), ("秩父", "埼玉"), ("大宮", "埼玉"), ("さいたま", "埼玉"), ("所沢", "埼玉"), ("長瀞", "埼玉"),
         ("成田", "千葉"), ("幕張", "千葉"), ("鴨川", "千葉"), ("船橋", "千葉"), ("木更津", "千葉"), ("横須賀", "神奈川"),
         ("小田原", "神奈川"), ("江の島", "神奈川"), ("湘南", "神奈川"), ("みなとみらい", "神奈川"), ("八王子", "東京"),
         ("吉祥寺", "東京"), ("六本木", "東京"), ("丸の内", "東京"), ("日本橋", "東京"), ("表参道", "東京"), ("立川", "東京"),
         ("つくば", "茨城"), ("大洗", "茨城"), ("笠間", "茨城"), ("鬼怒川", "栃木"), ("益子", "栃木"),
         ("大阪", "大阪"), ("梅田", "大阪"), ("なんば", "大阪"), ("難波", "大阪"), ("天王寺", "大阪"), ("福島", "大阪"),
         ("京都", "京都"), ("嵐山", "京都"), ("神戸", "兵庫"), ("兵庫", "兵庫"), ("有馬", "兵庫"), ("城崎", "兵庫"),
         ("姫路", "兵庫"), ("奈良", "奈良"), ("和歌山", "和歌山"), ("高野山", "和歌山"), ("滋賀", "滋賀"), ("琵琶湖", "滋賀")]
KANTO = {"東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"}
KANTO_ORDER = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"]  # HPのしぼりこみの並び
REGION_COLOR = {"関東": "#5D7FA3", "関西": "#C27A63"}  # しぼりこみは「関東・関西」の2つ（10/24 オーナー「東京、大阪、兵庫は変だ」）


def region(pref):
    return "関東" if pref in KANTO else "関西" if pref else ""


PREF_ORDER = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬", "大阪", "京都", "兵庫", "奈良", "和歌山", "滋賀"]
# 関東7都県は地図（TOWN NOTES MAP）と同じ色（10/29 オーナー「C」：月の関西と同じ明るさで、7都県がはっきり違う色）
PREF_COLOR = {"東京": "#4F86C6", "神奈川": "#3FA3B5", "埼玉": "#E09A3E", "千葉": "#D9775A", "茨城": "#5FA06A",
              "栃木": "#D2697E", "群馬": "#9C7BB8", "大阪": "#C27A63",
              "京都": "#8E7BA6", "兵庫": "#4F6A8A", "奈良": "#6F8F5F", "和歌山": "#B5788A", "滋賀": "#5F9A9A"}
DATE_HEAD = re.compile(r"^((?:今日|明日|あす)?\s*\d{1,2}/\d{1,2}[^、,]{0,14}?(?:から|まで)?)[、,]\s*")
BLOCKS = {  # 章の英語名
    "odekake": "GO OUT", "shop": "NEW OPEN", "deal": "LIMITED", "pr": "USAGI PICK", "ended": "ARCHIVE",
}


def _text(e):
    return e["title"] + " " + " ".join(e["bullets"])


def _pref(e):
    if e.get("pref_fixed"):
        return e["pref_fixed"]
    # 名前と場所に地名があればそれを先に使う（10/25 横浜赤レンガ倉庫が、文の最初の「神戸」で関西になっていた）
    t = " ".join(x for x in (e.get("name"), e.get("place")) if x) + " " + _text(e)
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
    return _cut(x, "でのとも", n) if marks == "はが" else [x]


def phr(text):
    """見出しを言葉の切れ目（、・空白、長い所は「は」「が」のあと）で区切り、
    言葉の途中で改行しないようにする（月のページと同じ作り）。"""
    parts = []
    for x in re.findall(r"[^、，。・ 　]+[、，。・]?[ 　]?", text or ""):
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
    if e.get("page"):
        return "無料" if e.get("free_fixed") else ""
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


ARROW = ('<svg class="arw" width="22" height="11" viewBox="0 0 24 12" aria-hidden="true"><path d="M1 6H22M17.5 1.8 22 6l-4.5 4.2" fill="none" '
         'stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/></svg>')
OUT = ('<svg class="out" width="9" height="9" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 9 9 3M4.2 3H9v4.8" fill="none" '
       'stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/></svg>')


MEDIA = ("walkerplus.com", "happyell.co.jp", "iko-yo.net", "pretty-online.jp", "voyvoi.com", "storm.mg", "prtimes.jp", "jorudan.co.jp",
         "jalan.net", "tabelog.com", "timeout.jp", "fashion-press.net", "yahoo.co.jp", "note.com", "enjoytokyo.jp")


def link_label(url):
    """カードの下の言葉。施設・主催・役所のページは「公式ページ」、ニュースや情報サイトは「紹介記事」（10/24 オーナー「もっと正確に」）。"""
    host = (urllib.parse.urlparse(url or "").hostname or "").lower()
    return "紹介記事" if any(host == m or host.endswith("." + m) for m in MEDIA) else "公式ページ"


def _dt(x):
    try:
        return datetime.fromisoformat(x).replace(tzinfo=JST) if x else None
    except ValueError:
        return None


def _md(d):
    return f"{d.month}/{d.day}（{WEEK[d.weekday()]}）"


def _span(e, now=None):
    """月のページと同じ日付の書き方：開催中は「11/8（日）まで」、これからは「10/31（土）」「10/31（土）〜11/1（日）」。"""
    now = now or now_jst()
    st, en = _dt(e.get("start")), _dt(e.get("ends"))
    if st and st > now:
        if not en or en.date() == st.date():
            return _md(st)
        if (en.date() - st.date()).days <= 7:
            return f"{_md(st)}〜{_md(en)}"
        return f"{_md(st)}から"
    if en:
        return "今日まで" if en.date() == now.date() else f"{_md(en)}まで"
    return ""


_NOW = []  # render が今の時刻を入れる（今週末・あと何日の判定に使う）


def _weekend(now):
    """今週末（土・日）。土日に開いたときは、その週末。"""
    d = now.date()
    sat = d + timedelta(days=(5 - d.weekday()) % 7) if d.weekday() != 6 else d - timedelta(days=1)
    return sat, sat + timedelta(days=1)


def spot(e):
    pref = _pref(e)
    color = PREF_COLOR.get(pref, "#A07E66")
    when, name = _split_title(e["title"].replace("AIが比べた", "", 1).strip("、 "))
    when = re.sub(r"^(?:今日|明日|あす)\s*", "", when or "")  # 11/1 月：投稿した日の「あす」がHPに残って、11/1 に「あす10/28」と出ていた
    when = _wd(when, e["year"]) if when else _wd(e["day"], e["year"]) + "調べ"
    if e.get("name"):
        name = e["name"]
    span = _span(e)
    if span and e.get("kind") != "deal":
        when = span
    if e.get("opennote"):  # 11/9 夜「月曜休館なのに今日行けると出る」→ 開く曜日をカードに出す
        when += f"（{e['opennote']}）"
    free = _free(e)
    tag = f'<span class="tg">・{esc(free)}</span>' if free else ""
    now = _NOW[0] if _NOW else now_jst()
    st, en = _dt(e.get("start")), _dt(e.get("ends"))
    sat, sun = _weekend(now)
    wk = e.get("kind") not in ("deal", "shop") and (not st or st.date() <= sun) and (not en or en.date() >= max(sat, now.date()))
    left = (en.date() - now.date()).days if en and not (st and st > now) else None
    # 「あと◯日」は外した（10/31 オーナー「月とサイト作りは同じで良い」。月のカードには無い）
    pl = f'<span class="pl">{esc(pref)}</span>' if pref else ""
    if not e.get("url"):  # リンクのないカードは載せない（押しても何も開かないため）
        return ""
    href = esc(e["url"])
    q = map_query(e, pref)
    nt = ""  # 月のページと同じく、カードは「どこ・いつ・名前・地図」だけ（説明は公式ページで）
    # 矢印（カード全体）＝公式ページ、「地図」＝地図アプリ（10/24 オーナー「矢印おしたら公式ページ、地図おしたらマップ」）
    mp = (f'<a class="mp" href="https://www.google.com/maps/search/?api=1&amp;query={esc(urllib.parse.quote(q))}" '
          f'rel="noopener">地図{OUT}</a>') if q else ""
    mpr = f'<div class="mpr">{mp}</div>' if mp else ""  # 地図だけの行（この行は押しても公式ページが開かない）
    de = f' data-e="{en.date().isoformat()}"' if en else ""  # 10/31 終わった日を過ぎたら、次の作り直しを待たずにページ側で隠す
    if st:  # 10/31 泊まりのページ（scripts/tomari.py）が「開催中／これから」を分けるのに使う
        de += f' data-s="{st.date().isoformat()}"'
    if e.get("days"):  # 11/6 夜「土曜だけ・日曜だけの催しが平日の『いまから』に出る」→ 開く日（sat・sun・we＝土日祝・日付）
        de += f' data-days="{esc(e["days"])}"'
    return (f'<div class="card it" data-pref="{esc(pref)}" data-free="{1 if free else 0}" data-wk="{1 if wk else 0}"{de} style="--pc:{color}">'
            f'<div class="d">{pl}<span class="when">{esc(when)}</span>{tag}</div>'
            f'<div class="t"><a class="go" href="{href}" rel="noopener" aria-label="{esc(link_label(e["url"]))}を開く">{phr(name)}</a></div>'
            f'{_where(e)}{nt}{mpr}{ARROW}</div>')


def _where(e):
    """11/9 全文点検：関東のカードに「どこ」が無く「● 栃木 |」で終わっていた → 月と同じく「市｜会場」の行を出す"""
    city = (e.get("note") or "").split("｜")[0].strip()
    if not re.fullmatch(r"[^\s、。]{1,10}?[市区町村]", city):
        city = ""
    place = (e.get("place") or "").strip()
    if place in ("-", city):
        place = ""
    s = "｜".join(x for x in (city, place) if x)
    return f'<div class="m">{esc(s)}</div>' if s else ""


_PLACE = re.compile(r"(?:場所は|会場は)[「『]?(.+?)(?:[」』]|です|（|。|、|$)")


def map_query(e, pref):
    """地図で探す言葉。夜の回が書いた place（"-"は地図なし）を使い、無ければ本文の「場所は・会場は」。当て推量はしない。"""
    q = (e.get("place") or "").strip()
    if q == "-" or e.get("kind") == "deal":
        return ""
    if not q:
        for line in [e["title"]] + e.get("bullets", []):
            m = _PLACE.search(line)
            if m:
                q = m.group(1)
                break
    if not q:
        return ""
    return q if (not pref or pref in q) else f"{q} {pref}"


def _img(e):
    u = e.get("image") or ""
    if not u.startswith("https://"):
        return ""
    return (f'<img class="ph" src="{esc(u)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" '
            f'onerror="this.remove()">')  # 10/30 宿の写真が2枚壊れて空の枠になっていた


SHOW_SHOP = 6  # 買い物の「すべて」は6件まで見せ、残りは「もっと見る」
SHOW_GOODS = 2  # 商品の欄は新しい2件だけ見せ、残りはたたむ（10/24 オーナー「HP改善したい」：長すぎて下まで見られない）


def go_label(e):
    """ボタンの言葉。押した先が分かるように、行き先を書く（「詳しく」だと押す前に何が開くか分からない）。"""
    if e.get("amazon"):
        return "Amazonで見る"
    if e.get("cat") == "stay":
        return "楽天トラベルで見る"
    return "楽天で見る"


def compare(e):
    """AIが比べたPR：選んだ1つと理由と「詳しく」だけを見せ、比べた表はたたんでおく。"""
    rows = _rows(e) or []
    title = e["title"].replace("AIが比べた", "", 1).strip("、 ")
    chosen = next((r for r in rows if r.get("pick")), None)
    if chosen:
        head = (f'<div class="cho"><div class="tx"><span class="lb">選んだのは</span><b>{phr(chosen["name"])}</b>'
                f'<span class="sc">★ {esc(chosen["avg"])}<i>｜</i>レビュー {chosen["count"]:,}件</span></div></div>')
    else:
        head = ""
    if rows:
        top = max(r["count"] for r in rows) or 1
        trs = "".join(
            f'<div class="row{" on" if r.get("pick") else ""}"><div class="nm">{esc(r["name"])}</div>'
            f'<div class="nu"><span class="av">★ {esc(r["avg"])}</span><span class="ct">{r["count"]:,}件</span></div>'
            + (f'<div class="nt">{esc(r["note"])}</div>' if r.get("note") else "") +
            f'<div class="br"><i style="width:{max(3, round(r["count"] / top * 100))}%"></i></div></div>' for r in rows)
        table = f'<details class="fold"><summary>比べた{len(rows)}つを見る</summary>{head}<div class="tbl">{trs}</div></details>'
        head = ""  # 選んだ物はたたんだ中に（10/25 オーナー「ごちゃごちゃ」。見出しに選んだ物の名前がある）
    else:
        table = ""
    reason = f'<p class="why">{esc(e["reason"])}</p>' if e.get("reason") else ""
    if e.get("but"):  # 10/25 オーナー「内容ペラペラ」：負けた所も見せる
        reason += f'<p class="why but">{esc(e["but"])}</p>'
    btn = f'<a class="buy" href="{esc(e["url"])}" rel="sponsored noopener">{go_label(e)}{ARROW}</a>'
    sample = '<p class="smp">見本：本番は楽天で販売中を確かめたPRリンクになります</p>' if e.get("sample") else ""
    img = _img(e)  # 写真は見出しの横に出す（10/26 オーナー「商品や宿とかの画像消えてるね。もったいない」：たたんだ中に入れて見えなくなっていた）
    yen = f'<span class="yen">税込 {int(e["price"]):,}円〜</span>' if e.get("price") else ""  # 10/30 オーナー「見やすいように」：押す前に値段が分かるように
    top = (f'<div class="tw">{img}<div><div class="t">{phr(title)}</div>{yen}</div></div>' if img
           else f'<div class="t">{phr(title)}</div>{yen}')
    return (f'<article class="card cmp{" hot" if e.get("hot") else ""}">'
            f'{top}{head}{reason}{table}<div class="ft2">{btn}</div>{sample}</article>')


def pick(e):
    meta = []
    if e.get("avg"):
        meta.append(f'<span class="av">★ {esc(str(e["avg"]))}</span>')
    if e.get("count"):
        meta.append(f'<span class="ct">レビュー {int(e["count"]):,}件</span>')
    if isinstance(e.get("price"), (int, float)) and e["price"]:
        meta.append(f'<span class="yen">税込 {int(e["price"]):,}円</span>')
    lis = "".join(f'<p class="why{" but" if i else ""}">{esc(ln)}</p>' for i, ln in enumerate(e["lines"][:3]))
    sample = '<p class="smp">見本：本番は楽天で販売中を確かめたPRリンクになります</p>' if e.get("sample") else ""
    return (f'<article class="card cmp pk2"><div class="d"><span class="when">{esc(e["day"])}　うさぎが選んだ</span></div>'
            f'<div class="cho">{_img(e)}<div class="tx"><span class="lb">選んだのは</span><b>{phr(e["name"])}</b>'
            f'<div class="meta">{"".join(meta)}</div></div></div>{lis}'
            f'<div class="ft2">'
            f'<a class="buy" href="{esc(e["url"])}" rel="sponsored noopener">{go_label(e)}{ARROW}</a></div>{sample}</article>')


def sale(e):
    when, name = _split_title(e["title"].replace("AIが比べた", "", 1).strip("、 "))
    when = re.sub(r"^(?:今日|明日|あす)\s*", "", when or "")  # 11/1 月：投稿した日の「あす」がHPに残って、11/1 に「あす10/28」と出ていた
    when = _wd(when, e["year"]) if when else _wd(e["day"], e["year"]) + "調べ"
    btn = f'<a class="buy" href="{esc(e["url"])}" rel="sponsored noopener">楽天で見る{ARROW}</a>'
    return (f'<article class="card cmp"><div class="d"><span class="when">{esc(when)}</span></div>'
            f'<div class="t">{phr(name)}</div><div class="ft2">{btn}</div></article>')


def a8card(e):
    note = f'<p class="why">{esc(e["note"])}</p>' if e.get("note") else ""
    btn = f'<a class="buy" href="{esc(e["url"])}" rel="sponsored noopener">申し込みページへ{ARROW}</a>'
    return (f'<article class="card cmp"><div class="d"><span class="when">予約・申し込み</span></div>'
            f'<div class="t">{phr(e["name"])}</div>{note}<div class="ft2">{btn}</div></article>')


def _season(now):
    """表紙の季節：時期（seasons.json）の季節で、色・春夏秋冬の印・見出しを切り替える。"""
    pe = period(now)
    sea = pe.get("season", "autumn")
    i = SEASON_I.get(sea, 2)
    year = now.year - (1 if now.month <= 2 and sea == "winter" else 0)
    return i, sea, f"{sea.upper()} {year}", f'{"春夏秋冬"[i]}のおでかけ'  # 表紙は季節の名前だけ（時期の名前「冬じたく」は商品の欄だけで使う。10/24 オーナー）


def _year_ring(cur):
    gs = []
    for i, (x, ch) in enumerate(zip((81, 107, 133, 159), "春夏秋冬")):
        cls = "yp" if i < cur else "yn" if i == cur else "yx"
        ring = f'<path class="ring" d="M{x} 3l11 11-11 11-11-11z"/>' if i == cur else ""
        gs.append(f'<g class="{cls}">{ring}<path class="dm" d="M{x} 8.5l5.5 5.5-5.5 5.5-5.5-5.5z"/>'
                  f'<text x="{x}" y="39">{ch}</text></g>')
    return ('<svg class="yr" width="240" height="44" viewBox="0 0 240 44" aria-hidden="true"><g class="ln"><path d="M46 14h18M176 14h18"/></g>'
            '<g class="dt"><circle cx="38" cy="14" r="1.3"/><circle cx="202" cy="14" r="1.3"/>'
            '<circle cx="29" cy="14" r="1" opacity=".7"/><circle cx="211" cy="14" r="1" opacity=".7"/>'
            '<circle cx="21" cy="14" r=".8" opacity=".45"/><circle cx="219" cy="14" r=".8" opacity=".45"/></g>'
            + "".join(gs) + "</svg>")


def _hot(prs):
    """今日のいち押し：いちばん新しい日の「AIが比べた」PRのうち、選んだ物のレビュー件数がいちばん多い1つ。"""
    best, key = None, None
    for e in prs:
        if e.get("cat") == "sale":
            continue
        rows = _rows(e) or []
        ch = next((r for r in rows if r.get("pick")), None)
        if not ch:
            continue
        m, d = (int(x) for x in e["day"].split("/"))
        k = (e.get("year", 0), m, d, ch["count"])
        if key is None or k > key:
            best, key = e, k
    return best


def all_spots(items, now):
    """HPのおでかけの欄に出す物。並び：きのう・きょう投稿した物 → HPだけのおすすめ → それより前に投稿した物"""
    posted = [e for e in items["odekake"] + items["shop"] if e.get("url")]
    seen_t = {re.sub(r"\W", "", e["title"])[:12] for e in posted}
    ps = _page_spots(now)
    extra = [e for e in ps if not any(k and k in re.sub(r"\W", "", e["title"]) for k in seen_t)]
    # 11/9 夜#155：投稿したカードが先に出ると、page-spots の「開く曜日（days）・opennote」が付かず、休館日も「行ける」に出ていた → 同じ催しなら移す
    for p in ps:
        if not (p.get("days") or p.get("opennote")):
            continue
        pk = re.sub(r"\W", "", p["title"])[:12]
        for e in posted:
            if pk and pk in re.sub(r"\W", "", e["title"]):
                if not e.get("days"):
                    e["days"] = p.get("days", "")
                if not e.get("opennote"):
                    e["opennote"] = p.get("opennote", "")

    def _age(e):
        m, d = (int(x) for x in e["day"].split("/"))
        return (now.date() - datetime(e.get("year", now.year), m, d).date()).days
    out, seen = [], set()
    # 関東だけ（10/26 オーナー「関東と関西は広すぎ。関東おでかけリスト」）
    # 同じ催しを2回出さない（10/25 オーナー「ごちゃごちゃして分かりにくい」：NAKED meets 二条城 が2枚、やきいもフェスが3枚）
    for e in [e for e in posted if _age(e) <= 1] + extra + [e for e in posted if _age(e) > 1]:
        if e.get("url") in _HOLD:
            continue
        reg = region(_pref(e))
        if reg != "関東":
            continue
        nm = e.get("name") or _split_title(e["title"].replace("AIが比べた", "", 1).strip("、 "))[1]
        n0 = re.sub(r"\W", "", nm or "").lower()
        u0 = re.sub(r"[?#].*$", "", str(e.get("url") or "")).rstrip("/")
        # 同じ名前、または同じ公式ページで名前の頭が同じ物（やきいもフェス TOKYO と TOKYO・OSAKA）。観光サイトの別の催しは名前の頭が違うので残る
        keys = {k for k in ((n0, reg), (u0, n0[:6], reg)) if k[0]}
        keys = {k for k in keys if k[0]}
        if keys & seen:
            continue
        seen |= keys
        out.append(e)
    return out


def spot_counts(now):
    """その時刻にHPのおでかけの欄に並ぶ数（関東・関西）。予約係が投稿の最後の1行に使う（楽天には確かめない）。"""
    items, _ = collect(now, light=True)
    out = {"関東": 0, "関西": 0, "週末関東": 0, "週末関西": 0}
    _NOW[:] = [now]
    for e in all_spots(items, now):
        r = region(_pref(e))
        if r in ("関東", "関西"):
            out[r] += 1
            if 'data-wk="1"' in spot(e):
                out["週末" + r] += 1
    return out


def spot_match(text, now):
    """文に名前が出てくるHPのおでかけ（無ければ None）。"""
    items, _ = collect(now, light=True)
    t = re.sub(r"\W", "", text).lower()
    for e in all_spots(items, now):
        nm = re.sub(r"\W", "", re.sub(r"（.*?）|\s(19|20)\d\d.*$", "", e.get("name") or "")).lower()  # 名前の後ろの年と（10/24開店）は文に無いことが多い
        if len(nm) >= 4 and nm in t:
            return e
    return None


def spot_region(text, now):
    """文に名前が出てくるHPのおでかけから地域を決める（「二条城」のように地名の入らない名前の時）。"""
    e = spot_match(text, now)
    return region(_pref(e)) if e else ""


def post_region(texts):
    """投稿の文から、関東の話か関西の話か（分からなければ空）。"""
    return region(_pref({"title": " ".join(texts), "bullets": []}))


def past_list(ended, now, n=5):
    """終わったおでかけ（関東・終わって30日以内）を新しい順に1行ずつ：日付｜名前｜場所。月の「終わったおでかけ」と同じ。"""
    rows, seen = [], set()
    for e in sorted(ended + page_spots_ended(now), key=lambda e: _dt(e.get("ends")) or now, reverse=True):
        d = _dt(e.get("ends"))
        if not d or d < now - timedelta(days=30) or region(_pref(e)) != "関東":
            continue
        nm = e.get("name") or _split_title(e["title"].replace("AIが比べた", "", 1).strip("、 "))[1]
        k = re.sub(r"\W", "", nm or "")[:10]
        if not k or k in seen:
            continue
        seen.add(k)
        place = e.get("place") if e.get("place") not in ("", "-") else _pref(e)
        rows.append(f'<li><span>{_md(d)}</span>{esc(nm)}｜{esc(place)}</li>')
    if not rows:
        return ""
    more = (f'<button class="pmo" type="button">もっと見る（{len(rows) - n}件）</button>') if len(rows) > n else ""
    return ('<ul class="past">' + "".join(r if i < n else r.replace("<li>", "<li hidden>", 1) for i, r in enumerate(rows)) + '</ul>' + more)


def render(items, ended, now, cfg):
    _NOW[:] = [now]
    p = cfg.get("page", {})
    sns = [("Instagram", "@usagichan_ai_si", "https://www.instagram.com/usagichan_ai_si/"),
           ("Threads", "@usagichan_ai_si", "https://www.threads.com/@usagichan_ai_si"),
           ("X", "@ai_usagichan", "https://x.com/ai_usagichan")]
    follow = "".join(f'<a href="{esc(u)}" rel="noopener">{esc(n)}<span>{esc(h)}</span></a>' for n, h, u in sns)
    if p.get("room_url"):
        follow += (f'<a class="co" data-en="RAKUTEN ROOM" href="{esc(p["room_url"])}" rel="noopener">楽天ROOM'
                   f'<span>うさぎが比べて選んだ物を、まとめて置いています</span></a>')
    # おでかけ掲載のご相談（10/26 オーナー「月のhpにはおでかけ先の依頼とかやってる、まねしよ」：月と同じくインスタのDMへ）
    follow += ('<a class="co" data-en="LISTING" href="https://ig.me/m/usagichan_ai_si" rel="noopener">おでかけ掲載'
               '<span>新しいお店や、毎年のイベント。<br>うさぎがご紹介します。ご相談はこちら</span></a>')
    spots = all_spots(items, now)
    deals, dk = [], set()
    for e in items["deal"]:
        if not e.get("url") or e["url"] in _HOLD:
            continue
        e["title"] = re.sub(r"(は)?あと\d+日[!！]?", "", e["title"]).strip("、 ")  # 日数はカードの印（あと◯日）が毎回数える。文の日数は古くなる
        k = re.sub(r"[0-9０-９/／~〜（）()：:｜|、・ 　]|まで|から|今日|明日|AIが比べた", "", e["title"])[:6]
        if k in dk:  # 同じお得を2回載せない（10/30「無印良品週間」が2件、あと9日とあと5日で食い違い）
            continue
        dk.add(k)
        deals.append(e)
    # しぼりこみは都県ごと（10/26 オーナー「関東と関西は広すぎ。月の見て、綺麗に分けてる」：月は府県ごと）
    tabs = '<button class="on" data-p="">すべて</button>' + "".join(
        f'<button data-p="{esc(x)}" style="--pc:{PREF_COLOR[x]}">{esc(x)}</button>' for x in KANTO_ORDER
        if any(_pref(e) == x for e in spots))  # 0件の都県はタブを出さない（月と同じ）
    cs = cats(now)
    goods = {k: [] for k, *_ in cs}
    hot = _hot(items["pr"])
    for e in items["pr"]:
        if e is hot:
            continue
        m = re.match(r"(?:AIが比べた)?\s*今日\s*(\d{1,2})/(\d{1,2})", e.get("title") or "")
        if e.get("cat") == "sale" and m and (int(m[1]), int(m[2])) < (now.month, now.day):
            continue  # 「今日10/24の20時から」のような、過ぎたセールは出さない
        goods.get(e.get("cat"), goods["life"]).append(sale(e) if e.get("cat") == "sale" else compare(e))
    for e in items.get("pick", []):
        if (e.get("count") or 0) < 1000 or float(e.get("avg") or 0) < 4.0:  # PRの決まり（レビュー1,000件以上・★4.0以上）
            continue
        goods.get(e.get("cat"), goods["life"]).append(pick(e))
    goods["book"] += [a8card(e) for e in items.get("a8", [])]
    blocks, nav = [], []

    def head(en, jp, lead):
        return (f'<div class="wk"><span class="en2">{en}</span><span class="jp2">{jp}</span></div>'
                + (f'<p class="lead">{lead}</p>' if lead else ""))

    if spots:  # 1. おでかけ：月のページと同じく「開催中」と「これから」に分ける（10/24 オーナー「これ真似したら？」）
        far = datetime(2100, 1, 1, tzinfo=JST)
        # 4つの欄（月と同じ）：開催中／これから／もうすぐ（これから開く施設）／できた（開いたばかりの施設）
        shops = [e for e in spots if e.get("kind") == "shop"]
        spots_ev = [e for e in spots if e.get("kind") != "shop"]

        def _open_day(e):
            if e.get("open"):
                try:
                    return datetime.fromisoformat(e["open"]).date()
                except ValueError:
                    pass
            m = re.search(r"(\d{1,2})/(\d{1,2})(?:（.）)?\s*(?:に)?開店", (e.get("name") or "") + e.get("title", ""))
            if not m:
                return None
            try:
                return datetime(now.year, int(m[1]), int(m[2]), tzinfo=JST).date()
            except ValueError:
                return None
        soon = [e for e in shops if _open_day(e) and _open_day(e) > now.date()]
        opened = sorted([e for e in shops if e not in soon], key=lambda e: _open_day(e) or now.date(), reverse=True)
        soon.sort(key=_open_day)
        now_on = sorted([e for e in spots_ev if not (_dt(e.get("start")) and _dt(e["start"]) > now)],
                        key=lambda e: _dt(e.get("ends")) or far)
        coming = sorted([e for e in spots_ev if _dt(e.get("start")) and _dt(e["start"]) > now], key=lambda e: _dt(e["start"]))

        def cardlist(es, label):
            # 見せる5件は「選んだ地域の中で」数える（10/25 オーナー「枠数おかしくない？」：全体の5件で切っていたので関東が1件しか出なかった）
            cs_ = [spot(e) for e in es]
            more = (f'<button class="gm" type="button" data-l="もっと見る（あと">もっと見る（あと{len(cs_) - SHOW_GO}件）</button>'
                    if len(cs_) > SHOW_GO else "")
            return "".join(cs_) + more

        n_free = sum(1 for e in now_on if _free(e))
        sat, sun = _weekend(now)
        nav.append(f'<button type="button" class="on" data-v="odekake">おでかけ<small>{len(spots)}</small></button>')
        panes = [("now", "NOW ON", "開催中", now_on), ("up", "COMING UP", "これから", coming),
                 ("soon", "SOON", "もうすぐ", soon), ("new", "NEW OPEN", "できた", opened)]
        first = next((k for k, _, _, es in panes if es), "now")
        # 10/26 オーナー「押したら中身が切り替わる仕組みを、見た目だけでなく押して動くところまで同じに」（月の .tabs と同じ動き）
        tabs2 = '<nav class="otab" aria-label="おでかけ">' + "".join(
            f'<button type="button" data-t="{k}"{" class=on" if k == first else ""}{"" if es else " disabled"}><i>{en}</i>{jp}<small>{len(es)}件</small></button>'
            for k, en, jp, es in panes) + '</nav>'
        blocks.append(f'<nav class="flt" data-v="odekake" aria-label="しぼりこみ">{tabs}</nav>'
                      # 「今週末」は外した（10/26 オーナー「今週末いらない。休みが平日の人もいる」）。件数は月と同じ「開催中｜無料で楽しめる」
                      # 「無料だけ」ボタンは外した（10/30 オーナー「無料だけいらない、変にスペースとる」）。月のリストにも無い。戻さないこと
                      f'<p class="cnt" data-v="odekake"><span>開催中<b id="n-now">{len(now_on)}</b>件</span><span>無料で楽しめる<b id="n-free">{n_free}</b>件</span></p>'
                      f'<section class="blk" id="odekake" data-v="odekake">{tabs2}'
                      + "".join(f'<div class="pane" data-t="{k}"{"" if k == first else " hidden"}>{cardlist(es, jp)}<p class="none">この都県のおでかけは、これから増やしていきます</p></div>'
                                for k, en, jp, es in panes)
                      + '</section>')
        # 10/31 月と同じ：終わったおでかけは別の箱（ARCHIVE）。注意書きもその下（オーナー「サイト作り自体は同じで良い」）
        blocks.append(f'<section class="blk arch" id="archive" data-v="odekake">{head("ARCHIVE", "終わったおでかけ", "")}'
                      + past_list(ended, now, n=4)
                      + '<p class="tip">出かける前に、必ず公式ページで<br>最新の情報を確かめてください。</p></section>')
    if hot:  # 2. 今日のいち押し（おでかけの下。10/24 オーナー「おでかけの後でいい」）
        hot["hot"] = True
        blocks.append(f'<section class="blk hotb" id="hot" data-v="odekake">{head("TODAY&#39;S PICK", "今日のうさぎのいち押し", "その日にうさぎが比べて選んだ物のうち、使っている人がいちばん多い1つ。リンクは広告です")}'
                      + compare(hot) + '</section>')
    deal_cards = [spot(e) for e in deals] + goods.pop("sale")
    if deal_cards:  # 3. 今だけのお得（期間のあるお得と楽天のセールを1つに）
        nav.append(f'<button type="button" data-v="deal">お得<small>{len(deal_cards)}</small></button>')
        blocks.append(f'<section class="blk" id="deal" data-v="deal">{head("DEAL", "今だけのお得", "期間のあるお得とセール。終わる日を先に書いています。楽天のリンクは広告です")}'
                      + "".join(deal_cards) + '</section>')
    trip = goods.pop("stay") + goods.pop("book")
    if trip:  # 4. 宿と予約
        nav.append(f'<button type="button" data-v="trip">宿<small>{len(trip)}</small></button>')
        blocks.append(f'<section class="blk" id="trip" data-v="trip">{head("STAY", "宿と予約", "宿は口コミ1,000件以上・評価4.5以上だけ。リンクは広告です")}'
                      + "".join(trip[:SHOW_GOODS])
                      + (f'<details class="fold more"><summary>ほかに{len(trip) - SHOW_GOODS}件を見る</summary>{"".join(trip[SHOW_GOODS:])}</details>'
                         if len(trip) > SHOW_GOODS else "") + '</section>')
    shop = [(k, n, goods[k]) for k, _, n, _, _ in cs if k in goods and goods[k]]
    if shop:  # 5. 買い物（タブで項目を切り替え。項目が増えても欄は1つ）
        n_all = sum(len(g) for _, _, g in shop)
        nav.append(f'<button type="button" data-v="shop">買い物<small>{n_all}</small></button>')
        stabs = '<button class="on" data-c="">すべて</button>' + "".join(
            f'<button data-c="{k}">{esc(n)}<i>{len(g)}</i></button>' for k, n, g in shop)
        cards, i = [], 0
        for k, _, g in shop:
            for c in g:
                cards.append(c.replace('<article class="card', f'<article data-c="{k}" class="card sh{" ex" if i >= SHOW_SHOP else ""}', 1))
                i += 1
        moreb = f'<button class="mo" type="button">もっと見る（{n_all - SHOW_SHOP}件）</button>' if n_all > SHOW_SHOP else ""
        blocks.append(f'<section class="blk" id="shop" data-v="shop">{head("SHOP", "うさぎが比べた買い物", "3つ以上を数字で比べて選んだ物。<br>レビュー1,000件以上・評価4.0以上だけ。リンクは広告です")}'
                      f'<nav class="stab" aria-label="項目">{stabs}</nav>{"".join(cards)}{moreb}</section>')
    cur, sea, sea_en, sea_jp = _season(now)
    return TEMPLATE.format(
        nav="".join(nav), blocks=re.sub("[\U0001F000-\U0001FAFF\uFE0F]", "", "".join(blocks)), follow=follow, ring=_year_ring(cur), sea_en=sea_en, sea_jp=sea_jp, sea=sea, show_go=SHOW_GO,
        n_pr=sum(len(v) for v in goods.values()),
        pr_note=("このページには楽天アフィリエイトとAmazonアソシエイトの広告（PR）があります。<br>"
                 "Amazonのアソシエイトとして、当サイトは適格販売により収入を得ています。"
                 if any(e.get("amazon") for e in items["pr"] + items.get("pick", [])) else
                 "このページにはアフィリエイト広告（PR）があります" if items.get("a8") else
                 "このページには楽天アフィリエイトの広告（PR）があります"),
        updated=f"{now.month}/{now.day}（{WEEK[now.weekday()]}）{now:%H:%M}", salebox=sale_box())


TEMPLATE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="google-site-verification" content="19Vt8Ili5pokwJHyAI3SwQ2UKI-eqeLVJSHS3PVUO54">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>関東おでかけリスト｜うさぎ│LIFE NOTES</title>
<meta name="description" content="関東で、今日から・新しく・無料で行ける場所の公式ページまとめと、うさぎが数字で比べた物を毎日。">
<meta property="og:title" content="関東おでかけリスト｜うさぎ│LIFE NOTES">
<meta property="og:description" content="おでかけ先と宿と、うさぎが比べて選んだ物を毎日更新。">
<meta property="og:image" content="https://usagi-life-notes.pages.dev/og-v10.png">
<meta property="og:url" content="https://usagi-life-notes.pages.dev/">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#FFFFFF">
<link rel="icon" href="logo.png"><link rel="apple-touch-icon" href="logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Jost:wght@300;400;500&display=swap">
<style>
/* 紙の手帳のような生成りの地に、白い紙を重ねる。色はロゴの茶と、地域ごとの淡い色だけ */
:root{{
  color-scheme:light;
  --bg:#FFFFFF; --paper:#FFFFFF; --ink:#2B2622; --sub:#6B6058; --mute:#8C7B6E; --line:#DDDDDD; --line2:#CECECE;
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
.head img{{width:64px;height:64px;display:block;margin:0 auto;border-radius:50%;background:#fff}}
.en{{font:300 10px/1 var(--en);letter-spacing:.5em;color:var(--brown);margin:16px 0 0;padding-left:.5em}}
.ttl:not(:where(.tn *,.tnbtn *)){{font:600 26px/1.3 var(--min);letter-spacing:.18em;font-feature-settings:"palt";color:#231E1B;margin:16px 0 10px;padding-left:.18em}}
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
.seg button{{font:700 12.5px/1 var(--go);letter-spacing:.12em;color:var(--mute);background:#fff;border:1px solid #CFCFCF;padding:9px 18px;cursor:pointer;margin-left:-1px}}
.seg button.on{{background:var(--ink);border-color:var(--ink);color:#fff}}
.flt{{display:flex;flex-wrap:wrap;justify-content:center;gap:0 11px;border-top:1px solid #D3D3D3;border-bottom:1px solid #D3D3D3;padding:10px 0;margin:12px 0 14px}}
.flt button{{font:700 13px/1 var(--go);letter-spacing:.02em;color:var(--pc,var(--mute));background:none;border:0;border-bottom:1px solid transparent;padding:11px 2px 9px;cursor:pointer}}
.flt button.on{{color:var(--pc,var(--ink));border-bottom-color:var(--pc,var(--ink))}}
.flt button.fr{{color:#5E8C5A;border:1px solid #CFE0CC;border-radius:99px;padding:8px 12px;margin:3px 0 0}}
.flt button.fr.on{{background:#5E8C5A;color:#fff;border-color:#5E8C5A}}
.cnt{{display:flex;justify-content:center;margin:0 0 26px}}
.cnt span{{font-size:12px;color:var(--sub);padding:0 10px;letter-spacing:.04em}}
.cnt span+span{{border-left:1px solid var(--line2)}}
.cnt b{{font:600 17px/1 var(--min);color:var(--ink);margin:0 3px}}
.nt{{font-size:12px;line-height:1.6;color:var(--sub);margin:2px 0 0}}
.stab{{display:flex;gap:6px;overflow-x:auto;margin:4px -2px 14px;padding:2px;scrollbar-width:none}} .stab::-webkit-scrollbar{{display:none}}
.stab button{{flex:none;font:700 12.5px/1 var(--go);letter-spacing:.06em;color:var(--mute);background:#fff;border:1px solid #CFCFCF;border-radius:99px;padding:9px 14px;cursor:pointer}}
.stab button i{{font:400 11px/1 var(--en);font-style:normal;margin-left:5px;opacity:.7}}
.stab button.on{{background:var(--ink);border-color:var(--ink);color:#fff}}
.js .card.sh.ex{{display:none}} .js #shop.open .card.sh.ex{{display:block}} .card.sh[hidden]{{display:none!important}}
.mo:not(:where(.tn *,.tnbtn *,#utheme *)){{display:block;width:100%;font:700 13px/1 var(--go);letter-spacing:.08em;color:var(--ink);background:#fff;border:1px solid var(--line2);padding:14px;cursor:pointer}}
#shop.open .mo,#shop.tab .mo{{display:none}}
.pr-note{{font-size:11px;line-height:1.8;color:var(--mute);text-align:center;margin:0 0 20px}}
.cats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin:24px 0 10px}}
.cats a{{display:flex;align-items:center;justify-content:space-between;gap:8px;background:#fff;border:1px solid var(--line);border-left:3px solid var(--acc);padding:11px 14px 12px;font:700 13.5px/1.3 var(--go);letter-spacing:.06em;transition:background .2s}}
.cats a:hover{{background:color-mix(in srgb,var(--acc) 5%,#fff)}}
.cats a span{{display:flex;flex-direction:column;gap:5px}}
.cats a i{{font:400 9px/1 var(--en);font-style:normal;letter-spacing:.28em;color:var(--acc)}}
.cats a b{{font:400 18px/1 var(--en);color:var(--acc)}}
.cats a.g{{border-left-color:#5D7FA3}} .cats a.g i,.cats a.g b{{color:#5D7FA3}}
.go .seg{{margin:4px 0 0}}
.more{{margin:4px 0 12px}} .more summary{{display:block;width:max-content;margin:0 auto 12px;padding:10px 4px 2px}} .more[hidden]{{display:none}}

/* 章 */
.blk{{background:var(--paper);border:1px solid #E4E4E4;border-top:3px solid var(--acc);padding:22px 14px 12px;margin-bottom:18px;scroll-margin-top:12px}}
.blk.hid{{display:none}}
.wk{{display:flex;flex-direction:column;gap:6px;margin:0 0 6px}}
.en2{{font:400 10px/1 var(--en);letter-spacing:.36em;color:var(--acc)}}
.jp2{{font:600 18px/1.4 var(--min);letter-spacing:.08em}}
.lead{{font-size:11.5px;color:var(--mute);margin:0 0 14px}}
.none{{display:none;font-size:12px;color:var(--mute);text-align:center;margin:4px 0 12px}}
.blk.empty .none{{display:block}}
.gm{{display:none}} .js .gm{{display:block;width:max-content;margin:0 auto 12px;padding:10px 4px 2px;background:none;border:0;border-bottom:1px solid #C8C8C8;font-size:11.5px;letter-spacing:.12em;color:#5B514A;cursor:pointer}} .js .gm[hidden]{{display:none}}

/* おでかけのカード */
.card{{display:block;position:relative;background:#fff;border:1px solid var(--line);margin-bottom:12px;padding:12px 42px 38px 14px;box-shadow:inset 3px 0 0 var(--pc,var(--brown));transition:background .2s}}
a.card:hover{{background:color-mix(in srgb,var(--pc,var(--brown)) 4%,#fff)}}
.card[hidden]{{display:none}}
.d:not(:where(.tn *,.tnbtn *)){{display:flex;flex-wrap:wrap;align-items:center;gap:2px 0;font-size:12px;line-height:1.5;letter-spacing:.02em;color:#8A6E5C}}
.pl{{font-weight:700;letter-spacing:.12em;color:var(--pc);margin-right:8px}}
.pl:before{{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--pc);margin-right:5px;vertical-align:1px}}
.pl:after{{content:"";display:inline-block;width:1px;height:9px;background:var(--line2);margin-left:8px;vertical-align:-1px}}
.tg{{font-size:11px;letter-spacing:.12em;color:var(--free);margin-left:8px}}
.t:not(:where(.tn *,.tnbtn *)){{font:700 15px/1.4 var(--go);letter-spacing:0;margin:3px 0 2px}}
.nwp{{display:inline-block}} .nwp.sp{{margin-right:.3em}}
.m:not(:where(.tn *,.tnbtn *)){{list-style:none;margin:6px 0 0;padding:0;display:grid;gap:2px}}
.m:not(:where(.tn *,.tnbtn *)) li{{font-size:12px;line-height:1.7;color:var(--sub);padding-left:11px;position:relative}}
.m:not(:where(.tn *,.tnbtn *)) li:before{{content:"";position:absolute;left:0;top:.8em;width:4px;height:1px;background:var(--line2)}}
.card .go{{color:inherit;text-decoration:none}} .card .go:after{{content:"";position:absolute;inset:0;z-index:1}}
.card.it:hover{{background:color-mix(in srgb,var(--pc,var(--brown)) 4%,#fff)}} .card.it:hover .arw{{transform:translate(3px,-50%)}}
a.mp{{z-index:2;text-decoration:none;padding-top:10px}}
.mp{{position:absolute;left:14px;bottom:12px;display:inline-flex;align-items:center;gap:3px;font-size:11.5px;font-weight:500;letter-spacing:.14em;color:#5B514A;border-bottom:1px solid #C8C8C8;padding-bottom:1px}}
.out{{width:9px;height:9px}}
.arw{{position:absolute;right:14px;top:50%;width:22px;height:11px;transform:translateY(-50%);color:#A99C90;transition:transform .2s}}
a.card:hover .arw{{transform:translate(3px,-50%)}}

/* AIが比べた */
.cmp{{padding:14px 16px 16px;box-shadow:none}}
.prm{{font:500 9.5px/1 var(--en);letter-spacing:.14em;color:var(--pr);border:1px solid var(--pr);padding:3px 6px 2px;margin-right:8px}}
.cmp .t{{margin-top:8px}}
.tbl{{margin:10px 0 0;border-top:1px solid var(--line)}}
.row:not(:where(.tn *,.tnbtn *)){{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;padding:10px 0 9px;border-bottom:1px solid var(--line)}}
.nm{{font-size:13px;font-weight:500;min-width:0}}
.nt{{display:block;font-size:11px;font-weight:400;color:var(--mute)}}
.nu{{display:flex;gap:12px;align-items:baseline;white-space:nowrap}}
.av{{font:400 13px/1 var(--en);letter-spacing:.02em;color:var(--brown2)}}
.ct{{font:300 12px/1 var(--en);color:var(--mute);min-width:4.4em;text-align:right;font-variant-numeric:tabular-nums}}
.br{{grid-column:1/-1;height:2px;background:#EDEDED}}
.br i{{display:block;height:100%;background:#CDCDCD}}
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
.cho{{margin:10px 0 0;padding:10px 12px;background:#F6F6F6;display:flex;align-items:center;gap:12px}}
.cho .tx{{display:grid;gap:2px;min-width:0}}
.cho .ph{{flex:0 0 104px;width:104px;height:104px;object-fit:contain;background:#fff;border:1px solid var(--line)}}
.cho .meta{{margin:2px 0 0}}
.cho .lb{{font:400 10px/1.4 var(--en);letter-spacing:.2em;color:var(--brown)}}
.cho b{{font-size:14.5px;line-height:1.5}}
.cho .sc{{font:400 12px/1.4 var(--en);color:var(--sub)}} .cho .sc i{{font-style:normal;color:var(--line2);margin:0 6px}}
.nt{{grid-column:1/-1;font-size:11.5px;color:var(--sub)}}
.cmp .why.but,.pk2 .why.but{{margin-top:4px}}
.cmp .why,.pk2 .why{{margin:10px 0 0;padding:0;border:0;font-size:12.5px;line-height:1.8;color:var(--sub)}}
.hotb{{border-top-color:var(--pr)}}
.hot{{border:1.5px solid var(--pr);background:linear-gradient(180deg,#F9F9F9,#fff 60%)}}
.hot .t{{font-size:17px}}
.hot .cho{{background:#F3F3F3}}
.hot .buy{{background:var(--pr)}}
.fold{{margin:10px 0 0}}
.fold summary{{cursor:pointer;list-style:none;font-size:11.5px;letter-spacing:.12em;color:#5B514A;display:inline-block;border-bottom:1px solid #C8C8C8}}
.fold summary::-webkit-details-marker{{display:none}}
.fold summary:after{{content:" ＋";color:var(--brown)}} .fold[open] summary:after{{content:" −"}}
.ft2{{justify-content:flex-end}}
.meta{{display:flex;flex-wrap:wrap;gap:4px 14px;align-items:baseline;margin:4px 0 0}}
.meta .ct{{min-width:0;text-align:left}}
.yen{{font:400 12.5px/1 var(--en);color:var(--ink);letter-spacing:.02em}}
.tw .yen,.cmp>.yen{{display:block;margin:8px 0 0;font-size:14px;font-weight:600}}
.pk2 .m{{margin-top:10px}}
.smp{{font-size:10px;color:var(--mute);text-align:right;margin:8px 0 0}}

.tip,.ft,.lead{{text-wrap:balance}}
.past{{list-style:none;margin:6px 0 4px;padding:0;font-size:12px;line-height:2;color:#5B514A}}
.past{{border-top:1px solid var(--line);margin:12px 0 0;padding:12px 2px 0}}
.past .ph{{font:600 13px/1 var(--min);letter-spacing:.12em;color:var(--sub);margin:0 0 8px;text-align:center}}
.past ul{{list-style:none;margin:0;padding:0}}
.past li{{font-size:11.5px;line-height:1.7;color:var(--mute);padding:3px 0;border-bottom:1px dotted var(--line)}}
.past li span{{margin-right:6px}}
.tip{{border-top:1px solid var(--line);margin:10px 0 0;padding:12px 2px 2px;font-size:11.5px;line-height:1.8;color:var(--sub);text-align:center}}

/* FOLLOW */
.sns{{margin-top:36px;text-align:center}}
.sns h2{{display:flex;align-items:center;justify-content:center;gap:14px;font:400 10.5px/1 var(--en);letter-spacing:.42em;color:var(--mute);margin:0 0 16px}}
.sns h2:before,.sns h2:after{{content:"";width:40px;height:1px;background:var(--line2)}}
.sns a{{display:block;border:1px solid var(--ink);padding:14px;margin:0 0 10px;font:500 13px/1.5 var(--go);letter-spacing:.1em}}
.sns a span{{font:400 12px var(--en);color:var(--mute);margin-left:8px;letter-spacing:.06em}}
.sns a.co{{background:#5B5450;border-color:#5B5450;color:#fff}}
.sns a.co span{{display:block;margin:4px 0 0;color:#E1E1E1;font-family:var(--go)}}
.ft{{text-align:center;font-size:10.5px;letter-spacing:.06em;color:var(--mute);margin-top:28px;line-height:1.9}}
#totop{{position:fixed;right:max(16px,env(safe-area-inset-right,0px));bottom:calc(20px + env(safe-area-inset-bottom,0px));width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.94);border:1px solid #C7C7C7;box-shadow:0 2px 8px rgba(60,45,35,.12);display:flex;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity .3s;cursor:pointer;padding:0}}
#totop.on{{opacity:1;pointer-events:auto}}
/* 10/26 オーナー「月のhp配色、綺麗な配置なってるから真似して」：月の並べ方と色に合わせる */
.cats{{display:flex;justify-content:center;gap:0 22px;margin:22px 0 0;padding:12px 0;border-top:1px solid #D3D3D3;border-bottom:1px solid #D3D3D3}}
.cats button{{background:none;border:0;border-bottom:2px solid transparent;cursor:pointer;font:500 13.5px/1 var(--go);letter-spacing:.08em;color:var(--mute);padding:9px 2px 8px}}
.cats button small{{font:400 11px/1 var(--en);margin-left:4px;color:var(--mute)}}
.cats button.on{{color:var(--ink);font-weight:700;border-bottom-color:var(--ink)}}
.wrap > [data-v][hidden]{{display:none!important}}
.flt{{margin:0;border:0;padding:0}} .cats{{margin-bottom:18px}}
.cnt{{margin:14px 0 22px}}
.blk,.hotb{{border:1px solid #E4E4E4;border-top:2px solid var(--ink)}}
.otab{{display:flex;border-bottom:1px solid var(--line);margin:-6px -2px 16px}}
.otab button{{flex:1;background:none;border:0;border-bottom:3px solid transparent;margin-bottom:-1px;padding:6px 0 12px;cursor:pointer;color:var(--mute);font:600 15px/1.3 var(--min);letter-spacing:.1em}}
.otab button i{{display:block;font:400 9.5px/1 var(--en);font-style:normal;letter-spacing:.3em;margin-bottom:7px}}
.otab button small{{display:block;font:400 11px/1 var(--go);letter-spacing:.04em;margin-top:7px}}
.otab button.on{{color:var(--ink);border-bottom-color:var(--ink)}}
.otab button[disabled]{{opacity:.35;cursor:default}}
.otab button{{font-size:14px;letter-spacing:.04em;min-width:0}} .otab button i{{letter-spacing:.16em;font-size:8.5px}}
.pane[hidden]{{display:none}} .pane.empty .none{{display:block}}
.card.it{{padding:13px 70px 14px 14px}}
.card.it .arw{{top:50%;transform:translateY(-50%)}} .card.it:hover .arw{{transform:translate(3px,-50%)}}
/* 地図と公式ページの押し間違いをなくす（10/26 オーナー「地図とリンクを押し間違える、クレームが来る前に」、月の直しと同じ）：
   地図は名前の下の左に1行で置き、その行は押しても公式ページが開かない。矢印は右の真ん中 */
.card.it .mpr{{position:relative;z-index:2;margin:12px -70px -14px -14px;padding:0 70px 14px 14px;background:transparent}}
.card.it .mp{{position:static;padding:8px 10px 6px 0;border-bottom:0;text-decoration:underline;text-underline-offset:4px;text-decoration-color:#C8C8C8}}
.chips:not(:where(.tn *,.tnbtn *)){{display:flex;justify-content:center;gap:8px;margin:12px 0 0}}
.chips .fr{{font:700 12.5px/1 var(--go);letter-spacing:.04em;color:var(--sub);background:#fff;border:1px solid #CFCFCF;border-radius:99px;padding:9px 14px;cursor:pointer}}
.chips .fr[data-k=free]{{color:#5E8C5A;border-color:#CFE0CC}}
.chips .fr.on{{background:var(--ink);border-color:var(--ink);color:#fff}} .chips .fr[data-k=free].on{{background:#5E8C5A;border-color:#5E8C5A}}
.lf{{font-size:11px;font-weight:700;letter-spacing:.04em;color:var(--pr);margin-left:8px}}
.cats{{position:sticky;top:0;z-index:20;background:var(--bg);margin-left:-16px;margin-right:-16px;padding-left:16px;padding-right:16px}}
.blk{{scroll-margin-top:62px}}
.buy{{padding:11px 16px 11px 18px;font-size:12.5px}}
.js .gm{{font-size:13px;color:var(--ink);border-bottom-color:var(--ink);letter-spacing:.06em}}
#odekake .tip{{margin-top:6px}}
.tw{{display:flex;align-items:center;gap:12px}} .tw .t{{margin:0}}
.tw .ph{{flex:0 0 104px;width:104px;height:104px;object-fit:contain;background:#fff;border:1px solid var(--line)}}
/* 黒い四角のボタンは重く見える（月で10/26 オーナー「重圧感」）→ 白に細い線 */
.buy{{background:#fff;color:var(--ink);border:1px solid var(--ink)}} .buy .arw{{color:var(--ink)}}
.hot{{border:1px solid #E6CDBE;background:#fff}} .hot .cho{{background:#F6F6F6}}
.hot .buy{{background:#fff;color:var(--pr);border-color:var(--pr)}} .hot .buy .arw{{color:var(--pr)}}
.sns{{margin-top:40px}}
.sns a:not(.co){{display:inline-block;border:0;border-bottom:1px solid var(--ink);padding:4px 0;margin:0 12px 26px;font-size:13px;letter-spacing:.1em}}
.sns a:not(.co) span{{display:none}}
.sns a.co{{display:block;position:relative;background:#fff;border:1px solid #D8D8D8;margin:0 0 10px;color:var(--ink);text-align:left;padding:18px 44px 18px 18px;font:600 16px/1.5 var(--min);letter-spacing:.08em}}
.sns a.co:before{{content:attr(data-en);display:block;font:500 9.5px/1 var(--en);letter-spacing:.32em;color:#9C8775;margin-bottom:8px}}
.sns a.co:after{{content:"→";position:absolute;right:18px;top:50%;transform:translateY(-50%);font-family:var(--en);color:#9C8775;font-size:16px}}
.sns a.co span{{color:var(--mute);font:400 11.5px/1.6 var(--go);letter-spacing:.04em;margin-top:6px}}
/* 10/31 月とそろえる：ARCHIVE の箱・いち押しの色・終わったの行 */
.arch .past{{list-style:none;margin:4px 0 0;padding:0;border:0}}
.arch .past li{{font-size:12.5px;line-height:1.9;color:#3A302A;padding:2px 0 2px calc(12px + 1em);text-indent:-1em;border:0}}
.ft{{font-size:10px;letter-spacing:.04em;text-wrap:balance}}
.arch .past li span{{margin-right:4px}}
.arch .pmo{{display:block;margin:10px auto 0;background:none;border:0;border-bottom:1px solid var(--ink);padding:4px 2px;font:500 13px/1 var(--go);letter-spacing:.06em;color:var(--ink);cursor:pointer}}
.arch .tip{{margin-top:18px}}
.hot{{border:1px solid #D8D8D8}} .hot .cho{{background:#F7F7F7}}
.hot .buy{{color:var(--ink);border-color:var(--ink)}} .hot .buy .arw{{color:var(--ink)}}
/* 10/31 近くの宿（月と同じ形） */
.yk[hidden],.ykl[hidden]{{display:none}}
.yk{{display:flex;justify-content:flex-end;margin:-4px 2px 12px;font-size:11.5px;letter-spacing:.04em}}
.yk a{{color:#8C6A55;text-decoration:none;border:1px solid #D9C7B8;background:#fff;border-radius:99px;padding:6px 12px}}
.yk a:before{{content:"";display:inline-block;width:9px;height:9px;margin-right:5px;vertical-align:-1px;background:currentColor;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Cpath d='M1 9V4l4-3 4 3v5H6V6H4v3z'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Cpath d='M1 9V4l4-3 4 3v5H6V6H4v3z'/%3E%3C/svg%3E") center/contain no-repeat}}
.yk a.op{{background:#F2F2F2}}
.ykl{{letter-spacing:0;list-style:none;margin:-4px 2px 14px;padding:4px 14px;background:#fff;border:1px solid #DDDDDD;border-radius:10px;font-size:12px}}
.ykl li{{border-top:1px solid #EAEAEA}} .ykl li:first-child{{border-top:0}}
.ykl a{{display:flex;justify-content:space-between;gap:10px;padding:10px 0;color:#3A302A;text-decoration:none}}
.ykl .nm{{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}} .ykl .mt{{color:#8C7B6E;white-space:nowrap;font-size:11px}}
.ykl .src{{font-size:10px;color:#A89A8E;padding:6px 0 2px;text-align:right}}
.sbox{{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;max-width:420px;margin:0 auto 20px;background:#fff;border:1px solid #CECECE;border-radius:14px;padding:12px 14px 10px}}.sb-x{{flex:1;min-width:0}}.sb-t{{font:600 15px/1.4 var(--min);letter-spacing:.06em;margin:0;color:#231E1B}}.sb-w{{font-size:12px;font-weight:700;color:#BF0000;margin:2px 0 0}}.sb-go{{flex:none;background:#BF0000;color:#fff;text-decoration:none;font-weight:700;font-size:13px;letter-spacing:.06em;padding:10px 14px;border-radius:99px}}.sb-go span{{margin-left:6px}}.sb-s{{flex-basis:100%;font-size:11px;line-height:1.6;color:#857A70;margin:2px 0 0}}.sb-s span{{color:#A89A8E}}.tnx{{display:block;margin:18px auto 6px;max-width:420px;text-align:center;text-decoration:none;color:#2B2622;background:#fff;border:1px solid #CECECE;border-radius:14px;padding:14px 16px 13px}}.tnx small{{display:block;font-family:"Zen Kaku Gothic New",sans-serif;font-size:10.5px;font-weight:700;letter-spacing:.2em;color:#9C8775;margin-bottom:4px}}.tnx b{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;letter-spacing:.08em}}.tnx b span{{font-family:Jost;margin-left:8px;color:#9C8775}}.tnx i{{display:block;font-style:normal;font-family:"Zen Kaku Gothic New",sans-serif;font-size:12px;color:#857A70;margin-top:4px}}html body a.tnx.buy{{display:block;background:#fff;color:#2B2622;border:1px solid #CECECE;font:inherit;letter-spacing:normal;padding:14px 16px 13px;gap:0}}.ilk{{display:block;width:max-content;max-width:100%;margin:4px auto 18px;color:#231E1B;text-decoration:none;font:600 14px/1.5 var(--min);letter-spacing:.08em;border-bottom:1px solid #231E1B;padding-bottom:3px}}.ilk span{{font-family:Jost;margin-left:8px;color:#9C8775}}
</style><script src="/assets/night.js?v=14"></script><script src="/assets/menu.js?v=41" defer></script></head>
<body class="s-{sea}"><div class="wrap">
<header class="head">
<span class="blob b1"></span><span class="blob b2"></span><span class="blob b3"></span><span class="blob b4"></span>
<img src="logo-s.png" alt="うさぎ│LIFE NOTES" width="64" height="64">
<div class="en">USAGI LIFE NOTES</div>
<h1 class="ttl">関東おでかけリスト</h1>
<p class="sub">関東の今日から・新しく・無料で行ける場所と、<br>うさぎが数字で比べて選んだ物を、毎日のせています</p>
<div class="sea"><span>{sea_en}</span><b>{sea_jp}</b></div>
{ring}
</header>
{salebox}
<a class="ilk" href="illumination">関東イルミネーション 2026 日程一覧<span>→</span></a>
<a class="ilk" href="ima">いまから行けるおでかけ（近い順）<span>→</span></a>
<nav class="cats" id="cats" aria-label="項目">{nav}</nav>
{blocks}
<p class="pr-note">{pr_note}<br>買う前に、楽天のページで最新の情報を確かめてください。</p>
<div class="sns"><h2>FOLLOW</h2>{follow}</div>
<p class="ft">うさぎ│LIFE NOTES│過去のおでかけも、このページに残していきます</p><a class="tnx buy" href="nesage" data-k="下の入口｜買い時"><small>関連ページ</small><b>いまが買い時の日用品<span>→</span></b><i>楽天の毎日の物を毎日記録</i></a><a class="tnx buy" href="furusato" data-k="下の入口｜ふるさと納税"><small>関連ページ</small><b>ふるさと納税を比べた<span>→</span></b><i>寄付1万円あたりの量で・12/31まで</i></a><a class="tnx" href="tanka" data-k="下の入口｜1個あたり"><small>関連ページ</small><b>1個あたりで比べた<span>→</span></b><i>楽天の水・お米などを1Lあたり・1kgあたりで</i></a><a class="tnx" href="kaimawari" data-k="下の入口｜買いまわり"><small>関連ページ</small><b>買いまわりの1,000円ぽっきり<span>→</span></b><i>楽天お買い物マラソンの時に</i></a>
</div>
<button id="totop" aria-label="上にもどる"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="#4A403A" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 13V3M3.5 7.5 8 3l4.5 4.5"/></svg></button>
<script>
/* 10/31 終わった日を過ぎたカードは、朝の作り直しを待たずに出さない（夜中〜朝のあいだ用） */
(function(){{var t=new Date(Date.now()+9*36e5).toISOString().slice(0,10);document.querySelectorAll(".card.it[data-e]").forEach(function(c){{if(c.getAttribute("data-e")<t)c.remove();}});}})();
(function(){{
var d=document.documentElement;d.classList.add("js");
var pref=(location.search.match(/[?&]pref=([^&]+)/)||[])[1]||"",free="0",wk="0";try{{pref=decodeURIComponent(pref);}}catch(e){{pref="";}}try{{localStorage.removeItem("pref");}}catch(e){{}}
function okc(c){{
  if(pref&&c.dataset.pref&&c.dataset.pref!==pref)return false;
  if(free==="1"&&c.dataset.free!=="1")return false;
  if(wk==="1"&&c.dataset.wk!=="1")return false;
  return true;
}}
function apply(){{
  var nw=0,nf=0;
  document.querySelectorAll("#odekake .card.it").forEach(function(c){{
    if(pref&&c.dataset.pref&&c.dataset.pref!==pref)return;
    if(c.dataset.wk==="1"&&(free!=="1"||c.dataset.free==="1"))nw++;
    if(c.closest('.pane').dataset.t==="now"&&c.dataset.free==="1"&&(wk!=="1"||c.dataset.wk==="1"))nf++;}});
  var a=document.getElementById("n-wk"),b2=document.getElementById("n-free");if(a)a.textContent=nw;if(b2)b2.textContent=nf;
  document.querySelectorAll("#odekake .pane").forEach(function(b){{
    var k=0,op=b.classList.contains("open");
    b.querySelectorAll(".card.it").forEach(function(c){{var ok=okc(c);if(ok)k++;c.hidden=!ok||(!op&&k>{show_go});}});
    b.classList.toggle("empty",!k);
    var tbb=document.querySelector('.otab button[data-t="'+b.dataset.t+'"]');if(tbb){{tbb.querySelector("small").textContent=k+"件";tbb.disabled=!k;}}
    if(b.dataset.t==="now"){{var nn=document.getElementById("n-now");if(nn)nn.textContent=k;}}
    var m=b.querySelector(".gm");if(m){{m.textContent=m.dataset.l+(k-{show_go})+"件）";m.hidden=op||k<={show_go};}}
  }});
}}
function fixtab(){{var on=document.querySelector(".otab button.on");if(on&&!on.disabled)return;
  var f=document.querySelector(".otab button:not([disabled])");if(f)show(f.dataset.t);}}
function show(t){{document.querySelectorAll(".otab button").forEach(function(y){{y.classList.toggle("on",y.dataset.t===t);}});
  document.querySelectorAll("#odekake .pane").forEach(function(g){{g.hidden=g.dataset.t!==t;}});}}
function reset(){{document.querySelectorAll("#odekake .pane.open").forEach(function(g){{g.classList.remove("open");}});}}
document.querySelectorAll("#odekake .gm").forEach(function(x){{x.addEventListener("click",function(){{x.closest(".pane").classList.add("open");apply();}});}});
document.querySelectorAll(".otab button").forEach(function(x){{x.addEventListener("click",function(){{if(!x.disabled)show(x.dataset.t);}});}});
apply();
function setp(v){{pref=v;document.querySelectorAll(".flt button[data-p]").forEach(function(y){{y.classList.toggle("on",y.dataset.p===v);}});
  reset();apply();fixtab();}}
document.querySelectorAll(".flt button[data-p]").forEach(function(x){{x.addEventListener("click",function(){{setp(x.dataset.p);}});}});
if(pref&&document.querySelector('.flt button[data-p="'+pref+'"]')){{setp(pref);setTimeout(function(){{var f=document.querySelector(".flt");if(f)scrollTo(0,Math.max(0,f.getBoundingClientRect().top+scrollY-80));}},350);}}else pref="";
document.querySelectorAll(".chips button").forEach(function(x){{x.addEventListener("click",function(){{
  var on=!x.classList.contains("on");x.classList.toggle("on",on);x.setAttribute("aria-pressed",on);
  if(x.dataset.k==="wk")wk=on?"1":"0";else free=on?"1":"0";reset();apply();fixtab();}});}});
document.querySelectorAll(".stab button").forEach(function(x){{x.addEventListener("click",function(){{
  var sh=document.getElementById("shop"),c=x.dataset.c;
  document.querySelectorAll(".stab button").forEach(function(y){{y.classList.toggle("on",y===x);}});
  sh.classList.toggle("tab",!!c);if(c)sh.classList.add("open");else sh.classList.remove("open");
  sh.querySelectorAll(".card.sh").forEach(function(k){{k.hidden=!!c&&k.dataset.c!==c;}});}});}});
document.querySelectorAll("#cats button[data-v]").forEach(function(x){{x.addEventListener("click",function(){{
  var v=x.dataset.v;document.querySelectorAll("#cats button").forEach(function(y){{y.classList.toggle("on",y===x);}});
  document.querySelectorAll(".wrap > [data-v]").forEach(function(e){{e.hidden=e.dataset.v!==v;}});
  var n=document.getElementById("cats");if(n.getBoundingClientRect().top<0||scrollY>n.offsetTop)scrollTo(0,n.offsetTop);}});}});
document.querySelectorAll(".wrap > [data-v]").forEach(function(e){{e.hidden=e.dataset.v!=="odekake";}});
var mo=document.querySelector("#shop .mo");if(mo)mo.addEventListener("click",function(){{document.getElementById("shop").classList.add("open");}});
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
var pm=document.querySelector(".arch .pmo");if(pm)pm.addEventListener("click",function(){{document.querySelectorAll(".arch .past li[hidden]").forEach(function(l){{l.hidden=false;}});pm.remove();}});
}})();
</script>
<script>
/* 10/31 近くの宿（月と同じ）：遠い場所のカードの下に、楽天トラベルの評価の高い宿を3つ。宿の一覧は /kanto-yado.json（page.yml が作る） */
(function(){{
var Y={{}};
function vis(e){{for(;e&&e!==document.body;e=e.parentElement){{if(e.hidden||getComputedStyle(e).display=="none")return false;}}return true;}}
function sync(){{document.querySelectorAll(".yk,.ykl").forEach(function(x){{x.hidden=!(x._c&&vis(x._c))||(x.className=="ykl"&&!x.dataset.op);}});}}
function ck(k){{try{{navigator.sendBeacon("/c?f=yado&s=yado&k="+encodeURIComponent(k.slice(0,40)));}}catch(e){{}}}}
function run(){{document.querySelectorAll("#odekake .card.it,#wsec .card.it").forEach(function(c){{var t=c.querySelector(".t");if(!t||c.dataset.yk)return;
var nm=t.textContent.replace(/\\s+/g,""),H=Y[nm];if(!H)return;c.dataset.yk=1;
var d=document.createElement("div");d.className="yk";d._c=c;var b=document.createElement("a");b.href="#";b.className="inn";b.textContent="近くの宿";d.appendChild(b);
var u=document.createElement("ul");u.className="ykl";u._c=c;
H.forEach(function(h){{var li=document.createElement("li"),a=document.createElement("a");a.href=h.u;a.target="_blank";a.rel="noopener sponsored";
a.addEventListener("click",function(){{ck("宿｜"+nm.slice(0,16)+"｜"+h.n);}});
var m=document.createElement("span");m.className="nm";m.textContent=h.n;a.appendChild(m);
var s2=document.createElement("span");s2.className="mt";s2.textContent=(h.km<0.1?"すぐそば":h.km+"km")+(h.r?"・★"+h.r:"")+(h.min?"・"+Number(h.min).toLocaleString()+"円〜":"");a.appendChild(s2);li.appendChild(a);u.appendChild(li);}});
var li=document.createElement("li");li.className="src";li.textContent="楽天トラベルの評価3.5以上・ここからの近さ（PR）";u.appendChild(li);
b.addEventListener("click",function(e){{e.preventDefault();e.stopPropagation();if(!u.dataset.op)ck("宿を開く｜"+nm);u.dataset.op=u.dataset.op?"":"1";b.classList.toggle("op",!!u.dataset.op);sync();}});
c.insertAdjacentElement("afterend",d);d.insertAdjacentElement("afterend",u);}});sync();}}
fetch("/kanto-yado.json").then(function(r){{return r.ok?r.json():{{}}}}).then(function(j){{for(var k in (j||{{}}))Y[k.replace(/\\s+/g,"")]=j[k];run();}}).catch(function(){{}});
window.ykRun=run;document.addEventListener("click",function(){{setTimeout(run,80);}},true);
}})();
</script>
<script src="/assets/yado-date.js?v=1" defer></script>
</body></html>
"""


def main():
    now = now_jst()
    if "--now" in sys.argv:
        now = datetime.fromisoformat(sys.argv[sys.argv.index("--now") + 1]).replace(tzinfo=JST)
    cfg = load_json(path("config.json"), {}) or {}
    items, ended = collect(now)
    if os.environ.get("LINK_GATE"):  # 公開するとき（page.yml）だけ、載せる前にリンクを開いて確かめる
        _NOW[:] = [now]
        gate([e["url"] for e in all_spots(items, now)] + [e["url"] for e in items["deal"] if e.get("url")
                                                            and "hb.afl.rakuten" not in e["url"]], now)
    out = path("site", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render(items, ended, now, cfg))
    print(json.dumps({k: len(v) for k, v in items.items()} | {"ended": len(ended)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
