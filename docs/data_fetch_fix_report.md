# データ取得エラーの調査と修正レポート

## 問題の概要

銘柄コードを入力しても「銘柄コード {ticker} のデータを取得できませんでした。」というエラーが表示される問題を調査しました。

## 原因

`modules/data_manager.py` の `get_market_data` メソッドに以下の問題がありました:

### 1. 変数スコープの問題

```python
# 問題のあるコード (修正前)
try:
    info = ticker.info  # ここで例外が発生する可能性
    current_price = info.get('currentPrice') or ...
    name = info.get('longName', ticker_code)
except Exception as e:
    if not df.empty:
        current_price = df['Close'].iloc[-1]
        name = f"{ticker_code} (Price Only)"
    else:
        return pd.DataFrame(), {}

# 問題: ここで info が未定義の可能性
self._info_cache[ticker_code] = info  # NameError!
```

`ticker.info` の取得に失敗した場合、`info` 変数が未定義のまま後続の処理でアクセスしようとしていました。

### 2. エラーハンドリングの不足

データ取得失敗時のログが不十分で、トラブルシューティングが困難でした。

## 実施した修正

### 修正1: 変数の初期化

```python
# 修正後のコード
if df.empty:
    return pd.DataFrame(), {}

# Initialize info to avoid NameError
info = {}
sector = '不明'
industry = '不明'

try:
    info = ticker.info
    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or df['Close'].iloc[-1]
    name = info.get('longName', ticker_code)
    sector = info.get('sector', '不明')
    industry = info.get('industry', '不明')
except Exception as e:
    print(f"Failed to get ticker info for {ticker_code}: {e}")
    if not df.empty:
        current_price = df['Close'].iloc[-1]
        name = f"{ticker_code} (Price Only)"
    else:
        return pd.DataFrame(), {}

# 安全に info にアクセス
if info:
    self._info_cache[ticker_code] = info
```

### 修正2: エラーログの追加

```python
try:
    df = ticker.history(period=period, interval=interval)
    if df.empty:
        print(f"yfinance returned empty DataFrame for {ticker_code}")
except Exception as e:
    print(f"yfinance history fetch failed for {ticker_code}: {e}")
    df = pd.DataFrame()

if df.empty:
    print(f"Cannot fetch data for {ticker_code} - both FMP and yfinance failed or returned empty data")
    return pd.DataFrame(), {}
```

### 修正3: metaディクショナリの安全な構築

```python
meta = {
    'current_price': current_price,
    'change': change,
    'change_percent': change_percent,
    'name': name,
    'sector': sector,  # 変数を直接使用
    'industry': industry,  # 変数を直接使用
    'source': 'yfinance',
    'status': 'fresh'
}
```

## テスト結果

修正後、以下のティッカーコードでテストを実施しました:

```
Testing ticker: 9501
[SUCCESS] Data retrieved for 9501
   Name: Tokyo Electric Power Company Holdings, Incorporated
   Current Price: 609.6
   Change: -52.39999999999998
   Change %: -7.92%
   Sector: Utilities
   Source: yfinance
   DataFrame shape: (18, 7)
   Latest close: 609.60

Testing ticker: 7203
[SUCCESS] Data retrieved for 7203
   Name: Toyota Motor Corporation
   Current Price: 3459.0
   Change: -18.0
   Change %: -0.52%
   Sector: Consumer Cyclical
   Source: yfinance
   DataFrame shape: (18, 7)
   Latest close: 3459.00

Testing ticker: 6758
[SUCCESS] Data retrieved for 6758
   Name: Sony Group Corporation
   Current Price: 3490.0
   Change: -56.0
   Change %: -1.58%
   Sector: Technology
   Source: yfinance
   DataFrame shape: (18, 7)
   Latest close: 3490.00

Testing ticker: 9501.T
[SUCCESS] Data retrieved for 9501.T
   Name: Tokyo Electric Power Company Holdings, Incorporated
   Current Price: 609.6
   Change: -52.39999999999998
   Change %: -7.92%
   Sector: Utilities
   Source: yfinance
   DataFrame shape: (18, 7)
   Latest close: 609.60
```

**すべてのテストが成功しました！**

## 確認方法

1. **アプリケーションを起動**:
   ```bash
   python -m streamlit run app.py
   ```

2. **銘柄コードを入力**:
   - 9501 (東京電力)
   - 7203 (トヨタ)
   - 6758 (ソニー)
   など

3. **結果を確認**:
   - データが正常に表示されることを確認
   - チャートが表示されることを確認
   - AI分析が実行されることを確認

## もしまだエラーが発生する場合

以下の手順を試してください:

### 1. キャッシュのクリア

```bash
# Windowsの場合
Remove-Item -Recurse -Force .cache

# Streamlitを再起動
python -m streamlit run app.py
```

### 2. ブラウザのキャッシュをクリア

- Chrome/Edge: `Ctrl + Shift + Delete`
- または `Ctrl + F5` でハードリロード

### 3. ログの確認

アプリケーション起動時のターミナルで、以下のようなエラーメッセージがないか確認:
- `yfinance history fetch failed for {ticker_code}`
- `Cannot fetch data for {ticker_code}`
- `Failed to get ticker info for {ticker_code}`

### 4. ネットワークの確認

yfinance APIへの接続を確認:
```python
import yfinance as yf
ticker = yf.Ticker('9501.T')
print(ticker.history(period='1mo'))
```

## まとめ

- ✅ コードの問題を特定し修正しました
- ✅ すべてのテストケースが成功しました
- ✅ エラーログを強化し、今後のデバッグが容易になりました

修正したファイル:
- `modules/data_manager.py` (176-220行目付近)
