# TypeError 修正タスク

## 現状
- Streamlit Cloud 上で `TypeError` が発生し、株価の取得・分析が停止する。
- エラー箇所: `modules/llm.py` の f-string フォーマット部分。
- 原因推定: `strategic_data` 内の値が `None` や `str` になっており、`:,.0f` フォーマットが適用できない。

## タスク
- [x] エラー箇所の特定と詳細の確認 `modules/llm.py`
- [x] `strategic_data` の取得・解析ロジックを確認し、型変換を強化する
- [x] フォーマット処理でエラーが発生しないよう安全な実装に変更する (llm.py)
- [/] 他のモジュール (charts.py, backtest.py) の安全性を向上させる
- [ ] すべての変更を Streamlit Cloud に反映させるための準備
- [ ] 修正の検証
