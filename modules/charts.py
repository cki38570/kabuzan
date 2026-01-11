import pandas as pd
import json
import numpy as np

def create_credit_chart(credit_df):
    """
    Returns a dataframe suitable for st.bar_chart to display credit balance.
    """
    if credit_df is None or credit_df.empty:
        return None
        
    # Try to find Buy/Sell columns
    sell_col = next((c for c in credit_df.columns if '売残' in c), None)
    buy_col = next((c for c in credit_df.columns if '買残' in c), None)
    date_col = next((c for c in credit_df.columns if '日' in c or 'Date' in c), None)
    
    if not sell_col or not buy_col:
        return None

    # Filter columns for display
    chart_data = credit_df[[sell_col, buy_col]].copy()
    if date_col:
         chart_data.index = credit_df[date_col]
         
    return chart_data

def create_lightweight_chart(df, ticker_name, strategic_data=None, interval="1d"):
    """
    Generates an HTML string containing a Lightweight Charts instance with:
    - Candlestick Series
    - Moving Averages (SMA)
    - Bollinger Bands (3 Lines)
    - Parabolic SAR (as Dotted Line)
    - Volume
    - RSI (Separate Pane via scaleMargins)
    """
    if df is None or df.empty:
        return None

    # --- 1. Data Preparation ---
    chart_df = df.copy()
    
    # Handle Date Index to 'time' column
    if 'Date' in chart_df.columns:
        chart_df = chart_df.rename(columns={'Date': 'time'})
    elif chart_df.index.name == 'Date' or isinstance(chart_df.index, pd.DatetimeIndex):
        chart_df['time'] = chart_df.index
    
    # Ensure time is string YYYY-MM-DD for daily
    chart_df['time'] = pd.to_datetime(chart_df['time']).dt.strftime('%Y-%m-%d')
    
    # Standardize OHLCV columns
    chart_df = chart_df.rename(columns={
        'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
    })

    # Helper to clean data for JSON (NaN -> None/null)
    def clean_data(df_subset):
        # Convert to dict records
        records = df_subset.to_dict('records')
        # Iterate and replace NaN with None (which becomes null in JSON)
        cleaned_records = []
        for row in records:
            cleaned_row = {}
            for k, v in row.items():
                if isinstance(v, float) and (np.isnan(v) or pd.isna(v)):
                    cleaned_row[k] = None
                else:
                    cleaned_row[k] = v
            cleaned_records.append(cleaned_row)
        return json.dumps(cleaned_records)

    # Main Candle Data
    candle_data_json = clean_data(chart_df[['time', 'open', 'high', 'low', 'close']])
    volume_data_json = clean_data(chart_df[['time', 'volume']].rename(columns={'volume': 'value'}))

    # Indicators Data Preparation
    sma_data = {}
    if interval == "1wk":
        ma_config = [('SMA_13', '#2962FF'), ('SMA_26', '#FF6D00'), ('SMA_52', '#00C853')]
    else:
        ma_config = [('SMA_5', '#FFFF00'), ('SMA_25', '#FF00FF'), ('SMA_75', '#00E676')]
        
    for ma_name, color in ma_config:
        # Find column (handle variants)
        col = next((c for c in [ma_name, ma_name.replace('_', '')] if c in chart_df.columns), None)
        if col:
            sma_data[ma_name] = {
                'color': color,
                'data': clean_data(chart_df[['time', col]].rename(columns={col: 'value'}))
            }

    # Bollinger Bands
    bb_data = {}
    # Search for pandas_ta generated columns (e.g. BBU_20_2.0) or custom names
    bb_upper_col = next((c for c in chart_df.columns if c.startswith('BBU_') or c == 'BB_Upper'), None)
    bb_lower_col = next((c for c in chart_df.columns if c.startswith('BBL_') or c == 'BB_Lower'), None)
    bb_mid_col = next((c for c in chart_df.columns if c.startswith('BBM_') or c == 'BB_Mid' or c == 'SMA_20'), None)
    
    if bb_upper_col and bb_lower_col:
        bb_data['upper'] = clean_data(chart_df[['time', bb_upper_col]].rename(columns={bb_upper_col: 'value'}))
        bb_data['lower'] = clean_data(chart_df[['time', bb_lower_col]].rename(columns={bb_lower_col: 'value'}))
        if bb_mid_col:
             bb_data['mid'] = clean_data(chart_df[['time', bb_mid_col]].rename(columns={bb_mid_col: 'value'}))

    # Parabolic SAR
    psar_data = None
    # Prefer the combined 'PSAR' column we just made in analysis.py
    if 'PSAR' in chart_df.columns:
         psar_data = clean_data(chart_df[['time', 'PSAR']].rename(columns={'PSAR': 'value'}))
    else:
         # Fallback search
         psar_col = next((c for c in chart_df.columns if c.startswith('PSAR') or c == 'SAR'), None)
         if psar_col:
             psar_data = clean_data(chart_df[['time', psar_col]].rename(columns={psar_col: 'value'}))

    # RSI Data
    rsi_data = None
    rsi_col = next((c for c in chart_df.columns if c.startswith('RSI')), 'RSI')
    if rsi_col in chart_df.columns:
         rsi_data = clean_data(chart_df[['time', rsi_col]].rename(columns={rsi_col: 'value'}))

    # Markers (AI Targets)
    markers = []
    if strategic_data:
        # Last Date
        last_time = chart_df['time'].iloc[-1]
        
        # Entry
        if 'entry_price' in strategic_data and strategic_data['entry_price']:
            markers.append({
                'time': last_time, 'position': 'inBar', 'color': '#00ffbd', 'shape': 'arrowUp', 'text': 'ENTRY'
            })
        
        # Profit Take (Target)
        if 'sell_limit' in strategic_data and strategic_data['sell_limit']:
            markers.append({
                'time': last_time, 'position': 'aboveBar', 'color': '#FFD700', 'shape': 'arrowDown', 'text': 'TP'
            })

        # Stop Loss
        if 'stop_loss' in strategic_data and strategic_data['stop_loss']:
             markers.append({
                'time': last_time, 'position': 'belowBar', 'color': '#ff4b4b', 'shape': 'arrowUp', 'text': 'SL'
            })
            
            
    markers_json = json.dumps(markers)
    
    # Price Lines Data (Japanese Labels)
    price_lines = []
    if strategic_data:
        if 'stop_loss' in strategic_data and strategic_data['stop_loss']:
            price_lines.append({
                'price': float(strategic_data['stop_loss']), 
                'color': '#ff4b4b', 
                'title': '損切', # Japanese
                'lineStyle': 2 # Dashed
            })
        if 'sell_limit' in strategic_data and strategic_data['sell_limit']:
             price_lines.append({
                'price': float(strategic_data['sell_limit']), 
                'color': '#FFD700', 
                'title': '利確', # Japanese
                'lineStyle': 2 # Dashed
            })
        if 'entry_price' in strategic_data and strategic_data['entry_price']:
             price_lines.append({
                'price': float(strategic_data['entry_price']), 
                'color': '#00ffbd', 
                'title': 'エントリー', # Japanese
                'lineStyle': 2 # Dashed
            })
    
    price_lines_json = json.dumps(price_lines)

    # --- 2. HTML/JS Construction ---
    # Using Lightweight Charts v4.1+ (API compliant)
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background-color: #0a192f; overflow: hidden; }}
            #chart {{ width: 100%; height: 600px; }}
            .legend {{
                position: absolute; left: 12px; top: 12px; z-index: 10;
                font-family: 'Roboto', sans-serif; font-size: 14px;
                color: #d1d4dc; pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <div class="legend">{ticker_name} ({interval})</div>
        <div id="chart-container" style="position: relative; width: 100%; height: 600px;">
            <div id="chart" style="position: absolute; width: 100%; height: 100%;"></div>
        </div>
        <div id="debug" style="color: red; padding: 10px;"></div>
        <script>
            try {{
                const container = document.getElementById('chart');
                
                // Initialize Chart
                const chart = LightweightCharts.createChart(container, {{
                    width: container.clientWidth,
                    height: 600,
                    layout: {{
                        background: {{ type: 'solid', color: '#0a192f' }}, // Dark Navy Background (v4 syntax)
                        textColor: '#d1d5db',
                    }},
                    grid: {{
                        vertLines: {{ color: '#1e293b' }},
                        horzLines: {{ color: '#1e293b' }},
                    }},
                    crosshair: {{
                        mode: LightweightCharts.CrosshairMode.Normal,
                    }},
                    rightPriceScale: {{
                        borderColor: '#2B2B43',
                        visible: true,
                        scaleMargins: {{
                            top: 0.1,    // Leave space at top
                            bottom: 0.25, // Leave space at bottom for RSI (Main Series Area)
                        }},
                    }},
                    timeScale: {{
                        borderColor: '#2B2B43',
                        timeVisible: true,
                    }},
                }});

                // --- 1. Main Series (Candle & Overlay) ---
                
                // Candlestick Series
                const candlestickSeries = chart.addCandlestickSeries({{
                    upColor: '#ef4444', downColor: '#22c55e', 
                    borderUpColor: '#ef4444', borderDownColor: '#22c55e',
                    wickUpColor: '#ef4444', wickDownColor: '#22c55e',
                }});
                candlestickSeries.setData({candle_data_json});

                // Volume (Overlay at bottom of main pane)
                const volumeSeries = chart.addHistogramSeries({{
                    color: '#26a69a',
                    priceFormat: {{ type: 'volume' }},
                    priceScaleId: '', // Same ID (right) means overlay on main scale
                    scaleMargins: {{ top: 0.8, bottom: 0.25 }}, // Stick to bottom of main area
                }});
                volumeSeries.setData({volume_data_json});

                // SMA Lines
                const smaData = {json.dumps(sma_data)};
                for (const [name, info] of Object.entries(smaData)) {{
                    const line = chart.addLineSeries({{
                        color: info.color, lineWidth: 2, title: name
                    }});
                    line.setData(JSON.parse(info.data));
                }}
                
                // Bollinger Bands
                const bbData = {json.dumps(bb_data)};
                if (bbData.upper && bbData.lower) {{
                    // Upper
                    const upper = chart.addLineSeries({{ color: 'rgba(255, 165, 0, 0.5)', lineWidth: 1, title: 'BB Upper' }});
                    upper.setData(JSON.parse(bbData.upper));
                    
                    // Lower
                    const lower = chart.addLineSeries({{ color: 'rgba(255, 165, 0, 0.5)', lineWidth: 1, title: 'BB Lower' }});
                    lower.setData(JSON.parse(bbData.lower));
                    
                    // Middle
                    if (bbData.mid) {{
                        const mid = chart.addLineSeries({{ 
                            color: 'rgba(255, 165, 0, 0.8)', // Orangeish
                            lineWidth: 1, 
                            title: 'BB Mid' 
                        }});
                        mid.setData(JSON.parse(bbData.mid));
                    }}
                }}
                
                // Parabolic SAR
                const psarJson = {json.dumps(psar_data if psar_data else 'null')};
                if (psarJson && psarJson !== 'null') {{
                    const rawData = typeof psarJson === 'string' ? JSON.parse(psarJson) : psarJson;
                    if (rawData && rawData.length > 0) {{
                        const psarSeries = chart.addLineSeries({{
                            color: '#BA68C8', 
                            lineWidth: 2,
                            lineStyle: 1, // Dotted
                            title: 'PSAR',
                            crosshairMarkerVisible: false
                        }});
                        psarSeries.setData(rawData);
                    }}
                }}
                
                // Markers
                const aiMarkers = {markers_json};
                if (aiMarkers.length > 0) {{
                    candlestickSeries.setMarkers(aiMarkers);
                }}

                // Price Lines
                const priceLines = {price_lines_json};
                if (priceLines && priceLines.length > 0) {{
                    priceLines.forEach(pl => {{
                        candlestickSeries.createPriceLine({{
                            price: pl.price,
                            color: pl.color,
                            lineWidth: 1,
                            lineStyle: pl.lineStyle || 2, // Dashed
                            axisLabelVisible: true,
                            title: pl.title,
                        }});
                    }});
                }}

                // --- 2. RSI Sub-Pane (Bottom 20%) ---
                const rsiJson = {json.dumps(rsi_data if rsi_data else 'null')};
                if (rsiJson && rsiJson !== 'null') {{
                    const rsiData = typeof rsiJson === 'string' ? JSON.parse(rsiJson) : rsiJson;
                    if (rsiData && rsiData.length > 0) {{
                        // Separate Pane for RSI - Using a new PriceScaleId
                        const rsiSeries = chart.addLineSeries({{
                            color: '#fbbf24',
                            lineWidth: 2,
                            priceScaleId: 'rsi', // Separate Scale ID
                            title: 'RSI',
                        }});
                        
                        // Configure RSI Scale to sit at bottom
                        chart.priceScale('rsi').applyOptions({{
                            autoScale: false,
                            scaleMargins: {{
                                top: 0.8, // Top 80% used by main chart
                                bottom: 0,
                            }},
                        }});
                        
                        rsiSeries.setData(rsiData);
                        
                        // Reference Lines (70/30) - Manually via createPriceLine on the series
                        rsiSeries.createPriceLine({{
                            price: 70, color: '#ef5350', lineWidth: 1, lineStyle: 2, axisLabelVisible: false
                        }});
                        rsiSeries.createPriceLine({{
                            price: 30, color: '#26a69a', lineWidth: 1, lineStyle: 2, axisLabelVisible: false
                        }});
                    }}
                }}
                
                // Fit Content
                chart.timeScale().fitContent();
                
                // Auto Resize
                window.addEventListener('resize', () => {{
                    chart.applyOptions({{ width: container.clientWidth }});
                }});

            }} catch (e) {{
                document.getElementById('debug').innerHTML = "Chart Error: " + e.message;
                console.error(e);
            }}
        </script>
    </body>
    </html>
    """
    
    return html_template
