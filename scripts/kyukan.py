"""11/24 休館日の判定（関西・関東おなじ。usagi tools/kyukan.py と同じ中身）。
夜の見回り：11/23（月・祝）の翌日 11/24 は「月曜休館（祝日は開館・翌日休館）」の館が振替で休みなのに、一覧と1件ページが「開催中」のままだった。
→ 決まりで止める：
  dy  = "wd:0123456h"  開く曜日（0=日〜6=土）。h＝祝日は開く＋その代わりに次の平日が休み（翌日休館）
        "2026-11-13,2026-11-14,…"  開く日だけ
  cl  = "-2026-11-24,+2026-11-23"  休む日（-）・開く日（+）を1日ずつ
  dline = カードの日付の文。「（11/16・11/24は休館）」「（11/16・11/24は休み）」も休む日として読む
shin.js の SHIN.shut と同じ答えを返す。"""
import re, datetime

# 日本の祝日（振替休日を含む）。shin.js の HOL と同じ
HOL = {"2026-11-03", "2026-11-23", "2027-01-01", "2027-01-11", "2027-02-11", "2027-02-23", "2027-03-21", "2027-03-22",
       "2027-04-29", "2027-05-03", "2027-05-04", "2027-05-05", "2027-07-19", "2027-08-11", "2027-09-20", "2027-09-23",
       "2027-10-11", "2027-11-03", "2027-11-23", "2028-01-01", "2028-01-10"}


def _d(x):
    return x if isinstance(x, datetime.date) else datetime.date.fromisoformat(x)


def cl_from_text(dline, year_of):
    """「（11/16・11/24は休館）」→ ["-2026-11-16", "-2026-11-24"]。year_of(month) で年を決める"""
    out = []
    for grp in re.findall(r"([\d/・、,\s]+)は(?:休館|休み|休園|休業|お休み)", dline or ""):
        for mo, da in re.findall(r"(\d{1,2})/(\d{1,2})", grp):
            try:
                out.append("-" + datetime.date(year_of(int(mo)), int(mo), int(da)).isoformat())
            except ValueError:
                pass
    return out


def wd(d):  # 0=日〜6=土
    return (d.weekday() + 1) % 7


def shut(dy, cl, day, extra_cl=()):
    """day に休みなら理由の文（「休館日」曜日の休み・「祝日の翌日で休館」・「休みの日」決まった日の休み）、開いていれば ''。"""
    day = _d(day); t = day.isoformat()
    cls = [c for c in (cl or "").split(",") if c] + list(extra_cl)
    if "+" + t in cls: return ""
    if "-" + t in cls: return "休みの日"
    dy = (dy or "").strip()
    if re.fullmatch(r"\d{4}-\d\d-\d\d(,\d{4}-\d\d-\d\d)*", dy):
        return "" if t in dy.split(",") else "休みの日"
    m = re.fullmatch(r"wd:(\d+)(h?)", dy)
    if not m: return ""
    days, h = m.group(1), m.group(2)
    if h and t in HOL: return ""
    if str(wd(day)) not in days: return "休館日"
    if h:  # 祝日に開けた代わりに、次の平日が休み（11/23 月・祝 → 11/24 火 休館）
        p = day - datetime.timedelta(days=1)
        while p.isoformat() in HOL:
            if str(wd(p)) not in days: return "祝日の翌日で休館"
            p -= datetime.timedelta(days=1)
    return ""
