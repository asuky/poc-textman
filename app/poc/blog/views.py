from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.db import transaction
import json

# Django REST Framework のインポート
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .models import Post, Category, Comment, Tag
from .serializers import (
    PostListSerializer, 
    PostDetailSerializer, 
    PostCreateSerializer,
    CategorySerializer
)

# ============================================================
# ブログビュー（N+1問題対策済み）
# ============================================================
# このファイルでは、select_related と prefetch_related を使用して
# N+1問題を回避したビューを実装しています。
#
# Django Generic Views について:
# Djangoは一般的なWebアプリケーションのパターンを簡単に実装できる
# 「クラスベースビュー（CBV）」を提供しています。
#
# 公式ドキュメント:
# https://docs.djangoproject.com/en/stable/topics/class-based-views/
# https://docs.djangoproject.com/en/stable/ref/class-based-views/
#
# 主なGeneric Views:
# - ListView: 一覧表示（記事一覧、商品一覧など）
# - DetailView: 詳細表示（記事詳細、商品詳細など）
# - CreateView: 作成（新規投稿、新規登録など）
# - UpdateView: 更新（編集など）
# - DeleteView: 削除
# - FormView: フォーム処理
# - TemplateView: 単純なテンプレート表示
# ============================================================


class PostListView(ListView):
    """
    記事一覧ビュー（N+1対策済み）
    
    ListView を継承して記事一覧を表示します。
    
    ============================================================
    ListView で設定できる主な属性:
    ============================================================
    
    【必須】以下のいずれかを設定:
    - model: 表示するモデルクラス
    - queryset: カスタムクエリセット
    
    【オプション】
    - template_name: 使用するテンプレート（デフォルト: <app>/<model>_list.html）
    - context_object_name: テンプレート内での変数名（デフォルト: object_list）
    - paginate_by: ページあたりの件数（指定するとページネーション有効）
    - ordering: 並び順（例: ['-created_at']）
    
    【オーバーライド可能なメソッド】
    - get_queryset(): クエリセットをカスタマイズ
    - get_context_data(): コンテキストに追加データを渡す
    
    公式ドキュメント:
    https://docs.djangoproject.com/en/stable/ref/class-based-views/generic-display/#listview
    ============================================================
    """
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20  # ページあたり20件
    
    def get_queryset(self):
        """
        クエリセットを最適化
        
        N+1問題を避けるために、関連データを一括で取得します：
        - select_related: 外部キー（author, category）をJOINで取得
        - prefetch_related: 多対多（tags）と逆参照（comments）を別クエリで一括取得
        - annotate: 集計（コメント数）
        """
        return Post.objects.filter(
            status='published'  # 公開済みのみ
        ).select_related(
            'author',    # author.username などのアクセスでクエリが発行されない
            'category'   # category.name などのアクセスでクエリが発行されない
        ).prefetch_related(
            'tags',      # 多対多: タグを一括取得
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related('author')  # コメントの著者も一緒に取得
            )
        ).annotate(
            comment_count=Count('comments')  # コメント数を集計
        ).order_by('-published_at')  # 公開日時の降順


class PostDetailView(DetailView):
    """
    記事詳細ビュー（N+1対策済み）
    
    DetailView を継承して個別の記事を表示します。
    
    ============================================================
    DetailView で設定できる主な属性:
    ============================================================
    
    【必須】以下のいずれかを設定:
    - model: 表示するモデルクラス
    - queryset: カスタムクエリセット
    
    【オプション】
    - template_name: 使用するテンプレート（デフォルト: <app>/<model>_detail.html）
    - context_object_name: テンプレート内での変数名（デフォルト: object）
    - slug_field: モデルのスラッグフィールド名（デフォルト: 'slug'）
    - slug_url_kwarg: URLパターンのキーワード引数名（デフォルト: 'slug'）
    - pk_url_kwarg: URLパターンのPKキーワード引数名（デフォルト: 'pk'）
    
    【オーバーライド可能なメソッド】
    - get_queryset(): クエリセットをカスタマイズ
    - get_object(): 取得するオブジェクトをカスタマイズ
    - get_context_data(): コンテキストに追加データを渡す
    
    公式ドキュメント:
    https://docs.djangoproject.com/en/stable/ref/class-based-views/generic-display/#detailview
    ============================================================
    """
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        """
        クエリセットを最適化
        
        記事の詳細ページで必要な関連データを一括取得します。
        """
        return Post.objects.select_related(
            'author',
            'category'
        ).prefetch_related(
            'tags',
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related('author').order_by('created_at')
            )
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    記事作成ビュー
    
    CreateView を継承して新規記事を作成します。
    LoginRequiredMixin でログインを必須にしています。
    
    ============================================================
    CreateView で設定できる主な属性:
    ============================================================
    
    【必須】以下のいずれかを設定:
    - model + fields: モデルとフォームに表示するフィールド
    - form_class: カスタムフォームクラス
    
    【必須】成功時のリダイレクト先（以下のいずれか）:
    - success_url: 固定のURL（reverse_lazy使用推奨）
    - get_success_url(): 動的にURLを決定
    - モデルに get_absolute_url() メソッドを定義
    
    【オプション】
    - template_name: 使用するテンプレート（デフォルト: <app>/<model>_form.html）
    - context_object_name: テンプレート内での変数名
    - initial: フォームの初期値（辞書）
    
    【オーバーライド可能なメソッド】
    - form_valid(form): フォーム送信成功時の処理
    - form_invalid(form): フォーム送信失敗時の処理
    - get_form(): フォームインスタンスをカスタマイズ
    - get_context_data(): コンテキストに追加データを渡す
    
    【Mixin】
    - LoginRequiredMixin: ログインを必須にする
    - PermissionRequiredMixin: 権限チェック
    - UserPassesTestMixin: カスタム条件でアクセス制御
    
    公式ドキュメント:
    https://docs.djangoproject.com/en/stable/ref/class-based-views/generic-editing/#createview
    ============================================================
    """
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'slug', 'category', 'content', 'status']  # フォームに表示するフィールド
    success_url = reverse_lazy('blog:post_list')  # 名前空間を含める
    
    def form_valid(self, form):
        """
        フォーム送信時に著者を自動設定
        
        このメソッドは、フォームのバリデーションが成功した後、
        データベースに保存する前に呼ばれます。
        """
        form.instance.author = self.request.user  # 現在のユーザーを著者に設定
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """
    記事編集ビュー
    
    UpdateView を継承して記事を編集します。
    自分の記事のみ編集できるように制限しています。
    
    ============================================================
    UpdateView で設定できる主な属性:
    ============================================================
    
    CreateView とほぼ同じですが、既存のオブジェクトを編集します。
    
    【必須】以下のいずれかを設定:
    - model + fields: モデルとフォームに表示するフィールド
    - form_class: カスタムフォームクラス
    
    【必須】成功時のリダイレクト先
    【オプション】template_name, context_object_name など
    
    【オーバーライド可能なメソッド】
    - get_queryset(): 編集可能なオブジェクトを制限
    - form_valid(form): フォーム送信成功時の処理
    
    公式ドキュメント:
    https://docs.djangoproject.com/en/stable/ref/class-based-views/generic-editing/#updateview
    ============================================================
    """
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'slug', 'category', 'content', 'status']
    success_url = reverse_lazy('blog:post_list')  # 名前空間を含める
    
    def get_queryset(self):
        """
        自分の記事のみ取得
        
        他のユーザーの記事を編集しようとすると404エラーになります。
        """
        return Post.objects.filter(author=self.request.user)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """
    記事削除ビュー
    
    DeleteView を継承して記事を削除します。
    自分の記事のみ削除できるように制限しています。
    
    ============================================================
    DeleteView で設定できる主な属性:
    ============================================================
    
    【必須】
    - model: 削除するモデルクラス
    - success_url: 削除成功後のリダイレクト先
    
    【オプション】
    - template_name: 確認画面のテンプレート（デフォルト: <app>/<model>_confirm_delete.html）
    - context_object_name: テンプレート内での変数名
    
    【オーバーライド可能なメソッド】
    - get_queryset(): 削除可能なオブジェクトを制限
    - delete(request, *args, **kwargs): 削除処理をカスタマイズ
    
    公式ドキュメント:
    https://docs.djangoproject.com/en/stable/ref/class-based-views/generic-editing/#deleteview
    ============================================================
    """
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')  # 名前空間を含める
    
    def get_queryset(self):
        """
        自分の記事のみ取得
        
        他のユーザーの記事を削除しようとすると404エラーになります。
        """
        return Post.objects.filter(author=self.request.user)


class CategoryListView(ListView):
    """
    カテゴリ一覧ビュー（N+1対策済み）
    
    各カテゴリの記事数を集計して表示します。
    """
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        """
        カテゴリごとの記事数を集計
        
        annotate を使用して、各カテゴリに紐づく公開済み記事数をカウントします。
        """
        return Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published'))
        ).order_by('name')


# ============================================================
# API ビュー（Django REST Framework）
# ============================================================
"""
Django REST Framework (DRF) について
============================================================

DRFは、DjangoでRESTful APIを構築するための強力なツールキットです。

主な機能：
1. シリアライゼーション: モデル ⇔ JSON の変換
2. バリデーション: 自動的な入力検証
3. 認証・権限: 多様な認証方式をサポート
4. ブラウザ可能なAPI: Web UIで簡単にAPIをテスト可能
5. ドキュメント自動生成: Swagger/OpenAPI対応

Generic Views の種類:
- ListAPIView: 一覧取得（GET）
- RetrieveAPIView: 詳細取得（GET）
- CreateAPIView: 作成（POST）
- UpdateAPIView: 更新（PUT/PATCH）
- DestroyAPIView: 削除（DELETE）
- ListCreateAPIView: 一覧取得 + 作成
- RetrieveUpdateDestroyAPIView: 詳細取得 + 更新 + 削除

公式ドキュメント:
https://www.django-rest-framework.org/
https://www.django-rest-framework.org/api-guide/generic-views/
============================================================
"""


class PostListAPIView(generics.ListAPIView):
    """
    記事一覧API（GET）
    
    ============================================================
    DRF Generic Views の使い方
    ============================================================
    
    ListAPIView を継承すると、自動的に以下の機能が提供されます：
    - GET リクエストで一覧を返す
    - シリアライゼーション（モデル → JSON変換）
    - ページネーション（設定による）
    - フィルタリング（設定による）
    
    最小限必要な設定：
    - queryset または get_queryset()
    - serializer_class
    
    オプション設定：
    - permission_classes: 権限管理
    - filter_backends: フィルタリング
    - pagination_class: ページネーション
    - ordering_fields: ソート可能なフィールド
    ============================================================
    """
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # 読み取りは誰でも、書き込みは認証必須
    
    def get_queryset(self):
        """
        N+1問題を避けるために最適化したクエリセット
        
        HTML版のPostListViewと同じ最適化を行っています。
        """
        return Post.objects.filter(
            status='published'
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-published_at')


class PostDetailAPIView(generics.RetrieveAPIView):
    """
    記事詳細API（GET）
    
    RetrieveAPIView を継承すると、自動的に以下の機能が提供されます：
    - GET リクエストで特定のオブジェクトを返す
    - URL パラメータ（pk または slug）からオブジェクトを取得
    - 404エラーハンドリング
    
    lookup_field で検索に使うフィールドを指定できます。
    デフォルトは 'pk' ですが、'slug' に変更可能です。
    """
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'  # URL から slug でオブジェクトを検索
    
    def get_queryset(self):
        """N+1問題を避けるために最適化"""
        return Post.objects.filter(
            status='published'
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags',
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related('author')
            )
        )


class PostCreateAPIView(generics.CreateAPIView):
    """
    記事作成API（POST）
    
    ============================================================
    CreateAPIView の動作フロー
    ============================================================
    
    1. リクエスト受信
    2. Serializer でバリデーション（自動）
       - フィールドの型チェック
       - 必須フィールドチェック
       - カスタムバリデーション（validate_xxx メソッド）
    3. バリデーション成功 → perform_create() 呼び出し
    4. Serializer の create() メソッドでDB保存
    5. 201 Created レスポンス返却
    
    バリデーション失敗時:
    - 自動的に 400 Bad Request を返す
    - エラーメッセージも自動生成
    
    【トランザクション】
    DRFのGeneric Viewsは、デフォルトで @transaction.atomic が
    適用されているため、明示的に指定する必要はありません。
    ============================================================
    """
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]  # 認証必須
    
    def perform_create(self, serializer):
        """
        保存時に著者を自動設定
        
        このメソッドは、バリデーション成功後、保存前に呼ばれます。
        ここで追加のロジック（著者の設定など）を実行できます。
        """
        serializer.save(author=self.request.user)


# ============================================================
# 関数ベースAPIビュー（参考用）
# ============================================================
# クラスベースビューの方が推奨されますが、
# シンプルなAPIには @api_view デコレータも使えます。
# ============================================================

@api_view(['GET'])
def category_list_api(request):
    """
    カテゴリ一覧API（関数ベース）
    
    @api_view デコレータを使うと：
    - 指定したHTTPメソッドのみ受け付ける
    - DRFのResponse オブジェクトを使える
    - 自動的にブラウザ可能なAPIが生成される
    
    シンプルなAPIには便利ですが、複雑な処理には
    クラスベースビューの方が適しています。
    """
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('name')
    
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# ============================================================
# 従来のJSON APIビュー（参考用・非推奨）
# ============================================================
# 以下は、DRFを使わない従来の実装方法です。
# 学習のため残していますが、新規開発では上記のDRF版を使用してください。
# ============================================================


# ============================================================
# データベース接続確認ビュー
# ============================================================

def db_check(request):
    """
    データベース接続を確認するビュー
    
    データベースが正常に接続できているかチェックします。
    """
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Database connection successful',
            'database': connection.settings_dict['NAME']
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
