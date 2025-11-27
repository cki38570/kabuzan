import pandas as pd
import numpy as np

def calculate_advanced_metrics(df, current_price):
    """
    Calculate comprehensive market metrics for detailed analysis.
    Returns dict with all calculated metrics.
    """
    if df is None or len(df) < 20:
        return None
    
    metrics = {}
    
    # === Price Action Metrics ===
    
    # 52-week High/Low
    year_data = df.tail(252) if len(df) >= 252 else df
    metrics['52w_high'] = year_data['High'].max()
    metrics['52w_low'] = year_data['Low'].min()
    metrics['52w_high_pct'] = ((current_price - metrics['52w_high']) / metrics['52w_high']) * 100
    metrics['52w_low_pct'] = ((current_price - metrics['52w_low']) / metrics['52w_low']) * 100
    
    # Price Position (where current price sits in 52w range)
    price_range = metrics['52w_high'] - metrics['52w_low']
    if price_range > 0:
        metrics['price_position'] = ((current_price - metrics['52w_low']) / price_range) * 100
    else:
        metrics['price_position'] = 50
    
    # === Volatility Metrics ===
    
    # Historical Volatility (annualized)
    returns = df['Close'].pct_change().dropna()
    metrics['volatility_daily'] = returns.std()
    metrics['volatility_annual'] = metrics['volatility_daily'] * np.sqrt(252) * 100
    
    # Average True Range (ATR) - 14 period
    if 'ATR' in df.columns:
        metrics['atr'] = df['ATR'].iloc[-1]
        metrics['atr_pct'] = (metrics['atr'] / current_price) * 100
    
    # === Volume Metrics ===
    
    if 'Volume' in df.columns:
        recent_volume = df['Volume'].tail(20)
        metrics['avg_volume_20d'] = recent_volume.mean()
        metrics['current_volume'] = df['Volume'].iloc[-1]
        metrics['volume_ratio'] = metrics['current_volume'] / metrics['avg_volume_20d'] if metrics['avg_volume_20d'] > 0 else 1
        
        # Volume Trend (increasing or decreasing)
        volume_ma5 = df['Volume'].tail(10).head(5).mean()
        volume_ma5_recent = df['Volume'].tail(5).mean()
        metrics['volume_trend'] = 'increasing' if volume_ma5_recent > volume_ma5 else 'decreasing'
    
    # === Momentum Metrics ===
    
    # Rate of Change (ROC) - various periods
    metrics['roc_5d'] = ((df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6]) * 100 if len(df) >= 6 else 0
    metrics['roc_10d'] = ((df['Close'].iloc[-1] - df['Close'].iloc[-11]) / df['Close'].iloc[-11]) * 100 if len(df) >= 11 else 0
    metrics['roc_20d'] = ((df['Close'].iloc[-1] - df['Close'].iloc[-21]) / df['Close'].iloc[-21]) * 100 if len(df) >= 21 else 0
    
    # === Moving Average Analysis ===
    
    if 'SMA5' in df.columns and 'SMA25' in df.columns and 'SMA75' in df.columns:
        metrics['ma5'] = df['SMA5'].iloc[-1]
        metrics['ma25'] = df['SMA25'].iloc[-1]
        metrics['ma75'] = df['SMA75'].iloc[-1]
        
        # Distance from MAs
        metrics['dist_ma5'] = ((current_price - metrics['ma5']) / metrics['ma5']) * 100
        metrics['dist_ma25'] = ((current_price - metrics['ma25']) / metrics['ma25']) * 100
        metrics['dist_ma75'] = ((current_price - metrics['ma75']) / metrics['ma75']) * 100
        
        # MA Alignment (Perfect Order check)
        metrics['ma_alignment'] = 'bullish' if metrics['ma5'] > metrics['ma25'] > metrics['ma75'] else \
                                  'bearish' if metrics['ma5'] < metrics['ma25'] < metrics['ma75'] else 'neutral'
    
    # === RSI Analysis ===
    
    if 'RSI' in df.columns:
        metrics['rsi'] = df['RSI'].iloc[-1]
        rsi_history = df['RSI'].tail(14)
        metrics['rsi_avg'] = rsi_history.mean()
        metrics['rsi_trend'] = 'rising' if df['RSI'].iloc[-1] > df['RSI'].iloc[-5] else 'falling'
    
    # === MACD Analysis ===
    
    if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
        metrics['macd'] = df['MACD'].iloc[-1]
        metrics['macd_signal'] = df['MACD_Signal'].iloc[-1]
        metrics['macd_histogram'] = metrics['macd'] - metrics['macd_signal']
        
        # MACD Crossover detection
        prev_macd = df['MACD'].iloc[-2]
        prev_signal = df['MACD_Signal'].iloc[-2]
        
        if metrics['macd'] > metrics['macd_signal'] and prev_macd <= prev_signal:
            metrics['macd_cross'] = 'golden'
        elif metrics['macd'] < metrics['macd_signal'] and prev_macd >= prev_signal:
            metrics['macd_cross'] = 'dead'
        else:
            metrics['macd_cross'] = 'none'
    
    # === Bollinger Bands Analysis ===
    
    if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
        metrics['bb_upper'] = df['BB_Upper'].iloc[-1]
        metrics['bb_lower'] = df['BB_Lower'].iloc[-1]
        metrics['bb_middle'] = df['SMA20'].iloc[-1] if 'SMA20' in df.columns else (metrics['bb_upper'] + metrics['bb_lower']) / 2
        
        # BB Width (volatility indicator)
        metrics['bb_width'] = ((metrics['bb_upper'] - metrics['bb_lower']) / metrics['bb_middle']) * 100
        
        # Price position in BB
        bb_range = metrics['bb_upper'] - metrics['bb_lower']
        if bb_range > 0:
            metrics['bb_position'] = ((current_price - metrics['bb_lower']) / bb_range) * 100
        else:
            metrics['bb_position'] = 50
    
    # === Trend Strength ===
    
    # ADX-like calculation (simplified)
    if len(df) >= 14:
        high_diff = df['High'].diff()
        low_diff = -df['Low'].diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        tr = df['High'] - df['Low']
        atr_14 = tr.rolling(14).mean()
        
        plus_di = 100 * (plus_dm.rolling(14).mean() / atr_14)
        minus_di = 100 * (minus_dm.rolling(14).mean() / atr_14)
        
        metrics['trend_strength'] = abs(plus_di.iloc[-1] - minus_di.iloc[-1])
    
    return metrics

def format_metrics_display(metrics):
    """
    Format metrics for beautiful display in Streamlit.
    Returns markdown string.
    """
    if not metrics:
        return "データが不足しています。"
    
    display = f"""
### 📊 詳細市場データ

#### 価格レンジ分析
- **52週高値**: ¥{metrics['52w_high']:,.0f} ({metrics['52w_high_pct']:+.1f}%)
- **52週安値**: ¥{metrics['52w_low']:,.0f} ({metrics['52w_low_pct']:+.1f}%)
- **価格位置**: {metrics['price_position']:.1f}% (52週レンジ内)

#### ボラティリティ
- **年率ボラティリティ**: {metrics['volatility_annual']:.1f}%
- **ATR**: ¥{metrics.get('atr', 0):,.0f} ({metrics.get('atr_pct', 0):.2f}%)
"""
    
    if 'avg_volume_20d' in metrics:
        display += f"""
#### 出来高分析
- **平均出来高(20日)**: {metrics['avg_volume_20d']:,.0f}
- **当日出来高**: {metrics['current_volume']:,.0f}
- **出来高比率**: {metrics['volume_ratio']:.2f}x
- **出来高トレンド**: {metrics['volume_trend']}
"""
    
    display += f"""
#### モメンタム
- **5日ROC**: {metrics['roc_5d']:+.2f}%
- **10日ROC**: {metrics['roc_10d']:+.2f}%
- **20日ROC**: {metrics['roc_20d']:+.2f}%

#### テクニカル指標
- **RSI**: {metrics.get('rsi', 0):.1f} ({metrics.get('rsi_trend', 'N/A')})
- **MACD**: {metrics.get('macd', 0):.2f} (シグナル: {metrics.get('macd_signal', 0):.2f})
- **BB幅**: {metrics.get('bb_width', 0):.2f}%
- **トレンド強度**: {metrics.get('trend_strength', 0):.1f}
"""
    
    return display.strip()
