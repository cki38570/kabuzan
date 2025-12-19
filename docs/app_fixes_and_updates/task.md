# タスクリスト: アプリの修正とアップデート

## 1. 調査と計画
- [x] 現状のコードの確認 (llm.py, charts.py, backtest.py)
- [x] 修正計画の作成 (implementation_plan.md)

## 2. モジュールの修正
- [x] `modules/llm.py`: `google-genai` への移行または API バージョン修正
- [x] `modules/charts.py`: pandas のインポート追加と `pd.isna` の修正
- [x] `modules/backtest.py`: `TypeError` (NoneType) の回避処理追加

## 3. 全体的なアップデート
- [x] `use_container_width=True` を `width='stretch'` に置換 (全ファイル)

## 4. 検証
- [x] 修正箇所の動作確認
- [x] 最終レポートの作成 (walkthrough.md)
