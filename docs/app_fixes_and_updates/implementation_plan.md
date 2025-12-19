# アプリの修正とアップデート計画

## 概要
Gemini APIを最新の `google-genai` パッケージへ移行し、Streamlitの非推奨警告（`use_container_width`）を解消します。また、`modules/charts.py` の `NameError` および `modules/backtest.py` の `TypeError` を修正します。

## 提案される変更

### 1. 依存関係の更新
#### [MODIFY] [requirements.txt](file:///c:/Users/GORO/Desktop/kabuzan/requirements.txt)
- `google-generativeai` を `google-genai` に置き換えます。

### 2. Gemini APIの最新化
#### [MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- `google-generativeai` から `google-genai` (Google API SDK v1相当) へ移行します。
- インポートを `from google import genai` に修正します。
- 万が一 `google-genai` が見つからない場合は、旧 `google-generativeai` を試みるフォールバックロジックを追加します。
- エラー発生時にモックレポート内にエラー内容を表示するデバッグ機能を追加します。

### 3. モジュールの修正
#### [MODIFY] [charts.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/charts.py)
- `import pandas as pd` を追加し、`pd.isna()` が動作するようにします。

#### [MODIFY] [backtest.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/backtest.py)
- `support_level` が `None` になる可能性を考慮し、数値計算前にチェックを追加します。

### 4. Streamlit 非推奨警告への対応
#### [MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)
- `use_container_width=True` を `width='stretch'` （または警告に従った適切な引数）に置換します。
- ※最新の Streamlit (1.52.2) の警告内容に基づき、`st.dataframe` や `st.plotly_chart` での `use_container_width` を `width` に変更します。

## 検証プラン

### 自動テスト
- 現状、プロジェクトに自動テストスイートがないため、各モジュールのインポートテストを行います。
- `python -c "import modules.llm; import modules.charts; import modules.backtest"` を実行し、構文エラーやインポートエラーがないか確認します。

### 手動検証
1. アプリを起動し、銘柄を検索してチャートが表示されるか確認（`charts.py` の修正確認）。
2. AI分析を実行し、Gemini 1.5 Flash からの結果が正しく表示されるか確認（`llm.py` の修正確認）。
3. バックテスト実行時にエラーが発生しないか確認（`backtest.py` の修正確認）。
4. ログを確認し、`use_container_width` に関する警告が消えているか確認。
