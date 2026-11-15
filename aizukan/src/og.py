"""共有の絵（1200×630）を作る。python3 src/og.py <フォントのフォルダ> <data.json>"""
import json, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F, DJ = sys.argv[1], sys.argv[2]
D = json.load(open(DJ))
ROOT = __file__.rsplit('/src/', 1)[0]
IMG = ROOT + '/site/img/'
OUT = ROOT + '/site/og/'
W, H = 1200, 630
f = lambda n, s: ImageFont.truetype(f'{F}/{n}.ttf', s)
GOLD, GOLD2, TEXT, MUTE = (214, 176, 104), (240, 220, 170), (238, 232, 218), (156, 150, 176)
HC = [(227, 122, 76), (110, 155, 227), (95, 179, 139), (174, 138, 230)]

def bg(glow):
    im = Image.new('RGB', (W, H), (7, 7, 15))
    g = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(g)
    d.ellipse((-200, -260, 900, 900), fill=tuple(int(c * .35) for c in glow))
    g = g.filter(ImageFilter.GaussianBlur(160))
    im = Image.blend(im, g, 1.0) if False else Image.composite(g, im, Image.new('L', (W, H), 255))
    base = Image.new('RGB', (W, H), (7, 7, 15))
    im = Image.blend(base, im, .9)
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    for _ in range(240):
        x, y, r = rnd.random() * W, rnd.random() * H, rnd.random() * 1.4 + .3
        c = GOLD2 if rnd.random() < .12 else (221, 227, 255)
        a = rnd.random() * .6 + .2
        col = tuple(int(7 + (cc - 7) * a) for cc in c)
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    return im

def put_card(im, path, x, y, w, rot=0):
    h = int(w * 1.5)
    c = Image.open(path).convert('RGB').resize((w, h), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    d.rectangle((9, 9, w - 10, h - 10), outline=(240, 220, 170), width=2)
    sh = Image.new('RGBA', (w + 80, h + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((40, 50, w + 40, h + 50), fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    c = c.convert('RGBA')
    if rot:
        c = c.rotate(rot, resample=Image.BICUBIC, expand=True)
        sh = sh.rotate(rot, resample=Image.BICUBIC, expand=True)
    im.paste(sh, (x - 40, y - 40), sh)
    im.paste(c, (x, y), c)

def wrap(d, text, font, maxw):
    lines, l = [], ''
    for ch in text:
        if d.textlength(l + ch, font=font) > maxw:
            lines.append(l); l = ch
        else:
            l += ch
    if l: lines.append(l)
    return lines

def card_og(t, k):
    T, K = D['TYPES'][t], D['KI'][k]
    ali, leg = D['CH'][t * 5 + k]
    im = bg(HC[t // 3]).convert('RGBA')
    put_card(im, f'{IMG}{t+1:02d}_{k+1}.webp', 96, 45, 360)
    d = ImageDraw.Draw(im)
    X = 540
    d.text((X, 92), f"AI TYPE TAROT  ·  {D['ROMAN'][t]}", font=f('cin700', 22), fill=GOLD)
    d.text((X, 140), T['star'] + '　' + D['HOUSES'][t // 3]['n'], font=f('min700', 30), fill=GOLD)
    name = K['n'] + T['n']
    sz = 84
    while d.textlength(name, font=f('min800', sz)) > 600: sz -= 4
    d.text((X, 186), name, font=f('min800', sz), fill=TEXT)
    d.text((X, 300), '〈 ' + ali + ' 〉', font=f('min700', 32), fill=GOLD2)
    y = 372
    for ln in wrap(d, leg, f('min700', 25), 580)[:3]:
        d.text((X, y), ln, font=f('min700', 25), fill=(201, 194, 214)); y += 42
    d.line((X, 522, X + 600, 522), fill=(51, 52, 79), width=1)
    d.text((X, 540), 'あなたのAIは、あなたを何だと思ってる？', font=f('zen700', 22), fill=MUTE)
    d.text((X, 572), 'AIタイプ図鑑', font=f('min800', 26), fill=GOLD2)
    im.convert('RGB').save(f'{OUT}{t+1:02d}-{k+1}.jpg', quality=86, optimize=True, progressive=True)

def default_og():
    im = bg((90, 70, 160)).convert('RGBA')
    put_card(im, f'{IMG}04_2.webp', 690, 120, 250, rot=10)
    put_card(im, f'{IMG}09_4.webp', 930, 130, 250, rot=-8)
    put_card(im, f'{IMG}00_guide.webp', 800, 40, 290)
    d = ImageDraw.Draw(im)
    d.text((80, 120), 'AI TYPE TAROT  ·  60 CARDS', font=f('cin700', 22), fill=GOLD)
    d.text((80, 170), 'あなたのAIは、', font=f('min800', 62), fill=TEXT)
    d.text((80, 252), 'あなたを何者だと', font=f('min800', 62), fill=TEXT)
    d.text((80, 334), '思っている？', font=f('min800', 62), fill=GOLD2)
    d.text((80, 446), 'いつものAIに呪文を一つ送るだけ。六十枚のカードと、', font=f('zen700', 22), fill=(201, 194, 214))
    d.text((80, 480), 'AIがあなたにつける「主の位」。登録なし・無料・約3分。', font=f('zen700', 22), fill=(201, 194, 214))
    d.text((80, 548), 'AIタイプ図鑑', font=f('min800', 32), fill=GOLD2)
    im.convert('RGB').save(f'{OUT}default.jpg', quality=88, optimize=True, progressive=True)

def icon():
    s = 180
    im = Image.new('RGB', (s, s), (7, 7, 15))
    d = ImageDraw.Draw(im)
    c = s / 2
    d.ellipse((14, 14, s - 14, s - 14), outline=GOLD, width=4)
    pts = []
    import math
    for i in range(8):
        r = 66 if i % 2 == 0 else 13
        a = -math.pi / 2 + i * math.pi / 4
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=GOLD2)
    im.save(ROOT + '/site/apple-touch-icon.png')

if __name__ == '__main__':
    default_og(); icon()
    only = sys.argv[3:] if len(sys.argv) > 3 else None
    for t in range(12):
        for k in range(5):
            if only and f'{t+1:02d}-{k+1}' not in only: continue
            card_og(t, k)
    print('ok')
