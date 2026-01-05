# Django path() 引数とnameパラメータの完全ガイド

## 📋 path() の基本構文

```python
from django.urls import path

path(route, view, kwargs=None, name=None)
```

---

## 🔍 各引数の詳細

### **第1引数: route（必須）**
```python
path('poc/', ...)
path('articles/<int:id>/', ...)
path('blog/<slug:slug>/', ...)
```

**役割**: URLパターンを定義

**書き方のルール**:
- 文字列で指定
- 末尾に `/` を付けるのが慣例
- `<型:変数名>` で動的パラメータを指定可能

**動的パラメータの型**:
- `<int:id>` - 整数（例: 123）
- `<str:name>` - 文字列（スラッシュ以外）
- `<slug:slug>` - スラッグ（英数字、ハイフン、アンダースコア）
- `<uuid:uuid>` - UUID
- `<path:path>` - スラッシュを含む任意の文字列

---

### **第2引数: view（必須）**
```python
# 関数ベースビュー
path('poc/', poc_status, ...)

# クラスベースビュー
path('api/', MyAPIView.as_view(), ...)
```

**役割**: 実行するビュー関数またはクラス

**重要**: 
- 関数は `()` を付けずに参照を渡す
- `poc_status` ○
- `poc_status()` ✗（実行してしまう）

---

### **第3引数: name（オプション、キーワード引数）**
```python
path('poc/', poc_status, name='poc_status')
```

**役割**: URLパターンに識別名を付ける

**命名規則**:
- 小文字とアンダースコア推奨
- 一意である必要がある
- わかりやすい名前を付ける

---

## 🎯 name の使用方法

### **1. テンプレート内 - {% url %} タグ**

#### パラメータなし
```html
<!-- urls.py -->
path('poc/', poc_status, name='poc_status')

<!-- テンプレート -->
<a href="{% url 'poc_status' %}">POCページ</a>
<!-- 出力: <a href="/poc/">POCページ</a> -->
```

#### パラメータあり
```html
<!-- urls.py -->
path('articles/<int:id>/', article_detail, name='article_detail')

<!-- テンプレート -->
<a href="{% url 'article_detail' id=123 %}">記事123</a>
<!-- 出力: <a href="/articles/123/">記事123</a> -->

<!-- 変数を使用 -->
<a href="{% url 'article_detail' id=article.id %}">{{ article.title }}</a>
```

#### 複数パラメータ
```html
<!-- urls.py -->
path('blog/<int:year>/<int:month>/', archive, name='blog_archive')

<!-- テンプレート -->
<a href="{% url 'blog_archive' year=2026 month=1 %}">2026年1月</a>
<!-- 出力: <a href="/blog/2026/1/">2026年1月</a> -->
```

---

### **2. ビュー関数内 - redirect()**

```python
from django.shortcuts import redirect

def my_view(request):
    # 処理...
    
    # パラメータなし
    return redirect('poc_status')
    # → /poc/ にリダイレクト
    
    # パラメータあり
    return redirect('article_detail', id=123)
    # → /articles/123/ にリダイレクト
```

---

### **3. ビュー関数内 - reverse()**

```python
from django.urls import reverse

def my_view(request):
    # URL文字列を取得
    url = reverse('poc_status')
    print(url)  # '/poc/'
    
    # パラメータ付き
    url = reverse('article_detail', kwargs={'id': 123})
    print(url)  # '/articles/123/'
    
    # JSONレスポンスに含める
    return JsonResponse({
        'next_url': reverse('poc_status'),
        'article_url': reverse('article_detail', kwargs={'id': 123})
    })
```

---

### **4. JavaScript内での使用**

```html
<script>
    // テンプレートでURL生成してJSに渡す
    const apiEndpoint = "{% url 'poc_status' %}";
    
    fetch(apiEndpoint)
        .then(response => response.json())
        .then(data => console.log(data));
</script>
```

---

## 💡 name を使うメリット

### ✅ **メリット1: URLの一元管理**
```python
# urls.py でパスを変更
path('api/v2/poc/', poc_status, name='poc_status')  # 'poc/' → 'api/v2/poc/'

# テンプレートは修正不要！
<a href="{% url 'poc_status' %}">POCページ</a>
# 自動的に /api/v2/poc/ に変換される
```

### ✅ **メリット2: リファクタリングが楽**
- URLパス変更時、urls.py だけ修正すればOK
- 全テンプレート・ビューを検索して修正する必要なし

### ✅ **メリット3: タイポの防止**
```python
# ハードコード（タイポしやすい）
return redirect('/poc/')  # '/poc' と書いてしまうミス

# name使用（間違えるとエラーで気づける）
return redirect('poc_status')  # 存在しない名前だとエラー
```

---

## 🚫 name を使わない場合の問題点

### ❌ **ハードコードの問題**

```python
# urls.py
path('poc/', poc_status, name='poc_status')

# ビュー（悪い例）
return redirect('/poc/')

# テンプレート（悪い例）
<a href="/poc/">POCページ</a>
```

**問題点**:
1. URLを変更したら、全ファイルを検索・置換が必要
2. 変更漏れでリンク切れが発生しやすい
3. 大規模プロジェクトでは保守が困難

---

## 📚 実践例

### **例1: 記事システム**

```python
# urls.py
urlpatterns = [
    path('articles/', article_list, name='article_list'),
    path('articles/<int:id>/', article_detail, name='article_detail'),
    path('articles/<int:id>/edit/', article_edit, name='article_edit'),
    path('articles/<int:id>/delete/', article_delete, name='article_delete'),
]

# views.py
def article_edit(request, id):
    # 保存後、詳細ページにリダイレクト
    return redirect('article_detail', id=id)

# テンプレート（article_list.html）
{% for article in articles %}
    <div>
        <a href="{% url 'article_detail' id=article.id %}">{{ article.title }}</a>
        <a href="{% url 'article_edit' id=article.id %}">編集</a>
        <a href="{% url 'article_delete' id=article.id %}">削除</a>
    </div>
{% endfor %}
```

### **例2: API エンドポイント**

```python
# urls.py
urlpatterns = [
    path('api/status/', api_status, name='api_status'),
    path('api/users/<int:user_id>/', api_user_detail, name='api_user_detail'),
]

# views.py
def api_status(request):
    return JsonResponse({
        'status': 'OK',
        'endpoints': {
            'user_detail': reverse('api_user_detail', kwargs={'user_id': 1})
        }
    })
```

---

## ⚠️ よくある間違い

### ❌ **間違い1: 関数を実行してしまう**
```python
# 間違い
path('poc/', poc_status(), name='poc_status')  # ()を付けてはダメ

# 正しい
path('poc/', poc_status, name='poc_status')
```

### ❌ **間違い2: name の重複**
```python
# 間違い（同じ名前を複数使用）
path('api/v1/status/', api_status_v1, name='api_status'),
path('api/v2/status/', api_status_v2, name='api_status'),  # 重複！

# 正しい（一意な名前）
path('api/v1/status/', api_status_v1, name='api_status_v1'),
path('api/v2/status/', api_status_v2, name='api_status_v2'),
```

### ❌ **間違い3: reverse()のパラメータ指定**
```python
# 間違い
reverse('article_detail', id=123)

# 正しい
reverse('article_detail', kwargs={'id': 123})
# または
reverse('article_detail', args=[123])
```

---

## 🎓 まとめ

| 引数 | 必須/任意 | 役割 | 例 |
|-----|---------|------|---|
| **route** | 必須 | URLパターン | `'poc/'`, `'articles/<int:id>/'` |
| **view** | 必須 | ビュー関数 | `poc_status`, `MyView.as_view()` |
| **name** | 任意 | URL識別名 | `'poc_status'`, `'article_detail'` |

**ベストプラクティス**:
- ✅ name は必ず付ける
- ✅ わかりやすい名前を使う
- ✅ ハードコードせず、必ず name を使う
- ✅ URL変更時は urls.py だけ修正
