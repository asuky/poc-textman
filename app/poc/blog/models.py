from django.db import models
from django.contrib.auth.models import User

# ============================================================
# ブログアプリのモデル定義
# ============================================================
# このファイルでは、ブログシステムに必要な以下のモデルを定義します：
# - Category: カテゴリ（1対多の例）
# - Post: ブログ記事（外部キー、インデックス、ステータス管理）
# - Comment: コメント（1対多の例）
# - Tag: タグ（多対多の例）
# ============================================================


class Category(models.Model):
    """
    カテゴリモデル
    
    ブログ記事を分類するためのカテゴリを管理します。
    1つのカテゴリに複数の記事が紐づく（1対多）関係です。
    """
    # フィールド定義
    name = models.CharField(
        max_length=100,
        unique=True,  # カテゴリ名は一意である必要がある
        verbose_name='カテゴリ名',
        help_text='カテゴリの名前（例: Technology, Sports）'
    )
    description = models.TextField(
        blank=True,  # 空白を許可（必須ではない）
        verbose_name='説明',
        help_text='カテゴリの詳細説明'
    )
    
    # 自動的にタイムスタンプを記録
    created_at = models.DateTimeField(
        auto_now_add=True,  # 作成時に自動設定
        verbose_name='作成日時'
    )
    updated_at = models.DateTimeField(
        auto_now=True,  # 更新時に自動更新
        verbose_name='更新日時'
    )
    
    class Meta:
        # 管理画面での表示名（複数形）
        verbose_name_plural = "Categories"
        verbose_name = "カテゴリ"
        
        # デフォルトの並び順（名前の昇順）
        ordering = ['name']
        
        # テーブル名を明示的に指定したい場合（オプション）
        # db_table = 'blog_category'
    
    def __str__(self):
        """
        オブジェクトの文字列表現
        管理画面やシェルで表示される際に使用されます
        """
        return self.name


class Post(models.Model):
    """
    ブログ記事モデル
    
    ブログの投稿を管理します。
    ユーザー（author）とカテゴリへの外部キーを持ちます。
    """
    # ステータスの選択肢を定義
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('published', '公開済み'),
    ]
    
    # 基本フィールド
    title = models.CharField(
        max_length=200,
        verbose_name='タイトル',
        help_text='記事のタイトル'
    )
    slug = models.SlugField(
        unique=True,  # URL用の一意な識別子
        verbose_name='スラッグ',
        help_text='URL用の識別子（例: my-first-post）'
    )
    content = models.TextField(
        verbose_name='本文',
        help_text='記事の本文'
    )
    
    # 外部キー（リレーション）
    author = models.ForeignKey(
        User,  # Djangoの組み込みユーザーモデル
        on_delete=models.CASCADE,  # ユーザーが削除されたら記事も削除
        related_name='posts',  # 逆参照用（user.posts.all()でアクセス可能）
        verbose_name='著者'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # カテゴリが削除されてもNULLに設定（記事は残す）
        null=True,  # NULLを許可
        blank=True,  # フォームで空白を許可
        related_name='posts',  # category.posts.all()でアクセス可能
        verbose_name='カテゴリ'
    )
    
    # ステータス管理
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,  # 選択肢を制限
        default='draft',
        verbose_name='ステータス'
    )
    
    # タイムスタンプ
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='作成日時'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新日時'
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='公開日時',
        help_text='記事が公開された日時'
    )
    
    class Meta:
        verbose_name = "記事"
        verbose_name_plural = "記事一覧"
        
        # デフォルトの並び順（作成日時の降順 = 新しい順）
        ordering = ['-created_at']
        
        # インデックスを設定してクエリパフォーマンスを向上
        indexes = [
            models.Index(fields=['slug']),  # スラッグでの検索を高速化
            models.Index(fields=['status', '-published_at']),  # ステータスと公開日での検索を高速化
        ]
    
    def __str__(self):
        return self.title
    
    def publish(self):
        """
        記事を公開するビジネスロジック
        
        ステータスを'published'に変更し、公開日時を設定します。
        """
        from django.utils import timezone
        self.status = 'published'
        if not self.published_at:
            self.published_at = timezone.now()
        self.save()


class Comment(models.Model):
    """
    コメントモデル
    
    ブログ記事に対するコメントを管理します。
    Postとの1対多の関係を持ちます（1つの記事に複数のコメント）。
    """
    # 外部キー
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,  # 記事が削除されたらコメントも削除
        related_name='comments',  # post.comments.all()でアクセス可能
        verbose_name='記事'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # ユーザーが削除されたらコメントも削除
        verbose_name='投稿者'
    )
    
    # コメント本文
    content = models.TextField(
        verbose_name='コメント内容'
    )
    
    # タイムスタンプ
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='投稿日時'
    )
    
    class Meta:
        verbose_name = "コメント"
        verbose_name_plural = "コメント一覧"
        
        # デフォルトの並び順（投稿日時の昇順 = 古い順）
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Tag(models.Model):
    """
    タグモデル
    
    記事にタグ付けするためのモデルです。
    Postとの多対多の関係を持ちます（1つの記事に複数のタグ、1つのタグが複数の記事に紐づく）。
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='タグ名'
    )
    
    # 多対多のリレーション
    posts = models.ManyToManyField(
        Post,
        related_name='tags',  # post.tags.all()でアクセス可能
        blank=True,  # タグが記事に紐づいていなくてもOK
        verbose_name='記事一覧'
    )
    
    class Meta:
        verbose_name = "タグ"
        verbose_name_plural = "タグ一覧"
        ordering = ['name']
    
    def __str__(self):
        return self.name
