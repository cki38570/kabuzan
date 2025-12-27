import pandas as pd
import streamlit as st
from modules.data_manager import get_data_manager
from modules.analysis import calculate_indicators
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ticker Categories
from modules.constants import SCREENER_CATEGORIES as CATEGORIES

def scan_single_stock(stock):
    """Worker function for parallel scanning."""
    try:
        dm = get_data_manager()
        df, info = dm.get_market_data(stock['code'])
        if df is None or df.empty:
            return None
            
        df = calculate_indicators(df)
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        score = 0
        
        if last['SMA5'] > last['SMA25'] and prev['SMA5'] <= prev['SMA25']:
            signals.append("🔼 短期GC")
            score += 2
        
        if last['MACD'] > last['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
            signals.append("🚀 MACD GC")
            score += 3
        
        rsi = last['RSI']
        if rsi < 30:
            signals.append("💎 売られすぎ")
            score += 2
        elif rsi > 70:
            signals.append("⚠️ 買われすぎ")
            score -= 1
        
        bb_width = (last['BB_Upper'] - last['BB_Lower']) / last['BB_Mid']
        if bb_width < 0.05:
            signals.append("⚡ バンド凝縮")
            score += 1

        recommendation = "様子見"
        if score >= 3: recommendation = "🔥 強気買い"
        elif score >= 1 or (rsi < 30): recommendation = "🟢 買い検討"
        elif score <= -1: recommendation = "🟣 売り検討"
        
        if signals or score != 0:
            return {
                'コード': stock['code'],
                '銘柄名': stock['name'],
                '現在値': f"¥{info['current_price']:,.0f}",
                '前日比': f"{info['change_percent']:+.2f}%",
                '判定': recommendation,
                'シグナル': ", ".join(signals),
                'RSI': f"{rsi:.1f}",
                'raw_score': score
            }
    except Exception:
        pass
    return None

def scan_market(category_name="主要大型株 (48)", progress_bar=None):
    """Scan market using parallel processing."""
    results = []
    target_stocks = CATEGORIES.get(category_name, CATEGORIES["主要大型株 (48)"])
    total = len(target_stocks)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_stock = {executor.submit(scan_single_stock, s): s for s in target_stocks}
        
        completed = 0
        for future in as_completed(future_to_stock):
            completed += 1
            if progress_bar:
                progress_bar.progress(completed / total, text=f"スキャン進行中... ({completed}/{total})")
            
            res = future.result()
            if res:
                results.append(res)
                
    if results:
        res_df = pd.DataFrame(results)
        return res_df.sort_values('raw_score', ascending=False)
    return pd.DataFrame()
