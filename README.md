# WebSearcher

`WebSearcher` は、DuckDuckGo を用いた簡易ウェブ検索ツールです。企業名や製品名などのキーワードに基づき検索を行い、検索結果のページ内容（本文＋表など）を自動で取得・整形します。

---

## 機能

- DuckDuckGo検索による情報収集（Google API不要）
- 複数の製品名に対して企業名を結合した検索クエリを自動生成
- 上位2件の検索結果URLから本文を自動抽出
- PDFリンクにも対応（PyMuPDFで解析）
- HTML内の `<table>` 要素を本文と別で抽出・合成
- 各クエリにランダムな待機時間を入れてスパム回避

---

## 使用方法
### １. インストール
```python
pip install git+https://github.com/west0714/web_search.git
```

### ２. 実行コード
```python
from web_search import WebSearcher

keyword = {
    "enterprise": "トヨタ",
    "product": ["クラウン", "プリウス"]
}
ーー追加の条件指定（指定しない場合は入力不要）ーー
#件数を指定(１０件以内)
item_count = 2
#内容の文字数指定
content_length = 500

searcher = WebSearcher(keyword, item_count, content_length).results
```
### 3. 出力
```python
[
  {
    'query': 'トヨタクラウン',
    'results': [
      {
        'link': 'https://...',
        'content': 'クラウンの公式ページ...'
      },
      {
        'link': 'https://...',
        'content': '2025年に発売された新型クラウン（エステート）の詳細情報...'
      },
      ...
    ]
  }
  ...
]
```
