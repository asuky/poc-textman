# ============================================================
# views.py - ビュー（View）ファイル
# ============================================================
# Djangoでは、「ビュー」がHTTPリクエストを受け取り、
# HTTPレスポンスを返す役割を担います。
# ============================================================

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


def poc_status(request):
    """
    /poc エンドポイントのビュー関数（全HTTPメソッド対応）
    
    【処理の流れ】
    1. クライアントが GET /poc にアクセス
    2. DjangoのURLルーター（urls.py）がこの関数を呼び出す
    3. この関数が実行され、JSONレスポンスを作成
    4. クライアントにレスポンスが返される
    
    Args:
        request (HttpRequest): Djangoが自動的に渡すリクエストオブジェクト
                              - request.method: HTTPメソッド（GET, POST等）
                              - request.GET: GETパラメータ
                              - request.POST: POSTデータ
                              など、リクエスト情報が含まれる
    
    Returns:
        JsonResponse: JSON形式のHTTPレスポンス
                      {"status": "OK"} をクライアントに返す
    """
    # JsonResponseはDjangoの便利なクラス。
    # Pythonの辞書（dict）を自動的にJSON形式に変換してくれます。
    # Content-Type: application/json のヘッダーも自動設定されます。
    return JsonResponse({"status": "OK"})


# ============================================================
# 【方法1】関数ベースビュー + request.methodで分岐
# ============================================================
@csrf_exempt  # CSRF保護を無効化（APIの場合。本番環境では適切な認証を実装すべき）
def poc_method_example(request):
    """
    HTTPメソッドごとに異なる処理を行う例
    
    同じURLパス（例: /poc-method/）でも、HTTPメソッドによって
    異なる処理を実行することができます。
    
    使い方:
        urls.py に以下を追加:
        path('poc-method/', poc_method_example, name='poc_method'),
    """
    if request.method == 'GET':
        # GETリクエストの処理
        return JsonResponse({
            "method": "GET",
            "message": "データを取得しました",
            "data": {"id": 1, "name": "サンプル"}
        })
    
    elif request.method == 'POST':
        # POSTリクエストの処理（データ作成）
        # request.POST または request.body でデータを取得
        return JsonResponse({
            "method": "POST",
            "message": "データを作成しました",
            "status": "created"
        }, status=201)  # HTTP 201 Created
    
    elif request.method == 'PUT':
        # PUTリクエストの処理（データ更新）
        return JsonResponse({
            "method": "PUT",
            "message": "データを更新しました"
        })
    
    elif request.method == 'DELETE':
        # DELETEリクエストの処理（データ削除）
        return JsonResponse({
            "method": "DELETE",
            "message": "データを削除しました"
        })
    
    else:
        # 上記以外のメソッド（PATCH, OPTIONS等）
        return JsonResponse({
            "error": "サポートされていないメソッドです"
        }, status=405)  # HTTP 405 Method Not Allowed


# ============================================================
# 【方法2】デコレータで許可するメソッドを制限
# ============================================================
@require_http_methods(["GET", "POST"])  # GETとPOSTのみ許可
def poc_restricted_methods(request):
    """
    特定のHTTPメソッドのみを許可する例
    
    @require_http_methods デコレータを使用すると、
    指定したメソッド以外のリクエストは自動的に
    HTTP 405 Method Not Allowed で拒否されます。
    
    使い方:
        urls.py に以下を追加:
        path('poc-restricted/', poc_restricted_methods, name='poc_restricted'),
    """
    if request.method == 'GET':
        return JsonResponse({"message": "GET リクエストです"})
    elif request.method == 'POST':
        return JsonResponse({"message": "POST リクエストです"})


# ============================================================
# 【方法3】個別のメソッド専用関数 + デコレータ
# ============================================================
from django.views.decorators.http import require_GET, require_POST

@require_GET  # GETメソッドのみ許可
def poc_get_only(request):
    """
    GETリクエスト専用のビュー関数
    
    @require_GET デコレータにより、GET以外のメソッドは
    自動的に拒否されます（HTTP 405）
    
    使い方:
        urls.py に以下を追加:
        path('poc-get/', poc_get_only, name='poc_get'),
    """
    return JsonResponse({"message": "このエンドポイントはGETのみ対応しています"})


@require_POST  # POSTメソッドのみ許可
@csrf_exempt   # CSRF保護を無効化（テスト用）
def poc_post_only(request):
    """
    POSTリクエスト専用のビュー関数
    
    @require_POST デコレータにより、POST以外のメソッドは
    自動的に拒否されます（HTTP 405）
    
    使い方:
        urls.py に以下を追加:
        path('poc-post/', poc_post_only, name='poc_post'),
    """
    # POSTデータの取得例
    # データがJSON形式の場合:
    # import json
    # data = json.loads(request.body)
    
    return JsonResponse({
        "message": "このエンドポイントはPOSTのみ対応しています",
        "status": "received"
    })


# ============================================================
# 【ミドルウェアテスト用】処理時間がかかるエンドポイント
# ============================================================
def poc_slow(request):
    """
    意図的に処理を遅らせるエンドポイント
    
    ミドルウェアの処理時間計測機能をテストするために、
    0.5秒のスリープを入れています。
    
    【確認できること】
    - SimpleLoggingMiddleware が処理時間を計測
    - RequestIDMiddleware がリクエストIDをヘッダーに追加
    - CustomHeaderMiddleware がカスタムヘッダーを追加
    
    使い方:
        urls.py に以下を追加:
        path('poc-slow/', poc_slow, name='poc_slow'),
        
    テスト:
        curl -v http://127.0.0.1:8000/poc-slow/
    """
    import time
    
    # 0.5秒待機（処理時間の計測テスト用）
    time.sleep(0.5)
    
    # request.request_id はミドルウェアが追加した属性
    request_id = getattr(request, 'request_id', 'なし')
    
    return JsonResponse({
        "message": "0.5秒の処理が完了しました",
        "request_id": request_id,
        "note": "ミドルウェアが処理時間を計測しています"
    })

