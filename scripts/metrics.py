"""数字係。毎朝、前の日に出た投稿の数字（閲覧・反応など）を Buffer から取り、data/metrics/日付.json に書く。

燈は毎晩これを読んで学ぶ。澪の手作業の台帳の代わり。
2日前の分も取り直す（数字は1日たってから増えるため）。
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import JST, append_log, buffer_gql, load_json, now_jst, path, save_json  # noqa: E402

Q = """query($o: OrganizationId!, $ch: [ChannelId!], $s: DateTime, $e: DateTime, $after: String) {
  posts(first: 50, after: $after, input: {organizationId: $o,
        filter: {channelIds: $ch, status: [sent], dueAt: {start: $s, end: $e}}}) {
    edges { node { id channelService dueAt sentAt text externalLink
                   metrics { type value } } }
    pageInfo { hasNextPage endCursor } } }"""


def slot_of(state, post_id):
    for key, rec in state.items():
        for s, r in rec.items():
            if isinstance(r, dict) and r.get("id") == post_id:
                return key.split(" ")[1], r.get("kind")
    return None, None


def fetch_day(cfg, state, day):
    start = datetime.fromisoformat(f"{day}T00:00").replace(tzinfo=JST).astimezone(timezone.utc)
    end = start + timedelta(days=1)
    rows, after = [], None
    while True:
        d = buffer_gql(Q, {"o": cfg["organizationId"], "ch": list(cfg["channels"].values()),
                           "s": start.isoformat().replace("+00:00", "Z"),
                           "e": end.isoformat().replace("+00:00", "Z"), "after": after})["posts"]
        for e in d["edges"] or []:
            n = e["node"]
            slot, kind = slot_of(state, n["id"])
            sent = n.get("sentAt") or n.get("dueAt")
            rows.append({
                "service": n["channelService"],
                "slot": slot or (datetime.fromisoformat(sent.replace("Z", "+00:00")).astimezone(JST).strftime("%H:%M") if sent else ""),
                "kind": kind or "手動",
                "first": (n["text"] or "").splitlines()[0][:40],
                "url": n.get("externalLink"),
                "metrics": {m["type"]: m["value"] for m in (n.get("metrics") or [])},
            })
        if not d["pageInfo"]["hasNextPage"]:
            break
        after = d["pageInfo"]["endCursor"]
    rows.sort(key=lambda r: (r["slot"], r["service"]))
    return rows


def main():
    cfg = load_json(path("config.json"))
    state = load_json(path("state", "booked.json"), {})
    today = now_jst().date()
    for back in (1, 2):
        day = (today - timedelta(days=back)).isoformat()
        rows = fetch_day(cfg, state, day)
        save_json(path("data", "metrics", f"{day}.json"),
                  {"day": day, "fetchedAt": now_jst().isoformat(timespec="minutes"), "posts": rows})
        if back == 1:
            views = sum(r["metrics"].get("views", r["metrics"].get("impressions", 0)) or 0 for r in rows)
            append_log(day, f"数字：{len(rows)}本、閲覧合計 {int(views)}（data/metrics/{day}.json）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
