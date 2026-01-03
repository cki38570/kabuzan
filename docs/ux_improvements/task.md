# Task: アプリのUX向上とパフォーマンス改善

ユーザーからのフィードバックに基づき、キャッシュの実装、UIの整理、不要な機能の削除を行います。

- [x] 実装計画の作成と承認 [x]
- [x] 1. アプリ状態の永続化（キャッシュ） [x]
    - [x] `st.session_state` を拡張し、`analysis_cache` 辞書を実装
    - [x] 分析実行時に結果（`report_data`, `df`, `info` 等）を保存
    - [x] 銘柄入力時にキャッシュが存在すれば再計算をスキップして表示
- [x] 2. UIのタブ化（HTMXライクな操作感） [x]
    - [x] 分析結果エリアを `st.tabs` で分割
    - [x] タブ構成案: [🤖 AI分析], [📈 チャート], [📰 ニュース・財務], [📊 比較・詳細]
    - [x] 各情報を適切なタブ内に移動
- [x] 3. ポートフォリオ機能の移動 [x]
    - [x] メインエリア上部（検索の下）またはサイドバーに常設化
    - [x] 銘柄未選択時でも閲覧・操作可能にする
- [x] 4. Plotly の完全削除 [x]
    - [x] `modules/charts.py`: `create_main_chart` (Plotly版) を削除
    - [x] `modules/charts.py`: `create_credit_chart` を `altair` または `lightweight_charts` 版に移行（信用残は棒グラフなので `st.bar_chart` でも可）
    - [x] `app.py`: `st.plotly_chart` の呼び出しを `st.write(chart.load())` (Lightweight Charts) に置換
    - [x] 依存関係 (`requirements.txt`) から `plotly` を削除
- [x] 5. プリセットボタンの削除 [x]
    - [x] `app.py`: 検索バー下のクイック選択ボタン（トヨタ等）を削除
- [x] 動作確認とデプロイ [x]

