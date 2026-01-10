# 実装計画 - 本番環境での表示・分析不具合の修正

本番環境（Streamlit Cloud）において、チャート上の指標（SMA, BB）や戦略ラインが表示されない問題、およびAI分析が正常に機能しない問題を修正します。

## ユーザーレビューが必要な項目

> [!IMPORTANT]
> この修正により、チャートの日付軸の処理がより厳密になり、表示の安定性が向上します。AI分析については、最新の Gemini 2.0 モデル（flash, pro）を確実に利用できるように候補を整理します。

## 提案される変更

### [Component: Charts]

#### [MODIFY] [charts.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/charts.py)
- `chart_df['time']` を生成する際、`pd.to_datetime` を通した上で `.dt.strftime('%Y-%m-%d')` を行い、文字列形式でライブラリに渡すようにします。これにより、シリアライズエラーを防ぎます。
- 指標（SMA, BB）の描画ロジックで、`dropna()` を行う前にインデックスを確実に文字列化し、データポイントの紐付けを強化します。

### [Component: AI Analysis]

#### [MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- `MODEL_CANDIDATES` に最新のモデル名（`gemini-2.0-flash`, `gemini-2.0-pro-exp-02-05` など）を整理して追加します。
- エラー発生時のログ出力を強化し、どのモデルで失敗したかを把握しやすくします（内部ログ）。
- プロンプトの微調整（データ不足時の推論をより強調）。

## 検証計画

### 自動検証
- `python -m py_compile modules/charts.py modules/llm.py` で構文エラーがないことを確認。

### 手動検証
1. ローカル環境でアプリを起動し、チャートに SMA, BB, 戦略ライン（水平線）が表示されることを確認。
2. AI分析を実行し、モックではなく本物の AI からの応答（詳細な分析文）が返ってくることを確認。
3. 変更を GitHub にプッシュし、本番環境（Streamlit Cloud）で同様の表示・動作を確認。
