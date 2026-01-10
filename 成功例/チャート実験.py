import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
from scipy.signal import argrelextrema
import streamlit.components.v1 as components
import json

# ページ設定
st.set_page_config(layout="wide", page_title="Advanced Stock Chart")

st.title("高機能株価チャート (Lightweight Charts - Custom)")

# サイドバー設定
st.sidebar.header("設定")
ticker_input = st.sidebar.text_input("銘柄コード (例: 7203.T)", value="7203.T")
period = st.sidebar.selectbox("期間", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

# データ取得関数
@st.cache_data(ttl=3600)
def get_stock_data(ticker, period):
    try:
        df = yf.download(ticker, period=period)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        date_col = None
        for col in df.columns:
            if str(col).lower() in ['date', 'datetime', 'timestamp']:
                date_col = col
                break
        if date_col:
            df.rename(columns={date_col: 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        return df
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return None

data = get_stock_data(ticker_input, period)

if data is not None and not data.empty:
    # --- テクニカル指標計算 ---
    # SMA
    data['SMA_25'] = ta.sma(data['Close'], length=25)
    # BB
    bbands = ta.bbands(data['Close'], length=20, std=2)
    if bbands is not None:
        data = pd.concat([data, bbands], axis=1)
    # PSAR
    psar = ta.psar(data['High'], data['Low'], data['Close'], af0=0.02, af=0.02, max_af=0.2)
    if psar is not None:
        # Combine PSAR columns
        psar_cols = [c for c in data.columns if 'PSAR' in c]
        if psar_cols:
             data['PSAR'] = data[psar_cols].bfill(axis=1).iloc[:, 0]

    # --- トレンドライン (マーカー用) ---
    highs = argrelextrema(data['High'].values, np.greater_equal, order=5)[0]
    lows = argrelextrema(data['Low'].values, np.less_equal, order=5)[0]
    
    markers = []
    for idx in highs[-5:]:
        markers.append({
            'time': str(data.iloc[idx]['Date']),
            'position': 'aboveBar',
            'color': '#ef5350',
            'shape': 'arrowDown',
            'text': 'Res'
        })
    for idx in lows[-5:]:
        markers.append({
            'time': str(data.iloc[idx]['Date']),
            'position': 'belowBar',
            'color': '#26a69a',
            'shape': 'arrowUp',
            'text': 'Sup'
        })

    # --- データ整形 (JSON用) ---
    candlestick_data = []
    sma_data = []
    bb_upper_data = []
    bb_lower_data = []
    psar_data = []

    bb_upper_col = [c for c in data.columns if 'BBU' in c][0] if [c for c in data.columns if 'BBU' in c] else None
    bb_lower_col = [c for c in data.columns if 'BBL' in c][0] if [c for c in data.columns if 'BBL' in c] else None

    for i, row in data.iterrows():
        t = str(row['Date'])
        candlestick_data.append({
            'time': t,
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close']),
        })
        
        if 'SMA_25' in data.columns and not pd.isna(row['SMA_25']):
            sma_data.append({'time': t, 'value': float(row['SMA_25'])})
            
        if bb_upper_col and not pd.isna(row[bb_upper_col]):
            bb_upper_data.append({'time': t, 'value': float(row[bb_upper_col])})
        if bb_lower_col and not pd.isna(row[bb_lower_col]):
            bb_lower_data.append({'time': t, 'value': float(row[bb_lower_col])})
            
        if 'PSAR' in data.columns and not pd.isna(row['PSAR']):
            psar_data.append({'time': t, 'value': float(row['PSAR'])})

    # --- HTML/JS 生成 ---
    # NaNをNoneに変換してからdumpする (JSでのパースエラー防止)
    # ignore_nan=True for simplejson, but for standard json we need to clean data.
    # My manual construction above largely avoids NaNs by simple if checks.
    # But let's be double sure and handle chart resize better.

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/lightweight-charts@3.8.0/dist/lightweight-charts.standalone.production.js"></script>
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; font-family: sans-serif; }}
            #chart {{ width: 100%; height: 500px; }}
            #error-log {{ color: red; font-size: 12px; display: none; }}
        </style>
    </head>
    <body>
        <div id="error-log"></div>
        <div id="chart"></div>
        <script>
            window.onerror = function(message, source, lineno, colno, error) {{
                document.getElementById('error-log').style.display = 'block';
                document.getElementById('error-log').innerText = 'Chart Error: ' + message;
            }};

            const chartContainer = document.getElementById('chart');
            
            // Fallback width if clientWidth is 0 (can happen in some iframe contexts)
            const width = chartContainer.clientWidth || 800;

            const chart = LightweightCharts.createChart(chartContainer, {{
                width: width,
                height: 500,
                layout: {{
                    background: {{ type: 'solid', color: 'white' }},
                    textColor: 'black',
                }},
                grid: {{
                    vertLines: {{ color: 'rgba(197, 203, 206, 0.5)' }},
                    horzLines: {{ color: 'rgba(197, 203, 206, 0.5)' }},
                }},
                rightPriceScale: {{
                    borderColor: 'rgba(197, 203, 206, 0.8)',
                }},
                timeScale: {{
                    borderColor: 'rgba(197, 203, 206, 0.8)',
                }},
            }});

            const candlestickSeries = chart.addCandlestickSeries({{
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderVisible: false,
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350',
            }});
            
            // Data Injection with cleaning
            const candleData = {json.dumps(candlestick_data).replace("NaN", "null")};
            const markerData = {json.dumps(markers).replace("NaN", "null")};
            const smaData = {json.dumps(sma_data).replace("NaN", "null")};
            const bbUpperData = {json.dumps(bb_upper_data).replace("NaN", "null")};
            const bbLowerData = {json.dumps(bb_lower_data).replace("NaN", "null")};
            const psarData = {json.dumps(psar_data).replace("NaN", "null")};

            candlestickSeries.setData(candleData);
            candlestickSeries.setMarkers(markerData);

            const smaSeries = chart.addLineSeries({{
                color: '#2196F3',
                lineWidth: 2,
                title: 'SMA(25)',
            }});
            smaSeries.setData(smaData);

            const bbUpperSeries = chart.addLineSeries({{
                color: 'rgba(76, 175, 80, 0.5)',
                lineWidth: 1,
                title: 'BB Upper',
            }});
            bbUpperSeries.setData(bbUpperData);

            const bbLowerSeries = chart.addLineSeries({{
                color: 'rgba(76, 175, 80, 0.5)',
                lineWidth: 1,
                title: 'BB Lower',
            }});
            bbLowerSeries.setData(bbLowerData);

            const psarSeries = chart.addLineSeries({{
                color: '#FFA726',
                lineWidth: 0, 
                title: 'Parabolic SAR',
            }});
            
            psarSeries.applyOptions({{
                lineStyle: 3, // Dotted
                lineWidth: 2
            }});
            
            psarSeries.setData(psarData);

            // Resize handle
            window.addEventListener('resize', () => {{
                chart.applyOptions({{ width: chartContainer.clientWidth }});
            }});
        </script>
    </body>
    </html>
    """

    st.markdown("### テクニカル分析チャート")
    components.html(html_code, height=500)
    
    st.info("トレンドライン情報: チャート上に直近のサポート(Sup)/レジスタンス(Res)ポイントをマーカーで表示しています。PSARはドットラインで表示しています。")

else:
    st.warning("データを取得できませんでした。銘柄コードを確認してください。")

st.markdown("""
### 表示要素解説
- **SMA (青線)**: 25日単純移動平均線。
- **ボリンジャーバンド (緑線)**: ±2σの範囲。
- **パラボリックSAR (オレンジ点線)**: トレンド転換のシグナル。
- **Sup/Resマーカー**: AI(アルゴリズム)が検出した重要高値・安値。
""")
