# アプリ改善とUI最適化の実装計画

ユーザー体験を向上させるため、分析結果の保持、情報の整理、および不要なライブラリの削除を行います。

## 概要
1. **キャッシュ機能**: `st.session_state['analysis_cache']` を導入し、銘柄コードをキーにして分析結果をメモリ内に保持します。ページ遷移や再訪問時のロード時間を短縮します。
2. **UIタブ化**: 縦長のスクロールを解消するため、`st.tabs` を使用して情報を整理します。HTMXのような軽快な切り替え感を実現します。
3. **ポートフォリオ移動**: 常に資産状況を確認できるよう、ポートフォリオをトップレベルに配置します。
4. **脱Plotly**: 重たい `plotly` に依存せず、軽量な `lightweight-charts` に一本化します。
5. **UI整理**: 不要なプリセットボタンを削除し、検索バー周りをすっきりさせます。

## 詳細設計

### 1. キャッシング (`app.py`)
- `if 'analysis_cache' not in st.session_state: st.session_state.analysis_cache = {}`
- 分析完了時:
  ```python
  st.session_state.analysis_cache[ticker_input] = {
      'df': df, 'info': info, 'report_data': report_data, 'strategic_data': strategic_data, ...
  }
  ```
- 銘柄選択時:
  ```python
  if ticker_input in st.session_state.analysis_cache:
      data = st.session_state.analysis_cache[ticker_input]
      # データを復元して表示処理へ
  else:
      # 新規分析実行
  ```

### 2. UI構成案 (`app.py`)
```python
tab_ai, tab_chart, tab_data, tab_portfolio = st.tabs(["🤖 AI分析", "📈 チャート", "📊 データ・ニュース", "💰 資産管理"])

with tab_ai:
    # Decision Center (AIスコア、売買判断バッジ)
    # AIの深層分析テキスト
    
with tab_chart:
    # Lightweight Charts (日足/週足)
    
with tab_data:
    # テクニカル指標一覧
    # 関連ニュース
    # 信用残推移
```

### 3. ポートフォリオ (`app.py`)
- `if ticker_input:` ブロックの外、検索バーの上または直下に `render_portfolio_summary()` のようなコンポーネントを配置。
- 詳細な管理画面は上記の `tab_portfolio` 内、またはアコーディオンで常設。

### 4. Plotly削除 (`modules/charts.py`, `app.py`)
- `modules/charts.py`: `create_main_chart` (Plotly版) を削除。
- `create_credit_chart`: Plotly依存を排除し、`st.bar_chart` でネイティブ描画するように変更。
- `app.py`: `st.plotly_chart` の呼び出しをすべて削除。
- `requirements.txt`: `plotly` を削除。

### 5. プリセット削除
- `QUICK_TICKERS` のボタン配置コードを削除。

## 検証計画
- ブラウザリロード後、同じ銘柄を検索して瞬時に表示されるか（キャッシュ確認）。
- タブ切り替えがスムーズに行えるか。
- チャートが軽量化され、正しく表示されるか（Plotly削除の影響がないか）。
