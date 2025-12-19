# インポート修正と新規機能（LINE通知等）の実装計画

`modules/llm.py` および `modules/charts.py` のエラーを修正し、以前の機能（エントリーポイント表示）の復元、およびAIによる銘柄ニュースの要約とLINE通知機能を追加します。

## ユーザーレビューが必要な事項
- **LINE通知のタイミング**: 「毎朝」の通知を実現するために、Streamlitの起動時（その日最初のアカウントアクセス時）にチェックを行うか、外部トリガー（GitHub Actions等）を推奨するかの判断が必要です。本実装では、アプリ起動時に本日未送信であれば送信する簡易的な仕組みを提案します。
- **ニュースのソース**: `yfinance` のニュース機能を使用します。

## 変更内容

### LLM・インジケーター・チャート関連

#### [MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- `GENAI_AVAILABLE` 定数を定義し、`GENAI_V1_AVAILABLE` または `GENAI_LEGACY_AVAILABLE` が真の場合に True となるようにします。

#### [MODIFY] [charts.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/charts.py)
- `pd` (pandas) の未定義エラーを再確認し、必要に応じてインポートの配置や関数内での利用を修正します。

#### [MODIFY] [analysis.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/analysis.py)
- `calculate_trading_strategy` 関数において、下落トレンド時でも `entry_price`、`target_price`、`stop_loss` を返却するように修正（`None` にしていた箇所を削除）。

---

### 新規機能：LINE通知とニュース分析

#### [NEW] [news.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/news.py)
- `yfinance` を用いて銘柄に関連するニュースを取得する関数 `get_stock_news(ticker)` を実装。

#### [NEW] [line.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/line.py)
- LINE Notify API を用いてメッセージを送信する関数 `send_line_notification(message, token)` を実装。

#### [MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- ニュース一覧から保有株への影響を分析・要約するAIプロンプトと関数 `analyze_news_impact(portfolio, news_data)` を追加。

#### [MODIFY] [notifications.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/notifications.py)
- 定期通知のロジック（最終送信日の記録とチェック、LINE送信の呼び出し）を追加。

#### [MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)
- アプリ起動時に「本日のニュース要約」を実行・通知するトリガーを追加。
- ユーザーインターフェースにLINE通知設定や手動実行ボタンを追加。

## 検証計画

### 自動テスト
- `python -m pytest` （既存のテストがあれば実行）
- 各モジュールの独立した動作確認スクリプトの作成

### 手動検証
1. Streamlitを起動し、下落トレンドの銘柄を検索してチャート上にエントリーポイント等が表示されることを確認。
2. LINE Notify のトークンを設定し、テスト通知が届くことを確認。
3. ポートフォリオがある状態で、ニュース要約通知が実行されることを確認。
