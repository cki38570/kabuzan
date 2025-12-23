# 実装計画: Kabuzan v3.0 次世代版への改修

## 目的
Kabuzan を Streamlit ベースのアプリから、`defeatbeta-api` と `htmx` を活用したプロ向けの高機能・高速投資判断ツールへと進化させます。

## 主な変更点

### 1. チャート・エンジンの完全刷新 (`lightweight-charts-python`)
- **[NEW] [charts.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/charts.py)**: Plotly を廃止し、TradingView と同様の UI を提供する `lightweight-charts` へ移行します。
- **インジケーター**: MA(5/25/75)、ボリンジャーバンド、ATR を標準装備。
- **AI ライン**: Gemini が算出したレベルをチャート上に自動描画。
- **Transcript Mapping**: 決算説明会の日付にアイコンを表示し、クリックで要約を表示。

### 2. データ連携の深化 (`defeatbeta-api`)
- **[MODIFY] [defeatbeta_client.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/defeatbeta_client.py)**: 既存の DuckDB 連携に加え、文字起こしデータと需給データの取得ロジックを追加します。
- **フォールバック戦略**: yfinance の制限時に `defeatbeta-api` のデータセットへ自動切り替え。

### 3. Gemini AI アナリストの高度化
- **[MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)**: 
    - **Self-Reflection**: 「強気」と「弱気」の両方の視点で分析させ、客観的な最終判断を下すプロンプト。
    - **マクロ連携**: ドル円や日経平均のトレンドを分析材料に注入。
    - **構造化出力**: 常に JSON 形式で応答を受け取り、UI でパース。
- **Context Caching**: 大量の過去データをキャッシュし、コスト削減とレスポンス高速化を実現。

### 4. htmx によるインタラクティブ UX と FastAPI
- **[NEW] FastAPI Backend**: 高速なレスポンスと htmx のための API サーバーを構築。
- **AI 対話パネル**: 画面遷移なしで銘柄の深掘り質問ができるチャット窓。

## 実施スケジュール (優先順位順)
1. **lightweight-charts-python の導入**: 最も視覚的な変化が大きく、基盤となるチャート機能を刷新。
2. **defeatbeta-api 連携強化**: 文字起こしデータを Gemini のコンテキストに注入。
3. **Gemini プロンプト刷新**: Self-Reflection と JSON 出力の実装。
4. **htmx/FastAPI の導入**: インタラクティブな操作感の提供。

## ユーザーへの確認事項
> [!IMPORTANT]
> `lightweight-charts-python` を使用するには、pip でのインストールが必要です。また、`defeatbeta-api` の文字起こしデータへのアクセス権限（APIキー等）が有効であることを前提として進めます。
