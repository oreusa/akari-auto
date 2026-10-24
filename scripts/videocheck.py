"""雫の4コマ動画（リール）を、予約の前に機械で確かめる。10/24から。

10/24 雫は「音を実際に聴けない」と動画を作らなかった。聴くのは雫には無理なので、音は数字で確かめる。
雫は数字を見て保存まで、最後の確認はここ（燈の機械）。だめな動画は出さない（その日はリールなし・画像の投稿は出す）。

確かめること：縦 1080x1920／長さ 10〜15秒／音がある／平均の音量が -45〜-28dB（BGM 8％の目安）／最大が -1dB 以下（音割れなし）／
最後の1秒が4コマ全体の絵に近い（違う話の動画を防ぐ）。

使い方（book.yml の中）：python3 scripts/videocheck.py --need → 「yes」なら ffmpeg を入れて python3 scripts/videocheck.py
"""
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import UA, append_log, fetch_image, image_diff, load_json, now_jst, path, save_json  # noqa: E402

LAST_DIFF_MAX = 40  # 最後の画面と4コマ全体の絵の違い（ぼかし背景があるので緩め）


def koma_file(now):
    return path("koma4", f"{now.date().isoformat()}.json")


def need(now):
    k = load_json(koma_file(now))
    return bool(k and k.get("video_url") and k.get("image_url") and not k.get("video_ok") and not k.get("video_error"))


def problems(mp4, still=None):
    """動画のおかしい所の並び（空なら合格）。"""
    out = []
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                        "-of", "compact", mp4], capture_output=True, text=True).stdout
    if "width=1080|height=1920" not in r:
        out.append("大きさが1080x1920でない")
    m = re.search(r"duration=([\d.]+)", r)
    dur = float(m.group(1)) if m else 0
    if not 10 <= dur <= 15.5:
        out.append(f"長さが{dur:.1f}秒（10〜15秒）")
    if "codec_type=audio" not in r:
        out.append("音がない")
    else:
        v = subprocess.run(["ffmpeg", "-v", "info", "-i", mp4, "-vn", "-af", "volumedetect", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        mean = re.search(r"mean_volume: (-?[\d.]+) dB", v)
        peak = re.search(r"max_volume: (-?[\d.]+) dB", v)
        mean, peak = (float(mean.group(1)) if mean else -99), (float(peak.group(1)) if peak else 0)
        if not -45 <= mean <= -28:
            out.append(f"音の大きさが{mean:.0f}dB（-45〜-28dB）")
        if peak > -1:
            out.append(f"音割れのおそれ（最大{peak:.1f}dB）")
    if still is not None and dur:
        with tempfile.TemporaryDirectory() as d:
            png = os.path.join(d, "last.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(max(0, dur - 0.5)), "-i", mp4, "-frames:v", "1", png])
            if os.path.exists(png):
                from PIL import Image
                last = Image.open(png).convert("RGB")
                d2 = 999
                for k in (1.0, 0.95, 0.9):  # 全体の絵の大きさは作り方で少し違うので、いくつかの大きさで比べて一番近い物
                    s = min(1080 / still.width, 1920 * k / still.height)
                    sm = still.convert("RGB").resize((round(still.width * s), round(still.height * s)))
                    x, y = (1080 - sm.width) // 2, (1920 - sm.height) // 2
                    d2 = min(d2, image_diff(last.crop((x, y, x + sm.width, y + sm.height)), sm))
                if d2 > LAST_DIFF_MAX:
                    out.append(f"最後の画面が今日の4コマと違う（違い{d2:.0f}）")
    return out


def main():
    now = now_jst()
    if sys.argv[1:] == ["--need"]:
        print("yes" if need(now) else "no")
        return 0
    if len(sys.argv) > 2 and sys.argv[1] == "--file":  # 手元で試す：python3 scripts/videocheck.py --file 動画.mp4 [絵.png]
        from PIL import Image
        print(problems(sys.argv[2], Image.open(sys.argv[3]) if len(sys.argv) > 3 else None) or "合格")
        return 0
    if not need(now):
        return 0
    fp = koma_file(now)
    k = load_json(fp)
    day, ep = now.date().isoformat(), k.get("episode", "?")
    try:
        with tempfile.TemporaryDirectory() as d:
            mp4 = os.path.join(d, "v.mp4")
            req = urllib.request.Request(k["video_url"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r, open(mp4, "wb") as f:
                f.write(r.read())
            bad = problems(mp4, fetch_image(k["image_url"]))
    except Exception as e:
        bad = [f"動画を開けない（{str(e)[:80]}）"]
    if bad:
        k["video_error"] = "／".join(bad)
        append_log(day, f"4コマ 第{ep}話 リールは出さない（動画の確認×：{k['video_error']}）")
    else:
        k["video_ok"] = now.strftime("%H:%M")
        append_log(day, f"4コマ 第{ep}話 動画の確認OK")
    save_json(fp, k)
    return 0


if __name__ == "__main__":
    sys.exit(main())
