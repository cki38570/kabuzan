# 投資分析アプリ (kabuzan) の技術スタック刷新計画

このドキュメントでは、現在の `yfinance` を利用したデータ取得から `defeatbeta-api` への移行、および UI フレームワークを Streamlit から HTMX へ刷新する計画について述べます。

## 概要
現在のアプリは Streamlit をベースに構築されており、手軽に高度な UI を提供していますが、拡張性やパフォーマンス、データ取得の安定性に課題があります。これを解消するために、以下の2段階の刷新を計画します。

---

### [CANCELLED] データソースの刷新: `yfinance` から `defeatbeta-api` へ

> [!WARNING]
> **中止 (2025-12-22)**
> 検証の結果、`defeatbeta-api` およびそのデータソースが不安定であることが判明しました。`yfinance` が正常に動作しているため、当面は `yfinance` を継続利用します。

(以下、旧計画内容はアーカイブとして保持、または削除)
- ~~[MODIFY] `modules/data.py`~~
- ~~[NEW] `modules/defeatbeta_client.py`~~

### 技術的詳細
- **データソース**: `https://huggingface.co/datasets/bwzheng2010/yahoo-finance-data/resolve/main/data/stock_prices.parquet`
- **認証**: ユーザー提供の HuggingFace Token を使用。
- **クエリ方法**: `duckdb.query()` を使用してリモート Parquet ファイルに対して SQL を実行（高速化のため）。失敗時は `pandas.read_parquet` でフォールバック。

---

## 2. フロントエンドの刷新: Streamlit から HTMX へ

### 新アーキテクチャ (FastAPI + HTMX)
Streamlit の制約（再実行モデル、WebSocket オーバーヘッド）を解消するため、標準的な Web アーキテクチャへ移行します。

#### 技術スタック
- **Backend**: FastAPI (Python) - 高速、非同期対応、型安全性。
- **Frontend Logic**: HTMX - JavaScript を書かずに HTML 属性で AJAX リクエストを行う。
- **Templating**: Jinja2 - サーバーサイドレンダリング。
- **Styling**: Vanilla CSS (Modern CSS Variables & Flexbox/Grid) - "Design Aesthetics" に従い、リッチでプレミアムなデザインを実装。

#### 移行ステップ (PoC)
まずは小規模なプロトタイプ (Proof of Concept) を作成し、HTMX の挙動と既存ロジック (`modules/`) の再利用性を確認します。

1.  **環境構築**: `fastapi`, `uvicorn`, `jinja2`, `python-multipart` のインストール。
2.  **基本構造の作成**:
    - `main.py`: エントリーポイント。
    - `templates/`: HTML テンプレート。
    - `static/`: CSS, JS, Images。
3.  **機能移植 (Phase 1)**:
    - **ウォッチリスト表示**: 現在の `watchlist.json` を読み込み、株価カードを表示する。
    - **株価詳細モーダル/ページ**: カードクリックで詳細情報を表示。
    - **チャート表示**: Plotly.js をクライアントサイドで使用し、FastAPI から JSON データを受け取る。

### コンポーネント設計
- **App Shell**: ヘッダー、ナビゲーション、メインコンテンツエリア。
- **Stock Card**: 株価、前日比、ミニチャート（Sparkline）を表示するコンポーネント。HTML fragment としてサーバーから返す。
- **Search Bar**: インクリメンタルサーチを HTMX (`hx-trigger="keyup changed delay:500ms"`) で実装。

---

## ユーザーレビューが必要な項目

> [!IMPORTANT]
> **HTMX 移行は大規模なリファクタリング（ほぼ全面書き換え）を伴います。**
> Streamlit の手軽さを失う代わりに、プロフェッショナルなウェブアプリとしての自由度と速度を得るトレードオフになります。

---

## 検証プラン

### 自動テスト
- `pytest` を使用して、`defeatbeta-api` からのデータ取得が `yfinance` と同等以上の精度であることを検証する。
- FastAPI の `TestClient` を使用して、HTMX 経由の各ルートが正しい HTML 断片を返すことを検証する。

### 手動検証
- ブラウザの開発者ツールを使用して、通信量とレスポンス速度の比較を行う。
- モバイル端末での操作感（スクロール、タブ切り替え）が改善されているか確認する。
