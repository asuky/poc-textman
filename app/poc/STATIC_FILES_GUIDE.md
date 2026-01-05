# Django 静的ファイル完全ガイド

## 📁 ディレクトリ構造

```
app/poc/
├── manage.py
├── static/              # 静的ファイルのルートディレクトリ
│   ├── css/            # スタイルシート
│   │   └── style.css
│   ├── js/             # JavaScript
│   │   └── script.js
│   └── images/         # 画像ファイル
│       └── (ここに画像を配置)
├── templates/          # HTMLテンプレート
│   └── index.html
└── poc/               # プロジェクト設定
    ├── settings.py
    ├── urls.py
    └── views.py
```

---

## ⚙️ 設定（settings.py）

### 必須の設定項目

```python
# 静的ファイルのURLプレフィックス
STATIC_URL = 'static/'

# 開発環境での静的ファイル配置場所
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# テンプレートディレクトリ
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ← これを追加
        ...
    },
]
```

---

## 🎯 静的ファイルの使い方

### 1. テンプレート内での読み込み

```html
{% load static %}  <!-- ← 必ず最初に記述 -->

<!-- CSS -->
<link rel="stylesheet" href="{% static 'css/style.css' %}">

<!-- JavaScript -->
<script src="{% static 'js/script.js' %}"></script>

<!-- 画像 -->
<img src="{% static 'images/logo.png' %}" alt="ロゴ">
```

### 2. ブラウザから直接アクセス

```
http://localhost:8000/static/css/style.css
http://localhost:8000/static/js/script.js
http://localhost:8000/static/images/logo.png
```

---

## 🔄 処理の流れ

### テンプレート読み込みの流れ

```
1. ビュー関数
   render(request, 'index.html', context)
   ↓
2. TEMPLATES の DIRS 設定を参照
   templates/index.html を検索
   ↓
3. テンプレートエンジンが処理
   {% static 'css/style.css' %} → /static/css/style.css
   ↓
4. HTMLをレンダリング
   <link rel="stylesheet" href="/static/css/style.css">
   ↓
5. クライアントへ送信
```

### 静的ファイル読み込みの流れ

```
1. ブラウザが /static/css/style.css をリクエスト
   ↓
2. Django の静的ファイルハンドラが処理
   ↓
3. STATICFILES_DIRS を検索
   static/css/style.css を発見
   ↓
4. ファイルを読み込んでレスポンス
```

---

## 📝 重要なポイント

### ✅ 開発環境（DEBUG=True）

- `python manage.py runserver` が自動的に静的ファイルを提供
- `STATICFILES_DIRS` のディレクトリから直接配信
- 設定は簡単、そのまま使える

### ⚠️ 本番環境（DEBUG=False）

本番環境では別の設定が必要：

```python
# settings.py
STATIC_ROOT = BASE_DIR / 'staticfiles'

# コマンド実行
python manage.py collectstatic
```

これにより、すべての静的ファイルが `STATIC_ROOT` に集約され、
Nginx や Apache などの Web サーバーから配信します。

---

## 🎨 ファイル追加方法

### CSS ファイルを追加

1. `static/css/新しいファイル.css` を作成
2. テンプレートに追加：
   ```html
   {% load static %}
   <link rel="stylesheet" href="{% static 'css/新しいファイル.css' %}">
   ```

### JavaScript ファイルを追加

1. `static/js/新しいスクリプト.js` を作成
2. テンプレートに追加：
   ```html
   <script src="{% static 'js/新しいスクリプト.js' %}"></script>
   ```

### 画像ファイルを追加

1. `static/images/画像.png` を配置
2. テンプレートに追加：
   ```html
   <img src="{% static 'images/画像.png' %}" alt="説明">
   ```

---

## 🚀 テスト方法

### サーバー起動

```bash
cd /home/asuky/poc-textman/app/poc
python3 manage.py runserver
```

### アクセス

```
http://127.0.0.1:8000/          # トップページ
http://127.0.0.1:8000/static/css/style.css   # CSS直接
http://127.0.0.1:8000/static/js/script.js    # JS直接
```

---

## 🔍 トラブルシューティング

### 静的ファイルが読み込まれない

1. **STATICFILES_DIRS の確認**
   ```python
   STATICFILES_DIRS = [BASE_DIR / 'static']
   ```

2. **ディレクトリ構造の確認**
   ```
   static/css/style.css  ← このパス構造か？
   ```

3. **テンプレートタグの確認**
   ```html
   {% load static %}  ← これがあるか？
   ```

4. **サーバーの再起動**
   ```bash
   Ctrl+C でサーバー停止
   python3 manage.py runserver で再起動
   ```

### ファイルが見つからない（404）

- パスの確認：`{% static 'css/style.css' %}` と `static/css/style.css` が一致しているか
- ファイルが実際に存在するか
- ファイル名の大文字小文字（Linux では区別される）

---

## 💡 ベストプラクティス

### ファイル整理

```
static/
├── css/
│   ├── base.css        # 共通スタイル
│   ├── style.css       # メインスタイル
│   └── components.css  # コンポーネント用
├── js/
│   ├── main.js         # メインスクリプト
│   └── utils.js        # ユーティリティ
└── images/
    ├── logo.png
    └── icons/
        └── favicon.ico
```

### バージョン管理

静的ファイルの更新時、ブラウザキャッシュ対策：

```html
<link rel="stylesheet" href="{% static 'css/style.css' %}?v=1.0.0">
```

または、Django のバージョニング機能を使用：

```python
# settings.py
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

---

これで静的ファイルの完全な説明は完了です！
