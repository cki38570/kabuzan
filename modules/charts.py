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

    # Prepare data for lightweight-charts
    # Columns expected: time, open, high, low, close, volume (lowercase)
    chart_df = df.copy()
    if 'Date' in chart_df.columns:
        chart_df = chart_df.rename(columns={'Date': 'time'})
    elif chart_df.index.name == 'Date' or isinstance(chart_df.index, pd.DatetimeIndex):
        chart_df['time'] = chart_df.index
        
    # CRITICAL: Ensure 'time' is string YYYY-MM-DD for lightweight-charts stability
    chart_df['time'] = pd.to_datetime(chart_df['time']).dt.strftime('%Y-%m-%d')
    
    # Also ensure the original df used for technical indicators has string time index for mapping
    df_str = df.copy()
    if isinstance(df_str.index, pd.DatetimeIndex):
        df_str.index = df_str.index.strftime('%Y-%m-%d')
        
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
        ma_col = next((c for c in cols if c in df_str.columns), None)
        if ma_col:
            line_data = pd.DataFrame({'time': chart_df['time'], 'value': df_str[ma_col].values})
            line_data = line_data.dropna()
            
            if not line_data.empty:
                try:
                    line = chart.create_line(name=ma_col, color=color)
                    line.set(line_data)
                except Exception as e:
                    print(f"Error setting line {ma_col}: {e}")

    # Bollinger Bands (Support multiple naming variants)
    bb_upper_col = next((c for c in ['BB_Upper', 'BBU_20_2.0', 'BBU_20_2'] if c in df.columns), None)
    bb_lower_col = next((c for c in ['BB_Lower', 'BBL_20_2.0', 'BBL_20_2'] if c in df.columns), None)

    if bb_upper_col and bb_lower_col:
        try:
            upper = chart.create_line(name='BB Upper', color='rgba(0, 212, 255, 0.4)')
            upper.set(pd.DataFrame({'time': chart_df['time'], 'value': df[bb_upper_col]}))
            lower = chart.create_line(name='BB Lower', color='rgba(0, 212, 255, 0.4)')
            lower.set(pd.DataFrame({'time': chart_df['time'], 'value': df[bb_lower_col]}))
        except Exception as e:
            print(f"Error adding BB to chart: {e}")

    # RSI (New Pane)
    rsi_col = next((c for c in ['RSI', 'RSI_14'] if c in df.columns), None)
    if rsi_col:
        try:
            rsi_chart = chart.create_line(name='RSI', color='#FFEB3B', price_line=True, price_label=True)
            rsi_data = pd.DataFrame({'time': chart_df['time'], 'value': df[rsi_col]})
            rsi_chart.set(rsi_data.dropna())
            # Add horizons for RSI
            rsi_chart.horizontal_line(70, color='#ff4b4b', style='dashed')
            rsi_chart.horizontal_line(30, color='#00ffbd', style='dashed')
        except Exception as e:
            print(f"Error adding RSI to chart: {e}")

    # MACD (New Pane)
    macd_col = next((c for c in ['MACD'] if c in df.columns), None)
    macd_sig_col = next((c for c in ['MACD_Signal'] if c in df.columns), None)
    macd_hist_col = next((c for c in ['MACD_Hist'] if c in df.columns), None)

    if macd_col and macd_sig_col:
        try:
            # Create MACD and Signal lines
            m_line = chart.create_line(name='MACD', color='#2196F3')
            m_line.set(pd.DataFrame({'time': chart_df['time'], 'value': df[macd_col]}).dropna())
            s_line = chart.create_line(name='Signal', color='#FF9800')
            s_line.set(pd.DataFrame({'time': chart_df['time'], 'value': df[macd_sig_col]}).dropna())
            
            # Histogram
            if macd_hist_col:
                hist = chart.create_histogram(name='Histogram', color='rgba(255, 255, 255, 0.3)')
                hist.set(pd.DataFrame({'time': chart_df['time'], 'value': df[macd_hist_col]}).dropna())
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
