# 高度な株式チャート技術報告書

## 1. 実装方式の概要
今回の実装は、**PythonのStreamlit** アプリケーション内に **生のHTMLとJavaScript** を埋め込む「Custom HTML/JS Injection」方式を採用しています。

### アーキテクチャ図
```mermaid
graph TD
    A[Python (Streamlit)] -->|データ取得 (yfinance)| B(Pandas DataFrame)
    B -->|テクニカル計算 (pandas_ta)| C(加工済みデータ)
    C -->|JSON変換 & NaN除去| D{HTMLテンプレート}
    D -->|st.components.v1.html| E[ブラウザ (IFrame)]
    E -->|JavaScript実行| F[Lightweight Charts (JS Lib)]
    F -->|描画| G[Canvasキャンバス]
```

## 2. 使用技術の詳細

### Q. これはJAVAですか？Pythonですか？
**A. JavaScript (TypeScript) です。**

-   **ライブラリ名**: [Lightweight Charts](https://github.com/tradingview/lightweight-charts)
-   **開発元**: TradingView
-   **言語**: ブラウザ上で動作する **JavaScript** (正確にはTypeScriptで作られています)

今回はPythonのラッパーライブラリ（`streamlit-lightweight-charts`等）を使用せず、**Pythonから直接JavaScriptコードを生成して実行**させているため、ライブラリの全機能（バージョンの指定、細かいオプション設定、イベントハンドリングなど）をフルに活用できています。

### Q. なぜPythonラッパーを使わなかったのか？
当初はPythonラッパーでの実装を試みましたが、以下の問題が発生したため、より確実な直接制御方式（Custom Injection）に切り替えました。
1.  **バージョン不整合**: ラッパーが内包するJSライブラリのバージョンと、渡しているデータ形式の間にズレがあり、エラーが発生しやすい。
2.  **柔軟性の欠如**: 「トレンドラインをマーカーで描画する」「PSARをドットで表示する」といった細かいカスタマイズが、ラッパー経由では難しい（または不可能）。
3.  **デバッグの難易度**: エラーが起きた際、Python側なのかJS側なのかの切り分けがブラックボックスになりがち。

## 3. 他のアプリへの導入手順

この方式を他のStreamlitアプリ等のPythonプロジェクトに導入するためのステップは以下の通りです。

### ステップ 1: データのJSON化
PythonのDataFrameデータを、JavaScriptが読めるJSON形式（リスト型）に変換します。重要なのは `NaN` (欠損値) の処理です。
```python
import json

# Pythonでの前処理
candlestick_data = [
    {"time": "2023-01-01", "open": 100, "high": 110, "low": 90, "close": 105},
    ...
]

# JSON文字列に変換（NaNはnullに置換）
json_data = json.dumps(candlestick_data).replace("NaN", "null")
```

### ステップ 2: HTMLテンプレートの用意
`app.py` 内に記述したような、以下の要素を持つHTML文字列を用意します。
1.  **ライブラリ読み込み**: `<script src="https://unpkg.com/lightweight-charts@3.8.0/..."></script>`
2.  **コンテナ**: `<div id="chart"></div>`
3.  **初期化スクリプト**: `LightweightCharts.createChart(...)`

### ステップ 3: データの注入 (Injection)
Pythonのf-string機能を使って、ステップ1で作ったJSONデータをHTML内のJavaScript変数に埋め込みます。
```python
html_code = f"""
...
<script>
    const series = chart.addCandlestickSeries();
    series.setData({json_data}); // ここでデータを注入
</script>
...
"""
```

### ステップ 4: Streamlitでの表示
`streamlit.components.v1.html` を使ってレンダリングします。
```python
import streamlit.components.v1 as components
components.html(html_code, height=500)
```

## 4. この方式のメリット
-   **高速**: ブラウザのCanvas機能を使うため、大量のデータでもサクサク動きます（Matplotlibなどの画像生成方式とは比較にならないほど高速です）。
-   **インタラクティブ**: ユーザーが自由にズーム、スクロール、価格確認（ツールチップ）を行えます。
-   **自由度**: TradingViewが提供するプロ向けのチャート機能を、Pythonアプリ内で制限なく利用できます。
