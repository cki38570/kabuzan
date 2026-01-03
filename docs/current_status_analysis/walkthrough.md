# Kabuzan システム構成・現状分析

「株山（kabuzan）」プロジェクトの現状を、最新のソースコードスキャンに基づいて整理しました。

## 1. 全体システム構成と各モジュール役割

### 🏗️ システム構成
このアプリは **Streamlit** を主軸にした **「AI駆動型株式分析プラットフォーム」** です。
モバイルでの操作性を最優先した UI 設計（PWA対応）と、複数の外部ソース（Yahoo Finance, Gemini AI, Google Sheets, LINE API）を連携させた高度なアーキテクチャで構成されています。

### 🧩 モデジュール別役割
| モジュール | 主な役割 |
| :--- | :--- |
| `app.py` | メインエントリーポイント。タブUI（チャート、AI分析、PF、スキャン等）の統合管理。 |
| `modules/analysis.py` | テクニカル指標（SMA, RSI, MACD, BB）の計算、売買戦略ロジックの実装。 |
| `modules/llm.py` | Google Gemini APIとの連携。Self-Reflection（多角的視点）を用いたレポート生成。 |
| `modules/data_manager.py` | 市場データ、財務データ取得の統括。キャッシュ管理とフォールバック処理。 |
| `modules/storage.py` | データの永続化。Google SheetsとローカルJSONのハイブリッド管理。 |
| `modules/notifications.py` | LINE通知、価格アラート、テクニカルシグナルの検知と送信制御。 |
| `modules/charts.py` | Plotly および Lightweight-charts を用いた動的チャートの生成。 |
| `modules/patterns.py` | ローソク足・チャートパターンの検知。 |
| `modules/backtest.py` | 提案された売買戦略の過去データによる検証。 |

---

## 2. データの管理（永続化機能）

データの保存先は **`modules/storage.py`** で一元管理されており、環境に応じて最適な保存先を自動選択します。

- **クラウド保存 (Google Sheets)**:
  - Streamlit Cloud デプロイ時は `streamlit-gsheets` を使用。
  - GitHub Actions 等のヘッドレス環境では `gspread` を使用。
  - 対象: ウォッチリスト、ポートフォリオ、通知ログ、ユーザー設定。
- **ローカル保存 (JSON)**:
  - ローカル開発環境時やクラウド連携失敗時のフォールバック。
  - `watchlist.json`, `portfolio.json`, `settings.json`, `alerts.json` に保存。

---

## 3. 実装済み機能チェック ✅

ご質問いただいた重要機能はすべて **実装済み** です。

| 機能 | 実装状況 | コードの場所 |
| :--- | :--- | :--- |
| **信用残（需給）分析** | ✅ 実装済み | `modules/data.py:get_credit_data`, `modules/analysis.py:239-254` |
| **AI Self-Reflection** | ✅ 実装済み | `modules/llm.py:67-126` (Bull/Bear Persona) |
| **LINE通知** | ✅ 実装済み | `modules/notifications.py`, `modules/line.py` |
| **データの永続化** | ✅ 実装済み | `modules/storage.py` (GSheets & JSON) |

---

## 4. 今後の改善・TODO 🚀

### 現時点での未完成部分・課題
1.  **リアルタイム性の向上**:
    - 現在は `yfinance` をメインソースとしているため、数分〜20分程度の遅延があります。秒単位のリアルタイム性を求めるなら、楽天証券公式APIや有料データプロバイダーとの連携検討が必要です。
2.  **売買タイミングの精度**:
    - 現在のタイミング抽出は `analysis.py` のルールベース（SMAやBB）です。これに「出来高の急増」や「板情報の変化（可能であれば）」をトリガーに加えると、より初動を捉えやすくなります。
3.  **エラーハンドリングの強化**:
    - Gemini API の 429 エラー（レート制限）へのリトライ処理は入っていますが、市場データ取得失敗時のモック表示との切り替えをよりスムーズにする余地があります。

### AIの視点：次の一手
- **「ニュース・センチメントの即時反映」**:
  - `modules/news.py` で取得したニュースを自動でAIが要約し、LINE通知で「このニュースで株価がどう動きそうか」を一言添えて送る機能を強化すると、忙しい日中でも判断しやすくなります。
- **「マルチタイムフレーム分析の強化」**:
  - 現在日足と週足をタブで切り替えていますが、AI判定時に「日足は逆張り、週足は順張り」といった**時間軸の矛盾**を自動で整理し、最適なホールド期間を提示するロジックを深掘りすると良いでしょう。
