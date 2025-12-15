import pandas as pd
import numpy as np

def identify_candlestick_patterns(df):
    """
    Identify basic candlestick patterns from the DataFrame.
    Returns a list of dictionaries with 'name' and 'signal'.
    """
    patterns = []
    if len(df) < 5:
        return patterns

    # Get latest data
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Calculate body and shadows
    body_size = abs(latest['Close'] - latest['Open'])
    upper_shadow = latest['High'] - max(latest['Close'], latest['Open'])
    lower_shadow = min(latest['Close'], latest['Open']) - latest['Low']
    total_range = latest['High'] - latest['Low']
    
    # Avoid division by zero
    if total_range == 0:
        return patterns

    # 1. Doji (十字足)
    if body_size <= total_range * 0.1:
        signal = "転換の可能性 (迷い)"
        patterns.append({'name': '十字足 (Doji)', 'signal': signal, 'type': 'neutral'})

    # 2. Hammer (カラカサ/ハンマー) - Bullish Reversal
    # Small body, long lower shadow, little upper shadow
    if (lower_shadow >= body_size * 2) and (upper_shadow <= body_size * 0.5):
        signal = "強気リバーサル (底打ち示唆)"
        patterns.append({'name': 'カラカサ (Hammer)', 'signal': signal, 'type': 'bullish'})

    # 3. Shooting Star (流れ星) - Bearish Reversal
    # Small body, long upper shadow, little lower shadow
    if (upper_shadow >= body_size * 2) and (lower_shadow <= body_size * 0.5):
        signal = "弱気リバーサル (天井示唆)"
        patterns.append({'name': '流れ星 (Shooting Star)', 'signal': signal, 'type': 'bearish'})

    # 4. Engulfing (包み足)
    # Previous candle body is engulfed by current candle body
    prev_body_size = abs(prev['Close'] - prev['Open'])
    if body_size > prev_body_size:
        # Bullish Engulfing
        if prev['Close'] < prev['Open'] and latest['Close'] > latest['Open'] and latest['Close'] > prev['Open'] and latest['Open'] < prev['Close']:
             patterns.append({'name': '強気の包み足 (Bullish Engulfing)', 'signal': '強い買いシグナル', 'type': 'bullish'})
        # Bearish Engulfing
        elif prev['Close'] > prev['Open'] and latest['Close'] < latest['Open'] and latest['Close'] < prev['Open'] and latest['Open'] > prev['Close']:
             patterns.append({'name': '弱気の包み足 (Bearish Engulfing)', 'signal': '強い売りシグナル', 'type': 'bearish'})

    return patterns

def identify_chart_patterns(df):
    """
    Identify broader chart patterns (trends, higher lows, etc.)
    """
    patterns = []
    if len(df) < 20:
        return patterns

    # Helper to find local minima/maxima
    # Using a simple window approach for last 20 days
    recent_df = df.tail(20).copy()
    
    # Check for Higher Lows (Uptrend Support)
    # We look at the lowest low of the first 10 days vs last 10 days
    first_half = recent_df.iloc[:10]
    last_half = recent_df.iloc[10:]
    
    min1 = first_half['Low'].min()
    min2 = last_half['Low'].min()
    
    if min2 > min1 * 1.01: # 1% higher
        patterns.append({'name': '切り上がる安値 (Higher Lows)', 'signal': '上昇トレンドの継続示唆', 'type': 'bullish'})
        
    # Check for Lower Highs (Downtrend Resistance)
    max1 = first_half['High'].max()
    max2 = last_half['High'].max()
    
    if max2 < max1 * 0.99: # 1% lower
        patterns.append({'name': '切り下がる高値 (Lower Highs)', 'signal': '下落圧力の継続', 'type': 'bearish'})

    return patterns

def enhance_ai_analysis_with_patterns(df):
    """
    Main function to get all patterns for AI.
    """
    return {
        'candlestick_patterns': identify_candlestick_patterns(df),
        'chart_patterns': identify_chart_patterns(df)
    }
