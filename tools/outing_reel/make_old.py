"""関東のおでかけリール（月の 10/28 型と同じ動き・約29秒・曲つき）を作る。

使い方: python3 tools/outing_reel/make.py reel/D.json reel/D.mp4 [確かめる秒,…]
  - 先に `python3 scripts/page.py` で site/index.html を作っておく（リストの画面に使う）。
  - spec の形は docs/outing-reel.md。lat/lon から地図のピンの位置を出す。
  - 曲は bgm/reel_bgm.m4a（オーナーのフリー音源）を最後に重ね、終わりを2秒で小さくする。
2026-10-29 オーナー「燈のインスタにも月と同じおでかけ動画をつくる」。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(D, '..', '..'))
# 表紙の上の2行（全部のリールで同じ。キャプションの1行目にも使う）
KICKER = ('街の調査で見つけた', '関東おでかけリスト')  # 10/29 オーナー「1ありだな」
PREFS = {"東京": "tokyo", "神奈川": "kanagawa", "埼玉": "saitama", "千葉": "chiba", "茨城": "ibaraki", "栃木": "tochigi", "群馬": "gunma"}
SECONDS = 28.8


def xy(lat, lon):
    """paths.json と同じ一次式（tools/outing_reel の地図の作り方は docs/outing-reel.md）。"""
    return 24.0 * (lon - 139.65) + 225, 267.6 - 29.67 * (lat - 35.95)


def main():
    spec = json.load(open(sys.argv[1]))
    out = os.path.abspath(sys.argv[2])
    tab = spec['tab']
    pref = PREFS[tab]
    px, py = xy(spec['lat'], spec['lon'])
    work = tempfile.mkdtemp()
    for f in ('grain.png', 'logo.png'):
        shutil.copy(os.path.join(D, f), work)
    page = os.path.join(ROOT, 'site', 'index.html')
    if not os.path.exists(page):
        sys.exit('site/index.html がない（先に python3 scripts/page.py）')
    # リストの画面（都県のボタンを押した所）。数える通信は止める
    shot = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:390,height:844}},deviceScaleFactor:2}});
await p.route(/^https?:/,r=>r.request().resourceType()==='document'||r.request().url().includes('fonts.g')?r.continue():r.fulfill({{status:204}}));
await p.goto('file://{page}');await p.waitForTimeout(1500);
const x=await p.$('.flt button[data-p="{tab}"]');if(x)await x.click();
await p.waitForTimeout(700);await p.screenshot({{path:'{work}/list.png',fullPage:true}});await b.close()}})();"""
    open(f'{work}/shot.js', 'w').write(shot)
    subprocess.run(['node', f'{work}/shot.js'], check=True)
    h = open(os.path.join(D, 'template.html')).read()
    t = spec['text']
    rep = dict(CORNER=t['corner'], K1=KICKER[0], K2=KICKER[1], A1=t['title'][0], A2=t['title'][1], A3=t['place'],
               MT1=t['map_tag'][0], MT2=t['map_tag'][1], MT3=t['map_tag'][2], MC1=t['map_caption'],
               B1=t['date'][0], B1D=t['date'][1], B2=t['date'][2], B2D=t['date'][3], B3=t['date_title'],
               B3S=str(t.get('date_title_size', 58)), B4=t['date_note'],
               C0=t['point_kicker'], C1=t['point_title'], C2=t['points'][0], C3=t['points'][1], C4=t['points'][2],
               D1K=t['info'][0][0], D1V=t['info'][0][1], D2K=t['info'][1][0], D2V=t['info'][1][1],
               D3K=t['info'][2][0], D3V=t['info'][2][1], D4K=t['info'][3][0], D4V=t['info'][3][1], D5=t['info_note'],
               E2=t['list_caption'], LISTPNG='list.png', PX=f'{px:.2f}', PY=f'{py:.2f}', PREF=pref,
               FONTS=os.path.join(ROOT, 'tools', 'fonts'))
    for k, v in rep.items():
        h = h.replace(f'__{k}__', v)
    assert '__' not in h.replace('__proto__', ''), 'placeholder left'
    open(f'{work}/reel.html', 'w').write(h)
    rec = f"""const {{chromium}}=require('playwright');const fs=require('fs');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{work}/reel.html');await p.waitForTimeout(900);fs.mkdirSync('{work}/fr',{{recursive:true}});
const only=process.argv[2];if(only){{for(const t of only.split(',')){{await p.evaluate(t=>render(t),+t);await p.screenshot({{path:'{work}/c-'+t+'.jpg',type:'jpeg',quality:85}});}}await b.close();return;}}
for(let i=0;i<30*{SECONDS};i++){{await p.evaluate(t=>render(t),i/30);await p.screenshot({{path:'{work}/fr/'+String(i).padStart(4,'0')+'.jpg',type:'jpeg',quality:92}});}}await b.close()}})();"""
    open(f'{work}/rec.js', 'w').write(rec)
    if len(sys.argv) > 3:  # 確かめる静止画だけ
        subprocess.run(['node', f'{work}/rec.js', sys.argv[3]], check=True)
        print(work)
        return
    subprocess.run(['node', f'{work}/rec.js'], check=True)
    bgm = os.path.join(ROOT, 'bgm', 'reel_bgm.m4a')
    if os.path.exists(bgm):
        audio = ['-stream_loop', '-1', '-i', bgm, '-af', f'afade=t=out:st={SECONDS - 2}:d=2']
    else:
        audio = ['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo']
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{work}/fr/%04d.jpg', *audio,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'medium',
                    '-c:a', 'aac', '-b:a', '128k', '-t', str(SECONDS), '-movflags', '+faststart', out], check=True)
    shutil.rmtree(work, ignore_errors=True)
    print(out)


if __name__ == '__main__':
    main()
