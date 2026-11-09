"""見本：物件1件の情報から、SNS投稿セット（X・Threads・インスタ画像・Web説明）を作る。
11/9 3代表の話し合いで燈が推した案の最小見本。架空の物件だけを使う（実在の物件・写真・会社は使わない）。
使い方：python3 samples/fudosan-sns/make.py [properties.json]  → out/<id>/ に4つ書く。かかった秒を最後に出す。
表示の決まり（不動産の公正競争規約）で必ず入れる項目は、公式でまだ確かめていない（夜に頼んだ）。今は主な項目を全部の出力に入れている。"""
import json, os, sys, time
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(D, "..", "..", "tools", "fonts")
T0 = time.time()


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


def yen(v):
    return f"{v:,}円"


def must_line(it):
    # 広告に入れる主な項目（取引態様・所在地・交通・賃料・管理費・敷金礼金・間取り・面積・築年月・情報の日付）
    return (f"{it['kind']}｜取引態様：{it['deal']}｜{it['town']}｜{it['station']} 徒歩{it['walk']}分｜"
            f"賃料{yen(it['rent'])}・管理費{yen(it['fee'])}・敷金{it['deposit']}・礼金{it['key']}｜"
            f"{it['layout']}・{it['area']}㎡・{it['floor']}・{it['built']}築｜情報更新日{it['updated']}（次回{it['next']}）")


def x_text(it, co):
    head = f"【{it['layout']}｜{it['station'].split('「')[-1].rstrip('」')}徒歩{it['walk']}分】{yen(it['rent'])}"
    body = "・" + "\n・".join(it["points"])
    tail = f"{co['name']}（{it['deal']}）"
    return f"{head}\n{body}\n{tail}"


def threads_text(it, co):
    return (f"{it['town']}の{it['layout']}です。\n"
            f"{it['station']}から歩いて{it['walk']}分、{it['points'][0]}と{it['points'][1]}があります。\n"
            f"賃料は{yen(it['rent'])}（管理費{yen(it['fee'])}）。\n\n"
            f"くわしい条件：{must_line(it)}\n{co['name']}｜{co['license']}")


def web_text(it, co):
    pts = "".join(f"<li>{p}</li>" for p in it["points"])
    return (f"<h2>{it['layout']}｜{it['town']}</h2>\n<ul>{pts}</ul>\n"
            f"<table>\n<tr><th>賃料</th><td>{yen(it['rent'])}（管理費{yen(it['fee'])}）</td></tr>\n"
            f"<tr><th>敷金・礼金</th><td>{it['deposit']}・{it['key']}</td></tr>\n"
            f"<tr><th>交通</th><td>{it['station']} 徒歩{it['walk']}分</td></tr>\n"
            f"<tr><th>間取り・面積</th><td>{it['layout']}・{it['area']}㎡</td></tr>\n"
            f"<tr><th>階・築年月</th><td>{it['floor']}・{it['built']}</td></tr>\n"
            f"<tr><th>取引態様</th><td>{it['deal']}</td></tr>\n"
            f"<tr><th>情報更新日</th><td>{it['updated']}（次回更新予定 {it['next']}）</td></tr>\n</table>\n"
            f"<p>{co['name']}｜{co['license']}｜{co['tel']}</p>\n")


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
    small = font("ZenKakuGothicNew-Medium.ttf", 24)
    d.text((70, H - 120), f"{it['kind']}｜{it['town']}｜{it['floor']}・{it['built']}築｜取引態様：{it['deal']}", font=small, fill="#555")
    d.text((70, H - 80), f"{co['name']}｜{co['license']}｜情報更新日 {it['updated']}", font=small, fill="#555")
    im.save(path)


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
        ig_image(it, co, os.path.join(out, "ig.png"))
        print(it["id"], "X", len(x_text(it, co)), "字", "Threads", len(threads_text(it, co)), "字")
    print(f"かかった秒：{time.time() - T0:.2f}")


if __name__ == "__main__":
    main()
