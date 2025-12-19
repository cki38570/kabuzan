# AI分析エラーの修正と品質向上タスク

- [ ] `modules/llm.py` の修正
    - [ ] モデル名指定の修正 (`models/gemini-1.5-flash` への統一など)
    - [ ] `GENAI_AVAILABLE` の定義不足の修正
    - [ ] ニュース分析関数 (`analyze_news_impact`) のエクスポート確認
- [ ] AI分析の整合性・正確性のチェックロジック強化
    - [ ] テクニカル指標と推奨アクションの矛盾チェック用プロンプトの調整
    - [ ] `calculate_trading_strategy` と AI判定の比較ロジック検討
- [ ] 動作確認とデバッグ
    - [ ] Streamlit Cloud 上での動作を想定した検証
- [ ] コミットとプッシュ
