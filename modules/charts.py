import pandas as pd
from lightweight_charts.widgets import StreamlitChart

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
    Create a TradingView-style chart using lightweight-charts.
    """
    if df is None or df.empty:
        return None

    # Prepare main chart data
    chart_df = df.copy()
    if 'Date' in chart_df.columns:
        chart_df = chart_df.rename(columns={'Date': 'time'})
    elif chart_df.index.name == 'Date' or isinstance(chart_df.index, pd.DatetimeIndex):
        chart_df['time'] = chart_df.index
        
    # lightweight-charts expects 'time' column to be 'YYYY-MM-DD' strings for daily data
    chart_df['time'] = pd.to_datetime(chart_df['time']).dt.strftime('%Y-%m-%d')
    
    chart_df = chart_df.rename(columns={
        'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
    })
    
    # Initialize StreamlitChart
    chart = StreamlitChart(width=900, height=600)
    
    # Appearance Settings
    chart.layout(background_color='#0a192f', text_color='#ccd6f6', font_size=12)
    chart.candle_style(up_color='#00ffbd', down_color='#ff4b4b', border_up_color='#00ffbd', border_down_color='#ff4b4b', wick_up_color='#00ffbd', wick_down_color='#ff4b4b')
    # chart.grid() often only accepts bools in newer versions, colors are set in layout or via specific options dictionaries.
    # To fix 'AbstractChart.grid() got an unexpected keyword argument 'vert_color''
    chart.grid(vert_enabled=True, horz_enabled=True)

    # Set Main Data
    chart.set(chart_df)

    # Moving Averages (Synced with Plotly colors)
    if interval == "1wk":
        # Weekly: Support both SMA_X and SMA X
        ma_list = [
            (['SMA_13', 'SMA13'], '#2962FF'), 
            (['SMA_26', 'SMA26'], '#FF6D00'), 
            (['SMA_52', 'SMA52'], '#00C853')
        ]
    else:
        # Daily: Support both SMA_X and SMA X
        ma_list = [
            (['SMA_5', 'SMA5'], '#FFFF00'), 
            (['SMA_25', 'SMA25'], '#FF00FF'), 
            (['SMA_75', 'SMA75'], '#00E676')
        ]

    for cols, color in ma_list:
        ma_col = next((c for c in cols if c in df.columns), None)
        if ma_col:
            try:
                # IMPORTANT: Use .values to ensure alignment with chart_df['time']
                # since chart_df and df might have different index types/values now
                line_data = pd.DataFrame({
                    'time': chart_df['time'],
                    'value': df[ma_col].values
                }).dropna()
                if not line_data.empty:
                    line = chart.create_line(name=ma_col, color=color)
                    line.set(line_data)
            except Exception as e:
                print(f"Error setting line {ma_col}: {e}")

    # Bollinger Bands (Support multiple naming variants)
    # Priority: pandas-ta naming, then standard naming
    bb_upper_col = next((c for c in ['BBU_20_2.0', 'BB_Upper', 'BBU_20'] if c in df.columns), None)
    bb_lower_col = next((c for c in ['BBL_20_2.0', 'BB_Lower', 'BBL_20'] if c in df.columns), None)

    if bb_upper_col and bb_lower_col:
        try:
            # Upper Line
            upper_data = pd.DataFrame({
                'time': chart_df['time'],
                'value': df[bb_upper_col].values
            }).dropna()
            if not upper_data.empty:
                upper_line = chart.create_line(name='BB Upper', color='rgba(255, 255, 255, 0.3)', width=1)
                upper_line.set(upper_data)
            
            # Lower Line
            lower_data = pd.DataFrame({
                'time': chart_df['time'],
                'value': df[bb_lower_col].values
            }).dropna()
            if not lower_data.empty:
                lower_line = chart.create_line(name='BB Lower', color='rgba(255, 255, 255, 0.3)', width=1)
                lower_line.set(lower_data)
        except Exception as e:
            print(f"Error adding BB to chart: {e}")

    # RSI (New Pane)
    rsi_col = next((c for c in ['RSI_14', 'RSI'] if c in df.columns), None)
    if rsi_col:
        try:
            rsi_data = chart_df[['time', rsi_col]].rename(columns={rsi_col: 'value'}).dropna()
            if not rsi_data.empty:
                rsi_chart = chart.create_line(name='RSI', color='#FFEB3B', price_line=True, price_label=True)
                rsi_chart.set(rsi_data)
                # Add horizons for RSI
                rsi_chart.horizontal_line(70, color='#ff4b4b', style='dashed')
                rsi_chart.horizontal_line(30, color='#00ffbd', style='dashed')
        except Exception as e:
            print(f"Error adding RSI to chart: {e}")

    # MACD (New Pane)
    macd_col = next((c for c in ['MACD_12_26_9', 'MACD'] if c in chart_df.columns), None)
    macd_sig_col = next((c for c in ['MACDs_12_26_9', 'MACD_Signal'] if c in chart_df.columns), None)
    macd_hist_col = next((c for c in ['MACDh_12_26_9', 'MACD_Hist'] if c in chart_df.columns), None)

    if macd_col and macd_sig_col:
        try:
            m_data = chart_df[['time', macd_col]].rename(columns={macd_col: 'value'}).dropna()
            s_data = chart_df[['time', macd_sig_col]].rename(columns={macd_sig_col: 'value'}).dropna()
            
            if not m_data.empty and not s_data.empty:
                m_line = chart.create_line(name='MACD', color='#2196F3')
                m_line.set(m_data)
                s_line = chart.create_line(name='Signal', color='#FF9800')
                s_line.set(s_data)
            
            # Histogram
            if macd_hist_col:
                h_data = chart_df[['time', macd_hist_col]].rename(columns={macd_hist_col: 'value'}).dropna()
                if not h_data.empty:
                    hist = chart.create_histogram(name='Histogram', color='rgba(255, 255, 255, 0.3)')
                    hist.set(h_data)
        except Exception as e:
            print(f"Error adding MACD to chart: {e}")

    # Strategic Lines (AI Target/Stop)
    if strategic_data:
        target = strategic_data.get('target_price')
        stop = strategic_data.get('stop_loss')
        entry = strategic_data.get('entry_price')
        
        if target and not pd.isna(target):
            chart.horizontal_line(target, color='#00ffbd', style='dashed', text='利確目標')
        if stop and not pd.isna(stop):
            chart.horizontal_line(stop, color='#ff4b4b', style='dashed', text='損切')
        if entry and not pd.isna(entry):
            chart.horizontal_line(entry, color='#00d4ff', style='dotted', text='ENTRY')

    return chart
