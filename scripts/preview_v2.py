"""燈のおでかけリストの見た目（月の links/assets/v2.css・v2.js と同じ形）を入れる。
10/31 見本 /preview-v2 を作成、11/1 オーナー「改善してから本番OK」で本番の / にも入れる。
page.yml が page.py のあとに毎回動かす。site/index.html（本番）と site/preview-v2.html（見本・検索に出さない）。"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = '<link rel="stylesheet" href="/assets/v2.css?v=3">'
JS = '<script src="/assets/v2.js?v=2"></script>'
src = os.path.join(R, 'site/index.html')
h = open(src, encoding='utf-8').read()
if 'assets/v2.css' not in h:
    h = h.replace('</head>', CSS + '</head>', 1)
    i = h.rfind('</body>')
    h = h[:i] + JS + h[i:]
    open(src, 'w', encoding='utf-8').write(h)
p = h.replace('<head>', '<head><meta name="robots" content="noindex">', 1)
p = re.sub(r'<link rel="canonical"[^>]*>', '', p)
open(os.path.join(R, 'site/preview-v2.html'), 'w', encoding='utf-8').write(p)
print('v2 index+preview', len(h))
