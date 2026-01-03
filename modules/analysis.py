import pandas as pd
import numpy as np

def calculate_indicators(df, params=None, interval="1d", **kwargs):
    """
    Add technical indicators to the DataFrame.
    """
    if params is None:
        params = {
            'sma_short': 5, 'sma_mid': 25, 'sma_long': 75,
            'rsi_period': 14,
            'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9,
            'bb_window': 20, 'bb_std': 2
        }
    
    df = df.copy()
    
    # Simple Moving Averages
    if interval == "1wk":
        # Weekly standard: 13, 26, 52 weeks
        df['SMA13'] = df['Close'].rolling(window=13).mean()
        df['SMA26'] = df['Close'].rolling(window=26).mean()
        df['SMA52'] = df['Close'].rolling(window=52).mean()
    else:
        # Daily/Default: Use params or 5, 25, 75
        df['SMA5'] = df['Close'].rolling(window=params.get('sma_short', 5)).mean()
        df['SMA25'] = df['Close'].rolling(window=params.get('sma_mid', 25)).mean()
        df['SMA75'] = df['Close'].rolling(window=params.get('sma_long', 75)).mean()
    
    # RSI
    period = params.get('rsi_period', 14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df['Close'].ewm(span=params.get('macd_fast', 12), adjust=False).mean()
    ema26 = df['Close'].ewm(span=params.get('macd_slow', 26), adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=params.get('macd_signal', 9), adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # Bollinger Bands
    bb_window = params.get('bb_window', 20)
    bb_std_dev = params.get('bb_std', 2)
    df['BB_Mid'] = df['Close'].rolling(window=bb_window).mean()
    df['BB_Std'] = df['Close'].rolling(window=bb_window).std()
    df['BB_Upper'] = df['BB_Mid'] + (bb_std_dev * df['BB_Std'])
    df['BB_Lower'] = df['BB_Mid'] - (bb_std_dev * df['BB_Std'])
    
    # Volume MA
    if 'Volume' in df.columns:
        df['VolSMA5'] = df['Volume'].rolling(window=5).mean()
        
    # ATR (14)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(window=14).mean()
    
    return df

from modules.llm import generate_gemini_analysis
from modules.enhanced_metrics import calculate_advanced_metrics
from modules.patterns import enhance_ai_analysis_with_patterns

def calculate_trading_strategy(df, settings=None):
    """
    Calculate trading strategy levels (Entry, TP, SL) and trend status.
    Now supports dynamic ATR-based Stop Loss with a safety guardrail from settings.
    Returns strategic_data dict.
    """
    if df is None or df.empty:
        return {}

    if settings is None:
        settings = {}

    last = df.iloc[-1]
    price = last['Close']
    
    needed = ['SMA5', 'SMA25', 'SMA75', 'BB_Upper', 'BB_Lower', 'ATR']
    if not all(col in df.columns for col in needed):
        if 'SMA13' in df.columns:
            return {}
        return {}
        
    sma5, sma25, sma75 = last['SMA5'], last['SMA25'], last['SMA75']
    bb_up, bb_low = last['BB_Upper'], last['BB_Lower']
    atr = last['ATR']
    
    # 1. Trend Analysis
    trend_score = 0
    trend_desc = ""
    
    if sma5 > sma25 > sma75:
        trend_desc = "🟢 パーフェクトオーダー（上昇）"
        trend_score += 2
    elif sma5 < sma25 < sma75:
        trend_desc = "🔴 パーフェクトオーダー（下落）"
        trend_score -= 2
    else:
        if price > sma25:
            trend_desc = "📈 上昇基調"
            trend_score += 1
        else:
            trend_desc = "📉 下落基調"
            trend_score -= 1
            
    # 2. Strategy Levels
    support_candidates = [l for l in [sma25, sma75, bb_low] if l < price]
    support_level = max(support_candidates) if support_candidates else price * 0.95
    resistance_level = bb_up
    
    # --- Dynamic Stop Loss Logic ---
    buy_zone_min = support_level
    buy_zone_max = support_level * 1.015
    entry_price = int((buy_zone_min + buy_zone_max) / 2)
    
    # ATR-based SL (Standard: 1.5x - 2.0x ATR)
    multiplier = 2.0
    atr_stop_loss = entry_price - (multiplier * atr)
    
    # Guardrail from Settings (Default -5% if not set)
    sl_limit_pct = float(settings.get('stop_loss_limit', -5.0))
    limit_stop_loss = entry_price * (1 + (sl_limit_pct / 100))
    
    # Choose the safer (tighter) stop loss if ATR SL is too deep
    # but also respect the volatility if it's within limits
    stop_loss = atr_stop_loss
    sl_source = "ATR"
    is_high_risk = False
    
    if atr_stop_loss < limit_stop_loss:
        # ATR suggests a deeper cut than our fixed limit
        stop_loss = limit_stop_loss
        sl_source = "Fixed Limit (-5%)"
        is_high_risk = True # Signal that volatility exceeds safety limit
    
    target_price = resistance_level
    
    risk = entry_price - stop_loss
    reward = target_price - entry_price
    rr_ratio = reward / risk if risk > 0 else 0
    
    strategy_msg = ""
    action_msg = ""
    if trend_score >= 1:
        strategy_msg = "🐂 押し目買い戦略"
        action_msg = f"上昇トレンド継続中。**¥{entry_price:,}円付近**でエントリーを検討してください。"
    elif trend_score <= -1:
        strategy_msg = "🐻 戻り売り/様子見"
        action_msg = "下落トレンド中。無理なエントリーは控え、底打ちシグナルを待つべきです。"
    else:
        strategy_msg = "⚖️ レンジ戦略"
        action_msg = f"方向感が乏しい展開。**¥{entry_price:,}円付近**まで待ってからエントリーを検討。"
    
    if is_high_risk:
        action_msg += f"\n\n⚠️ **リスク警告**: ボラティリティが非常に高いため、通常の損切り設定({sl_limit_pct}%)を優先しました。リスク許容度に注意してください。"

    # --- Volume Spike Detection ---
    volume_spike_data = detect_volume_spike(df)

    return {
        'trend_desc': trend_desc,
        'trend_score': trend_score,
        'action_msg': action_msg,
        'target_price': int(target_price),
        'stop_loss': int(stop_loss),
        'entry_price': entry_price,
        'strategy_msg': strategy_msg,
        'risk_reward': rr_ratio,
        'sl_source': sl_source,
        'is_high_risk': is_high_risk,
        'atr_value': atr,
        'volume_spike': volume_spike_data['is_spike'],
        'volume_ratio': volume_spike_data['ratio']
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
    prev = df.iloc[-2]
    
    price = last['Close']
    # Safe access to columns that might depend on interval
    sma5 = last.get('SMA5', 0)
    sma25 = last.get('SMA25', 0)
    sma75 = last.get('SMA75', 0)
    rsi = last.get('RSI', 50)
    macd = last.get('MACD', 0)
    macd_sig = last.get('MACD_Signal', 0)
    bb_up = last.get('BB_Upper', price * 1.05)
    bb_low = last.get('BB_Lower', price * 0.95)
    bb_mid = last.get('BB_Mid', price)
    atr = last.get('ATR', price * 0.02)
    
    # Calculate Enhanced Metrics
    enhanced_metrics = calculate_advanced_metrics(df, price)
    
    # Detect Patterns
    patterns = enhance_ai_analysis_with_patterns(df)
    
    # Strategy Calculation (if not provided/re-calc)
    strategic_data = calculate_trading_strategy(df)
    trend_desc = strategic_data.get('trend_desc', '')

    # --- Momentum & Volatility (MACD & BB) ---
    signals = []
    macd_status = "中立"
    
    if macd > macd_sig and prev.get('MACD', 0) <= prev.get('MACD_Signal', 0):
        signals.append("🚀 ゴールデンクロス (MACD)")
        macd_status = "ゴールデンクロス発生"
    elif macd < macd_sig and prev.get('MACD', 0) >= prev.get('MACD_Signal', 0):
        signals.append("⚠️ デッドクロス (MACD)")
        macd_status = "デッドクロス発生"
    elif macd > macd_sig:
        macd_status = "買いシグナル継続"
    else:
        macd_status = "売りシグナル継続"
    
    bb_width = (bb_up - bb_low) / bb_mid if bb_mid > 0 else 0
    volatility_msg = ""
    bb_status = "通常"
    if bb_width < 0.10: 
        volatility_msg = "⚡ スクイーズ（収束）"
        bb_status = "スクイーズ（爆発前夜）"
    
    if price >= bb_up:
        signals.append("🔥 バンドウォーク警戒")
        bb_status = "バンドウォーク（過熱）"
    elif price <= bb_low:
        signals.append("💧 売られすぎ")
        bb_status = "売られすぎ（反発期待）"

    rsi_msg = ""
    rsi_status = "中立"
    if rsi > 70:
        rsi_msg = f"🔴 RSI {rsi:.1f} (過熱)"
        rsi_status = "買われすぎ"
    elif rsi < 30:
        rsi_msg = f"🟢 RSI {rsi:.1f} (底値圏)"
        rsi_status = "売られすぎ"
    else:
        rsi_msg = f"⚪ RSI {rsi:.1f} (中立)"

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
