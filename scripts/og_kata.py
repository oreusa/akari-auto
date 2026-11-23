"""11/23 owner「リンク送る時の画像、ふるいまま？」→ HP と同じ今の形（白に近い地・上だけ淡いオーロラ・すりガラスのカード・細い字）の
リンクの絵（1200×630）を描く部品。関西 usagi tools/og_kata.py と 関東 akari scripts/og_kata.py は同じ物（直す時は両方）。"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
BG = (248, 248, 250)
INK = (17, 17, 20)
SUB = (110, 110, 118)
AU = [((159, 227, 211), (-160, -330)), ((185, 168, 242), (330, -380)), ((247, 182, 210), (820, -320)), ((143, 208, 232), (560, -230))]


def font(fd, size, w):
    f = ImageFont.truetype(os.path.join(fd, "NotoSansJP-VF.ttf"), size)
    try:
        f.set_variation_by_axes([w])
    except Exception:
        pass
    return f


def ground():
    """白に近い地＋上だけ淡いオーロラ（下へ溶ける）"""
    img = Image.new("RGB", (W, H), BG)
    lay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(lay)
    for c, (x, y) in AU:
        d.ellipse([x, y, x + 760, y + 760], fill=c)
    lay = lay.filter(ImageFilter.GaussianBlur(110))
    mask = Image.linear_gradient("L").resize((W, H)).point(lambda v: int(max(0, 255 - v * 1.6) * .62))
    img.paste(lay, (0, 0), mask)
    return img


def glass(img, box, r=34):
    """すりガラスのカード（白 .62・細い白の縁・やわらかい影）"""
    x0, y0, x1, y1 = box
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 10, x1, y1 + 10], r, fill=34)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    img.paste((20, 24, 40), (0, 0), sh)
    blur = img.crop(box).filter(ImageFilter.GaussianBlur(18))
    m = Image.new("L", blur.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, blur.size[0] - 1, blur.size[1] - 1], r, fill=255)
    img.paste(blur, (x0, y0), m)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rounded_rectangle(box, r, fill=(255, 255, 255, 158), outline=(255, 255, 255, 230), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"))
    return img


def spaced(d, xy, text, f, fill, sp):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + sp
    return x


def wrap(d, text, f, width, lines):
    out, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=f) > width:
            out.append(cur); cur = ch
            if len(out) == lines:
                break
        else:
            cur += ch
    if len(out) < lines and cur:
        out.append(cur)
    if len(out) == lines and "".join(out) != text:
        out[-1] = out[-1][:-1] + "…"
    return out


def spot(fd, mapimg, tag, dot, name, when, where, brand, area):
    """1件ページの絵：左に地図のカード、右に名前・日程・場所、下にブランド"""
    img = ground()
    if mapimg is not None:
        box = (44, 44, 584, 586)
        img = glass(img, box, 30)
        mw, mh = box[2] - box[0] - 24, box[3] - box[1] - 24
        mp = mapimg.copy()
        # 地図は切らずに全部入れる（府県の名前が左上にあるため）。余白は地図の角の色（海）で埋める
        s = min(mw / mp.width, mh / mp.height)
        mp = mp.resize((round(mp.width * s), round(mp.height * s)))
        bgc = mp.getpixel((2, mp.height - 3))
        fr = Image.new("RGB", (mw, mh), bgc)
        fr.paste(mp, ((mw - mp.width) // 2, (mh - mp.height) // 2))
        mp = fr
        m = Image.new("L", mp.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, mw - 1, mh - 1], 20, fill=255)
        img.paste(mp, (box[0] + 12, box[1] + 12), m)
        x0, w = 640, 510
    else:
        x0, w = 90, 1020
    top = 74 if mapimg is not None else 150  # 地図が無い時は字を画面のまん中寄りに大きく
    d = ImageDraw.Draw(img)
    d.ellipse([x0, top + 10, x0 + 12, top + 22], fill=dot)
    spaced(d, (x0 + 26, top), tag, font(fd, 20, 500), SUB, 5)
    big, mid = (font(fd, 54, 300), font(fd, 46, 300)) if mapimg is not None else (font(fd, 66, 300), font(fd, 54, 300))
    f = big if d.textlength(name, font=big) <= w * 2 else mid
    lines = wrap(d, name, f, w, 3)
    if len(lines) > 1 and len(lines[-1]) <= 2 and f is big:
        f = mid; lines = wrap(d, name, f, w, 3)
    y = top + 54
    for ln in lines:
        d.text((x0, y), ln, font=f, fill=INK); y += f.size + 18
    y += 18
    fw = font(fd, 30, 400)
    for ln in wrap(d, when, fw, w, 2):
        d.text((x0, y), ln, font=fw, fill=INK); y += 44
    fs = font(fd, 24, 300)
    for ln in wrap(d, where, fs, w, 2):
        d.text((x0, y + 6), ln, font=fs, fill=SUB); y += 36
    d.line([x0, 540, x0 + w, 540], fill=(225, 225, 230), width=1)
    e = spaced(d, (x0, 558), brand, font(fd, 24, 200), INK, 7)
    d.text((e + 14, 560), area, font=font(fd, 20, 300), fill=SUB)
    return img


def site(fd, logo, brand, lead, tags, area):
    """サイト全体の絵：まん中にロゴの丸・細い題・一言"""
    img = ground()
    d = ImageDraw.Draw(img)
    if logo and os.path.exists(logo):
        r = 62
        cx, cy = W // 2, 168
        sh = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sh).ellipse([cx - r, cy - r + 8, cx + r, cy + r + 8], fill=40)
        img.paste((20, 24, 40), (0, 0), sh.filter(ImageFilter.GaussianBlur(16)))
        d = ImageDraw.Draw(img)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
        lg = Image.open(logo).convert("RGBA")
        s = (r * 2 - 6) / max(lg.size)
        lg = lg.resize((round(lg.width * s), round(lg.height * s)))
        cm = Image.new("L", lg.size, 0)
        ImageDraw.Draw(cm).ellipse([0, 0, lg.width - 1, lg.height - 1], fill=255)
        from PIL import ImageChops
        img.paste(lg, (cx - lg.width // 2, cy - lg.height // 2), ImageChops.multiply(lg.getchannel("A"), cm))
        d = ImageDraw.Draw(img)
    ft = font(fd, 84, 200)
    sp = 22
    tw = sum(d.textlength(c, font=ft) + sp for c in brand) - sp
    spaced(d, ((W - tw) / 2, 262), brand, ft, INK, sp)
    fl = font(fd, 30, 300)
    lw = sum(d.textlength(c, font=fl) + 4 for c in lead) - 4
    spaced(d, ((W - lw) / 2, 392), lead, fl, SUB, 4)
    fa = font(fd, 20, 500)
    aw = sum(d.textlength(c, font=fa) + 6 for c in tags) - 6
    spaced(d, ((W - aw) / 2, 478), tags, fa, SUB, 6)
    if area:
        fz = font(fd, 22, 400)
        zw = d.textlength(area, font=fz) + 56
        img = glass(img, (int((W - zw) / 2), 528, int((W + zw) / 2), 584), 28)
        d = ImageDraw.Draw(img)
        d.text(((W - d.textlength(area, font=fz)) / 2, 541), area, font=fz, fill=INK)
    return img
