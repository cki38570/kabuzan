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
    bb_upper_col = next((c for c in ['BBU_20_2.0', 'BB_Upper', 'BBU_20'] if c in chart_df.columns), None)
    bb_lower_col = next((c for c in ['BBL_20_2.0', 'BB_Lower', 'BBL_20'] if c in chart_df.columns), None)
    bb_mid_col = next((c for c in ['BBM_20_2.0', 'BB_Mid', 'BBM_20', 'SMA_20'] if c in chart_df.columns), None)
    
    if bb_upper_col and bb_lower_col:
        bb_data['upper'] = clean_data(chart_df[['time', bb_upper_col]].rename(columns={bb_upper_col: 'value'}))
        bb_data['lower'] = clean_data(chart_df[['time', bb_lower_col]].rename(columns={bb_lower_col: 'value'}))
        if bb_mid_col:
             bb_data['mid'] = clean_data(chart_df[['time', bb_mid_col]].rename(columns={bb_mid_col: 'value'}))

    # Parabolic SAR
    psar_data = None
    psar_col = next((c for c in chart_df.columns if c.startswith('PSAR') or c == 'SAR'), None)
    if psar_col:
        psar_data = clean_data(chart_df[['time', psar_col]].rename(columns={psar_col: 'value'}))

    # Markers (AI Targets)
    markers = []
    if strategic_data:
        # Last Date
        last_time = chart_df['time'].iloc[-1]
        
        if 'entry_price' in strategic_data:
            markers.append({
                'time': last_time, 'position': 'inBar', 'color': '#00BFFF', 'shape': 'arrowUp', 'text': 'Entry'
            })
        if 'stop_loss' in strategic_data:
             markers.append({
                'time': last_time, 'position': 'belowBar', 'color': '#FF0000', 'shape': 'circle', 'text': 'SL'
            })
            
    markers_json = json.dumps(markers)

    # --- 2. HTML/JS Construction ---
    # Using Lightweight Charts v5.1.0
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/lightweight-charts@5.1.0/dist/lightweight-charts.standalone.production.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background-color: #0e1117; overflow: hidden; }}
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
                const {{ createChart, CandlestickSeries, HistogramSeries, LineSeries, LineStyle }} = LightweightCharts;
                
                const chartOptions = {{
                    layout: {{
                        textColor: '#d1d4dc',
                        backgroundColor: '#0e1117',
                    }},
                    grid: {{
                        vertLines: {{ color: '#2B2B43' }},
                        horzLines: {{ color: '#2B2B43' }},
                    }},
                    crosshair: {{
                        mode: LightweightCharts.CrosshairMode.Normal,
                    }},
                    rightPriceScale: {{
                        borderColor: '#2B2B43',
                    }},
                    timeScale: {{
                        borderColor: '#2B2B43',
                        timeVisible: true,
                    }},
                }};
                
                const container = document.getElementById('chart');
                const chart = createChart(container, chartOptions);
                
                // 1. Candlestick Series
                const candleSeries = chart.addSeries(CandlestickSeries, {{
                    upColor: '#00ffbd', downColor: '#ff4b4b', borderVisible: false, wickUpColor: '#00ffbd', wickDownColor: '#ff4b4b'
                }});
                const cData = {candle_data_json};
                if (!cData || cData.length === 0) throw new Error("Candle data empty");
                candleSeries.setData(cData);
                
                // 2. Volume Series
                const volumeSeries = chart.addSeries(HistogramSeries, {{
                    color: '#26a69a',
                    priceFormat: {{ type: 'volume' }},
                    priceScaleId: '', // Set as overlay
                    scaleMargins: {{ top: 0.8, bottom: 0 }},
                }});
                volumeSeries.setData({volume_data_json});

                // 3. SMA Lines
                const smaData = {json.dumps(sma_data)};
                for (const [name, info] of Object.entries(smaData)) {{
                    const line = chart.addSeries(LineSeries, {{
                        color: info.color, lineWidth: 2, title: name
                    }});
                    line.setData(JSON.parse(info.data));
                }}
                
                // 4. Bollinger Bands (3 Lines)
                const bbData = {json.dumps(bb_data)};
                if (bbData.upper && bbData.lower) {{
                    // Upper
                    const upper = chart.addSeries(LineSeries, {{ color: 'rgba(255, 255, 255, 0.5)', lineWidth: 1, title: 'BB Upper' }});
                    upper.setData(JSON.parse(bbData.upper));
                    
                    // Lower
                    const lower = chart.addSeries(LineSeries, {{ color: 'rgba(255, 255, 255, 0.5)', lineWidth: 1, title: 'BB Lower' }});
                    lower.setData(JSON.parse(bbData.lower));
                    
                    // Middle
                    if (bbData.mid) {{
                        const mid = chart.addSeries(LineSeries, {{ 
                            color: 'rgba(255, 165, 0, 0.8)', // Orangeish
                            lineWidth: 1, 
                            title: 'BB Mid' 
                        }});
                        mid.setData(JSON.parse(bbData.mid));
                    }}
                }}

                // 5. Parabolic SAR (Dotted Line)
                const psarJson = {json.dumps(psar_data if psar_data else 'null')};
                if (psarJson) {{
                    const rawData = JSON.parse(psarJson);
                    const psarSeries = chart.addSeries(LineSeries, {{
                        color: '#BA68C8', 
                        lineWidth: 2,
                        lineStyle: 1, // Dotted (LineStyle.Dotted is usually 1 or 2)
                        title: 'PSAR',
                        crosshairMarkerVisible: false
                    }});
                    psarSeries.setData(rawData);
                }}

                // 6. Markers (AI)
                const aiMarkers = {markers_json};
                if (aiMarkers.length > 0) {{
                   // Safe check for setMarkers
                   if (typeof candleSeries.setMarkers === 'function') {{
                       candleSeries.setMarkers(aiMarkers);
                   }} else {{
                       console.warn("setMarkers is not supported on this series type");
                   }}
                }}

                // Fit content
                chart.timeScale().fitContent();

                // Resize Observer
                new ResizeObserver(entries => {{
                    if (entries.length === 0 || entries[0].target !== container) {{ return; }}
                    const newRect = entries[0].contentRect;
                    chart.applyOptions({{ height: newRect.height, width: newRect.width }});
                }}).observe(container);

            }} catch (e) {{
                document.getElementById('debug').innerHTML = "Chart Error: " + e.message + "<br><pre>" + e.stack + "</pre>";
                console.error(e);
            }}
        </script>
    </body>
    </html>
    """
    
    return html_template
