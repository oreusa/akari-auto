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
GIVE_UP_MIN = 90  # 出す時刻からこの分数すぎても出せなければ Buffer に任せる


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
    if cfg.get("ig_video_volume"):
        ac["video_volume"] = int(cfg["ig_video_volume"])
    if cfg.get("ig_audio_volume"):
        ac["audio_volume"] = int(cfg["ig_audio_volume"])
    return json.dumps(ac)


def make_container(cfg, token, ig, k, due):
    """動画を直接送って、リールの入れ物を作る。戻り値：(container_id, エラー)"""
    q = {"media_type": "REELS", "caption": caption(k, due), "share_to_feed": "true"}
    ac = audio_config(cfg)
    if ac:
        q["audio_configuration"] = ac
    if cfg.get("ig_upload", "url") == "url":
        # 月と同じ：動画の URL を渡す（ドライブの公開リンク）。曲はこの形で付くのを月で確かめ済み
        c = call("POST", f"{ig}/media", token, dict(q, video_url=k["video_url"]))
        if c.get("id"):
            return c["id"], None
    q["upload_type"] = "resumable"
    c = call("POST", f"{ig}/media", token, q)
    if not c.get("id") or not c.get("uri"):
        return None, f"入れ物を作れない：{json.dumps(c.get('error') or c, ensure_ascii=False)[:200]}"
    try:
        video = download(k["video_url"])
    except Exception as e:
        return None, f"動画をドライブから受け取れない：{str(e)[:120]}"
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
