## Windows に mkcert 入れる
確認はホスト側でやるので、
```Powershell
PS C:\Users\asuky> winget install mkcert
'msstore' ソースでは、使用する前に次の契約を表示する必要があります。
Terms of Transaction: https://aka.ms/microsoft-store-terms-of-transaction
ソースが正常に機能するには、現在のマシンの 2 文字の地理的リージョンをバックエンド サービスに送信する必要があります (例: "US")。

すべてのソース契約条件に同意しますか?
[Y] はい  [N] いいえ: y
見つかりました mkcert [FiloSottile.mkcert] バージョン 1.4.4
このアプリケーションは所有者からライセンス供与されます。
Microsoft はサードパーティのパッケージに対して責任を負わず、ライセンスも付与しません。
ダウンロード中 https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-windows-amd64.exe
  ██████████████████████████████  4.66 MB / 4.66 MB
インストーラーハッシュが正常に検証されました
パッケージのインストールを開始しています...
パス環境変数が変更されました; 新しい値を使用するにはシェルを再起動してください。
コマンド ライン エイリアスが追加されました: "mkcert"
インストールが完了しました
```
一度 PowerShell を終了する (exit)。

```PowerShell
PS C:\Users\asuky> mkcert --install
Created a new local CA 💥
The local CA is now installed in the system trust store! ⚡️
（警告が出るので「はい」）
PS C:\Users\asuky> mkcert -CAROOT
C:\Users\asuky\AppData\Local\mkcert
```
WSL の場合は /mnt/c に C ドライブがマウントされているのでそのまま cp できる。

```bash
sudo cp /mnt/c/Users/asuky/AppData/Local/mkcert/rootCA.pem /usr/local/share/ca-certificates/mkcert-rootCA.crt
sudo update-ca-certificates
```

hosts に関しては Windows の場合は WSL と勝手に同期される（らしい、未検証）。
気になる場合は /etc/wsl.conf の generateHosts を見る。

## docker login できない
docker を直接 WSL 側に入れた場合（未検証）。

- 必要パッケージ入れる
```bash
$ sudo apt update
$ sudo apt install libsecret-1-0 gnupg2 pass
```
- [docker-credential-pass](https://github.com/docker/docker-credential-helpers/releases) が必要、WSL なら linux-amd64 か

```bash
$ curl -LO https://github.com/docker/docker-credential-helpers/releases/download/v0.9.4/docker-credential-pass-v0.9.4.linux-amd64
$ sudo mv docker-credential-pass-v0.9.4.linux-amd64 /usr/local/bin/docker-credential-pass
$ sudo chmod +x /usr/local/bin/docker-credential-pass
$ docker-credential-pass version
docker-credential-pass (github.com/docker/docker-credential-helpers) v0.9.4 # 動作確認
$ gpg init
# ユーザ名とメールアドレスとパスワードを入れる
# 生成後の pub の下に出るフィンガープリント？を控える
$ pass init {控えたフィンガープリント}
# pinentry の変更
$ sudo apt install pinentry-curses
$ mkdir -p ~/.gnupg
$ echo "pinentry-program /usr/bin/pinentry-curses" >> ~/.gnupg/gpg-agent.conf
$ chmod 700 ~/.gnupg
$ chmod 600 ~/.gnupg/gpg-agent.confv
# gpg-agent 再起動
$ gpgconf --kill gpg-agent
$ gpgconf --launch gpg-agent
# gpg-agent の端末有無確認
$ echo $GPG_TTY
# 無いなら設定、.bashrc へ追記
$ export GPG_TTY=$(tty)
$ echo 'export GPG_TTY=$(tty)' >> ~/.bashrc
$ docker login
# -u 使わない、パスワード入れる
```

# Django メモ
ある程度のステップで copilot に下記依頼すること。
```
ここまででまだまとめられてない会話の内容を prompts/YYYYMMDD-枝番.md にまとめてください。
フォーマットは問いませんが、こちらの発言内容自体は identical に記載してください。
```
## Django 開始手順
app ディレクトリ内前提
project が全体、app が機能単位、project 内の app は project の設定を共有する。
```bash
$ uv venv
$ uv init
$ uv add django
$ uv run django-admin startproject {project_name} .
# とりあえず動作確認
$ uv run python manage.py runserver
# .gitignore 追加
$ touch {project_name}/.gitignore
```
.gitignore
```gitignore
# ---- Python ----
__pycache__/
*.py[cod]
*.pyo
*.pyd

# ---- Virtual Environment (uv / venv) ----
.venv/
venv/

# ---- Django ----
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media/
staticfiles/

# ---- OS / Editor ----
.DS_Store
Thumbs.db
.vscode/
.idea/

```

## 管理
uv run python manage.py の後へ

|やること|コマンド|
|-|-|
|サーバ起動|runserver|
|マイグレーション作成|makemigrations|
|マイグレーション実行|migrate|
|管理ユーザー作成|createsuperuser|
|アプリ作成|startapp {appname}|

## wsgi/asgi
ChatGPT に聞いた結果、asgi only で良さそう。
runserver は内部的に asgi で、django channels を入れると asgi 相当の挙動になるらしい。
```
結論（短く）
- ASGI で困ることはほぼ無い
- それでも WSGI が選ばれる現場は今も多い

理由は「歴史・安定性・依存関係・運用の単純さ」

1️⃣ 「WSGI でないと困る」典型ケース
① レガシー環境・制約のある基盤
Apache + mod_wsgi 固定
社内標準が WSGI
セキュリティ審査済み構成
👉 ASGI を入れられない

② ライブラリ・ミドルウェアの制約（意外と多い）
一部の Django middleware / 拡張
「非同期非対応」を前提にした設計
ASGI でも 動くが内部で thread 化されるため：
想定外のパフォーマンス劣化
デバッグ困難

③ DB アクセス中心の業務アプリ
リクエストの大半が
ORM
テンプレート
同期 I/O
👉 ASGI のメリットが出ない

④ プロセスモデルを厳密に管理したい
Gunicorn（WSGI）は：
worker 数
preload
graceful reload
が 非常に枯れている。

ASGI は：
event loop
async / sync 混在
で トラブルシュートが難しい。

2️⃣ ASGI を選ばない「現実的理由」
「後から WebSocket したくなる」は本当？
実際には ならない案件も多い
要件追加より API 拡張の方が多い

👉 将来性だけで ASGI にする必要はない

3️⃣ パフォーマンス面の誤解
よくある勘違い
❌ ASGI = 高速
❌ async = スケールする

実際は：
同期 ORM がボトルネック
ASGI でも thread pool 行き

4️⃣ 「WSGI の方が安全」なケース
観点	WSGI	ASGI
運用の単純さ	◎	△
障害解析	◎	△
チーム理解	◎	△
WebSocket	✕	◎
5️⃣ 実務での選択パターン（本音）
パターンA：WSGI（今も最多）
管理画面
業務 CRUD
API サーバ

パターンB：ASGI（増加中）
チャット
通知
SaaS

パターンC：混在
HTTP: WSGI
WS: ASGI

6️⃣ 「最初から ASGI」はアリ？
アリだが条件付き。
チーム全員が async を理解
Channels / Uvicorn 前提
非同期 I/O を多用
そうでなければ：
WSGI + 必要になったら ASGI

が最も事故が少ない。

7️⃣ 一言でまとめると
WSGI は「不要」ではなく「保守的に正しい選択肢」
ASGI は可能性
WSGI は安定
```

## 書き方
### ルーティング
- urls.py に path を追加する
- views.py にロジックの関数を書く
- urls.py に書いたロジックの関数を追加する


