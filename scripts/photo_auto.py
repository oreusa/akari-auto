# 投稿の写真の表紙を機械で作る（11/19 オーナー「投稿に使う写真も劇的に変えれる」「関東の方も全部の話だよね？」）。
# 予約の前（book.yml）に動く。今日の予定表のおでかけの枠で、まだ予約していない物を data/photo-pick.json の写真と照らし、
# 合う写真があれば scripts/post_photo.js で表紙を作って site/card/ に置き、data/photo-auto.json に「日付 時刻 → 絵のURL」を書く。
# book.py はこの表を見て、予定表の image より先にこの絵を付ける。
# 写真は data/photo-pick.json に月か燈が目で見て入れた物だけ（催しそのもの・季節が合う・幅900px以上・cr あり）。合わない枠は今の絵のまま。
# 使い方：python3 scripts/photo_auto.py [--need]（--need は作る物があれば yes を出すだけ。道具を入れるかどうかに使う）
import json, os, re, subprocess, sys, tempfile, time
from datetime import datetime, timedelta, timezone

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JST = timezone(timedelta(hours=9))
RAW = "https://raw.githubusercontent.com/oreusa/akari-auto/main/site/card/"
WD = "月火水木金土日"


def load(p, d):
    try:
        with open(os.path.join(R, p), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return d


def in_season(pk, day):
    md = day[5:]
    a, b = pk.get("from", "01-01"), pk.get("to", "12-31")
    return a <= md <= b if a <= b else (md >= a or md <= b)


def pick_for(post, day, picks):
    t = (post.get("threads") or post.get("x") or [""])[0].split("\n")[0] + " " + str(post.get("place", ""))
    for pk in picks:
        if all(w in t for w in pk["all"]) and (not pk.get("any") or any(w in t for w in pk["any"])) and in_season(pk, day):
            return pk
    return None


def spec_for(post, day, slot, pk):
    line = (post.get("threads") or post.get("x") or [""])[0].split("\n")[0]
    m = re.match(r"【([^｜]+)｜([^】]+)】", line)
    if not m:
        return None
    left, body = m.group(1).strip(), m.group(2).strip()
    parts = re.split(r"[　 ]+", left, maxsplit=1)
    when, place = (parts[0], parts[1]) if len(parts) == 2 else ("", left)
    dm = re.match(r"(\d{1,2})/(\d{1,2})(.*)", when)
    big, unit = (f"{int(dm.group(1))}.{int(dm.group(2)):02d}", dm.group(3)[:4]) if dm else (None, None)
    pill = post.get("topic", "")
    if dm:
        try:
            wd = WD[datetime(int(day[:4]) + (1 if int(dm.group(1)) < int(day[5:7]) else 0), int(dm.group(1)), int(dm.group(2))).weekday()]
            pill += f"　{int(dm.group(1))}/{int(dm.group(2))}（{wd}）{dm.group(3)}"
        except ValueError:
            pill += "　" + when
    elif when:
        pill += "　" + when
    name = f"photo-{day[5:].replace('-', '')}-{slot.replace(':', '')}"
    base = {"name": name, "im": pk["file"], "cr": pk["cr"], "pos": pk.get("pos", "50% 50%"), "pill": pill.strip(),
            "big": big, "unit": unit, "en": pk.get("en", "")}
    cap = pk.get("cap", "")
    # 長い見出しは字を小さく、まだ入らなければ名前だけを見出しにして中身は下の小さい字へ
    return [dict(base, head=f"<em>{place}</em><br>{body}", cap=cap, nowrap=True),
            dict(base, head=f"<em>{place}</em><br>{body}", cap=cap, hs=60, nowrap=True),
            dict(base, head=f"<em>{place}</em>", cap=body, nowrap=True),
            dict(base, head=f"<em>{place}</em>", cap=body, hs=60, nowrap=True)]


EN = {"路線ごとの街ランキング": "KANTO TOWN RANKING", "ひと駅しらべ": "HITOEKI NOTE", "実家・空き家": "JIKKA NOTE",
      "できる・開く": "NEW OPEN", "X速報": "NEW OPEN", "くらべた話": "KURABETA NOTE", "おでかけ": "WEEKEND"}
PEN = {"東京": "TOKYO", "神奈川": "KANAGAWA", "千葉": "CHIBA", "埼玉": "SAITAMA", "茨城": "IBARAKI", "栃木": "TOCHIGI", "群馬": "GUNMA"}


def has_pic(post):
    """book.py の post_image と同じ見方：投稿の中のHPのページに絵があるか"""
    idx = (load("data/postimg.json", {}) or {}).get("items") or {}
    t = " ".join((post.get("threads") or []) + (post.get("x") or []))
    return any(idx.get("/" + m.group(1)) for m in re.finditer(r"townnote\.app/((?:o/)?[a-z0-9-]+)", t))


def card_specs(post, day, slot):
    """写真の無い枠の表紙（post_card.js の作り）。1行目【A｜B】から見出しを作る"""
    line = ((post.get("threads") or post.get("x") or [""])[0].strip().split("\n") or [""])[0]
    m = re.match(r"【([^｜]+)｜([^】]+)】", line)
    if not m:
        return []
    left, body = m.group(1).strip(), re.sub(r"[🌀-🫶☀-➿]+$", "", m.group(2).strip())
    parts = re.split(r"[　 ]+", left, maxsplit=1)
    when, place = (parts[0], parts[1]) if len(parts) == 2 and re.match(r"\d", parts[0]) else ("", left)
    dm = re.match(r"(\d{1,2})/(\d{1,2})(.*)", when)
    rest = dm.group(3) if dm else ""
    unit = next((u for u in ("から", "まで", "開店", "開業", "オープン") if u in rest), "開店" if "開き" in rest else "新装" if "リニューアル" in rest else "")
    big = f"{int(dm.group(1))}.{int(dm.group(2)):02d}" if dm else None
    en = EN.get(str(post.get("series", "")), "KANTO TOWN NOTE")
    if PEN.get(post.get("topic", "")) and en in ("NEW OPEN", "WEEKEND", "HITOEKI NOTE"):
        en += "　" + PEN[post["topic"]]
    lines = wrap2(body)
    t0 = (post.get("threads") or [""])[0]
    if not big:  # 順位・ひと駅：本文の1位の数字を大きく
        n = re.search(r"([+＋−-]?\d[\d,.]*)(%|％|人|万円|円)", t0)
        if n:
            big, unit = n.group(1).replace("＋", "+"), n.group(2).replace("％", "%")
    sub = re.search(r"◎\s*(.+)", t0)
    cap = re.sub(r"[！!。]+$", "", sub.group(1).strip()) if sub else ""
    base = {"name": f"auto-{day[5:].replace('-', '')}-{slot.replace(':', '')}", "en": en, "big": big, "unit": unit, "nowrap": True}
    out = []
    if lines:
        h = "<em>" + place + "</em><br>" + "<br>".join(lines)
        for hs in (58, 54, 50):
            out += [dict(base, head=h, hs=hs, cap=cap), dict(base, head=h, hs=hs)]
    out += [dict(base, head="<em>" + place + "</em>", cap=body), dict(base, head="<em>" + place + "</em>")]
    return out


def wrap2(body, n=15):
    """見出しの中身を2行までに（「、」か助詞の後で切る。言葉の途中では切らない）"""
    body = body.strip()
    if len(body) <= n:
        return [body]
    cuts = [k + 1 for k, c in enumerate(body) if c in "、，" ] or []
    cuts += [k + 1 for k, c in enumerate(body) if c in "にでのがをはと" and 0 < k < len(body) - 2]
    best = None
    for c in sorted(set(cuts)):
        a, b = body[:c].rstrip("、，"), body[c:]
        if len(a) <= n and len(b) <= n:
            score = abs(len(a) - len(b)) - (10 if body[c - 1] in "、，" else 0)
            if best is None or score < best[0]:
                best = (score, [a, b])
    return best[1] if best else []


def main():
    now = datetime.now(JST)
    day = now.date().isoformat()
    sched = load(f"schedule/{day}.json", {}) or {}
    picks = (load("data/photo-pick.json", {}) or {}).get("items") or []
    booked = load("state/booked.json", {}) or {}
    made = load("data/photo-auto.json", {}) or {}
    todo = []
    for post in sched.get("posts", []):
        slot = post.get("slot", "")
        key = f"{day} {slot}"
        if key in made or any(isinstance((booked.get(key) or {}).get(s), dict) and (booked.get(key) or {})[s].get("id") for s in ("threads", "twitter")):
            continue
        pk = pick_for(post, day, picks) if "おでかけ" in str(post.get("series", "")) else None
        sp = spec_for(post, day, slot, pk) if pk else None
        if sp:
            todo.append((key, sp, "post_photo.js"))
        elif not str(post.get("image", "")).startswith("https://") and not has_pic(post):  # 11/19 owner「どしたの？画像なし」：絵の無い枠を残さない
            cs = card_specs(post, day, slot)
            if cs:
                todo.append((key, cs, "post_card.js"))
    if "--need" in sys.argv:
        print("yes" if todo else "no")
        return 0
    for key, tries, tool in todo:
        for sp in tries:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                json.dump([sp], f, ensure_ascii=False)
            r = subprocess.run(["node", os.path.join(R, "scripts", tool), f.name], capture_output=True, text=True, timeout=120)
            out = os.path.join(R, "site", "card", f"card-{sp['name']}.jpg")
            if "作った 1 枚" in r.stdout and os.path.exists(out):
                made[key] = {"url": RAW + f"card-{sp['name']}.jpg?v={int(time.time()) % 100000000:x}",
                             "photo": sp.get("im", ""), "cr": sp.get("cr", ""), "head": sp["head"]}
                print(f"表紙：{key} {sp.get('im', tool)}")
                break
            print(f"写真の表紙×（次の形で）：{key} {r.stdout.strip()[-120:]} {r.stderr.strip()[-200:]}")
    old = (now - timedelta(days=14)).date().isoformat()
    made = {k: v for k, v in made.items() if k[:10] >= old}
    with open(os.path.join(R, "data", "photo-auto.json"), "w", encoding="utf-8") as f:
        json.dump(made, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
