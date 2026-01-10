# 本番環境不具合修正タスク

## チャート表示不具合 (SMA, BB, トレンドライン)
- [x] `modules/charts.py` の描画ロジック修正 [x]
- [x] `modules/analysis.py` での指標計算結果のデータフレーム確認 [x]
- [x] `lightweight-charts` の本番環境での動作確認（ライブラリバージョン等） [x]

## AI分析不具合
- [x] `modules/llm.py` のプロンプトとレスポンス処理の修正 [x]
- [x] APIキーやモデル設定の再確認（本番環境の secrets 等） [x]
- [x] `generate_gemini_analysis` の呼び出し部分のデバッグ [x]

## デプロイと検証
- [x] 修正の適用とローカル・本番での検証 [x]
- [x] GitHub へのプッシュとデプロイ確認 [x]
