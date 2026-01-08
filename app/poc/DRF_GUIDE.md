# Django REST Framework 利用ガイド

Django REST Frameworkを使ったAPI開発の完全ガイド

## 📚 目次

1. [概要](#概要)
2. [インストールと設定](#インストールと設定)
3. [実装したAPI](#実装したapi)
4. [使い方](#使い方)
5. [バリデーション](#バリデーション)
6. [トランザクション](#トランザクション)
7. [HTMLビューとの比較](#htmlビューとの比較)

---

## 概要

Django REST Framework (DRF) は、DjangoでRESTful APIを構築するための強力なツールキットです。

### 主な特徴

- **自動バリデーション**: Serializerが入力データを自動検証
- **ブラウザ可能なAPI**: Web UIで簡単にテスト可能
- **認証・権限**: 多様な認証方式をサポート
- **自動ドキュメント**: Swagger/OpenAPI対応
- **N+1問題対策**: QuerySetの最適化が容易

### 公式ドキュメント

- https://www.django-rest-framework.org/
- https://www.django-rest-framework.org/tutorial/quickstart/

---

## インストールと設定

### 1. インストール

```bash
# uvを使用している場合
cd app
uv pip install djangorestframework

# pipを使用している場合
pip install djangorestframework
```

### 2. settings.py に追加

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'blog',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

---

## 実装したAPI

### エンドポイント一覧

| メソッド | URL | 説明 | 認証 |
|---------|-----|------|------|
| GET | `/blog/api/posts/` | 記事一覧を取得 | 不要 |
| GET | `/blog/api/posts/<slug>/` | 記事詳細を取得 | 不要 |
| POST | `/blog/api/posts/create/` | 記事を作成 | 必須 |
| GET | `/blog/api/categories/` | カテゴリ一覧を取得 | 不要 |

### ファイル構成

```
blog/
├── serializers.py    # シリアライザー（バリデーション + データ変換）
├── views.py          # APIビュー
└── urls.py           # URLルーティング
```

---

## 使い方

### 1. ブラウザでテスト（開発時）

Djangoサーバーを起動して、ブラウザでアクセス：

```
http://localhost:8000/blog/api/posts/
```

DRFの「Browsable API」が表示され、GUIでテストできます。

### 2. curlでテスト

#### 記事一覧を取得

```bash
curl http://localhost:8000/blog/api/posts/
```

#### 記事詳細を取得

```bash
curl http://localhost:8000/blog/api/posts/my-first-post/
```

#### 記事を作成（認証が必要）

```bash
curl -X POST http://localhost:8000/blog/api/posts/create/ \
  -H "Content-Type: application/json" \
  -u username:password \
  -d '{
    "title": "New Post",
    "slug": "new-post",
    "content": "This is the content",
    "status": "draft",
    "tag_names": ["python", "django"]
  }'
```

### 3. Pythonで呼び出し

```python
import requests

# 記事一覧を取得
response = requests.get('http://localhost:8000/blog/api/posts/')
posts = response.json()

# 記事を作成
response = requests.post(
    'http://localhost:8000/blog/api/posts/create/',
    json={
        'title': 'New Post',
        'slug': 'new-post',
        'content': 'This is the content',
        'status': 'draft',
        'tag_names': ['python', 'django']
    },
    auth=('username', 'password')
)
result = response.json()
```

---

## バリデーション

### Serializerによる自動バリデーション

DRFは、Serializerを使って入力データを自動的に検証します。

#### 基本的なバリデーション（自動）

```python
class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'status']
```

これだけで、以下が自動的に検証されます：
- 必須フィールドの存在チェック
- フィールドの型チェック
- 最大長チェック（モデル定義から）

#### カスタムバリデーション

特定のフィールドに独自のルールを追加：

```python
def validate_slug(self, value):
    """slugのカスタムバリデーション"""
    import re
    if not re.match(r'^[a-z0-9-]+$', value):
        raise serializers.ValidationError(
            'Slug can only contain lowercase letters, numbers, and hyphens'
        )
    return value
```

#### エラーレスポンス

バリデーションエラーが発生すると、自動的に400エラーを返します：

```json
{
  "slug": [
    "Post with slug \"test\" already exists"
  ],
  "title": [
    "Title cannot be empty"
  ]
}
```

### 従来の方法との比較

**❌ 従来の方法（手動バリデーション）**

```python
def create_post_api(request):
    # 必須フィールドチェック
    if 'title' not in data:
        return JsonResponse({'error': 'Title is required'}, status=400)
    
    # パターンマッチ
    if not re.match(r'^[a-z0-9-]+$', slug):
        return JsonResponse({'error': 'Invalid slug'}, status=400)
    
    # 重複チェック
    if Post.objects.filter(slug=slug).exists():
        return JsonResponse({'error': 'Slug exists'}, status=400)
```

**✅ DRFの方法（自動バリデーション）**

```python
class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    
    # バリデーションは Serializer が自動で行う！
```

---

## トランザクション

### DRFでのトランザクション処理

**重要**: DRFのGeneric Viewsは、**デフォルトで `@transaction.atomic` が適用されています**。

つまり、明示的に指定しなくても：
- 作成/更新/削除処理は自動的にトランザクション内で実行される
- エラー発生時は自動的にロールバックされる

#### 実装例

```python
class PostCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        
        # 記事を作成
        post = Post.objects.create(**validated_data)
        
        # タグを追加
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)
        
        # この全体が1つのトランザクション内で実行される
        # エラーが発生すると、すべてロールバックされる
        return post
```

#### 明示的にトランザクションを制御する場合

```python
from django.db import transaction

class PostCreateAPIView(generics.CreateAPIView):
    @transaction.atomic
    def perform_create(self, serializer):
        # 追加のトランザクション処理
        serializer.save(author=self.request.user)
```

---

## HTMLビューとの比較

このプロジェクトでは、HTMLテンプレートを使う方法とAPIの両方を実装しています。

### HTMLビュー（従来のDjango）

**ファイル**: `views.py`の上部

```python
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
```

**用途**:
- ブラウザで表示するWebページ
- テンプレート（HTML）を返す
- SEO対策が必要なページ

**URL**: `/blog/`

### APIビュー（DRF）

**ファイル**: `views.py`の下部、`serializers.py`

```python
class PostListAPIView(generics.ListAPIView):
    serializer_class = PostListSerializer
```

**用途**:
- モバイルアプリやSPAからの呼び出し
- JSON形式でデータを返す
- 外部システムとの連携

**URL**: `/blog/api/posts/`

### 比較表

| 特徴 | HTMLビュー | APIビュー |
|------|-----------|----------|
| 出力形式 | HTML | JSON |
| テンプレート | 必要 | 不要 |
| 認証 | セッション | トークン/セッション |
| バリデーション | Formで実装 | Serializerで実装 |
| 用途 | Webページ | モバイル/SPA/連携 |

### 両方を共存させる理由

1. **Webサイト**: HTMLビューで実装
2. **モバイルアプリ**: APIビューで同じデータを提供
3. **外部連携**: APIビューで他システムと連携

同じモデルとビジネスロジックを使いながら、異なるインターフェースを提供できます。

---

## まとめ

### DRFを使うメリット

1. ✅ **自動バリデーション**: 手動チェック不要
2. ✅ **標準化**: 業界標準のRESTful API設計
3. ✅ **セキュリティ**: 組み込みの認証・権限管理
4. ✅ **テストしやすい**: Serializerを独立してテスト可能
5. ✅ **ドキュメント自動生成**: Swagger/OpenAPI対応
6. ✅ **メンテナンス性**: コードが簡潔で理解しやすい

### 次のステップ

- [ ] 認証トークン（JWT）の実装
- [ ] フィルタリング機能の追加
- [ ] Swagger UIの統合
- [ ] テストコードの作成
- [ ] レート制限（throttling）の設定

### 参考リンク

- [Django REST Framework 公式](https://www.django-rest-framework.org/)
- [DRF Tutorial](https://www.django-rest-framework.org/tutorial/quickstart/)
- [DRF Generic Views](https://www.django-rest-framework.org/api-guide/generic-views/)
- [Serializers](https://www.django-rest-framework.org/api-guide/serializers/)
