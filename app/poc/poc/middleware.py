# ============================================================
# middleware.py - カスタムミドルウェア
# ============================================================
# ミドルウェアは、リクエスト/レスポンスの処理パイプラインに
# 独自の処理を挟み込むための仕組みです。
#
# 【処理の流れ】
# クライアント
#   ↓ HTTPリクエスト
# ミドルウェア1（前処理）
#   ↓
# ミドルウェア2（前処理）
#   ↓
# ビュー関数
#   ↓
# ミドルウェア2（後処理）
#   ↓
# ミドルウェア1（後処理）
#   ↓ HTTPレスポンス
# クライアント
# ============================================================

import time
from django.utils.deprecation import MiddlewareMixin


class SimpleLoggingMiddleware(MiddlewareMixin):
    """
    リクエストとレスポンスの情報をコンソールに出力する
    シンプルなロギングミドルウェア
    
    【機能】
    - リクエストのHTTPメソッドとURLパスを記録
    - レスポンスのステータスコードを記録
    - 処理時間を計測して表示
    """
    
    def process_request(self, request):
        """
        ビュー関数が実行される「前」に呼ばれるメソッド
        
        Args:
            request: HttpRequestオブジェクト
        
        Returns:
            None: 処理を続行
            HttpResponse: 処理を中断してこのレスポンスを返す（今回は使用しない）
        
        【用途例】
        - 認証チェック
        - リクエストの検証
        - リクエストデータの加工
        - ログ記録の開始
        """
        # リクエスト開始時刻を記録（レスポンス時に処理時間を計算）
        request._middleware_start_time = time.time()
        
        # コンソールにリクエスト情報を出力
        print(f"[ミドルウェア] リクエスト受信: {request.method} {request.path}")
        
        # Noneを返すと、次のミドルウェアまたはビュー関数に処理が進みます
        return None
    
    def process_response(self, request, response):
        """
        ビュー関数が実行された「後」に呼ばれるメソッド
        
        Args:
            request: HttpRequestオブジェクト
            response: HttpResponseオブジェクト（ビューが返したレスポンス）
        
        Returns:
            HttpResponse: クライアントに返すレスポンス
                         （加工したり、そのまま返したり）
        
        【用途例】
        - レスポンスヘッダーの追加
        - レスポンスデータの加工
        - ログ記録の完了
        - パフォーマンス計測
        """
        # 処理時間を計算
        if hasattr(request, '_middleware_start_time'):
            duration = time.time() - request._middleware_start_time
            duration_ms = duration * 1000  # ミリ秒に変換
            
            # コンソールにレスポンス情報を出力
            print(f"[ミドルウェア] レスポンス送信: ステータス {response.status_code} | 処理時間 {duration_ms:.2f}ms")
        
        # レスポンスをそのまま返す（加工せずに通過させる）
        return response


class RequestIDMiddleware(MiddlewareMixin):
    """
    各リクエストにユニークなIDを付与するミドルウェア
    
    【機能】
    - リクエストごとに一意のIDを生成
    - レスポンスヘッダーに X-Request-ID を追加
    - ログ追跡やデバッグに便利
    """
    
    def process_request(self, request):
        """リクエストにIDを付与"""
        import uuid
        # ユニークなリクエストIDを生成
        request.request_id = str(uuid.uuid4())
        print(f"[RequestID] リクエストID: {request.request_id}")
        return None
    
    def process_response(self, request, response):
        """レスポンスヘッダーにリクエストIDを追加"""
        if hasattr(request, 'request_id'):
            # カスタムヘッダーを追加
            response['X-Request-ID'] = request.request_id
        return response


class CustomHeaderMiddleware(MiddlewareMixin):
    """
    すべてのレスポンスにカスタムヘッダーを追加するミドルウェア
    
    【機能】
    - APIバージョン情報をヘッダーに追加
    - サーバー情報をヘッダーに追加
    """
    
    def process_response(self, request, response):
        """レスポンスにカスタムヘッダーを追加"""
        # カスタムヘッダーを追加
        response['X-API-Version'] = '1.0.0'
        response['X-Powered-By'] = 'Django-POC'
        return response


# ============================================================
# 【高度な例】例外処理ミドルウェア
# ============================================================
class ExceptionLoggingMiddleware(MiddlewareMixin):
    """
    ビュー内で発生した例外をキャッチしてログ出力するミドルウェア
    
    【機能】
    - ビュー関数で例外が発生した際の情報を記録
    - エラーレスポンスをカスタマイズ可能
    """
    
    def process_exception(self, request, exception):
        """
        ビュー関数内で例外が発生したときに呼ばれるメソッド
        
        Args:
            request: HttpRequestオブジェクト
            exception: 発生した例外オブジェクト
        
        Returns:
            None: 通常のエラー処理を続行
            HttpResponse: カスタムエラーレスポンスを返す
        """
        # 例外情報をコンソールに出力
        print(f"[エラー] {request.path} でエラー発生: {type(exception).__name__}: {str(exception)}")
        
        # Noneを返すと、Djangoの標準エラー処理が実行されます
        # カスタムエラーレスポンスを返すことも可能:
        # from django.http import JsonResponse
        # return JsonResponse({"error": str(exception)}, status=500)
        return None


# ============================================================
# 【関数ベースのミドルウェア】（Django推奨の新しい書き方）
# ============================================================
def simple_function_middleware(get_response):
    """
    関数ベースのミドルウェア（Django 1.10以降の推奨方式）
    
    Args:
        get_response: 次のミドルウェアまたはビュー関数を呼び出す関数
    
    Returns:
        middleware: 実際のミドルウェア関数
    
    【メリット】
    - よりシンプルな記述
    - 初期化処理を外側の関数で実行できる
    """
    
    # この部分は最初の1回だけ実行される（初期化処理）
    print("[ミドルウェア初期化] simple_function_middleware が読み込まれました")
    
    def middleware(request):
        # ========== リクエスト処理（ビュー実行前） ==========
        print(f"[関数MW] リクエスト前処理: {request.path}")
        
        # 次のミドルウェアまたはビューを呼び出す
        response = get_response(request)
        
        # ========== レスポンス処理（ビュー実行後） ==========
        print(f"[関数MW] レスポンス後処理: ステータス {response.status_code}")
        
        return response
    
    return middleware
