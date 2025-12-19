import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_main_chart(df, ticker_name, strategic_data=None):
    """
    Create a Plotly chart with Candlestick, MA, and RSI.
    Adds strategic lines if data is provided.
    """
    if df is None:
        return None
        
    # Create subplots: Row 1 for Price, Row 2 for RSI
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.7, 0.3],
                        subplot_titles=("", ""))  # Remove titles

    # Candlestick
    fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name='株価', increasing_line_color='#00ff00', 
                decreasing_line_color='#ff0000'), row=1, col=1)

    # Moving Averages
    ma_names = {'SMA5': '5日線', 'SMA25': '25日線', 'SMA75': '75日線'}
    colors = {'SMA5': '#00ff00', 'SMA25': '#ff00ff', 'SMA75': '#ffff00'}
    for ma, color in colors.items():
        if ma in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[ma], 
                                   mode='lines', name=ma_names[ma],
                                   line=dict(color=color, width=1)), row=1, col=1)
                                   
    # Strategic Lines with Price Annotations
    if strategic_data:
        target = strategic_data.get('target_price')
        stop = strategic_data.get('stop_loss')
        
        if target and not pd.isna(target):
            fig.add_hline(y=target, line_dash="dash", line_color="#00ff00", 
                          line_width=2, row=1, col=1)
            # Add annotation with price
            fig.add_annotation(
                x=df.index[-1], y=target,
                text=f"利確目標: ¥{target:,.0f}",
                showarrow=True, arrowhead=2,
                ax=40, ay=-30,
                bgcolor="#00ff00", font=dict(color="#000000", size=11),
                row=1, col=1
            )
        if stop and not pd.isna(stop):
            fig.add_hline(y=stop, line_dash="dash", line_color="#ff0000", 
                          line_width=2, row=1, col=1)
            # Add annotation with price
            fig.add_annotation(
                x=df.index[-1], y=stop,
                text=f"損切: ¥{stop:,.0f}",
                showarrow=True, arrowhead=2,
                ax=40, ay=30,
                bgcolor="#ff0000", font=dict(color="#ffffff", size=11),
                row=1, col=1
            )
        
        # Add Entry Point Indicator
        entry_price = strategic_data.get('entry_price')
        if entry_price and not pd.isna(entry_price):
            # Entry point horizontal line
            fig.add_hline(y=entry_price, line_dash="dot", line_color="#00ffff", 
                          line_width=2, row=1, col=1)
            # Entry point annotation with icon
            fig.add_annotation(
                x=df.index[-1], y=entry_price,
                text=f"🎯 エントリー: ¥{entry_price:,.0f}",
                showarrow=True, arrowhead=2,
                ax=-40, ay=0,
                bgcolor="#00ffff", font=dict(color="#000000", size=12, family="Arial Black"),
                row=1, col=1
            )

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], 
                           mode='lines', name='RSI',
                           line=dict(color='#00d4ff', width=1.5)), row=2, col=1)
    
    # RSI Zones
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    # Layout
    fig.update_layout(
        title=dict(text=f"{ticker_name}", font=dict(size=18, color='#ffffff')),
        xaxis_rangeslider_visible=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(17, 34, 64, 0.8)'
        )
    )
    
    # Update axes with Japanese labels
    fig.update_xaxes(title_text="日付", gridcolor='#233554', row=2, col=1)
    fig.update_yaxes(title_text="株価 (円)", gridcolor='#233554', row=1, col=1)
    fig.update_yaxes(title_text="RSI", gridcolor='#233554', row=2, col=1)
    
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
