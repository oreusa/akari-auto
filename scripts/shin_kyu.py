"""関東の前のページ（街・実家・解体・地価・おでかけ1件・申し込み …）を、関西と同じ新しい見た目（site/shin/kyu.css）で描き直す。
11/19 owner「その他も本気でやり直せ」「頭とバーをかぶせただけは作り直しに数えない」。page.yml の最後（shin_kanto.py の後）に毎回。
前の <style> は消さずに media="not all" で眠らせ、開く・閉じるに要る規則だけ残す。頭・下のバー（skin）は functions/_middleware.js が入れる。
関西の tools/shin/bake.py と同じ物（直す時は両方）。"""
import os
SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
SKIN = "\x00 (関東は functions が入れる)"
SKIP = {"shin", "kyu", "assets", "card", "promo", "townnotes", "gate"}
KYUMARK = 'data-kyu'
KYUV = "3"
import re as _re
_FN = _re.compile(r"\.(on|open|show|active|sel|cur|hide|hidden|is-[\w-]+)\b|\[open\]|:checked|\[hidden\]|\[aria-[\w-]+")


def _keep(css):
    out = []
    css = _re.sub(r"/\*[\s\S]*?\*/", "", css)
    i, n = 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        sel = css[i:j].strip()
        if sel.startswith("@"):
            # @media・@keyframes などは中ごと飛ばす（形の規則なので新しい見た目に任せる）
            d, k = 1, j + 1
            while k < n and d:
                d += {"{": 1, "}": -1}.get(css[k], 0); k += 1
            i = k
            continue
        k = css.find("}", j)
        if k < 0:
            break
        dec = css[j + 1:k]
        dz = dec.replace(" ", "")
        if ("display:none" in dz or "visibility:hidden" in dz or "-9999" in dz or "clip:rect" in dz or "clip-path:inset(50%" in dz
                or ("display" in dz and _FN.search(sel))):
            out.append(sel + "{" + dec + "}")
        i = k + 1
    return "".join(out)


def fam(rel, fn):
    if rel != ".":
        return rel.split(os.sep)[0]
    b = fn[:-5]
    if b.startswith("kaitai") and b != "kaitai-ranking":
        return "kaitai"
    if b.endswith("-ranking") or b.startswith("chika"):
        return "rank"
    if b.startswith(("okaimono-", "otoku", "tanka", "kaimawari", "furusato-")):
        return "kau"
    if b.startswith("gyosha"):
        return "gyosha"
    return b


def unkyu(h):
    """前に入れた物を外して元に戻す（KYUV を上げた時に入れ直すため）"""
    h = _re.sub(r'(?:<script>document\.documentElement\.dataset\.k="[^"]*"</script>)?<style data-kyu="keep">[\s\S]*?</style><link rel="stylesheet" href="/shin/kyu\.css\?v=[^"]*">', "", h)
    return _re.sub(r'<style data-kyu-old media="not all"', "<style", h)


def kyu(h, k="x"):
    keep = []

    def sleep(m):
        keep.append(_keep(m.group(2)))
        return '<style data-kyu-old media="not all"' + m.group(1) + ">" + m.group(2) + "</style>"
    h2 = _re.sub(r"<style((?:(?!media=)[^>])*)>([\s\S]*?)</style>", sleep, h)
    link = ('<script>document.documentElement.dataset.k="' + k + '"</script><style data-kyu="keep">' + "".join(keep) + '</style><link rel="stylesheet" href="/shin/kyu.css?v=' + KYUV + '">')
    i = h2.find(SKIN[:40]) if SKIN[:40] in h2 else h2.find("</head>")
    return h2[:i] + link + h2[i:]



def main(root=SITE):
    n = 0
    for d, dirs, files in os.walk(root):
        rel = os.path.relpath(d, root)
        if rel != "." and rel.split(os.sep)[0] in SKIP:
            dirs[:] = []
            continue
        for fn in files:
            if not fn.endswith(".html") or fn.startswith("index"):
                continue
            p = os.path.join(d, fn)
            h = open(p, encoding="utf-8", errors="ignore").read()
            if "/shin/shin.css" in h or "</head>" not in h or ("kyu.css?v=" + KYUV + '"') in h:
                continue
            if KYUMARK in h:
                h = unkyu(h)
            h = kyu(h, fam(rel, fn))
            open(p, "w", encoding="utf-8").write(h)
            n += 1
    print("shin_kyu: 新しい見た目にした", n, "枚")


if __name__ == "__main__":
    main()
