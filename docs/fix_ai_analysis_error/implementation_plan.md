# AI分析エラー修正と分析品質向上計画

AIによる株価分析で発生している 404 エラーを修正し、分析内容の正確性と整合性を厳格に向上させます。

## ユーザーレビューが必要な事項
- **AI分析の正確性チェック**: AIの回答がテクニカル指標（RSI, MACD等）から逸脱していないかを「プロンプトの厳格化」によって担保します。

## 変更内容

### 1. AI分析エラーの解消

#### [MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- **モデル名指定の修正**: Legacy SDK でのエラー `404 models/gemini-1.5-flash is not found` を解消するため、モデル名を `models/gemini-1.5-flash` に統一（または利用可能な `gemini-1.5-flash` に修正）します。
- **GENAI_AVAILABLE の再定義**: `GENAI_AVAILABLE` が他のモジュール（`app.py` 等）から正しく参照できるように、定義場所とインポートミスを修正します。

### 2. 分析品質の向上（正確性・整合性のチェック）

#### [MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- **プロンプトの厳格化**: プロンプト内で「テクニカル指標の数値を絶対に無視しないこと」「トレンドと売買推奨が矛盾した場合は、必ず保守的な（様子見の）意見を採用すること」を強調します。
- **出力言語の明示**: 回答が日本語で安定して出力されるよう、プロンプト末尾に「必ず日本語で回答してください」等の指示を追加します。

### 3. モジュール整合性の確保

#### [MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)
- **インポートの健全化**: `ImportError` を引き起こしていた `from modules.llm import GENAI_AVAILABLE` 周辺のインポート、および `use_container_width` 警告（ログに大量発生中）の修正を行います。

## 検証計画

### 自動テスト
- `tests/verification.py` を拡張し、Gemini API の呼び出しテスト（空文字チェック等）を追加。

### 手動検証
1. Streamlit Cloud での動作確認（ログに 404 エラーが出ないこと）。
2. 極端なデータ（RSI 90など）を渡し、AIが正しく「過熱」と判断して「追っかけ買いを控える」アドバイスをするか確認。
