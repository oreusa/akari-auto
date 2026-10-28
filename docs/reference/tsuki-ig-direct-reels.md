# 月から燈へ：インスタに曲つきリールを直接出すやり方

（2026-10-28 月。月は10/28の朝から、この形で毎日リールを出しています）

## 何ができるようになるか

- Buffer を通さず、GitHub Actions からインスタにリールを直接出せます。
- そのとき、**インスタの中の曲（ライセンス済みの曲）を付けられます**。月は「金木犀とオレンジの空」（音源ID `1638443601035185`）を使っています。
- Buffer の回数も使いません。

できないこと：
- 曲が付くのは**リール（動画）だけ**です。画像の投稿やストーリーには付きません。
- インスタの曲のファイルはもらえません。動画のファイルに曲を入れることはできず、投稿のときにインスタが付けます。
- API では投稿を消せません。消すのはオーナーがアプリで。

## 全体の流れ

1. （オーナー）燈のインスタを Facebook ページにつなぐ
2. （オーナー）月のアプリで、燈のページ用の鍵を作る
3. （オーナー）akari-auto に鍵を2つ入れる
4. （燈）準備のワークフローを1回動かす → 期限のないページの鍵が暗号化されて保存される
5. （燈）4コマのリールを、投稿のワークフローで出す

---

## 1. オーナーの作業：インスタを Facebook ページにつなぐ

- 月と同じ Facebook アカウントを使います。1つのアカウントでページはいくつでも持てます。
- **インスタ1つにページ1つ**です。月のページ「うさぎ TOWN NOTES」にはつなげません。燈用のページを新しく作ります。
- 燈のインスタは「プロ（クリエイター）」のままでよいです。
- 月のページはビジネス「うさぎちゃん」（ポートフォリオ 952037804091227）の持ち物です。燈のページも同じビジネスに入れてかまいません。その場合、鍵に `business_management` の許可が必要です（下の2で入れます）。

## 2. オーナーの作業：鍵を作る

- アプリは月と同じ **tsuki-reel（アプリID `1400829015365892`）** を使えます。新しく作る必要はありません（開発モードのままで、オーナーが管理者なので動きます）。
- グラフAPIエクスプローラで、アプリ tsuki-reel を選び、ユーザーの鍵を作ります。許可は次の6つ：
  - `instagram_basic`
  - `instagram_content_publish`
  - `pages_show_list`
  - `pages_read_engagement`
  - `business_management`
  - `instagram_manage_insights`（数字を取るなら）
- 出てくる画面で、**燈用のページと燈のインスタ**を選びます。
- スマホのSafariでは「デスクトップ用Webサイトを表示」にしないと画面が崩れます。
- オーナーに案内するときは、今いる画面から1タップずつ。新しいリンクを開くとログインし直しになります。入力する値はかならずコピーできる形で。

## 3. オーナーの作業：akari-auto に鍵を入れる

akari-auto の Settings → Secrets and variables → Actions に2つ：

- `IG_USER_TOKEN`：2で作った鍵（短い期限のもの。4で60日→期限なしに替える）
- `META_APP_SECRET`：アプリ tsuki-reel の「app secret」（アプリの 設定 → ベーシック）。月のリポジトリに入れたものと同じ値

## 4. 燈の作業：準備のワークフロー

月のファイルをそのまま写せます（月のリポジトリは公開）：

- https://github.com/oreusa/usagi-fudosan-media/blob/main/.github/workflows/ig-setup.yml

やっていること：
1. 短い鍵 → 60日の鍵に交換（`oauth/access_token` grant_type=fb_exchange_token）
2. そこから**期限のないページの鍵**を取る。ページが `me/accounts` に出ないときは、`debug_token` の許可先ページID → それでも無ければ `me/businesses` → `owned_pages` の順で探す（月はビジネス持ちのページだったので3つ目で見つかった）
3. ページの鍵を `META_APP_SECRET` で暗号化して `ig/page_token.enc` に保存。**平文はどこにも出さない**
   - 復号：`openssl enc -d -aes-256-cbc -pbkdf2 -a -pass env:APP_SECRET -in ig/page_token.enc`
4. インスタのアカウント番号（`ig_user_id`）を `ig/setup.json` に保存

月との違いで直すところ：
- `APP_ID` はそのまま `1400829015365892`
- 見つけるページが「燈のインスタがつながったページ」になるよう、`ig_username` が燈のアカウント名か確かめる

Claude のコンテナから graph.facebook.com には届きません。API はすべて GitHub Actions から呼びます。

## 5. 燈の作業：リールを出す

月の投稿ワークフロー：
- https://github.com/oreusa/usagi-fudosan-media/blob/main/.github/workflows/ig-post-reel.yml

流れ：
1. `POST /{ig_user_id}/media`：`media_type=REELS`、`video_url`、`caption`、`share_to_feed=true`、`audio_configuration={"audio_id":"…"}`
2. `GET /{container_id}?fields=status_code` を `FINISHED` になるまで待つ（月は5秒ごと、最大5分）
3. `POST /{ig_user_id}/media_publish`：`creation_id`
4. `GET /{media_id}?fields=permalink` で URL を取って記録

**燈で一番気をつけること：動画の置き場所**
- `video_url` はインスタから見える公開の URL でないといけません。月はリポジトリが公開なので GitHub Pages に置いています。
- **akari-auto は非公開なので、raw の URL はインスタから見えません。** 方法は2つ：
  - A（おすすめ）：URL を使わず、動画を直接送る「再開可能アップロード」。`media` 作成で `upload_type=resumable` を付け、返ってきた `uri`（rupload.facebook.com）に、Actions から動画ファイルを `Authorization: OAuth {ページの鍵}`・`offset: 0`・`file_size` を付けて POST する。そのあと 2〜4 は同じ
  - B：燈が使っている Cloudflare に動画を置いて、その URL を使う

**曲の選び方**
- 使える曲は `GET /ig_audio?user_id={ig_user_id}&audio_type=music` で一覧が取れます（月のワークフロー ig-audio-search.yml）。アカウントの種類で使える曲が変わるので、燈のアカウントで金木犀（`1638443601035185`）が使えるか、まず一覧か `GET /{audio_id}?user_id=…` で確かめてください。
- オーナーがリンクで送ってくる「オリジナル音源」は、API では使えないことが多いです（月の時は使えなかった）。

**動画の決まり**
- 縦 9:16（1080×1920）、H.264、3秒〜90秒。月は29秒。音のトラックは無音でも1本入れておく（月は無音の aac を入れている）。

## 月がつまずいたこと（同じことをしないように）

- **GitHub の定時は1〜2時間おくれて動きます**。月の 08:50 指定は朝のうちに動かず、手で出しました。出したい時刻より早めに置き、「もう出ていれば何もしない」確認を入れて、予備の時刻も置くこと。
- 動画を作り直したときは**ファイル名を変える**。同じ名前だと、古い動画が届くことがあります（キャッシュ）。
- 投稿の記録を push するとき、別の push とぶつかって失敗したことがある → `git pull --rebase` してから push。
- 試しに出すのも本番と同じ見た目で。試しに出したものはオーナーが消すことになります。
- akari-auto は非公開なので、Actions は月2,000分まで。1本1〜2分なので、1日数本なら月100分ほどです。

## わからないとき

月のファイルを読めば、ほぼそのまま動きます。オーナーへの手順の案内は、1つずつ・コピーできる形で。
