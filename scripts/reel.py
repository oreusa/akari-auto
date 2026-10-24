"""4コマのリール（Instagram用の縦動画）を機械で作る。10/24から。

雫が動画を作れない日（10/24：音を聴いて確かめられないので作らなかった）でもリールを出すため。
雫の動画（koma4/日付.json の video_url）があるときは何もしない。

作り方（雫の第16話と同じ形）：1080x1920・12秒。1コマずつ2.5秒（後ろにぼかした同じコマ）→最後に4コマ全体2秒。
音は assets/bgm_303pm.mp3 を音量8％、最後の1秒で小さくする。
できた動画は Cloudflare Pages（usagi-life-reels.pages.dev）に置き、そのURLを video_url に入れる。予約は book.py。

使い方（book.yml の中）：
  python3 scripts/reel.py --need   → 今日作る必要があれば「yes」を出す
  python3 scripts/reel.py          → 作って置いて、koma4/日付.json に video_url を書く
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import append_log, fetch_image, http_raw, koma4_boxes, load_json, now_jst, path, save_json  # noqa: E402

W, H = 1080, 1920
PANEL_SEC, LAST_SEC = 2.5, 2.0
PROJECT = "usagi-life-reels"
BGM = path("assets", "bgm_303pm.mp3")
VOLUME = 0.08


def koma_file(now):
    return path("koma4", f"{now.date().isoformat()}.json")


def need(now):
    k = load_json(koma_file(now))
    cfg = load_json(path("config.json")) or {}
    return bool(k and k.get("image_url") and not k.get("video_url") and not k.get("reel_error")
                and "instagram" in cfg.get("channels", {}) and os.environ.get("CLOUDFLARE_API_TOKEN"))


def frame(fg, bg_src):
    """後ろにぼかした絵、前に fg を真ん中に置いた 1080x1920 の1枚。"""
    from PIL import Image, ImageEnhance, ImageFilter
    s = max(W / bg_src.width, H / bg_src.height)
    bg = bg_src.resize((round(bg_src.width * s), round(bg_src.height * s)))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(28))).enhance(0.8)
    s = min(W / fg.width, H * 0.95 / fg.height)
    fg = fg.resize((round(fg.width * s), round(fg.height * s)), Image.LANCZOS)
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    return bg


def frames(img):
    img = img.convert("RGB")
    boxes, _ = koma4_boxes(img)
    out = [frame(img.crop((x, y, x + bw, y + bh)), img.crop((x, y, x + bw, y + bh))) for x, y, bw, bh in boxes]
    out.append(frame(img, img))
    return out


def make_video(img, out):
    """絵から mp4 を作る。"""
    with tempfile.TemporaryDirectory() as d:
        lst = []
        for i, f in enumerate(frames(img)):
            p = os.path.join(d, f"{i}.png")
            f.save(p)
            lst.append((p, PANEL_SEC if i < 4 else LAST_SEC))
        listf = os.path.join(d, "list.txt")
        with open(listf, "w") as fh:
            for p, sec in lst:
                fh.write(f"file '{p}'\nduration {sec}\n")
            fh.write(f"file '{lst[-1][0]}'\n")  # 最後の1枚の長さを効かせるため
        total = PANEL_SEC * 4 + LAST_SEC
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", listf, "-i", BGM,
               "-filter_complex", f"[0:v]fps=30,format=yuv420p[v];[1:a]volume={VOLUME},afade=t=out:st={total - 1}:d=1[a]",
               "-map", "[v]", "-map", "[a]", "-t", str(total), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-movflags", "+faststart", out]
        subprocess.run(cmd, check=True)


def probe(p):
    """動画の中身を確かめる：縦1080x1920・12秒・音あり。だめなら理由。"""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                        "-of", "compact", p], capture_output=True, text=True)
    t = r.stdout
    if "width=1080|height=1920" not in t:
        return "大きさが1080x1920でない"
    if "codec_type=audio" not in t:
        return "音がない"
    try:
        dur = float(t.split("duration=")[-1].split()[0])
    except ValueError:
        return "長さが読めない"
    if abs(dur - (PANEL_SEC * 4 + LAST_SEC)) > 0.5:
        return f"長さが{dur:.1f}秒"
    return ""


def deploy(d):
    w = ["npx", "-y", "wrangler@3.80.0"]
    subprocess.run(w + ["pages", "project", "create", PROJECT, "--production-branch=main"], capture_output=True)
    r = subprocess.run(w + ["pages", "deploy", d, f"--project-name={PROJECT}", "--branch=main", "--commit-dirty=true"],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-300:])


def put(img, name):
    """作る→確かめる→置く→開けるか確かめる。置いたURLを返す（だめなら RuntimeError）。"""
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, f"{name}.mp4")
        make_video(img, out)
        bad = probe(out)
        if bad:
            raise RuntimeError(bad)
        deploy(d)
    url = f"https://{PROJECT}.pages.dev/{name}.mp4"
    st, body, _ = http_raw(url)
    if st != 200 or body[4:8] != b"ftyp":  # mp4 の頭の印（http_raw は頭の4KBだけ読む）
        raise RuntimeError(f"置いた動画が開けない（{st}）")
    return url


def main():
    now = now_jst()
    if len(sys.argv) > 2 and sys.argv[1] == "--test":  # online.yml：絵のURLで作って置けるかを試す（投稿しない）
        url = put(fetch_image(sys.argv[2]), "test")
        print("リールを置けた", url)
        cfg = load_json(path("config.json")) or {}
        if os.environ.get("BUFFER_API_KEY") and "instagram" in cfg.get("channels", {}):  # Bufferが受け取れるか：下書きを作ってすぐ消す
            from datetime import timedelta, timezone
            from lib import buffer_create, buffer_gql
            due = (now + timedelta(days=2)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            p = buffer_create(cfg["channels"]["instagram"], "instagram", ["リールのテスト（下書き・すぐ消す）"], due,
                              draft=True, image=sys.argv[2], video=url, alt="テスト")
            print("Bufferにリールの下書きOK", p)
            print("消した", buffer_gql('mutation($i:DeletePostInput!){deletePost(input:$i){__typename}}', {"i": {"id": p["id"]}}))
        return 0
    if sys.argv[1:] == ["--need"]:
        print("yes" if need(now) else "no")
        return 0
    if not need(now):
        print("リールは作らない（雫の動画がある、絵がまだない、など）")
        return 0
    day = now.date().isoformat()
    fp = koma_file(now)
    k = load_json(fp)
    ep = k.get("episode", "?")
    try:
        url = put(fetch_image(k["image_url"]), day)
    except Exception as e:
        k["reel_error"] = str(e)[:200]
        save_json(fp, k)
        append_log(day, f"4コマ 第{ep}話 リールを作れない：{str(e)[:150]}")
        return 0
    k["video_url"], k["video_by"] = url, "機械"
    save_json(fp, k)
    append_log(day, f"4コマ 第{ep}話 リールを機械で作った（雫の動画がないため）")
    print("リールOK", url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
