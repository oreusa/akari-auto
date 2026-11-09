"""見本：物件1件の情報から、SNS投稿セット（X・Threads・インスタ画像・Web説明）を作る。
11/9 3代表の話し合いで燈が推した案の最小見本。架空の物件だけを使う（実在の物件・写真・会社は使わない）。
使い方：python3 samples/fudosan-sns/make.py [properties.json]  → out/<id>/ に4つ書く。かかった秒を最後に出す。
表示の決まり（11/9 夜の調べ）：公取協通信365号 Q2＝概要を全部満たして明瞭なら画像でよい・全部入らない時は概要を載せたページへのURLでよい。
  → X は字数が足りないので、概要を全部のせた Web（web.html）への URL を入れる。Threads・インスタ画像・Web は概要を全部入れる。
  別表9 の項目の細かい照合は月・夜（REQUIRED は見本の確認項目。法の判断ではない）。
check() で、出力ごとに入れるべき項目の欠け・古い値の残り・募集終了の残りを数える。"""
import json, os, re, sys, time
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(D, "..", "..", "tools", "fonts")
T0 = time.time()


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


def yen(v):
    return f"{v:,}円"


# 出力に必ず入れる項目（見本の確認項目）。key と、出力の中に出る字
REQUIRED = ["kind", "deal", "town", "station", "walk", "rent", "fee", "deposit", "key", "layout", "area", "floor", "built",
            "term", "guarantor", "insurance", "other", "updated", "next"]


def shown(it, k):
    v = it[k]
    if k in ("rent", "fee"):
        return yen(v)
    if k == "walk":
        return f"徒歩{v}分"
    if k == "area":
        return f"{v}㎡"
    return str(v)


def has(text, s):
    """s が text にあるか。数字は前に数字・カンマが続かない所だけ（95,000円 の中の 5,000円 を数えない）"""
    return re.search(r"(?<![\d,])" + re.escape(s), text) is not None


def must_line(it):
    # 広告に入れる主な項目（取引態様・所在地・交通・賃料・管理費・敷金礼金・間取り・面積・築年月・情報の日付）
    return (f"{it['kind']}｜取引態様：{it['deal']}｜{it['town']}｜{it['station']} 徒歩{it['walk']}分｜"
            f"賃料{yen(it['rent'])}・管理費{yen(it['fee'])}・敷金{it['deposit']}・礼金{it['key']}｜"
            f"{it['layout']}・{it['area']}㎡・{it['floor']}・{it['built']}築｜{it['term']}｜{it['guarantor']}｜{it['insurance']}｜その他費用：{it['other']}｜"
            f"情報更新日{it['updated']}（次回更新予定{it['next']}）")


ENDED = "この物件の募集は終わりました。"


def x_text(it, co):
    if it.get("status") == "終了":
        return f"{ENDED}\n{co['name']}"
    head = f"【{it['layout']}｜{it['station'].split('「')[-1].rstrip('」')}徒歩{it['walk']}分】{yen(it['rent'])}"
    body = "・" + "\n・".join(it["points"])
    tail = f"{co['name']}（{it['deal']}）\n条件のすべて→{it['url']}"
    return f"{head}\n{body}\n{tail}"


def threads_text(it, co):
    if it.get("status") == "終了":
        return f"{ENDED}\n{co['name']}｜{co['license']}"
    return (f"{it['town']}の{it['layout']}です。\n"
            f"{it['station']}から歩いて{it['walk']}分、{it['points'][0]}と{it['points'][1]}があります。\n"
            f"賃料は{yen(it['rent'])}（管理費{yen(it['fee'])}）。\n\n"
            f"くわしい条件：{must_line(it)}\n{co['name']}｜{co['license']}")


def web_text(it, co):
    if it.get("status") == "終了":
        return f"<p>{ENDED}</p>\n<p>{co['name']}｜{co['license']}</p>\n"
    pts = "".join(f"<li>{p}</li>" for p in it["points"])
    return (f"<h2>{it['layout']}｜{it['town']}</h2>\n<ul>{pts}</ul>\n"
            f"<table>\n<tr><th>賃料</th><td>{yen(it['rent'])}（管理費{yen(it['fee'])}）</td></tr>\n"
            f"<tr><th>敷金・礼金</th><td>{it['deposit']}・{it['key']}</td></tr>\n"
            f"<tr><th>交通</th><td>{it['station']} 徒歩{it['walk']}分</td></tr>\n"
            f"<tr><th>間取り・面積</th><td>{it['layout']}・{it['area']}㎡</td></tr>\n"
            f"<tr><th>階・築年月</th><td>{it['floor']}・{it['built']}</td></tr>\n"
            f"<tr><th>種類</th><td>{it['kind']}</td></tr>\n"
            f"<tr><th>契約</th><td>{it['term']}</td></tr>\n"
            f"<tr><th>保証会社</th><td>{it['guarantor']}</td></tr>\n"
            f"<tr><th>保険</th><td>{it['insurance']}</td></tr>\n"
            f"<tr><th>その他費用</th><td>{it['other']}</td></tr>\n"
            f"<tr><th>取引態様</th><td>{it['deal']}</td></tr>\n"
            f"<tr><th>情報更新日</th><td>{it['updated']}（次回更新予定 {it['next']}）</td></tr>\n</table>\n"
            f"<p>{co['name']}｜{co['license']}｜{co['tel']}</p>\n")


def ig_lines(it, co):
    """画像にのせる字（check でも使う）"""
    if it.get("status") == "終了":
        return [ENDED, co["name"]]
    return [f"{it['layout']}　{it['area']}㎡", f"賃料 {yen(it['rent'])}",
            f"管理費 {yen(it['fee'])}／敷金 {it['deposit']}／礼金 {it['key']}", f"{it['station']} 徒歩{it['walk']}分"] + \
           ["・" + p for p in it["points"]] + \
           [f"{it['kind']}｜{it['town']}｜{it['floor']}・{it['built']}築｜取引態様：{it['deal']}",
            f"{it['term']}｜{it['guarantor']}",
            f"{it['insurance']}｜その他費用：{it['other']}",
            f"{co['name']}｜{co['license']}｜情報更新日 {it['updated']}（次回更新予定 {it['next']}）"]


def ig_image(it, co, path):
    W, H = 1080, 1350
    im = Image.new("RGB", (W, H), "#ffffff")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 520), fill="#eef1f4")
    d.text((W // 2, 260), "写真の場所（見本）", font=font("ZenKakuGothicNew-Medium.ttf", 40), fill="#9aa4ae", anchor="mm")
    y = 580
    d.text((70, y), f"{it['layout']}　{it['area']}㎡", font=font("ZenKakuGothicNew-Bold.ttf", 64), fill="#222")
    y += 100
    d.text((70, y), f"賃料 {yen(it['rent'])}", font=font("ZenKakuGothicNew-Bold.ttf", 76), fill="#c0392b")
    y += 110
    d.text((70, y), f"管理費 {yen(it['fee'])}／敷金 {it['deposit']}／礼金 {it['key']}", font=font("ZenKakuGothicNew-Medium.ttf", 36), fill="#333")
    y += 70
    d.text((70, y), f"{it['station']} 徒歩{it['walk']}分", font=font("ZenKakuGothicNew-Medium.ttf", 36), fill="#333")
    y += 80
    for p in it["points"]:
        d.text((70, y), "・" + p, font=font("ZenKakuGothicNew-Medium.ttf", 40), fill="#222")
        y += 62
    small = font("ZenKakuGothicNew-Medium.ttf", 22)
    rows = [r for line in ig_lines(it, co)[-4:] for r in wrap(line, small, W - 140)]
    for i, line in enumerate(rows):
        d.text((70, H - 40 - (len(rows) - i) * 36), line, font=small, fill="#555")
    im.save(path)


def wrap(text, f, width):
    """画像の幅に入るように折り返す（はみ出しを無くす）"""
    rows, cur = [], ""
    for ch in text:
        if f.getlength(cur + ch) > width:
            rows.append(cur)
            cur = ch
        else:
            cur += ch
    return rows + [cur] if cur else rows


def ig_ended(it, co, path):
    im = Image.new("RGB", (1080, 1350), "#ffffff")
    d = ImageDraw.Draw(im)
    d.text((540, 600), ENDED, font=font("ZenKakuGothicNew-Bold.ttf", 52), fill="#222", anchor="mm")
    d.text((540, 700), co["name"], font=font("ZenKakuGothicNew-Medium.ttf", 36), fill="#555", anchor="mm")
    im.save(path)


def outputs(it, co):
    return {"x": x_text(it, co), "threads": threads_text(it, co), "web": web_text(it, co), "ig": "\n".join(ig_lines(it, co))}


def check(it, co, old=None):
    """出力ごとに ①入れるべき項目の欠け ②古い値の残り ③募集終了なのに条件が残る を数える。X は URL があれば概要はリンク先でよい"""
    out, bad = outputs(it, co), []
    for name, text in out.items():
        if it.get("status") == "終了":
            if has(text, yen(it["rent"])):
                bad.append(f"{name}：募集終了なのに賃料が残る")
            continue
        if name == "x":
            if it["url"] not in text:
                bad.append("x：概要ページのURLが無い")
            continue
        for k in REQUIRED:
            if not has(text, shown(it, k)):
                bad.append(f"{name}：{k}（{shown(it, k)}）が無い")
        if old:
            for k in REQUIRED:
                if old.get(k) != it.get(k) and shown(old, k) not in shown(it, k) and has(text, shown(old, k)):
                    bad.append(f"{name}：{k} の古い値（{shown(old, k)}）が残る")
    return bad


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, "properties.json")
    data = json.load(open(src, encoding="utf-8"))
    co = data["company"]
    for it in data["items"]:
        out = os.path.join(D, "out", it["id"])
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "x.txt"), "w", encoding="utf-8").write(x_text(it, co))
        open(os.path.join(out, "threads.txt"), "w", encoding="utf-8").write(threads_text(it, co))
        open(os.path.join(out, "web.html"), "w", encoding="utf-8").write(web_text(it, co))
        (ig_ended if it.get("status") == "終了" else ig_image)(it, co, os.path.join(out, "ig.png"))
        bad = check(it, co)
        print(it["id"], "欠け・残り", len(bad), bad[:3])
        print(it["id"], "X", len(x_text(it, co)), "字", "Threads", len(threads_text(it, co)), "字")
    print(f"かかった秒：{time.time() - T0:.2f}")


if __name__ == "__main__":
    main()
