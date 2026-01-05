
# ============================================================
# DjangoのURLディスパッチャー（URLルーター）の設定ファイル。
# どのURLパスにアクセスしたときに、どのビュー関数を呼び出すかを定義します。
# ============================================================

"""
URL configuration for poc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

# ============================================================
# ビュー関数をインポート
# ============================================================
# views.pyで定義したビュー関数をインポートします。
# 「.views」の「.」は「同じディレクトリ内の」という意味です。
from .views import (
    index,                   # ルート (/) 用のビュー
    poc_status,
    poc_method_example,      # HTTPメソッド別処理の例
    poc_restricted_methods,  # 特定メソッドのみ許可
    poc_get_only,            # GET専用
    poc_post_only,           # POST専用
    poc_slow,                # ミドルウェアテスト用（処理時間計測）
)

# ============================================================
# URLパターンのリスト
# ============================================================
# URLとビュー関数を紐付けるリストです。
# Djangoは上から順にURLパターンをチェックし、
# マッチした最初のパターンのビュー関数を実行します。
#
# 【重要】path() 自体はHTTPメソッドを区別しません！
# 同じURLパスで GET/POST/PUT/DELETE などを区別するには、
# ビュー関数内で request.method をチェックして分岐させます。
#
# 【path()の引数】
# path(route, view, name=None)
#   第1引数 route: URLパス（文字列） 例: 'poc/', 'articles/<int:id>/'
#   第2引数 view:  呼び出すビュー関数（関数オブジェクト）
#   第3引数 name:  このURLパターンの識別名（逆引き用）
#
# 【nameの使い道】
# - テンプレート: {% url 'poc_status' %} → /poc/ に変換
# - ビュー: redirect('poc_status') → /poc/ にリダイレクト
# - reverse('poc_status') → '/poc/' を取得
# ============================================================
urlpatterns = [
    # ============================================================
    # ルート (/) - トップページ
    # ============================================================
    # ルートにアクセスしたときに、index.html を表示します
    # 静的ファイル（CSS, JavaScript, 画像）も読み込めます
    path('', index, name='index'),
    
    # 管理画面へのURL（Django標準機能）
    path('admin/', admin.site.urls),
    
    # /poc へのアクセスをpoc_status関数に紐付け
    # この1つのpath()で、すべてのHTTPメソッド（GET, POST, PUT等）を受け付けます
    # メソッド別の処理は、ビュー関数内で request.method を使って分岐します
    path('poc/', poc_status, name='poc_status'),
    
    # ============================================================
    # HTTPメソッド別処理の例（コメントを外して使用可能）
    # ============================================================
    # 同じ '/poc-method/' パスでも、HTTPメソッドによって異なるレスポンスを返します
    # 例: GET /poc-method/  → データ取得
    #     POST /poc-method/ → データ作成
    # path('poc-method/', poc_method_example, name='poc_method'),
    
    # GETとPOSTのみ許可する例（デコレータで制限）
    # それ以外のメソッドは HTTP 405 Method Not Allowed を返します
    # path('poc-restricted/', poc_restricted_methods, name='poc_restricted'),
    
    # GET専用エンドポイント（GET以外は HTTP 405）
    # path('poc-get/', poc_get_only, name='poc_get'),
    
    # POST専用エンドポイント（POST以外は HTTP 405）
    # path('poc-post/', poc_post_only, name='poc_post'),
    
    # ============================================================
    # ミドルウェアの動作確認用エンドポイント
    # ============================================================
    # 処理時間がかかるエンドポイント（ミドルウェアの処理時間計測をテスト）
    # アクセスすると、コンソールにミドルウェアのログが出力されます
    # レスポンスヘッダーに X-Request-ID と X-API-Version が追加されます
    path('poc-slow/', poc_slow, name='poc_slow'),
]
