# タスクリスト: 株価分析アプリの機能強化

## マルチタイムフレーム分析とUI改善
- [x] `modules/data_manager.py` の拡張（週足データの取得と指標計算に対応）
- [x] `modules/charts.py` の改善（レンジセレクター、マルチタイムフレーム、配色調整）
- [x] `app.py` のUI更新（日足/週足タブの追加、指標計算の呼び出し修正）
- [x] `modules/llm.py` のプロンプト更新（週足トレンドを考慮した思考ロジック）

## センチメント分析（ニュース連携）
- [x] `modules/news.py` の新規作成（yfinanceからのニュース取得）
- [x] `modules/llm.py` の更新（感情分析ロジック、100点満点スコアリングの導入）
- [x] `app.py` のUI表示追加（総合スコアゲージ、関連ニュース一覧）

## LINE通知機能の実装
- [x] `modules/notifications.py` にテクニカルシグナル検知ロジックを追加
- [x] `app.py` への統合（分析時の自動シグナルチェック）
- [x] `modules/line.py` の既存機能（LINE Notify）を活用した通知送信

## ドキュメント更新
- [x] `docs/system_overview_v2/system_design.md` の更新
- [x] `README.md` の更新
- [x] `docs/enhance_multi_timeframe_sentiment/implementation_plan.md` の作成
- [x] `docs/enhance_multi_timeframe_sentiment/walkthrough.md` の作成
