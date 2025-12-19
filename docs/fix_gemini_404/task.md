# Gemini 404 エラーの根本解決タスク

- [ ] `modules/llm.py` の修正
    - [ ] `gemini-1.5-flash` 以外のバリエーション（`-latest`, `-001`, `gemini-2.0-flash-exp` 等）をフォールバックとして試行するロジックの導入
    - [ ] モデル指定時の `models/` プレフィックスの有無を両方試す
    - [ ] API 応答の詳細ログを出力し、デバッグを容易にする
- [ ] 動作確認用の最小構成スクリプトの作成
    - [ ] `tests/test_gemini_connection.py` を作成し、どのモデル名が有効かを確認できるようにする
- [ ] 修正内容のプッシュと Streamlit Cloud での確認
