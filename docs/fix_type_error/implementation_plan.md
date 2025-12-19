# 包括的 TypeError (NoneType formatting) 修正計画

## 概要
前回 `modules/llm.py` に対して行った修正に加え、同様のリスクがある `modules/charts.py` や `modules/backtest.py` など、アプリ全体の堅牢性を向上させるための修正を行います。
下落トレンドなどで特定の値（エントリー価格、利確目標、損切目安など）が `None` になる状況でも、アプリが正常に動作し続けるようにします。

## 修正内容

### 1. [charts.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/charts.py)
- チャート上のアノテーション（利確目標、損切、エントリー）を表示する際、値が `None` の場合に f-string フォーマット (`:,`) でエラーにならないようガードを追加します。

### 2. [backtest.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/backtest.py)
- 数値比較 (`>=`, `<=`) を行う前に、値が `None` でないことを確認します。

### 3. [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- すべてのプロンプト内変数に対して `(value or 0)` などの安全な取得を徹底します。

### 4. [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)
- メトリクス表示部分での `None` に対するガードを確認・追加します。

## 変更ファイル

### [modules/charts.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/charts.py)
#### [MODIFY] [charts.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/charts.py)
- `target`, `stop`, `entry_price` のチェックとフォーマットを修正。

### [modules/backtest.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/backtest.py)
#### [MODIFY] [backtest.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/backtest.py)
- 比較演算子での `None` チェックを追加。

### [modules/llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
#### [MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- プロンプト内の変数をさらに安全に。

## 検証計画
- 下落トレンド判定銘柄（三菱重工など、直近調整中の銘柄を想定）での動作確認。
- ローカルテストスクリプト `tests/test_fix_type_error.py` の更新と実行。
