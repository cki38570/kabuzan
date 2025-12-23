# Kabuzan v3.0 アップグレード・タスクリスト

# Kabuzan v3.0 アップグレード・タスクリスト

## フェーズ1: 基礎インフラとチャートエンジンの刷新
- [x] `lightweight-charts` のインストールと動作確認
- [x] `modules/charts.py` の更新 (Lightweight Charts 連携機能の追加)
    - [x] ローソク足チャートの実装
    - [x] 移動平均線、ボリンジャーバンドの描画
    - [x] AI戦略ライン (利確・損切・ENTRY) の自動描画機能
- [x] `app.py` でのチャートエンジンの統合 (Engine切り替え機能)

## フェーズ2: データ連携の強化 (v3.0 Data Pipeline)
- [x] `modules/defeatbeta_client.py` の機能拡張
    - [x] 決算説明会文字起こし (Transcripts) データの取得機能
- [x] `modules/data_manager.py` の更新
    - [x] マクロデータ (USD/JPY, ^N225) 取得機能の実装
    - [x] キャッシュロジックの導入

## フェーズ3: Gemini AI アナリストの高度化
- [x] `modules/llm.py` のプロンプトエンジニアリング刷新
    - [x] Self-Reflection (強気 vs 弱気アナリスト) ロジックの実装
    - [x] マクロデータおよび文字起こしデータの分析コンテキスト注入
- [x] Gemini API からの構造化 JSON 出力対応
- [x] `app.py` での AI 分析リポートのリッチ表示化 (パースロジック実装)

## フェーズ4: ドキュメントと最終調整 (DONE)
- [x] `system_design.md` の v3.0 への更新
- [x] `README.md` の更新
- [x] 最終動作確認 (コードベース)
- [x] ブラウザでの実稼働確認
- [x] `lightweight-charts` の UnicodeDecodeError 修正 (Windows対応)

## フェーズ5: 将来の拡張計画 (Future)
- [ ] FastAPI + htmx への完全移行によるパフォーマンス向上
- [ ] 信用需給データ (買い残・売り残) の詳細視覚化
- [ ] Context Caching 機能の導入
