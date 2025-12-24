# Gemini API 無料枠安定化 実装計画

Gemini API の無料枠において、廃止済みモデルによる 404 エラーと、レート制限による 429 エラーを解消し、安定した動作を実現するための修正を行います。

## Proposed Changes

### LLM モジュール (`modules/llm.py`)

#### [MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)

1.  **モデル選択の最新化**:
    *   `MODEL_CANDIDATES` から `gemini-1.5-*` を削除。
    *   以下の優先順位でモデルを再設定：
        1.  `gemini-3-flash-preview`
        2.  `gemini-2.5-flash-lite`
        3.  `gemini-2.5-flash`
2.  **429エラー（レート制限）対策**:
    *   `generate_gemini_analysis` および `analyze_news_impact` 関数において、指数バックオフ（Exponential Backoff）を用いたリトライロジックを実装。
    *   `RESOURCE_EXHAUSTED` (429) エラーを検知した際、待機時間を倍増させながら最大3〜5回程度リトライ。
3.  **トークン節約の最適化**:
    *   システムプロンプトやインプットデータのトリミング処理を強化。
    *   特に「決算説明会文字起こし (`transcript_data`)」や「ニュースデータ」の入力文字数を制限（例：文字起こしは1500文字から1000文字へ削減、ニュースは上位2件に絞る等）。
4.  **SDK/エンドポイントの整合性**:
    *   `google-genai` SDK を使用し、必要に応じて `v1beta` エンドポイントが利用されるよう設定を確認。

## Verification Plan

### Automated Tests
- 新規テストスクリプト `tests/verify_gemini_logic.py` を作成し、以下の項目を検証：
    - モデルリストが正しく更新されているか。
    - 指数バックオフのロジックが（モック等を用いて）期待通り動作するか。
- コマンド: `python tests/verify_gemini_logic.py`

### Manual Verification
- Streamlit アプリケーションを起動 (`streamlit run app.py`)。
- 「AI分析」タブで株価分析を実行し、エラーが発生せずに結果が表示されることを確認。
- 429エラーが発生しやすい状況（連続実行など）で、リトライが行われ最終的に成功するか、または適切なメッセージが表示されるかを確認。
