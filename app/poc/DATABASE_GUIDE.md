# Django データベース操作ガイド (SQLite3)

## 1. 接続先の指定方法と接続確認

### 現在の設定 (settings.py)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # プロジェクトルートに作成される
    }
}
```

### 他のデータベースへの接続（参考）
```python
# PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 接続確認コマンド
```bash
# データベースシェルを起動
python manage.py dbshell

# SQLite3の場合、以下のSQLコマンドで確認
# .tables    # テーブル一覧
# .schema    # スキーマ確認
# .exit      # 終了

# または、Pythonシェルから確認
python manage.py shell

# シェル内で実行
from django.db import connection
cursor = connection.cursor()
print("Database connection OK!")
```

### 接続テストビューの例
```python
# views.py に追加
from django.http import JsonResponse
from django.db import connection

def db_check(request):
    """データベース接続を確認"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({'status': 'ok', 'message': 'Database connection successful'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
```

---

## 2. スキーマの定義とマイグレーション

### アプリケーションの作成
```bash
# 新しいアプリを作成
python manage.py startapp blog

# settings.py の INSTALLED_APPS に追加
INSTALLED_APPS = [
    ...
    'blog',
]
```

### モデルの定義 (models.py)
```python
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """カテゴリ"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Post(models.Model):
    """ブログ記事"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', '-published_at']),
        ]
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    """コメント"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Tag(models.Model):
    """タグ（多対多の例）"""
    name = models.CharField(max_length=50, unique=True)
    posts = models.ManyToManyField(Post, related_name='tags')
    
    def __str__(self):
        return self.name
```

### マイグレーションの基本コマンド
```bash
# マイグレーションファイルを作成
python manage.py makemigrations

# 特定のアプリのみ
python manage.py makemigrations blog

# マイグレーションを適用
python manage.py migrate

# 特定のアプリのみ
python manage.py migrate blog

# マイグレーション状態を確認
python manage.py showmigrations

# 特定のマイグレーションの SQL を確認
python manage.py sqlmigrate blog 0001
```

### ロールバック
```bash
# 特定のマイグレーションまで戻る
python manage.py migrate blog 0001

# すべてのマイグレーションを取り消し（アプリのテーブルを削除）
python manage.py migrate blog zero

# すべてのアプリを初期状態に
python manage.py migrate --fake-initial
```

### マイグレーションのベストプラクティス
```bash
# マイグレーション前にバックアップ
cp db.sqlite3 db.sqlite3.backup

# 本番環境では--planオプションで事前確認
python manage.py migrate --plan

# ダミーマイグレーション（実際には実行せずマークのみ）
python manage.py migrate --fake
```

---

## 3. N+1問題を避けたCRUD操作とトランザクション

### N+1問題とは
1回のクエリで取得したデータに対して、関連データを取得するために繰り返しクエリが発行される問題。

### select_related() - 1対1、多対1
```python
# ❌ BAD: N+1問題が発生
posts = Post.objects.all()
for post in posts:
    print(post.author.username)  # 各投稿ごとにクエリが発行される

# ✅ GOOD: JOIN を使用
posts = Post.objects.select_related('author', 'category').all()
for post in posts:
    print(post.author.username)  # 1回のJOINクエリで取得済み
```

### prefetch_related() - 多対多、逆参照
```python
# ❌ BAD: N+1問題が発生
posts = Post.objects.all()
for post in posts:
    print(post.comments.count())  # 各投稿ごとにクエリが発行される

# ✅ GOOD: 別クエリで一括取得
posts = Post.objects.prefetch_related('comments', 'tags').all()
for post in posts:
    print(post.comments.count())  # キャッシュから取得

# Prefetch オブジェクトで詳細制御
from django.db.models import Prefetch

posts = Post.objects.prefetch_related(
    Prefetch('comments', queryset=Comment.objects.select_related('author'))
).all()
```

### CRUD操作の例
```python
from django.db import transaction
from django.shortcuts import get_object_or_404

# ========================================
# CREATE
# ========================================

# 基本的な作成
post = Post.objects.create(
    title="Sample Post",
    slug="sample-post",
    author=request.user,
    content="Content here",
    status='draft'
)

# 外部キーの設定
category = Category.objects.get(name='Technology')
post.category = category
post.save()

# 多対多の追加
tag1 = Tag.objects.get(name='Python')
tag2 = Tag.objects.get(name='Django')
post.tags.add(tag1, tag2)

# または get_or_create を使用
category, created = Category.objects.get_or_create(
    name='Technology',
    defaults={'description': 'Tech articles'}
)

# ========================================
# READ
# ========================================

# 全件取得（N+1を避ける）
posts = Post.objects.select_related('author', 'category').prefetch_related('comments', 'tags').all()

# フィルタリング
published_posts = Post.objects.filter(status='published').select_related('author')

# 複雑な条件
from django.db.models import Q
posts = Post.objects.filter(
    Q(status='published') & (Q(category__name='Technology') | Q(category__name='Science'))
).select_related('author', 'category')

# 1件取得
post = Post.objects.select_related('author', 'category').get(id=1)
# または
post = get_object_or_404(Post.objects.select_related('author'), id=1)

# 集計
from django.db.models import Count, Avg
categories = Category.objects.annotate(
    post_count=Count('posts'),
    avg_comments=Avg('posts__comments')
)

# 最新N件
recent_posts = Post.objects.select_related('author').order_by('-created_at')[:10]

# EXISTS チェック
has_posts = Post.objects.filter(author=request.user).exists()

# ========================================
# UPDATE
# ========================================

# 単一レコード更新
post = Post.objects.get(id=1)
post.title = "Updated Title"
post.save()

# 特定フィールドのみ更新（パフォーマンス向上）
post.save(update_fields=['title', 'updated_at'])

# 一括更新
Post.objects.filter(status='draft').update(status='published')

# F式を使った更新（競合回避）
from django.db.models import F
Post.objects.filter(id=1).update(view_count=F('view_count') + 1)

# ========================================
# DELETE
# ========================================

# 単一削除
post = Post.objects.get(id=1)
post.delete()

# 一括削除
Post.objects.filter(status='draft').delete()

# 論理削除（物理削除の代わり）
# models.py にフィールド追加
# is_deleted = models.BooleanField(default=False)
# deleted_at = models.DateTimeField(null=True, blank=True)

from django.utils import timezone
Post.objects.filter(id=1).update(is_deleted=True, deleted_at=timezone.now())
```

### トランザクション
```python
from django.db import transaction

# デコレータ形式
@transaction.atomic
def create_post_with_comments(title, content, comment_texts):
    """投稿とコメントを同時に作成（全て成功または全て失敗）"""
    post = Post.objects.create(
        title=title,
        slug=slugify(title),
        author=get_current_user(),
        content=content
    )
    
    for comment_text in comment_texts:
        Comment.objects.create(
            post=post,
            author=get_current_user(),
            content=comment_text
        )
    
    return post

# コンテキストマネージャ形式
def update_post_and_notify(post_id, new_title):
    try:
        with transaction.atomic():
            post = Post.objects.select_for_update().get(id=post_id)
            post.title = new_title
            post.save()
            
            # 通知作成など他の操作
            notify_followers(post)
            
    except Exception as e:
        # ロールバックは自動的に行われる
        print(f"Error: {e}")

# セーブポイント（ネストしたトランザクション）
def complex_operation():
    with transaction.atomic():
        # 外側のトランザクション
        post = Post.objects.create(title="Main Post")
        
        try:
            with transaction.atomic():
                # 内側のトランザクション（セーブポイント）
                comment = Comment.objects.create(post=post, content="Bad comment")
                raise Exception("Oops!")
        except Exception:
            # 内側だけロールバック、外側は継続
            pass
        
        # postは保存される
        return post

# 悲観的ロック
with transaction.atomic():
    post = Post.objects.select_for_update().get(id=1)
    post.view_count += 1
    post.save()
```

### ビューでの実践例
```python
from django.views.generic import ListView, DetailView, CreateView
from django.db import transaction

class PostListView(ListView):
    """投稿一覧（N+1対策済み）"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        return Post.objects.filter(
            status='published'
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags',
            Prefetch('comments', queryset=Comment.objects.select_related('author'))
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-published_at')


class PostDetailView(DetailView):
    """投稿詳細（N+1対策済み）"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags',
            Prefetch('comments', queryset=Comment.objects.select_related('author').order_by('created_at'))
        )


@transaction.atomic
def create_post_api(request):
    """API: 投稿作成（トランザクション使用）"""
    from django.http import JsonResponse
    import json
    
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # トランザクション内で複数のDB操作
        post = Post.objects.create(
            title=data['title'],
            slug=data['slug'],
            author=request.user,
            content=data['content'],
            status='draft'
        )
        
        # タグの追加
        tag_names = data.get('tags', [])
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)
        
        return JsonResponse({'id': post.id, 'status': 'created'})
```

### デバッグ: 実行されたクエリを確認
```python
from django.db import connection
from django.db import reset_queries

# settings.py で DEBUG = True の時のみ動作
reset_queries()

# クエリを実行
posts = Post.objects.select_related('author').all()
for post in posts:
    print(post.title)

# 実行されたクエリを表示
print(len(connection.queries), "queries")
for query in connection.queries:
    print(query['sql'])
```

### django-debug-toolbar の使用（推奨）
```bash
pip install django-debug-toolbar
```

```python
# settings.py
INSTALLED_APPS = [
    ...
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    ...
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# urls.py
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

---

## 4. Scaffolding（管理画面）

Django には Ruby on Rails のような scaffold コマンドはありませんが、**管理画面（Admin）** が非常に強力です。

### 基本的な管理画面登録
```python
# admin.py
from django.contrib import admin
from .models import Category, Post, Comment, Tag

# シンプルな登録
admin.site.register(Category)
admin.site.register(Tag)

# カスタマイズした登録
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 一覧画面に表示するフィールド
    list_display = ['title', 'author', 'category', 'status', 'created_at']
    
    # フィルタリング
    list_filter = ['status', 'category', 'created_at']
    
    # 検索
    search_fields = ['title', 'content']
    
    # 編集画面のレイアウト
    fieldsets = [
        ('基本情報', {
            'fields': ['title', 'slug', 'author', 'category']
        }),
        ('内容', {
            'fields': ['content', 'status']
        }),
        ('日時', {
            'fields': ['published_at'],
            'classes': ['collapse']
        }),
    ]
    
    # 自動入力
    prepopulated_fields = {'slug': ('title',)}
    
    # 日付階層
    date_hierarchy = 'created_at'
    
    # ページネーション
    list_per_page = 50
    
    # 並び順
    ordering = ['-created_at']
    
    # 多対多フィールドの表示改善
    filter_horizontal = ['tags']  # または filter_vertical


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'post__title']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
```

### インライン編集（関連モデルを同時編集）
```python
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at']
    
    # コメントをインライン表示
    inlines = [CommentInline, TagInline]


class CommentInline(admin.TabularInline):  # またはStackedInline
    model = Comment
    extra = 1  # 空のフォームを1つ表示
    fields = ['author', 'content']


class TagInline(admin.TabularInline):
    model = Tag.posts.through
    extra = 1
```

### カスタムアクション
```python
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at']
    actions = ['make_published', 'make_draft']
    
    @admin.action(description='選択した投稿を公開する')
    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated}件の投稿を公開しました。')
    
    @admin.action(description='選択した投稿を下書きにする')
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated}件の投稿を下書きにしました。')
```

### 管理画面にアクセス
```bash
# スーパーユーザーを作成
python manage.py createsuperuser

# 開発サーバーを起動
python manage.py runserver

# ブラウザで http://localhost:8000/admin/ にアクセス
```

### サードパーティ製Scaffoldingツール

#### 1. django-admin-generator
```bash
pip install django-admin-generator

# 自動的にadmin.pyを生成
python manage.py admin_generator blog > blog/admin.py
```

#### 2. cookiecutter-django
プロジェクト全体のテンプレート
```bash
pip install cookiecutter
cookiecutter https://github.com/cookiecutter/cookiecutter-django
```

#### 3. django-extensions
便利なコマンド追加
```bash
pip install django-extensions

# グラフでモデルを可視化
python manage.py graph_models -a -o models.png
```

---

## チートシート

### よく使うコマンド
```bash
# マイグレーション
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# データベース
python manage.py dbshell
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json

# 開発
python manage.py runserver
python manage.py shell
python manage.py createsuperuser

# データリセット
python manage.py flush  # 全データ削除（構造は維持）
```

### Djangoシェルでの便利な操作
```python
# シェル起動
python manage.py shell

# モデルのインポート
from blog.models import Post, Category, Comment
from django.contrib.auth.models import User

# クエリ数を確認しながら実行
from django.db import connection, reset_queries
reset_queries()
# ... クエリ実行 ...
print(len(connection.queries), "queries executed")

# テストデータ作成
for i in range(100):
    Post.objects.create(
        title=f"Post {i}",
        slug=f"post-{i}",
        author=User.objects.first(),
        content="Lorem ipsum..."
    )
```

---

## トラブルシューティング

### マイグレーションエラー
```bash
# マイグレーションファイルを削除して再作成
rm blog/migrations/000*.py
python manage.py makemigrations blog

# マイグレーション状態をリセット
python manage.py migrate --fake blog zero
python manage.py migrate blog
```

### SQLite ロック問題
```python
# settings.py で timeout を増やす
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}
```

### クエリパフォーマンス確認
```bash
pip install django-debug-toolbar
# または
pip install django-silk
```

---

開発サーバーを起動してテストしたい場合は、以下を実行してください：
```bash
cd app/poc
python manage.py runserver
```
