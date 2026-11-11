"""この場所（関東）だけの決まり。make.py は関西（月）・関東（燈）で同じ物を使い、違いはこのファイルだけに書く。"""
import os
import sys

KICKER = ('街の調査で見つけた', '関東おでかけリスト')   # 表紙の上の2行（10/29 オーナー「1ありだな」）
ACC = '#A8783A'                          # 燈の金
PREFS = ['tokyo', 'kanagawa', 'saitama', 'chiba', 'ibaraki', 'tochigi', 'gunma']
BGM = 'bgm/reel_bgm.m4a'
VOICE_CREDIT = 'VOICEVOX:もち子(cv 明日葉よもぎ)'
_TAB = {"東京": "tokyo", "神奈川": "kanagawa", "埼玉": "saitama", "千葉": "chiba", "茨城": "ibaraki", "栃木": "tochigi", "群馬": "gunma"}


def pref(spec):
    return _TAB[spec['tab']]


def xy(lat, lon):
    """paths.json と同じ一次式（地図の作り方は docs/outing-reel.md）"""
    return 24.0 * (lon - 139.65) + 225, 267.6 - 29.67 * (lat - 35.95)


def shot_js(root, spec, work):
    """リストの画面（都県のボタンを押した所）を list.png に撮る node の文。先に scripts/page.py で site/index.html を作っておく"""
    page = os.path.join(root, 'site', 'index.html')
    if not os.path.exists(page):
        sys.exit('site/index.html がない（先に python3 scripts/page.py）')
    return f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:390,height:844}},deviceScaleFactor:2}});
await p.route(/^https?:/,r=>r.request().resourceType()==='document'||r.request().url().includes('fonts.g')?r.continue():r.fulfill({{status:204}}));
await p.goto('file://{page}');await p.waitForTimeout(1500);
const x=await p.$('.flt button[data-p="{spec['tab']}"]');if(x)await x.click();
await p.waitForTimeout(700);await p.screenshot({{path:'{work}/list.png',fullPage:true}});await b.close()}})();"""
