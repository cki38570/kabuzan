# 実装計画 - Gemini 1.5 PRO 排除とチャート表示不具合の根本解決

ユーザーからの指摘事項（Gemini 1.5 PROの使用禁止）を厳守し、本番環境でチャート指標やAI分析が表示されない問題を完全に解決します。

## ユーザーレビューが必要な項目

> [!CAUTION]
> **Gemini 1.5 PRO は今後一切使用しません。** 2.0 系の最新モデルのみを候補とします。
> また、チャート表示の修正に伴い、`lightweight-charts` へのデータ供給ロジックをより堅牢なものに変更します。

## 提案される変更

### [Component: AI Analysis]

#### [MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- `MODEL_CANDIDATES` から `gemini-1.5-pro` を**完全に削除**します。
- 代わりのフォールバック候補として `gemini-2.0-flash-lite-preview-02-05` を追加します。

### [Component: Charts & Logic]

#### [MODIFY] [charts.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/charts.py)
- `chart_df['time']` をすべての指標ポイントの共通キーとして、より厳密に管理します。
- **ボリンジャーバンドの描画**: カラム名の一致判定を強化し、`dropna()` でデータが消失しないよう、メインの `chart_df` とインデックスを完全同期させます。
- `line.set()` に渡すデータの `time` カラムが、メインチャートの `time` と完全に一致（文字列 YYYY-MM-DD）していることを保証します。

#### [MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)
- AI分析結果が表示されない原因として、例外処理で出力を飲み込んでしまっている可能性があるため、エラー発生時も状況がわかるように出力を調整します。

## 検証計画

### 自動検証
- `python -m py_compile app.py modules/charts.py modules/llm.py`: 構文エラーなしを確認。

### 手動検証
1. GitHub にプッシュ後、本番環境 (https://kabuzan-ai.streamlit.app/) で以下の点を目視確認する：
    - チャート上に SMA (5, 25, 75) および **ボリンジャーバンド (BB)** が描画されていること。
    - AI分析タブに、Gemini 2.0 による詳細な分析結果が表示されていること。
    - 分析が失敗した場合も、「1.5 Pro へのフォールバック」などの文言が一切含まれていないこと。
