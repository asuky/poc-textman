// ============================================================
// script.js - メインJavaScriptファイル
// ============================================================
// このファイルは Django の静的ファイルとして提供されます。
//
// 【配置場所】
// プロジェクトルート/static/js/script.js
//
// 【アクセス方法】
// - テンプレート内: {% static 'js/script.js' %}
// - ブラウザ直接: http://localhost:8000/static/js/script.js
//
// 【機能】
// - API エンドポイントへのリクエスト送信
// - レスポンスの表示
// - ミドルウェアが追加したヘッダー情報の表示
// ============================================================

console.log('📜 script.js が読み込まれました（静的ファイル）');

/**
 * /poc/ エンドポイントにGETリクエストを送信
 */
async function fetchPoc() {
    const resultElement = document.getElementById('result');
    resultElement.textContent = '🔄 リクエスト送信中...';
    
    try {
        // Fetch API でリクエスト送信
        const response = await fetch('/poc/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        // レスポンスボディ（JSON）を取得
        const data = await response.json();
        
        // ミドルウェアが追加したカスタムヘッダーを取得
        const requestId = response.headers.get('X-Request-ID');
        const apiVersion = response.headers.get('X-API-Version');
        const poweredBy = response.headers.get('X-Powered-By');
        
        // 結果を整形して表示
        const result = {
            '🎯 エンドポイント': '/poc/',
            '📊 ステータスコード': response.status,
            '📦 レスポンスボディ': data,
            '🔖 カスタムヘッダー': {
                'X-Request-ID': requestId,
                'X-API-Version': apiVersion,
                'X-Powered-By': poweredBy
            }
        };
        
        resultElement.textContent = JSON.stringify(result, null, 2);
        
    } catch (error) {
        resultElement.textContent = `❌ エラー: ${error.message}`;
        console.error('エラー詳細:', error);
    }
}

/**
 * /poc-slow/ エンドポイントにGETリクエストを送信
 * （処理時間計測のテスト用）
 */
async function fetchSlow() {
    const resultElement = document.getElementById('result');
    resultElement.textContent = '🔄 リクエスト送信中...\n（0.5秒待機します）';
    
    // リクエスト開始時刻を記録
    const startTime = performance.now();
    
    try {
        const response = await fetch('/poc-slow/', {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        const data = await response.json();
        
        // リクエスト完了時刻を計算
        const endTime = performance.now();
        const duration = (endTime - startTime).toFixed(2);
        
        // ミドルウェアが追加したヘッダーを取得
        const requestId = response.headers.get('X-Request-ID');
        
        const result = {
            '🎯 エンドポイント': '/poc-slow/',
            '📊 ステータスコード': response.status,
            '⏱️ クライアント側処理時間': `${duration}ms`,
            '📦 レスポンスボディ': data,
            '🔖 X-Request-ID': requestId,
            '💡 注意': 'サーバーのコンソールでミドルウェアのログを確認してください'
        };
        
        resultElement.textContent = JSON.stringify(result, null, 2);
        
    } catch (error) {
        resultElement.textContent = `❌ エラー: ${error.message}`;
        console.error('エラー詳細:', error);
    }
}

// ページ読み込み完了時の処理
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ ページ読み込み完了');
    console.log('📁 静的ファイル（CSS, JS）が正常に読み込まれています');
});
