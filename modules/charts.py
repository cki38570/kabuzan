import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from lightweight_charts.widgets import StreamlitChart

def create_main_chart(df, ticker_name, strategic_data=None, interval="1d"):
    """
    Create a Plotly chart with Candlestick, MA, and RSI.
    Adds strategic lines if data is provided.
    """
    if df is None or df.empty:
        return None
        
    # Create subplots: Row 1 for Price, Row 2 for RSI
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.04, row_heights=[0.75, 0.25],
                        subplot_titles=("", ""))

    # Candlestick
    fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name='株価', increasing_line_color='#00ffbd', 
                decreasing_line_color='#ff4b4b'), row=1, col=1)

    # Bollinger Bands (Fill)
    if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
        # Upper Band (Transparent line)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], 
                               line=dict(color='rgba(0, 212, 255, 0.1)', width=0),
                               mode='lines', name='BB Upper', showlegend=False), row=1, col=1)
        # Lower Band (Fill to Upper)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], 
                               line=dict(color='rgba(0, 212, 255, 0.1)', width=0),
                               mode='lines', fill='tonexty', fillcolor='rgba(0, 212, 255, 0.1)',
                               name='Bollinger Band'), row=1, col=1)

    # Moving Averages based on interval (Enhanced Colors)
    if interval == "1wk":
        ma_configs = {'SMA13': ('13週線', '#2962FF'), 'SMA26': ('26週線', '#FF6D00'), 'SMA52': ('52週線', '#00C853')} # Blue, Orange, Green
    else:
        ma_configs = {'SMA5': ('5日線', '#FFFF00'), 'SMA25': ('25日線', '#FF00FF'), 'SMA75': ('75日線', '#00E676')} # Yellow, Magenta, Green
    
    # Plot MAs on top of BB
    for ma_col, (name, color) in ma_configs.items():
        if ma_col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[ma_col], 
                                   mode='lines', name=name,
                                   line=dict(color=color, width=1.5)), row=1, col=1)
                                   
    # Strategic Lines with Price Annotations (Enhanced Visibility)
    if strategic_data:
        target = strategic_data.get('target_price')
        stop = strategic_data.get('stop_loss')
        
        if target and not pd.isna(target):
            fig.add_hline(y=target, line_dash="dash", line_color="#00E676", 
                          line_width=2, row=1, col=1)
            fig.add_annotation(
                x=df.index[-1], y=target,
                text=f"🚀 利確目標: ¥{target:,.0f}",
                showarrow=True, arrowhead=2, ax=60, ay=-20,
                bgcolor="rgba(0, 230, 118, 0.8)", font=dict(color="#000000", size=11, family="Roboto"),
                bordercolor="#00E676", borderwidth=1,
                row=1, col=1
            )
        if stop and not pd.isna(stop):
            fig.add_hline(y=stop, line_dash="dash", line_color="#FF1744", 
                          line_width=2, row=1, col=1)
            fig.add_annotation(
                x=df.index[-1], y=stop,
                text=f"⛔ 損切: ¥{stop:,.0f}",
                showarrow=True, arrowhead=2, ax=60, ay=20,
                bgcolor="rgba(255, 23, 68, 0.8)", font=dict(color="#ffffff", size=11, family="Roboto"),
                bordercolor="#FF1744", borderwidth=1,
                row=1, col=1
            )
        
        entry_price = strategic_data.get('entry_price')
        if entry_price and not pd.isna(entry_price):
            fig.add_hline(y=entry_price, line_dash="dot", line_color="#2979FF", 
                          line_width=2, row=1, col=1)
            fig.add_annotation(
                x=df.index[-1], y=entry_price,
                text=f"🔵 Entry: ¥{entry_price:,.0f}",
                showarrow=True, arrowhead=2, ax=-60, ay=0,
                bgcolor="rgba(41, 121, 255, 0.8)", font=dict(color="#ffffff", size=11),
                row=1, col=1
            )
    
    # RSI (Enhanced)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], 
                           mode='lines', name='RSI',
                           line=dict(color='#29B6F6', width=2)), row=2, col=1)
    
    # RSI Zones
    fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, line_width=0, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, line_width=0, row=2, col=1)
    
    fig.add_hline(y=70, line_dash="dot", line_color="#FF5252", opacity=0.6, row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="#69F0AE", opacity=0.6, row=2, col=1)

    # Layout & Aesthetics
    fig.update_layout(
        title=dict(text=f"{ticker_name} - {'週足' if interval == '1wk' else '日足'}", 
                   font=dict(size=20, color='#ffffff')),
        xaxis_rangeslider_visible=False,
        plot_bgcolor='rgba(10, 25, 47, 0.4)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ccd6f6'),
        height=700,
        margin=dict(l=50, r=50, t=80, b=50),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, bgcolor='rgba(10, 25, 47, 0.7)'
        )
    )
    
    # Range Selector
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all", label="All")
            ]),
            bgcolor='rgba(17, 34, 64, 0.9)',
            activecolor='#64ffda',
            font=dict(color='#ccd6f6')
        ),
        gridcolor='#233554',
        linecolor='#233554',
        row=1, col=1
    )
    
    fig.update_xaxes(title_text="日付", gridcolor='#233554', linecolor='#233554', row=2, col=1)
    fig.update_yaxes(title_text="価格 (円)", gridcolor='#233554', linecolor='#233554', row=1, col=1)
    fig.update_yaxes(title_text="RSI", gridcolor='#233554', linecolor='#233554', range=[0, 100], row=2, col=1)
    
    return fig

def create_credit_chart(credit_df):
    """
    Create a chart for credit balance trends.
    """
    if credit_df is None or credit_df.empty:
        return None
        
    # Create figure
    fig = go.Figure()
    
    # Try to find Buy/Sell columns
    sell_col = next((c for c in credit_df.columns if '売残' in c), None)
    buy_col = next((c for c in credit_df.columns if '買残' in c), None)
    date_col = next((c for c in credit_df.columns if '日' in c or 'Date' in c), None)
    
    x_axis = credit_df[date_col] if date_col else credit_df.index
    
    if sell_col:
        fig.add_trace(go.Bar(x=x_axis, y=credit_df[sell_col], name='売残', marker_color='red'))
    if buy_col:
        fig.add_trace(go.Bar(x=x_axis, y=credit_df[buy_col], name='買残', marker_color='green'))

    fig.update_layout(
        title="信用残推移",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10, 25, 47, 0.5)',
        font=dict(color='white'),
        barmode='group',
        height=300,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    return fig

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
