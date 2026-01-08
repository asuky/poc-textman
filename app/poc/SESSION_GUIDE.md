# Django セッション管理ガイド

Djangoのセッション保存場所の設定とRedisへの移行方法

## 📚 目次

1. [デフォルトのセッション保存場所](#デフォルトのセッション保存場所)
2. [利用可能なバックエンド](#利用可能なバックエンド)
3. [Redisに変更する方法](#redisに変更する方法)
4. [各バックエンドの比較](#各バックエンドの比較)
5. [セッションの設定項目](#セッションの設定項目)

---

## デフォルトのセッション保存場所

### 現在の設定

```python
# settings.py に何も設定していない場合
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # デフォルト
```

**保存場所**: データベースの `django_session` テーブル

### セッションを確認

```bash
# SQLiteの場合
cd app/poc
python manage.py dbshell

# テーブル構造を確認
.schema django_session

# セッションデータを確認
SELECT * FROM django_session;
```

---

## 利用可能なバックエンド

### 1. Database（デフォルト）

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

**メリット**:
- 設定不要（デフォルト）
- 永続化される
- トランザクション対応

**デメリット**:
- DB負荷が増える
- 速度が遅い

**用途**: 小規模サイト、開発環境

---

### 2. Cache（Redis/Memcached）

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
```

**メリット**:
- 高速
- スケーラブル

**デメリット**:
- キャッシュがクリアされるとセッションが消える
- 永続化されない

**用途**: 高速アクセスが必要、セッション消失OK

---

### 3. Cached DB（推奨）

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
```

**メリット**:
- 高速（キャッシュから読み取り）
- 安全（DBにバックアップ）
- キャッシュ消失時もDBから復元

**デメリット**:
- 書き込み時にDB + キャッシュ両方に保存

**用途**: 本番環境で推奨（速度と安全性のバランス）

---

### 4. File

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = '/tmp/django_sessions'  # 保存先
```

**メリット**:
- DB不要
- 永続化される

**デメリット**:
- ファイルI/Oが遅い
- 複数サーバー間で共有できない

**用途**: 特殊な環境、プロトタイプ

---

### 5. Signed Cookies

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
```

**メリット**:
- サーバー側にデータ保存不要
- スケーラブル

**デメリット**:
- データサイズ制限（4KB）
- クライアント側に保存（セキュリティ注意）

**用途**: ステートレスなアプリ、マイクロサービス

---

## Redisに変更する方法

### ステップ1: Redisのインストール（Docker使用）

```yaml
# compose.yaml に追加
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

起動：
```bash
docker compose up -d redis
```

### ステップ2: Pythonパッケージのインストール

```toml
# pyproject.toml に追加
dependencies = [
    "django>=6.0",
    "djangorestframework>=3.15.0",
    "redis>=5.0.0",
    "django-redis>=5.4.0",
]
```

インストール：
```bash
cd app
uv sync
```

### ステップ3: settings.py の設定

```python
# settings.py

# ============================================================
# キャッシュ設定（Redis）
# ============================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',  # DB 1を使用
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        }
    }
}

# ============================================================
# セッション設定（Redis使用）
# ============================================================

# 方法1: キャッシュのみ（高速だが永続化なし）
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 方法2: キャッシュ + DB（推奨：速度と安全性のバランス）
# SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
# SESSION_CACHE_ALIAS = 'default'

# セッション設定
SESSION_COOKIE_AGE = 1209600  # 2週間（秒単位）
SESSION_COOKIE_SECURE = False  # 本番環境では True（HTTPS必須）
SESSION_COOKIE_HTTPONLY = True  # JavaScriptからアクセス不可
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF対策
SESSION_SAVE_EVERY_REQUEST = False  # 毎リクエストで保存しない（パフォーマンス向上）
```

### ステップ4: 動作確認

```bash
# サーバー起動
cd app/poc
python manage.py runserver

# Redisに接続して確認
docker compose exec redis redis-cli
> SELECT 1
> KEYS *
> GET "<session_key>"
```

---

## 各バックエンドの比較

| 特徴 | Database | Cache | Cached DB | File | Cookie |
|------|----------|-------|-----------|------|--------|
| **速度** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| **永続性** | ✅ | ❌ | ✅ | ✅ | ❌ |
| **スケール** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐⭐ |
| **セキュリティ** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **容量制限** | なし | メモリ次第 | メモリ次第 | ディスク次第 | 4KB |
| **複数サーバー** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **推奨環境** | 小規模 | 中規模 | **本番** | テスト | API |

### 推奨

- **開発環境**: Database（デフォルト）
- **本番環境**: **Cached DB + Redis**（最もバランスが良い）
- **高トラフィック**: Cache + Redis（速度優先）
- **API専用**: Signed Cookies（ステートレス）

---

## セッションの設定項目

### settings.py で設定可能な項目

```python
# セッションエンジン
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# セッションの有効期限（秒）
SESSION_COOKIE_AGE = 1209600  # 2週間

# ブラウザを閉じたらセッション削除
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# セッションCookieの名前
SESSION_COOKIE_NAME = 'sessionid'

# セッションCookieのドメイン
SESSION_COOKIE_DOMAIN = None  # None = 現在のドメイン

# セッションCookieのパス
SESSION_COOKIE_PATH = '/'

# HTTPS接続のみでCookieを送信
SESSION_COOKIE_SECURE = False  # 本番では True

# JavaScriptからCookieにアクセス不可
SESSION_COOKIE_HTTPONLY = True

# SameSite属性（CSRF対策）
SESSION_COOKIE_SAMESITE = 'Lax'  # 'Strict', 'Lax', 'None', False

# 毎リクエストでセッションを保存
SESSION_SAVE_EVERY_REQUEST = False  # True にすると負荷増加

# セッションデータをシリアライズする方法
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# ファイルバックエンド使用時のパス
SESSION_FILE_PATH = None  # None = tempfile.gettempdir()

# キャッシュバックエンド使用時のキャッシュエイリアス
SESSION_CACHE_ALIAS = 'default'
```

---

## セッションの管理コマンド

### 期限切れセッションの削除

```bash
# データベースバックエンドの場合
python manage.py clearsessions

# 定期的に実行（cronなど）
0 3 * * * cd /path/to/project && python manage.py clearsessions
```

### セッションの確認（Python shell）

```python
python manage.py shell

from django.contrib.sessions.models import Session
from django.utils import timezone

# 全セッション数
Session.objects.count()

# 有効なセッション
Session.objects.filter(expire_date__gt=timezone.now()).count()

# 特定のセッション取得
session = Session.objects.get(session_key='<key>')
print(session.get_decoded())
```

---

## 実装例: Cached DB + Redis

### 完全な設定例

```python
# settings.py

# ============================================================
# Redis キャッシュ設定
# ============================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'myapp',  # キーのプレフィックス
        'TIMEOUT': 300,  # デフォルトタイムアウト（秒）
    }
}

# ============================================================
# セッション設定（Cached DB）
# ============================================================
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# セッション有効期限: 2週間
SESSION_COOKIE_AGE = 1209600

# セキュリティ設定
SESSION_COOKIE_SECURE = True  # HTTPS必須（本番）
SESSION_COOKIE_HTTPONLY = True  # XSS対策
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF対策

# パフォーマンス設定
SESSION_SAVE_EVERY_REQUEST = False  # 変更時のみ保存
```

### Docker Compose設定

```yaml
# compose.yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  redis_data:
```

---

## トラブルシューティング

### セッションが保存されない

1. `INSTALLED_APPS` に `django.contrib.sessions` があるか確認
2. `MIDDLEWARE` に `SessionMiddleware` があるか確認
3. マイグレーション実行: `python manage.py migrate`

### Redisに接続できない

```bash
# Redis起動確認
docker compose ps redis

# Redis接続テスト
docker compose exec redis redis-cli ping
# 「PONG」が返ればOK

# Djangoから接続テスト
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 10)
>>> cache.get('test')
'value'
```

### セッションがすぐ切れる

```python
# settings.py
SESSION_COOKIE_AGE = 86400  # 1日に延長
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # ブラウザ閉じても維持
```

---

## まとめ

### 環境別の推奨設定

**開発環境**
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # デフォルトでOK
```

**本番環境（小〜中規模）**
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
CACHES = {'default': {'BACKEND': 'django_redis.cache.RedisCache', ...}}
```

**本番環境（大規模・高トラフィック）**
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {'default': {'BACKEND': 'django_redis.cache.RedisCache', ...}}
# + セッション再生成の仕組みを実装
```

### 参考リンク

- [Django Sessions 公式](https://docs.djangoproject.com/en/stable/topics/http/sessions/)
- [django-redis](https://github.com/jazzband/django-redis)
- [Redis公式](https://redis.io/)
