# Django プロジェクト: /poc エンドポイント

## ✅ 実装完了

Django プロジェクトに `/poc` エンドポイントを追加しました。GETリクエストで `{"status": "OK"}` というJSONを返します。

---

## 📁 追加・変更したファイル

### 1. `app/poc/poc/views.py` (新規作成)
ビュー関数を定義するファイルです。HTTPリクエストを受け取り、レスポンスを返す処理を記述します。

### 2. `app/poc/poc/urls.py` (変更)
URLルーティングを設定するファイルです。`/poc/` というURLパスを `poc_status` ビュー関数に紐付けました。

---

## 🔄 GET /poc リクエストの処理フロー

```
1. クライアント（ブラウザ等）
   ↓ GET /poc リクエスト送信
   
2. Django開発サーバ（manage.py runserver）
   ↓ リクエストを受信
   
3. ミドルウェア処理
   ↓ セキュリティ、CSRF、認証などの前処理
   
4. URLディスパッチャー（urls.py）
   ↓ URLパターンをマッチング: 'poc/' → poc_status関数
   
5. ビュー関数（views.py: poc_status）
   ↓ JsonResponse({"status": "OK"}) を生成
   
6. ミドルウェア処理
   ↓ レスポンスの後処理
   
7. Django開発サーバ
   ↓ HTTPレスポンスを送信
   
8. クライアント
   {"status": "OK"} を受信
```

---

## 🚀 開発サーバの起動方法

### 方法1: WSL環境で直接実行（推奨）

WSLのUbuntuターミナルで以下を実行：

```bash
cd /home/asuky/poc-textman/app/poc
python3 manage.py runserver
```

### 方法2: Windowsから実行

PowerShellで以下を実行：

```powershell
wsl -e bash -c "cd /home/asuky/poc-textman/app/poc && python3 manage.py runserver"
```

サーバが起動すると、以下のような出力が表示されます：

```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.

January 05, 2026 - 12:00:00
Django version 6.0, using settings 'poc.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## 🧪 エンドポイントのテスト方法

### ブラウザでアクセス
```
http://127.0.0.1:8000/poc/
```

### curlコマンドで確認
```bash
curl http://127.0.0.1:8000/poc/
```

### 期待される結果
```json
{"status": "OK"}
```

---

## 📝 Django の基本概念

### 1. **プロジェクト (Project)**
- Djangoアプリケーション全体の設定とルート構成
- `django-admin startproject` で作成
- 本プロジェクト: `app/poc/poc/` ディレクトリ

### 2. **アプリケーション (App)**
- 特定の機能を持つモジュール（今回は未使用）
- `python manage.py startapp` で作成
- 再利用可能な部品として設計

### 3. **ビュー (View)**
- HTTPリクエストを受け取り、レスポンスを返す関数/クラス
- 本プロジェクト: `views.py` の `poc_status` 関数

### 4. **URLconf (URL Configuration)**
- URLパターンとビューを紐付ける設定
- 本プロジェクト: `urls.py`

### 5. **リクエスト/レスポンス**
- `HttpRequest`: リクエスト情報を保持
- `JsonResponse`: JSON形式のレスポンスを生成

---

## 📂 プロジェクト構造

```
app/poc/
├── manage.py          # Django管理コマンド
└── poc/               # プロジェクト設定ディレクトリ
    ├── __init__.py
    ├── settings.py    # プロジェクト設定
    ├── urls.py        # URLルーティング ★変更
    ├── views.py       # ビュー関数 ★新規
    ├── asgi.py        # ASGI設定
    └── wsgi.py        # WSGI設定
```

---

## 💡 コードの詳細説明

### views.py のコード

```python
from django.http import JsonResponse

def poc_status(request):
    return JsonResponse({"status": "OK"})
```

- `request`: Djangoが自動的に渡すリクエストオブジェクト
- `JsonResponse`: 辞書をJSON形式に変換してHTTPレスポンスを生成
- Content-Type: `application/json` が自動設定される

### urls.py のコード

```python
from .views import poc_status

urlpatterns = [
    path('admin/', admin.site.urls),
    path('poc/', poc_status, name='poc_status'),
]
```

- `path('poc/', ...)`: `/poc/` というURLパスを定義
- `poc_status`: このURLにアクセスしたときに呼び出す関数
- `name='poc_status'`: このURLパターンに名前を付ける（逆引き用）

---

## ⚠️ 注意事項

1. **開発サーバは本番環境で使用しない**
   - `runserver` は開発専用です
   - 本番環境では Gunicorn、uWSGI などを使用

2. **マイグレーション警告**
   - サーバ起動時に「未適用のマイグレーションがある」という警告が出ますが、今回の機能には影響しません
   - データベースを使う場合は `python manage.py migrate` を実行

3. **セキュリティ設定**
   - `settings.py` の `DEBUG = True` は開発環境のみ
   - 本番環境では `DEBUG = False` に設定
   - `SECRET_KEY` は秘密に保管

---

## 🎓 次のステップ

Djangoをさらに学ぶには：

1. **モデル (Model)** を学ぶ
   - データベースとのやり取り
   - ORM（オブジェクト関係マッピング）

2. **アプリケーション** を作成
   - 機能ごとにアプリを分割
   - 再利用性の向上

3. **テンプレート** を使う
   - HTMLレスポンスの生成
   - Django Template Language (DTL)

4. **フォーム処理** を実装
   - POSTリクエストの処理
   - バリデーション

5. **認証機能** を追加
   - ユーザー管理
   - ログイン/ログアウト
