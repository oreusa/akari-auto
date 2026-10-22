# akari-auto（燈の自動係）

燈（うさぎちゃんアフェリエイトAI）の X・Threads の予約と数字集めを、ボタンを押さずに機械で行う置き場です。
人やGPTのリレーをなくし、決まりはプログラムで守らせます。

## だれが何をするか
| 係 | いつ | すること |
| --- | --- | --- |
| 燈（Claude） | 毎晩 | `schedule/翌日の日付.json` に翌日の投稿を書く（書き方は `docs/how-to-write.md`） |
| check | 予定表が置かれたとき | 文字数・#PR・禁止URL・代わりの投稿の有無を確かめる（×はGitHubで赤） |
| book（予約係） | 1時間おき | 2時間半以内に出す投稿を燈のBufferに予約。PRは直前に楽天に「今も売っているか」を聞き、楽天の正式リンクを入れる。だめなら代わりの投稿 |
| metrics（数字係） | 毎朝6:40 | 前日・前々日の数字を `data/metrics/日付.json` に書く |
| 雫（GPT） | 毎朝 | 4コマだけ（今までどおり） |

何が起きたかは `log/日付.md` に1行ずつ残ります。燈は毎晩これを読みます。

## 秘密の値（Settings → Secrets and variables → Actions）
`BUFFER_API_KEY`（燈のBuffer）・`RAKUTEN_APP_ID`・`RAKUTEN_ACCESS_KEY`・`RAKUTEN_AFFILIATE_ID`。
ファイルや記録には書きません。変数 `RAKUTEN_ORIGIN` は楽天のアプリに登録したサイトのURL（なければ https://github.com）。

## 決まり
- 月（うさぎちゃん不動産）のアカウントには触れません（setup が月のアカウントを見つけたら止まります）
- Amazon と楽天の短縮リンクは使いません
- 公開済みの投稿は消しません
