# kabuzan 現状整理・報告計画

本計画は、現在開発中の株価分析アプリ「kabuzan」のシステム構成、各モジュールの役割、データ管理手法、および実装済み機能を網羅的に整理し、ユーザーに報告することを目的としています。

## 報告内容の骨子

### 1. 全体システム構成
- StreamlitをベースとしたWebアプリケーション構成
- モジュール化されたアーキテクチャ（データ取得、分析、UI、通知を分離）

### 2. 各モジュールの役割
- `app.py`: メインUI、ルーティング、セッション管理
- `analysis.py`: テクニカル指標計算、売買戦略策定（信用残分析含む）
- `llm.py`: Geminiによる高度なAI分析（プロンプト・自己反省ロジック反映）
- `data_manager.py`: データ取得の統合管理（yfinance / defeatbeta）
- `storage.py`: データの永続化（Local JSON / Google Sheets）
- `notifications.py`: LINE Messaging API通知、定期レポート送信

### 3. データ管理方式
- 永続化の仕組み：`storage.py`により、JSONファイルまたはGoogle Sheetsに保存。
- 環境対応：ローカル、Streamlit Cloud、GitHub Actionsの各環境で動作。

### 4. 実装済み機能の確認（ユーザー指定項目）
- [x] **信用残（需給）分析**: `analysis.py`の`calculate_trading_strategy`付近で信用倍率を考慮。
- [x] **AI Self-Reflection**: `llm.py`のプロンプトにて、強気派・弱気派の対立構造を組み込み済み。
- [x] **LINE通知**: `line.py`および`notifications.py`にて、定期レポートとシグナル通知機能を実装済み。
- [x] **データ永続化**: `storage.py`により、ブラウザセッションを超えたデータ保存を実装済み。

### 5. 今後の課題・TODO
- マーケットスキャンのさらなる高速化。
- リアルタイム性の向上と、売り買いのタイミング精度の微調整。

## 成果物
- [ ] `docs/project_status_summary/walkthrough.md` (最終報告書)
