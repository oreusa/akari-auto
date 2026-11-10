"""燈のおでかけリストの見た目（月の links/assets/v2.css・v2.js と同じ形）を入れる。
10/31 見本 /preview-v2 を作成、11/1 オーナー「改善してから本番OK」で本番の / にも入れる。
page.yml が page.py のあとに毎回動かす。site/index.html（本番）と site/preview-v2.html（見本・検索に出さない）。"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = '<link rel="stylesheet" href="/assets/v2.css?v=7">'
JS = '<script src="/assets/v2.js?v=3"></script>'
src = os.path.join(R, 'site/index.html')
h = open(src, encoding='utf-8').read()
if 'assets/v2.css' not in h:
    h = h.replace('</head>', CSS + '</head>', 1)
    i = h.rfind('</body>')
    h = h[:i] + JS + h[i:]
    open(src, 'w', encoding='utf-8').write(h)
p = h.replace('<head>', '<head><meta name="robots" content="noindex">', 1)
p = re.sub(r'<link rel="canonical"[^>]*>', '', p)
# 11/1 見本は本番に入ったので、/preview-v2 は本番の / へ送る（古い見本を人目に出さない）
open(os.path.join(R, 'site/preview-v2.html'), 'w', encoding='utf-8').write('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url=/"><link rel="canonical" href="/"><title>関東おでかけリスト</title><script>location.replace("/")</script></head><body></body></html>')
# 11/2 オーナー「詰め込まれすぎ」→ 見本 /preview-top → 11/2 5:13「もう全部本番にしていって」で本番の / に入れる
T1 = '<script>document.documentElement.classList.add("top2")</script><link rel="stylesheet" href="/assets/top2.css?v=2">'
T2 = '<script src="/assets/top2.js?v=2"></script>'
if 'assets/top2.css' not in h:
    h = h.replace('<head>', '<head>' + T1, 1)
    i = h.rfind('</body>')
    h = h[:i] + T2 + h[i:]
    open(src, 'w', encoding='utf-8').write(h)
open(os.path.join(R, 'site/preview-top.html'), 'w', encoding='utf-8').write('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url=/"><link rel="canonical" href="/"><title>関東おでかけリスト</title><script>location.replace("/")</script></head><body></body></html>')
print('v2 index+preview', len(h))
