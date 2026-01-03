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
        ma_list = [('SMA13', '#2962FF'), ('SMA26', '#FF6D00'), ('SMA52', '#00C853')] # Blue, Orange, Green
    else:
        ma_list = [('SMA5', '#FFFF00'), ('SMA25', '#FF00FF'), ('SMA75', '#00E676')] # Yellow, Magenta, Green

    for ma_col, color in ma_list:
        if ma_col in df.columns:
            # Pass color directly to create_line
            # Use 'time' from chart_df (renamed) and value from df (original)
            # Ensure indices align or use chart_df if ma_col was copied there (it wasn't copied above, so use df)
            # Safe way: create a mini DF with aligned time and value
            line_data = pd.DataFrame({'time': chart_df['time'], 'value': df[ma_col]})
            # Filter out NaNs to prevent errors in lightweight-charts if any
            line_data = line_data.dropna()
            
            if not line_data.empty:
                try:
                    line = chart.create_line(name=ma_col, color=color)
                    line.set(line_data)
                except Exception as e:
                    print(f"Error setting line {ma_col}: {e}")

    # Bollinger Bands
    if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
        try:
            # Use slightly transparent colors if supported, or just light solid colors
            upper = chart.create_line(name='BB Upper', color='rgba(0, 212, 255, 0.5)')
            upper.set(pd.DataFrame({'time': chart_df['time'], 'value': df['BB_Upper']}))
            lower = chart.create_line(name='BB Lower', color='rgba(0, 212, 255, 0.5)')
            lower.set(pd.DataFrame({'time': chart_df['time'], 'value': df['BB_Lower']}))
        except Exception as e:
            print(f"Error adding BB to chart: {e}")

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
