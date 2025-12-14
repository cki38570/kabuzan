import pandas as pd
import numpy as np

def calculate_indicators(df, params=None):
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

def generate_ai_report(df, credit_data, ticker_name, price_info=None):
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
    sma5 = last['SMA5']
    sma25 = last['SMA25']
    sma75 = last['SMA75']
    rsi = last['RSI']
    macd = last['MACD']
    macd_sig = last['MACD_Signal']
    bb_up = last['BB_Upper']
    bb_low = last['BB_Lower']
    bb_mid = last['BB_Mid']
    atr = last['ATR']
    
    # Calculate Enhanced Metrics
    enhanced_metrics = calculate_advanced_metrics(df, price)
    
    # Detect Patterns
    patterns = enhance_ai_analysis_with_patterns(df)
    
    # --- 1. Trend Analysis ---
    trend_score = 0
    trend_desc = ""
    
    # Perfect Order Check
    if sma5 > sma25 > sma75:
        trend_desc = "🟢 パーフェクトオーダー（上昇）"
        trend_score += 2
    elif sma5 < sma25 < sma75:
        trend_desc = "🔴 パーフェクトオーダー（下落）"
        trend_score -= 2
    else:
        # General Trend
        if price > sma25:
            trend_desc = "📈 上昇基調"
            trend_score += 1
        else:
            trend_desc = "📉 下落基調"
            trend_score -= 1

    # --- 2. Momentum & Volatility (MACD & BB) ---
    signals = []
    macd_status = "中立"
    
    # MACD
    if macd > macd_sig and prev['MACD'] <= prev['MACD_Signal']:
        signals.append("🚀 ゴールデンクロス (MACD)")
        macd_status = "ゴールデンクロス発生"
    elif macd < macd_sig and prev['MACD'] >= prev['MACD_Signal']:
        signals.append("⚠️ デッドクロス (MACD)")
        macd_status = "デッドクロス発生"
    elif macd > macd_sig:
        macd_status = "買いシグナル継続"
    else:
        macd_status = "売りシグナル継続"
    
    # Bollinger Bands
    bb_width = (bb_up - bb_low) / bb_mid
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

    # RSI
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

    # --- 3. Supply/Demand (Credit) ---
    credit_msg = "データなし"
    credit_score = 0
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
                    credit_score += 1
                elif ratio > 8.0:
                    credit_msg += " (買い残多)"
                    credit_score -= 1
        except:
            pass

    # --- 4. Strategic Scenarios (New) ---
    # Calculate Levels
    support_candidates = [l for l in [sma25, sma75, bb_low] if l < price]
    support_level = max(support_candidates) if support_candidates else price * 0.95
    resistance_level = bb_up
    
    buy_zone_min = support_level
    buy_zone_max = support_level * 1.015
    stop_loss = support_level - (1.5 * atr)
    target_price = resistance_level
    
    # Calculate optimal entry price (middle of buy zone)
    entry_price = int((buy_zone_min + buy_zone_max) / 2)
    
    risk = buy_zone_max - stop_loss
    reward = target_price - buy_zone_max
    rr_ratio = reward / risk if risk > 0 else 0
    
    strategy_msg = ""
    if trend_score >= 1:
        strategy_msg = "🐂 押し目買い戦略"
        action_msg = f"上昇トレンド継続中。**¥{entry_price:,}円付近**でエントリーを検討してください。"
    elif trend_score <= -1:
        strategy_msg = "🐻 戻り売り/様子見"
        action_msg = "下落トレンド中。無理なエントリーは控え、底打ちシグナルを待つべきです。"
    else:
        strategy_msg = "⚖️ レンジ戦略"
        action_msg = f"方向感が乏しい展開。**¥{entry_price:,}円付近**まで待ってからエントリーを検討。"

    # --- Prepare Data for LLM ---
    indicators_data = {
        'rsi': rsi,
        'rsi_status': rsi_status,
        'macd_status': macd_status,
        'bb_status': bb_status,
        'atr': atr
    }
    
    strategic_data = {
        'trend_desc': trend_desc,
        'action_msg': action_msg,
        'target_price': int(target_price),
        'stop_loss': int(stop_loss),
        'entry_price': entry_price,  # Added entry price
        'strategy_msg': strategy_msg,
        'risk_reward': rr_ratio
    }
    
    if price_info is None:
        price_info = {'current_price': price, 'change_percent': 0.0}

    # Call LLM with Enhanced Metrics and Patterns
    llm_report = generate_gemini_analysis(
        ticker_name, 
        price_info, 
        indicators_data, 
        credit_msg, 
        strategic_data,
        enhanced_metrics=enhanced_metrics,
        patterns=patterns
    )
    
    if llm_report:
        return llm_report, strategic_data

    # Fallback to Heuristic Report
    signal_bullet = "\n".join([f"- {s}" for s in signals]) if signals else "- 特になし"
    
    report = f"""
### 🧠 Deep AI Market Insight (Heuristic)

**1. 戦略的トレードシナリオ**
{strategy_msg}
- {action_msg}
- **🎯 利確目標**: {int(target_price):,} 円
- **🛡️ 損切ライン**: {int(stop_loss):,} 円
- **⚖️ リスクリワード比**: {rr_ratio:.2f}

**2. トレンド構造**
{trend_desc}

**3. テクニカル・シグナル**
{signal_bullet}
- {volatility_msg}
- {rsi_msg}

**4. 需給分析**
- {credit_msg}
    """
    return report.strip(), strategic_data
