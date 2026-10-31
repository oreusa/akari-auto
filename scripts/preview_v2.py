"""10/31 燈の見本ページ：site/index.html を写して site/preview-v2.html を作る（検索に出さない・数えない）。
本番は変えない。本番にするときは page.py の出力に v2.css と v2.js を足す。"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(R, 'site/index.html')
h = open(src, encoding='utf-8').read()
h = h.replace('<head>', '<head><meta name="robots" content="noindex">', 1)
h = re.sub(r'<link rel="canonical"[^>]*>', '', h)
h = h.replace('</head>', '<link rel="stylesheet" href="/assets/v2.css?v=1"></head>', 1)
i = h.rfind('</body>')
h = h[:i] + '<script src="/assets/v2.js?v=1"></script>' + h[i:]
open(os.path.join(R, 'site/preview-v2.html'), 'w', encoding='utf-8').write(h)
print('preview-v2.html', len(h))
