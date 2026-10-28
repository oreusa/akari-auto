#!/usr/bin/env python3
"""インスタのリール直接投稿の試し（10/28 オーナー「いまからリール投稿してくれ、その曲で、テストだ」）。
ig-test.yml から手で動かす。指定した日の4コマ動画を、曲つきでいますぐ直接出す。
毎日の予約（book.py・igreel.py）の記録には触らない。結果は state/ig_test.json と log に書く。
"""
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import igreel  # noqa: E402
from lib import JST, append_log, load_json, now_jst, path, save_json  # noqa: E402


def diag(token, ig):
    """鍵が今どうなっているか（10/29 権限が足りないと言われた時の調べ）。鍵そのものは書かない。"""
    d = {}
    sec = os.environ.get("APP_SECRET", "")
    if sec:
        r = igreel.call("GET", "debug_token", f"{APP_ID}|{sec}", {"input_token": token})
        x = r.get("data") or r
        d["debug"] = {k: x.get(k) for k in ("is_valid", "type", "profile_id", "expires_at", "data_access_expires_at",
                                             "scopes", "granular_scopes", "error")}
    d["me"] = igreel.call("GET", "me", token, {"fields": "id,name"})
    d["ig"] = igreel.call("GET", ig, token, {"fields": "id,username"})
    return d


APP_ID = "1400829015365892"


def main():
    token = os.environ.get("IG_PAGE_TOKEN", "").strip()
    if not token:
        print("IG_PAGE_TOKEN が無い")
        return 1
    cfg = load_json(path("config.json")) or {}
    if os.environ.get("AUDIO_ID"):
        cfg["ig_audio_id"] = os.environ["AUDIO_ID"]
    ig = load_json(path("ig", "setup.json"))["ig_user_id"]
    now = now_jst()
    day = os.environ.get("DAY") or now.date().isoformat()
    k = load_json(path("koma4", f"{day}.json"))
    if not k or not k.get("video_url"):
        print(f"{day} の4コマ動画が無い")
        return 1
    due = datetime.fromisoformat(f"{day}T{k.get('slot') or '08:00'}").replace(tzinfo=JST)
    out = {"day": day, "episode": k.get("episode"), "audio_id": cfg.get("ig_audio_id"), "at": now.strftime("%Y-%m-%d %H:%M")}
    today = now.date().isoformat()
    cid, err = igreel.make_container(cfg, token, ig, k, due)
    if err:
        out["error"] = err
        out["diag"] = diag(token, ig)
        append_log(today, f"リール直接の試し ×：{err}")
    else:
        st = {}
        for _ in range(60):
            st = igreel.call("GET", cid, token, {"fields": "status_code,status"})
            if st.get("status_code") in ("FINISHED", "ERROR", "EXPIRED") or st.get("error"):
                break
            time.sleep(10)
        if st.get("status_code") == "FINISHED" and os.environ.get("DRY") == "true":
            out["dry"] = "入れ物まで作れた（公開はしない）"
            append_log(today, "リール直接の試し（公開しない）：入れ物まで作れた")
        elif st.get("status_code") != "FINISHED":
            out["error"] = json.dumps(st, ensure_ascii=False)[:300]
            append_log(today, f"リール直接の試し ×：インスタが動画を受け付けない（{out['error'][:150]}）")
        else:
            p = igreel.call("POST", f"{ig}/media_publish", token, {"creation_id": cid})
            if not p.get("id"):
                out["error"] = json.dumps(p.get("error") or p, ensure_ascii=False)[:300]
                append_log(today, f"リール直接の試し 公開×：{out['error'][:150]}")
            else:
                link = igreel.call("GET", p["id"], token, {"fields": "permalink"}).get("permalink")
                out.update(media_id=p["id"], permalink=link)
                append_log(today, f"リール直接の試し 出た（曲 {cfg.get('ig_audio_id')}） {link or ''}".rstrip())
    save_json(path("state", "ig_test.json"), out)
    print(json.dumps(out, ensure_ascii=False))
    return 0 if not out.get("error") else 1


if __name__ == "__main__":
    sys.exit(main())
