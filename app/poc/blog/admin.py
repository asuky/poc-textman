from django.contrib import admin
from .models import Category, Post, Comment, Tag

# ============================================================
# Django 管理画面の設定
# ============================================================
# 管理画面でモデルのCRUD操作を行うための設定です。
# スーパーユーザーでログイン後、http://localhost:8000/admin/ にアクセス
# ============================================================


# シンプルな登録（カテゴリとタグ）
admin.site.register(Category)
admin.site.register(Tag)


class CommentInline(admin.TabularInline):
    """
    記事編集画面でコメントをインライン表示
    
    記事を編集する際に、関連するコメントも同時に表示・編集できます。
    """
    model = Comment
    extra = 1  # 空のフォームを1つ表示
    fields = ['author', 'content', 'created_at']
    readonly_fields = ['created_at']  # 作成日時は読み取り専用


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    記事の管理画面設定
    
    一覧画面での表示項目、フィルター、検索などを設定します。
    """
    # 一覧画面に表示するフィールド
    list_display = [
        'title',           # タイトル
        'author',          # 著者
        'category',        # カテゴリ
        'status',          # ステータス
        'published_at',    # 公開日時
        'created_at',      # 作成日時
    ]
    
    # サイドバーのフィルター
    list_filter = [
        'status',          # ステータスでフィルタ
        'category',        # カテゴリでフィルタ
        'created_at',      # 作成日時でフィルタ
        'published_at',    # 公開日時でフィルタ
    ]
    
    # 検索機能（タイトルと本文で検索）
    search_fields = [
        'title',           # タイトルで検索
        'content',         # 本文で検索
        'author__username', # 著者名で検索
    ]
    
    # 編集画面のレイアウト設定
    fieldsets = [
        ('基本情報', {
            'fields': ['title', 'slug', 'author', 'category']
        }),
        ('内容', {
            'fields': ['content', 'status']
        }),
        ('公開設定', {
            'fields': ['published_at'],
            'classes': ['collapse'],  # 折りたたみ可能
        }),
    ]
    
    # スラッグを自動入力（タイトルから生成）
    prepopulated_fields = {
        'slug': ('title',),
    }
    
    # 日付による階層表示
    date_hierarchy = 'created_at'
    
    # ページあたりの表示件数
    list_per_page = 50
    
    # デフォルトの並び順
    ordering = ['-created_at']  # 新しい順
    
    # コメントをインライン表示
    inlines = [CommentInline]
    
    # カスタムアクション
    actions = ['make_published', 'make_draft']
    
    @admin.action(description='選択した記事を公開する')
    def make_published(self, request, queryset):
        """
        複数の記事を一括で公開するアクション
        """
        from django.utils import timezone
        updated = queryset.update(
            status='published',
            published_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated}件の記事を公開しました。',
            level='success'
        )
    
    @admin.action(description='選択した記事を下書きにする')
    def make_draft(self, request, queryset):
        """
        複数の記事を一括で下書きに戻すアクション
        """
        updated = queryset.update(status='draft')
        self.message_user(
            request,
            f'{updated}件の記事を下書きにしました。',
            level='success'
        )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    コメントの管理画面設定
    """
    list_display = [
        'post',
        'author',
        'content_preview',  # カスタムメソッド
        'created_at',
    ]
    
    list_filter = [
        'created_at',
        'post__status',  # 記事のステータスでフィルタ
    ]
    
    search_fields = [
        'content',
        'author__username',
        'post__title',
    ]
    
    # デフォルトの並び順
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """
        コメント内容のプレビュー表示（最初の50文字）
        """
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    
    content_preview.short_description = 'コメント内容'
