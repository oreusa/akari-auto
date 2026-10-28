#!/usr/bin/env python3
"""インスタのリールを、Buffer を通さず直接出す（曲つき。10/28 月のやり方 docs/reference/tsuki-ig-direct-reels.md）。

book.yml の予約のあとに動く。config.json の "ig_direct": true で、ig/page_token.enc と ig/setup.json がある時だけ動く。
  1. その日の4コマ（koma4/D.json・D-tabi.json）で、雫の動画が機械の確認（video_ok）に通っていれば、
     出す時刻の90分前から、動画をドライブから受け取り、インスタへ直接送って入れ物（container）を作る（再開可能アップロード）。
     akari-auto は非公開なので、URLで渡さず動画そのものを送る。
  2. 出す時刻を過ぎた最初の回に公開する（12分以内なら待って時刻ちょうどに出す）。
  3. 失敗した時は state の ig_direct に failed を書く → book.py が Buffer で今までどおりリールを出す。
曲は config.json の ig_audio_id（無ければ付けない）。雫の動画の音は ig_video_volume（0〜100、既定0）にする。
鍵は環境変数 IG_PAGE_TOKEN（workflow で復号して渡す。ファイルには書かない）。
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import JST, append_log, load_json, now_jst, path, save_json  # noqa: E402

GV = "v23.0"
BEFORE_MIN = 90   # 出す時刻の何分前から入れ物を作るか
WAIT_MAX = 12     # 出す時刻まで、この分数以内なら待って時刻ちょうどに出す
GIVE_UP_MIN = 90
REELS_PROJECT = "akari-reels"  # もとの曲を消したリール動画の置き場（Cloudflare Pages）  # 出す時刻からこの分数すぎても出せなければ Buffer に任せる


def direct_ready(cfg):
    return bool(cfg.get("ig_direct")) and os.path.exists(path("ig", "page_token.enc")) \
        and bool((load_json(path("ig", "setup.json")) or {}).get("ig_user_id"))


def call(method, url, token, params=None, data=None, headers=None, timeout=120):
    params = dict(params or {})
    if token:
        params["access_token"] = token
    full = url if url.startswith("https://") else f"https://graph.facebook.com/{GV}/{url}"
    body = None
    if method == "GET":
        full += ("&" if "?" in full else "?") + urllib.parse.urlencode(params)
    elif data is not None:
        body = data
        if params:
            full += ("&" if "?" in full else "?") + urllib.parse.urlencode(params)
    else:
        body = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(full, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return {"error": json.loads(e.read().decode() or "{}").get("error", {"code": e.code})}
        except ValueError:
            return {"error": {"code": e.code}}
    except Exception as e:  # つながらない
        return {"error": {"message": str(e)[:200]}}


def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def caption(k, due):
    import book
    text = k["text"]
    if book.IG_HEAD in text:
        return text
    return text.rstrip() + "\n\n" + book.ig_profile([text], due) + "\n\n" + book.ig_tags(k, due)


def audio_config(cfg):
    aid = cfg.get("ig_audio_id")
    if not aid:
        return None
    # 月と同じ形：audio_id だけ。音量は指定がある時だけ（10/28 video_volume=0 を送った試しで曲が付かなかった）
    ac = {"audio_id": str(aid)}
    if cfg.get("ig_video_volume") is not None:
        ac["video_volume"] = int(cfg["ig_video_volume"])
    if cfg.get("ig_audio_volume"):
        ac["audio_volume"] = int(cfg["ig_audio_volume"])
    return json.dumps(ac)


def silence(video):
    """動画の音を無音に替える（10/28 オーナー「元々の音楽ついてるから2重になってる」）。戻り値：(動画, エラー)"""
    import shutil
    import subprocess
    import tempfile
    if not shutil.which("ffmpeg"):
        subprocess.run("sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg", shell=True)
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, "in.mp4"), os.path.join(d, "out.mp4")
        open(src, "wb").write(video)
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-shortest", dst],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(dst):
            return None, f"動画の音を消せない：{r.stderr[-150:]}"
        return open(dst, "rb").read(), None


def host_silent(video_url, name):
    """もとの曲を消した動画を Cloudflare Pages（akari-reels）に置く。戻り値：(URL, エラー)"""
    import subprocess
    import tempfile
    if not os.environ.get("CLOUDFLARE_API_TOKEN"):
        return None, "Cloudflare の鍵がない"
    try:
        video = download(video_url)
    except Exception as e:
        return None, f"動画をドライブから受け取れない：{str(e)[:120]}"
    video, err = silence(video)
    if err:
        return None, err
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, f"{name}.mp4"), "wb").write(video)
        w = ["npx", "-y", "wrangler@3.80.0", "pages"]
        subprocess.run(w + ["project", "create", REELS_PROJECT, "--production-branch=main"], capture_output=True)
        r = subprocess.run(w + ["deploy", d, f"--project-name={REELS_PROJECT}", "--branch=main", "--commit-dirty=true"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return None, f"Cloudflare に置けない：{(r.stderr or r.stdout)[-150:]}"
    import re
    m = re.findall(r"https://[\w.-]+\.pages\.dev", r.stdout or "")
    base = m[-1] if m else f"https://{REELS_PROJECT}.pages.dev"  # 置いた回ごとの URL（名前が取られていても確実）
    url = f"{base}/{name}.mp4"
    print("無音の動画：", url)
    for _ in range(36):  # 置いた直後は見えないことがある（最初の1回は数分かかる）
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=20) as r2:
                if r2.status == 200:
                    return url, None
        except Exception:
            pass
        time.sleep(5)
    return None, "置いた動画が開けない"


def make_container(cfg, token, ig, k, due):
    """動画を直接送って、リールの入れ物を作る。戻り値：(container_id, エラー)"""
    q = {"media_type": "REELS", "caption": caption(k, due), "share_to_feed": "true"}
    ac = audio_config(cfg)
    if ac:
        q["audio_configuration"] = ac
    # 10/28 の試し：再開可能アップロードだと曲が付かない、URL だと付く。video_volume=0 は受け付けない。
    # → 雫の動画のもとの曲を消した動画を Cloudflare（akari-reels.pages.dev）に置き、その URL を渡す（オーナー「元の曲は必要がない」）
    if cfg.get("ig_upload", "url") == "url":
        url, err = host_silent(k["video_url"], f"{k.get('episode', 'x')}-{now_jst().strftime('%Y%m%d%H%M%S')}")
        if url:
            q2 = dict(q, video_url=url)
        else:
            # 置けない時は、ドライブの URL でもとの曲を1にする（10/28 5回目でオーナーOKの形）
            print("無音の動画を置けない：", err)
            ac2 = json.loads(ac) if ac else None
            if ac2:
                ac2["video_volume"] = 1
                q2 = dict(q, video_url=k["video_url"], audio_configuration=json.dumps(ac2))
            else:
                q2 = dict(q, video_url=k["video_url"])
        c = call("POST", f"{ig}/media", token, q2)
        if c.get("id"):
            return c["id"], None
    try:
        video = download(k["video_url"])
    except Exception as e:
        return None, f"動画をドライブから受け取れない：{str(e)[:120]}"
    q["upload_type"] = "resumable"
    c = call("POST", f"{ig}/media", token, q)
    if not c.get("id") or not c.get("uri"):
        return None, f"入れ物を作れない：{json.dumps(c.get('error') or c, ensure_ascii=False)[:200]}"
    up = call("POST", c["uri"], None, data=video, headers={
        "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(video))}, timeout=300)
    if up.get("error") or up.get("success") is False:
        return None, f"動画を送れない：{json.dumps(up.get('error') or up, ensure_ascii=False)[:200]}"
    return c["id"], None


def run(now=None):
    cfg = load_json(path("config.json")) or {}
    if not direct_ready(cfg):
        print("インスタ直接投稿は未設定（config の ig_direct・ig/page_token.enc・ig/setup.json）")
        return 0
    token = os.environ.get("IG_PAGE_TOKEN", "").strip()
    if not token:
        print("IG_PAGE_TOKEN が無い")
        return 0
    ig = load_json(path("ig", "setup.json"))["ig_user_id"]
    now = now or now_jst()
    day = now.date().isoformat()
    state_p = path("state", "booked.json")
    state = load_json(state_p) or {}
    changed = False
    import book
    for suffix, label in book.KOMA_FILES:
        k = load_json(path("koma4", f"{day}{suffix}.json"))
        if not k or not k.get("text") or not k.get("video_url") or not k.get("video_ok"):
            continue
        due = datetime.fromisoformat(f"{day}T{k.get('slot') or '08:00'}").replace(tzinfo=JST)
        mins = (due - now).total_seconds() / 60
        rec = state.setdefault(f"{day} {label}", {})
        if rec.get("instagram", {}).get("id"):
            continue  # Buffer で予約済み（直接は出さない。2本出さない）
        d = rec.setdefault("ig_direct", {})
        if d.get("state") in ("published", "failed") or mins > BEFORE_MIN:
            continue
        ep = k.get("episode", "?")
        if mins < -GIVE_UP_MIN:
            d.update(state="failed", error="時刻を過ぎても出せない")
            append_log(day, f"{label} 第{ep}話 リール直接 ×：時刻を過ぎても出せない → Buffer で出す")
            changed = True
            continue
        if d.get("video") != k["video_url"]:  # 7:50の直しで動画が変わったら作り直す
            d.clear()
        if not d.get("container"):
            cid, err = make_container(cfg, token, ig, k, due)
            d["tries"] = d.get("tries", 0) + 1
            changed = True
            if err:
                d["error"] = err
                append_log(day, f"{label} 第{ep}話 リール直接 ×（{d['tries']}回目）：{err}")
                if d["tries"] >= 2:
                    d["state"] = "failed"
                    append_log(day, f"{label} 第{ep}話 リール直接をやめて Buffer で出す")
                continue
            d.update(container=cid, video=k["video_url"], state="uploaded")
            append_log(day, f"{label} 第{ep}話 リール直接：動画を送った（曲 {cfg.get('ig_audio_id') or 'なし'}）")
        # 入れ物ができるのを待つ
        st = {}
        for _ in range(30):
            st = call("GET", d["container"], token, {"fields": "status_code,status"})
            if st.get("status_code") in ("FINISHED", "ERROR", "EXPIRED") or st.get("error"):
                break
            time.sleep(10)
        code = st.get("status_code")
        if code != "FINISHED":
            if code in ("ERROR", "EXPIRED") or st.get("error"):
                d.update(state="failed", error=json.dumps(st, ensure_ascii=False)[:200])
                append_log(day, f"{label} 第{ep}話 リール直接 ×：インスタが動画を受け付けない（{d['error'][:120]}）→ Buffer で出す")
                changed = True
            continue
        mins = (due - now_jst()).total_seconds() / 60
        if mins > WAIT_MAX:
            continue  # 次の回で出す
        if mins > 0:
            time.sleep(mins * 60)
        p = call("POST", f"{ig}/media_publish", token, {"creation_id": d["container"]})
        changed = True
        if not p.get("id"):
            d["error"] = json.dumps(p.get("error") or p, ensure_ascii=False)[:200]
            append_log(day, f"{label} 第{ep}話 リール直接 公開×：{d['error'][:150]}")
            continue
        link = call("GET", p["id"], token, {"fields": "permalink"}).get("permalink")
        d.update(state="published", media_id=p["id"], permalink=link,
                 at=now_jst().strftime("%H:%M"))
        d.pop("error", None)
        append_log(day, f"{label} 第{ep}話 instagram リール直接 出た（曲つき） {link or ''}".rstrip())
    if changed:
        save_json(state_p, state)
    return 0


if __name__ == "__main__":
    sys.exit(run())
