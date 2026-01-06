from django.urls import path
from . import views

# ============================================================
# ブログアプリのURLルーティング
# ============================================================
# このファイルで定義したURLパターンを、プロジェクトのurls.pyで
# include()を使って登録する必要があります。
#
# 例: poc/urls.py に以下を追加
# from django.urls import include
# urlpatterns = [
#     path('blog/', include('blog.urls')),
# ]
# ============================================================

# アプリケーション名前空間（reverse()で使用）
app_name = 'blog'

urlpatterns = [
    # ============================================================
    # HTMLビュー（クラスベースビュー）
    # ============================================================
    # 注意: URLパターンは上から順に評価されます！
    # 固定パス（create, categories など）を先に配置し、
    # 可変パス（<slug> など）は後に配置してください。
    # ============================================================
    
    # 記事一覧: /blog/
    path(
        '',
        views.PostListView.as_view(),
        name='post_list'
    ),
    
    # 記事作成: /blog/create/
    # ⚠️ <slug> より先に配置すること！
    path(
        'create/',
        views.PostCreateView.as_view(),
        name='post_create'
    ),
    
    # カテゴリ一覧: /blog/categories/
    # ⚠️ <slug> より先に配置すること！
    path(
        'categories/',
        views.CategoryListView.as_view(),
        name='category_list'
    ),
    
    # 記事詳細: /blog/<slug>/
    # ⚠️ 可変パスなので固定パスより後に配置
    path(
        '<slug:slug>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    
    # 記事編集: /blog/<slug>/edit/
    path(
        '<slug:slug>/edit/',
        views.PostUpdateView.as_view(),
        name='post_update'
    ),
    
    # 記事削除: /blog/<slug>/delete/
    path(
        '<slug:slug>/delete/',
        views.PostDeleteView.as_view(),
        name='post_delete'
    ),
    
    # ============================================================
    # API エンドポイント（JSON）
    # ============================================================
    # API も固定パス（api/posts/create/）を可変パス（api/posts/<slug>/）より先に
    # ============================================================
    
    # 記事一覧API: /blog/api/posts/
    path(
        'api/posts/',
        views.post_list_api,
        name='post_list_api'
    ),
    
    # 記事作成API（トランザクション使用）: /blog/api/posts/create/
    # ⚠️ api/posts/<slug>/ より先に配置すること！
    path(
        'api/posts/create/',
        views.create_post_with_tags_api,
        name='create_post_api'
    ),
    
    # 記事詳細API: /blog/api/posts/<slug>/
    # ⚠️ 可変パスなので固定パスより後に配置
    path(
        'api/posts/<slug:slug>/',
        views.post_detail_api,
        name='post_detail_api'
    ),
    
    # ============================================================
    # ユーティリティ
    # ============================================================
    
    # データベース接続確認: /blog/db-check/
    path(
        'db-check/',
        views.db_check,
        name='db_check'
    ),
]
