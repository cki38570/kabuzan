import pandas as pd
import numpy as np
import pandas_ta as ta
from modules.llm import generate_gemini_analysis
from modules.enhanced_metrics import calculate_advanced_metrics
from modules.patterns import enhance_ai_analysis_with_patterns

def calculate_indicators(df, params=None, interval="1d", **kwargs):
    """
    Add technical indicators to the DataFrame.
    Standardizes column names to be friendly for downstream usage (SMA5, SMA25, etc.)
    """
    if params is None:
        params = {
            'sma_short': 5, 'sma_mid': 25, 'sma_long': 75,
            'rsi_period': 14,
            'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9,
            'bb_window': 20, 'bb_std': 2
        }
    
    df = df.copy()
    
    # --- SMA ---
    if interval == "1wk":
        # Weekly: 13, 26, 52
        df['SMA13'] = df.ta.sma(length=13)
        df['SMA26'] = df.ta.sma(length=26)
        df['SMA52'] = df.ta.sma(length=52)
        # Aliases for chart compatibility if needed
        df['SMA_13'] = df['SMA13']
        df['SMA_26'] = df['SMA26']
        df['SMA_52'] = df['SMA52']
    else:
        # Daily: Short, Mid, Long from params
        s_short = params.get('sma_short', 5)
        s_mid = params.get('sma_mid', 25)
        s_long = params.get('sma_long', 75)
        
        df[f'SMA{s_short}'] = df.ta.sma(length=s_short)
        df[f'SMA{s_mid}'] = df.ta.sma(length=s_mid)
        df[f'SMA{s_long}'] = df.ta.sma(length=s_long)
        
        # Ensure standard names exist regardless of params
        if f'SMA{s_short}' not in df.columns: df[f'SMA{s_short}'] = np.nan
        if f'SMA{s_mid}' not in df.columns: df[f'SMA{s_mid}'] = np.nan
        if f'SMA{s_long}' not in df.columns: df[f'SMA{s_long}'] = np.nan

        # Aliases
        df['SMA_5'] = df.get(f'SMA{s_short}')
        df['SMA_25'] = df.get(f'SMA{s_mid}')
        df['SMA_75'] = df.get(f'SMA{s_long}')

    # --- RSI ---
    rsi_len = params.get('rsi_period', 14)
    df['RSI'] = df.ta.rsi(length=rsi_len)
    
    # --- MACD ---
    macd = df.ta.macd(
        fast=params.get('macd_fast', 12), 
        slow=params.get('macd_slow', 26), 
        signal=params.get('macd_signal', 9)
    )
    # MACD returns multiple columns, e.g. MACD_12_26_9, MACDh_..., MACDs_...
    if macd is not None and not macd.empty:
        # Identify columns
        macd_col = next((c for c in macd.columns if c.startswith('MACD_')), None)
        hist_col = next((c for c in macd.columns if c.startswith('MACDh_')), None)
        sig_col = next((c for c in macd.columns if c.startswith('MACDs_')), None)
        
        if macd_col: df['MACD'] = macd[macd_col]
        if hist_col: df['MACD_Hist'] = macd[hist_col]
        if sig_col: df['MACD_Signal'] = macd[sig_col]

    # --- Bollinger Bands ---
    bb_len = params.get('bb_window', 20)
    bb_std = params.get('bb_std', 2)
    bbands = df.ta.bbands(length=bb_len, std=bb_std)
    
    if bbands is not None and not bbands.empty:
        # BBL_20_2.0, BBM_20_2.0, BBU_20_2.0
        lower = next((c for c in bbands.columns if c.startswith('BBL')), None)
        mid = next((c for c in bbands.columns if c.startswith('BBM')), None)
        upper = next((c for c in bbands.columns if c.startswith('BBU')), None)
        
        if lower: df['BB_Lower'] = bbands[lower]
        if mid: df['BB_Mid'] = bbands[mid]
        if upper: df['BB_Upper'] = bbands[upper]
        
        # Keep original names for charts.py compatibility if it relies on BBU_... pattern
        # checking charts.py, it looks for BBU_ or BB_Upper, so we are good.
        for c in bbands.columns:
            df[c] = bbands[c]

    # --- Parabolic SAR ---
    psar_df = df.ta.psar(append=False)
    if psar_df is not None and not psar_df.empty:
        # Combine PSARl and PSARs
        combined_psar = pd.Series(np.nan, index=df.index)
        for c in psar_df.columns:
            combined_psar = combined_psar.combine_first(psar_df[c])
        df['PSAR'] = combined_psar
    else:
        df['PSAR'] = np.nan

    # --- ATR ---
    df['ATR'] = df.ta.atr(length=14)
    
    # --- Volume SMA ---
    if 'Volume' in df.columns and df['Volume'].sum() > 0:
         df['VolSMA5'] = df.ta.sma(close='Volume', length=5)
        
    return df


def calculate_trading_strategy(df, settings=None):
    """
    Calculate trading strategy levels (Long and Short) and trend status.
    Uses robust data checking to proceed even if some indicators are missing.
    """
    if df is None or df.empty:
        return {}

    if settings is None:
        settings = {}

    last = df.iloc[-1]
    price = last['Close']
    
    # Get indicators with defaults if missing
    def get_val(key, alt_key=None):
        val = last.get(key)
        if val is None or pd.isna(val):
            val = last.get(alt_key)
        return val

    sma5 = get_val('SMA5', 'SMA_5')
    sma25 = get_val('SMA25', 'SMA_25')
    sma75 = get_val('SMA75', 'SMA_75')
    bb_up = get_val('BB_Upper', 'BBU_20_2.0')
    bb_low = get_val('BB_Lower', 'BBL_20_2.0')
    atr = get_val('ATR', 'ATRr_14')
    
    if pd.isna(sma25):
        return {
            'trend_desc': "データ不足",
            'strategy_msg': "十分な価格データがありません",
            'long': {'target_price': 0, 'stop_loss': 0, 'entry_price': 0},
            'short': {'target_price': 0, 'stop_loss': 0, 'entry_price': 0}
        }
    
    # --- 1. Trend Analysis ---
    trend_score = 0
    trend_desc = ""
    is_perfect_up = (sma5 is not None and sma75 is not None) and (sma5 > sma25 > sma75)
    is_perfect_down = (sma5 is not None and sma75 is not None) and (sma5 < sma25 < sma75)
    
    if is_perfect_up:
        trend_desc = "🟢 パーフェクトオーダー（上昇）"
        trend_score += 2
    elif is_perfect_down:
        trend_desc = "🔴 パーフェクトオーダー（下落）"
        trend_score -= 2
    else:
        if price > sma25:
            trend_desc = "📈 上昇基調"
            trend_score += 1
        else:
            trend_desc = "📉 下落基調"
            trend_score -= 1
            
    # --- 2. Strategy Levels (Long) ---
    support_candidates = []
    if sma25 and sma25 < price: support_candidates.append(sma25)
    if sma75 and sma75 < price: support_candidates.append(sma75)
    if bb_low and bb_low < price: support_candidates.append(bb_low)
    support_level = max(support_candidates) if support_candidates else price * 0.97
    
    resistance_level = bb_up if (bb_up and not pd.isna(bb_up)) else price * 1.05
    
    # Long Entry
    long_entry = int(support_level * 1.005)
    long_tp = int(resistance_level)
    
    val_atr = atr if (atr and not pd.isna(atr)) else price * 0.02
    long_sl = int(long_entry - (2.0 * val_atr))
    
    # --- 3. Strategy Levels (Short) ---
    res_candidates = []
    if sma25 and sma25 > price: res_candidates.append(sma25)
    if bb_up and bb_up > price: res_candidates.append(bb_up)
    res_level = min(res_candidates) if res_candidates else price * 1.03
    
    short_entry = int(res_level * 0.995)
    short_tp = int(bb_low if (bb_low and not pd.isna(bb_low)) else price * 0.95)
    short_sl = int(short_entry + (2.0 * val_atr))

    # --- Volume Spike ---
    volume_spike_data = detect_volume_spike(df)

    return {
        'trend_desc': trend_desc,
        'trend_score': trend_score,
        'long': {
            'entry_price': long_entry,
            'target_price': long_tp,
            'stop_loss': long_sl,
            'label': "買いシナリオ"
        },
        'short': {
            'entry_price': short_entry,
            'target_price': short_tp,
            'stop_loss': short_sl,
            'label': "空売りシナリオ"
        },
        'volume_spike': bool(volume_spike_data['is_spike']),
        'volume_ratio': float(volume_spike_data['ratio'])
    }


def detect_volume_spike(df, window=20, threshold=2.0):
    """
    Detect if the latest volume is significantly higher than the simple moving average of volume.
    Returns: dict with 'is_spike' (bool) and 'ratio' (float)
    """
    if df is None or len(df) < window:
        return {'is_spike': False, 'ratio': 1.0}
    
    # Calculate volume MA
    df = df.copy()
    df['VolMA'] = df['Volume'].rolling(window=window).mean()
    
    last_vol = df['Volume'].iloc[-1]
    avg_vol = df['VolMA'].iloc[-1]
    
    if avg_vol == 0 or pd.isna(avg_vol):
        return {'is_spike': False, 'ratio': 1.0}
        
    ratio = last_vol / avg_vol
    is_spike = ratio >= threshold
    
    return {'is_spike': is_spike, 'ratio': ratio}

def calculate_relative_strength(stock_df, macro_data):
    """
    Compare stock performance against Nikkei 225.
    Returns relative strength status and description.
    """
    if stock_df is None or stock_df.empty or 'n225' not in macro_data:
        return {"status": "中立", "diff": 0, "desc": "地合いデータ不足"}

    n225 = macro_data['n225']
    stock_last = stock_df.iloc[-1]
    stock_prev = stock_df.iloc[-2] if len(stock_df) > 1 else stock_last
    
    stock_change = ((stock_last['Close'] - stock_prev['Close']) / stock_prev['Close']) * 100
    market_change = n225['change_pct']
    
    diff = stock_change - market_change
    
    status = "中立"
    desc = ""
    
    if stock_change > 0 and market_change <= 0:
        status = "強力（逆行高）"
        desc = "市場が軟調な中で上昇しており、非常に強い買い需要があります。"
    elif diff > 2.0:
        status = "買い優勢（アウトパフォーム）"
        desc = "市場平均を大きく上回る強さを見せています。"
    elif diff < -2.0:
        status = "売り優勢（アンダーパフォーム）"
        desc = "市場平均を下回る弱さです。地合いの悪化に敏感な可能性があります。"
    elif stock_change < 0 and market_change >= 0:
        status = "軟調（逆行安）"
        desc = "市場が堅調な中で下落しており、独自の売り要因が警戒されます。"
    else:
        status = "連動"
        desc = "市場全体と概ね連動した動きです。"

    return {
        "status": status,
        "diff": diff,
        "stock_change": stock_change,
        "market_change": market_change,
        "desc": desc
    }

def generate_ai_report(df, credit_data, ticker_name, price_info=None, extra_context=None):
    """
    Generate a comprehensive 'Deep AI' analysis report with Strategic Scenarios.
    Uses Gemini if available, otherwise falls back to heuristic.
    """
    if df is None or df.empty:
        return "データ不足のため分析できません。", {}
    
    # Latest Data Points
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    
    price = last['Close']
    
    # Safe access
    sma5 = last.get('SMA5', 0)
    # Strategy Calculation
    strategic_data = calculate_trading_strategy(df)

    # ... Indicators status ...
    macd = last.get('MACD', 0)
    macd_sig = last.get('MACD_Signal', 0)
    bb_up = last.get('BB_Upper', price * 1.05)
    bb_low = last.get('BB_Lower', price * 0.95)
    bb_mid = last.get('BB_Mid', price)
    atr = last.get('ATR', price * 0.02)
    rsi = last.get('RSI', 50)
    
    # --- Momentum & Volatility (MACD & BB) ---
    macd_status = "中立"
    prev_macd = prev.get('MACD', 0)
    prev_sig = prev.get('MACD_Signal', 0)
    
    if macd > macd_sig and prev_macd <= prev_sig:
        macd_status = "ゴールデンクロス発生"
    elif macd < macd_sig and prev_macd >= prev_sig:
        macd_status = "デッドクロス発生"
    elif macd > macd_sig:
        macd_status = "買いシグナル継続"
    else:
        macd_status = "売りシグナル継続"
    
    bb_width = (bb_up - bb_low) / bb_mid if bb_mid > 0 else 0
    bb_status = "通常"
    if bb_width < 0.10: 
        bb_status = "スクイーズ（爆発前夜）"
    
    if price >= bb_up:
        bb_status = "バンドウォーク（過熱）"
    elif price <= bb_low:
        bb_status = "売られすぎ（反発期待）"

    rsi_status = "中立"
    if rsi > 70:
        rsi_status = "買われすぎ"
    elif rsi < 30:
        rsi_status = "売られすぎ"
    
    # --- Supply/Demand (Credit) ---
    credit_msg = "データなし"
    if credit_data is not None and not credit_data.empty:
        try:
            ratio_col = [c for c in credit_data.columns if '倍率' in c]
            if ratio_col:
                ratio = credit_data[ratio_col[0]].iloc[0]
                if isinstance(ratio, str):
                    ratio = float(ratio.replace('倍', ''))
                credit_msg = f"信用倍率: {ratio}倍"
                if ratio < 1.0:
                    credit_msg += " (売り長・好取組)"
                elif ratio > 8.0:
                    credit_msg += " (買い残多)"
        except:
            pass

    # --- Prepare Data for LLM ---
    indicators_data = {
        'rsi': rsi,
        'rsi_status': rsi_status,
        'macd_status': macd_status,
        'bb_status': bb_status,
        'atr': atr
    }
    
    if price_info is None:
        price_info = {'current_price': price, 'change_percent': 0.0}

    # Calculate Enhanced Metrics & Patterns
    enhanced_metrics = calculate_advanced_metrics(df, price)
    patterns = enhance_ai_analysis_with_patterns(df)

    # Call LLM with Enhanced Metrics, Patterns, and Extra Context
    llm_report = generate_gemini_analysis(
        ticker_name, 
        price_info, 
        indicators_data, 
        credit_msg, 
        strategic_data,
        enhanced_metrics=enhanced_metrics,
        patterns=patterns,
        extra_context=extra_context
    )
    
    if llm_report:
        return llm_report, strategic_data

    # Fallback only if LLM completely fails
    return "⚠️ AI分析レポートの生成に失敗しました。APIキーまたは通信状況を確認してください。", strategic_data
