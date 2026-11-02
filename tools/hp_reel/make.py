"""HPの紹介リール（約29秒・曲つき）を作る。HPの本物の画面を順番に見せて、最後は「プロフィールのリンクから」。

使い方: python3 tools/hp_reel/make.py reel-hp/D.json /tmp/D.mp4 [確かめる秒,…]
  - spec の形は docs/hp-reel.md。scenes の url を開いて撮る（その日の本物の画面。撮り直しは毎回）。
  - 開く前に /?me=on を開いて、HPの数え（見られた数）に入らないようにする。
  - 曲は bgm/reel_bgm.m4a（いつもの音源）。終わりを2秒で小さくする。
2026-11-02 オーナー「29秒のリールで、HPの本物の画面を順番に見せる。最後は『プロフィールのリンクから』。曲はいつもの音源、明るい背景、燈の金色」。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(D, '..', '..'))
SECONDS = 28.8
END = 3.8  # 最後の「プロフィールのリンクから」の秒


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    spec = json.load(open(sys.argv[1]))
    out = os.path.abspath(sys.argv[2])
    scenes = spec['scenes']
    assert 3 <= len(scenes) <= 6, '画面は3〜6つ'
    work = tempfile.mkdtemp()
    shutil.copy(os.path.join(D, 'logo.png'), work)
    base = spec.get('base') or 'https://usagi-life-notes.pages.dev'
    urls = [s['url'] if s['url'].startswith(('http', 'file:')) else base.rstrip('/') + s['url'] for s in scenes]
    shot = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
const c=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2});const p=await c.newPage();
const base=%s, urls=%s, work=%s, clicks=%s;
if(base.startsWith('http')){try{await p.goto(base.replace(/\\/$/,'')+'/?me=on',{waitUntil:'domcontentloaded',timeout:30000});await p.waitForTimeout(800)}catch(e){}}
for(let i=0;i<urls.length;i++){await p.goto(urls[i],{waitUntil:'networkidle',timeout:45000}).catch(()=>{});await p.waitForTimeout(1500);
 if(clicks[i]){const x=await p.$(clicks[i]);if(x){await x.click();await p.waitForTimeout(800)}}
 await p.screenshot({path:work+'/s'+i+'.png',fullPage:true});}
await b.close()})();""" % (json.dumps(base), json.dumps(urls), json.dumps(work), json.dumps([s.get('click') for s in scenes]))
    open(f'{work}/shot.js', 'w').write(shot)
    subprocess.run(['node', f'{work}/shot.js'], check=True)
    from PIL import Image
    hs = []
    for i in range(len(scenes)):
        im = Image.open(f'{work}/s{i}.png')
        if im.height > 5200:  # 長すぎる画面は上だけ使う
            im.crop((0, 0, im.width, 5200)).save(f'{work}/s{i}.png')
            hs.append(5200 * 690 / im.width)
        else:
            hs.append(im.height * 690 / im.width)
    h = open(os.path.join(D, 'template.html')).read()
    sc = ''.join(
        f'<div class="sc" id="sc{i}"><div class="top"><div class="k">HP の ご 紹 介<span>{i + 1:02d} / {len(scenes):02d}</span></div>'
        f'<div class="h">{esc(s["title"])}</div></div>'
        f'<div class="ph"><img src="s{i}.png" id="im{i}"></div><div class="note">{esc(s.get("note", ""))}</div></div>'
        for i, s in enumerate(scenes))
    rep = dict(FONTS=os.path.join(ROOT, 'tools', 'fonts'), SCENES=sc, N=str(len(scenes)), HS=json.dumps(hs),
               SECONDS=str(SECONDS), END=str(END), ENDNOTE=esc(spec.get('end_note', '')))
    for k, v in rep.items():
        h = h.replace(f'__{k}__', v)
    assert '__' not in h, 'placeholder left'
    open(f'{work}/reel.html', 'w').write(h)
    rec = """const {chromium}=require('playwright');const fs=require('fs');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://%s/reel.html');await p.waitForTimeout(900);fs.mkdirSync('%s/fr',{recursive:true});
const only=process.argv[2];if(only){for(const t of only.split(',')){await p.evaluate(t=>render(t),+t);await p.screenshot({path:'%s/c-'+t+'.jpg',type:'jpeg',quality:85});}await b.close();return;}
for(let i=0;i<30*%s;i++){await p.evaluate(t=>render(t),i/30);await p.screenshot({path:'%s/fr/'+String(i).padStart(4,'0')+'.jpg',type:'jpeg',quality:92});}await b.close()})();""" % (work, work, work, SECONDS, work)
    open(f'{work}/rec.js', 'w').write(rec)
    if len(sys.argv) > 3:  # 確かめる静止画だけ
        subprocess.run(['node', f'{work}/rec.js', sys.argv[3]], check=True)
        print(work)
        return
    subprocess.run(['node', f'{work}/rec.js'], check=True)
    try:  # 確かめ用の静止画6枚を1枚に（reel-hp/out/D.jpg。夜の回・見回りが中身を見る）
        from PIL import Image
        ts = (1, 6, 11, 16, 22, 27)
        sheet = Image.new('RGB', (360 * len(ts), 640), 'white')
        for n, t in enumerate(ts):
            sheet.paste(Image.open(f'{work}/fr/{int(t * 30):04d}.jpg').resize((360, 640)), (360 * n, 0))
        sheet.save(os.path.splitext(out)[0] + '.jpg', quality=80)
    except Exception as e:
        print('静止画を作れない', e)
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
