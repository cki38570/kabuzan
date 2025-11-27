import pandas as pd
import numpy as np

def detect_support_resistance(df, window=20):
    """
    Detect support and resistance levels using pivot points.
    Returns dict with support and resistance levels.
    """
    if df is None or len(df) < window:
        return {'support': [], 'resistance': []}
    
    recent = df.tail(window * 2)
    
    # Find local maxima (resistance)
    resistance_levels = []
    for i in range(window, len(recent) - window):
        if recent['High'].iloc[i] == recent['High'].iloc[i-window:i+window].max():
            resistance_levels.append(recent['High'].iloc[i])
    
    # Find local minima (support)
    support_levels = []
    for i in range(window, len(recent) - window):
        if recent['Low'].iloc[i] == recent['Low'].iloc[i-window:i+window].min():
            support_levels.append(recent['Low'].iloc[i])
    
    # Remove duplicates and sort
    support_levels = sorted(list(set([round(s, 0) for s in support_levels])))
    resistance_levels = sorted(list(set([round(r, 0) for r in resistance_levels])))
    
    return {
        'support': support_levels[-3:] if len(support_levels) > 0 else [],  # Top 3
        'resistance': resistance_levels[:3] if len(resistance_levels) > 0 else []  # Top 3
    }

def detect_candlestick_patterns(df):
    """
    Detect common candlestick patterns.
    Returns list of detected patterns.
    """
    if df is None or len(df) < 3:
        return []
    
    patterns = []
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Doji (Open ≈ Close)
    body = abs(last['Close'] - last['Open'])
    range_size = last['High'] - last['Low']
    
    if range_size > 0 and body / range_size < 0.1:
        patterns.append({
            'name': '十字線 (Doji)',
            'signal': '転換の可能性',
            'type': 'neutral'
        })
    
    # Hammer (Long lower shadow, small body at top)
    lower_shadow = min(last['Open'], last['Close']) - last['Low']
    upper_shadow = last['High'] - max(last['Open'], last['Close'])
    
    if range_size > 0 and lower_shadow > body * 2 and upper_shadow < body:
        patterns.append({
            'name': 'ハンマー (Hammer)',
            'signal': '下落トレンドの反転示唆',
            'type': 'bullish'
        })
    
    # Engulfing Pattern
    if last['Close'] > last['Open'] and prev['Close'] < prev['Open']:
        if last['Open'] <= prev['Close'] and last['Close'] >= prev['Open']:
            patterns.append({
                'name': '強気の包み線 (Bullish Engulfing)',
                'signal': '強い買いシグナル',
                'type': 'bullish'
            })
    
    if last['Close'] < last['Open'] and prev['Close'] > prev['Open']:
        if last['Open'] >= prev['Close'] and last['Close'] <= prev['Open']:
            patterns.append({
                'name': '弱気の包み線 (Bearish Engulfing)',
                'signal': '強い売りシグナル',
                'type': 'bearish'
            })
    
    return patterns

def detect_chart_patterns(df):
    """
    Detect chart patterns like Head & Shoulders, Double Top/Bottom.
    Returns list of detected patterns.
    """
    if df is None or len(df) < 30:
        return []
    
    patterns = []
    recent = df.tail(30)
    
    # Simplified Double Top detection
    highs = recent['High'].values
    peaks = []
    for i in range(5, len(highs) - 5):
        if highs[i] == max(highs[i-5:i+5]):
            peaks.append((i, highs[i]))
    
    if len(peaks) >= 2:
        # Check if last two peaks are similar height
        last_two = peaks[-2:]
        if abs(last_two[0][1] - last_two[1][1]) / last_two[0][1] < 0.03:  # Within 3%
            patterns.append({
                'name': 'ダブルトップ (Double Top)',
                'signal': '下落転換の可能性',
                'type': 'bearish'
            })
    
    # Simplified Double Bottom detection
    lows = recent['Low'].values
    troughs = []
    for i in range(5, len(lows) - 5):
        if lows[i] == min(lows[i-5:i+5]):
            troughs.append((i, lows[i]))
    
    if len(troughs) >= 2:
        last_two = troughs[-2:]
        if abs(last_two[0][1] - last_two[1][1]) / last_two[0][1] < 0.03:
            patterns.append({
                'name': 'ダブルボトム (Double Bottom)',
                'signal': '上昇転換の可能性',
                'type': 'bullish'
            })
    
    return patterns

def enhance_ai_analysis_with_patterns(df):
    """
    Combine all pattern detection for enhanced AI analysis.
    Returns comprehensive pattern analysis.
    """
    sr_levels = detect_support_resistance(df)
    candlestick = detect_candlestick_patterns(df)
    chart_patterns = detect_chart_patterns(df)
    
    return {
        'support_resistance': sr_levels,
        'candlestick_patterns': candlestick,
        'chart_patterns': chart_patterns
    }
