# Github Monitor Bot 修正計画

## 概要
Github Actions で実行される `auto_monitor.py` が失敗する問題を修正します。主な原因は、必要な関数のインポート漏れと、ヘッドレスモード用の `streamlit` モックの実装不備です。

## 変更案

### [auto_monitor.py](file:///c:/Users/GORO/Desktop/kabuzan/auto_monitor.py)

#### [MODIFY] auto_monitor.py
- `modules.notifications` から `process_morning_notifications` をインポートするように修正します。
- `st.session_state` のモックを、属性アクセス (`.attr`) と辞書アクセス (`['key']`) の両方に対応したクラスに変更します。これにより、`st.session_state.notify_line` のようなアクセスが可能になります。

## 検証
- ローカル環境で `python auto_monitor.py` を実行し、インポートエラーや属性エラーが発生しないことを確認します（環境変数が不足しているため完全な実行はできませんが、初期化フェーズのエラーは検出できます）。
