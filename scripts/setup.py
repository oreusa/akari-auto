"""最初の設定。燈のBufferの中にある X・Threads・インスタ の番号を調べて config.json に書く。

GitHub の Actions で「setup」を1回動かすだけ。キーが正しいかの確認にもなる。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import buffer_gql, path, save_json  # noqa: E402

Q_ORG = "{ account { email organizations { id name limits { scheduledPosts } } } }"
Q_CH = """query($o: OrganizationId!) { channels(input: {organizationId: $o}) {
  id service name displayName isDisconnected isQueuePaused } }"""


def main():
    acc = buffer_gql(Q_ORG)["account"]
    orgs = acc["organizations"]
    if not orgs:
        print("Bufferの組織が見つかりません")
        return 1
    org = orgs[0]
    chans = buffer_gql(Q_CH, {"o": org["id"]})["channels"]
    cfg = {"organizationId": org["id"], "channels": {}, "names": {}}
    for c in chans:
        print(f"{c['service']:10} {c['name']:25} 切断={c['isDisconnected']} 停止={c['isQueuePaused']}")
        if c["service"] in ("twitter", "threads", "instagram") and c["service"] not in cfg["channels"]:
            cfg["channels"][c["service"]] = c["id"]
            cfg["names"][c["service"]] = c["name"]
    # 月（不動産）のアカウントが入っていないかを確かめる。入っていたら止める。
    names = " ".join(cfg["names"].values()).lower()
    if "fudosan" in names or "fudousan" in names:
        print("× 月（不動産）のアカウントが見つかりました。燈のBufferのキーではありません。止めます。")
        return 1
    save_json(path("config.json"), cfg)
    print("config.json を書きました:", cfg["names"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
