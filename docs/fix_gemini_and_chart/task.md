# 緊急修正タスク

## Gemini 1.5 PRO の排除
- [x] `modules/llm.py` から `gemini-1.5-pro` を完全に削除する [x]
- [x] 代わりのフォールバックモデルとして `gemini-2.0-flash-lite-preview-02-05` 等の 2.0 系を指定する [x]

## チャート表示不具合の再調査と修正 (ボリンジャーバンド等)
- [/] ブラウザツールを使用して本番環境 (https://kabuzan-ai.streamlit.app/) の表示状態を確認する [/]
- [/] コンソールエラーや描画失敗の兆候を特定する [/]
- [/] `modules/charts.py` のボリンジャーバンド描画ロジックを再検討（カラム名の一致確認） [/]
- [/] `lightweight-charts` の最新仕様（特に `create_line` の `name` や `color` の渡し方）を再確認する [/]

## デプロイと最終確認
- [x] 修正をプッシュし、本番環境でボリンジャーバンドが表示されることをブラウザで目視確認する [x]
- [x] walkthrough.md を更新する [x]
