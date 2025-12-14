import pandas as pd
import streamlit as st
from modules.data import get_stock_data
from modules.analysis import calculate_indicators

# Major Japanese Stocks (Nikkei 225 & Large Cap Selection)
TARGET_TICKERS = [
    {'code': '7203', 'name': 'トヨタ自動車'},
    {'code': '9984', 'name': 'ソフトバンクG'},
    {'code': '6758', 'name': 'ソニーG'},
    {'code': '6861', 'name': 'キーエンス'},
    {'code': '6098', 'name': 'リクルートHD'},
    {'code': '9983', 'name': 'ファーストリテイリング'},
    {'code': '8316', 'name': '三井住友FG'},
    {'code': '9432', 'name': '日本電信電話'},
    {'code': '8306', 'name': '三菱UFJ'},
    {'code': '7974', 'name': '任天堂'},
    {'code': '8035', 'name': '東京エレクトロン'},
    {'code': '8058', 'name': '三菱商事'},
    {'code': '6501', 'name': '日立製作所'},
    {'code': '4063', 'name': '信越化学'},
    {'code': '4502', 'name': '武田薬品'},
    {'code': '3382', 'name': 'セブン＆アイ'},
    {'code': '8001', 'name': '伊藤忠商事'},
    {'code': '6954', 'name': 'ファナック'},
    {'code': '6367', 'name': 'ダイキン工業'},
    {'code': '4568', 'name': '第一三共'},
    {'code': '6273', 'name': 'SMC'},
    {'code': '7741', 'name': 'HOYA'},
    {'code': '6981', 'name': '村田製作所'},
    {'code': '7267', 'name': '本田技研'},
    {'code': '2914', 'name': 'JT'},
    {'code': '4452', 'name': '花王'},
    {'code': '8766', 'name': '東京海上HD'},
    {'code': '6902', 'name': 'デンソー'},
    {'code': '4543', 'name': 'テルモ'},
    {'code': '6594', 'name': 'ニデック'},
    {'code': '5401', 'name': '日本製鉄'},
    {'code': '8802', 'name': '三菱地所'},
    {'code': '8411', 'name': 'みずほFG'},
    {'code': '7201', 'name': '日産自動車'},
    {'code': '7733', 'name': 'オリンパス'},
    {'code': '6702', 'name': '富士通'},
    {'code': '9101', 'name': '日本郵船'},
    {'code': '7011', 'name': '三菱重工'},
    {'code': '4901', 'name': '富士フイルム'},
    {'code': '6146', 'name': 'ディスコ'},
]

def scan_market(progress_bar=None):
    """
    Scan target tickers for trading signals.
    """
    results = []
    total = len(TARGET_TICKERS)
    
    for i, stock in enumerate(TARGET_TICKERS):
        if progress_bar:
            progress_bar.progress((i + 1) / total, text=f"分析中: {stock['name']} ({stock['code']})...")
            
        try:
            # Get Data (Cached)
            df, info = get_stock_data(stock['code'])
            if df is None or df.empty:
                continue
                
            # Calculate Indicators (Standard params)
            df = calculate_indicators(df)
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Logic Analysis
            signals = []
            score = 0
            
            # 1. Moving Average Trend
            start_trend = False
            if last['SMA5'] > last['SMA25'] and prev['SMA5'] <= prev['SMA25']:
                signals.append("🔼 短期GC (5-25DMA)")
                score += 2
                start_trend = True
            
            trend_status = "上昇" if last['Close'] > last['SMA25'] else "下落"
            
            # 2. MACD
            if last['MACD'] > last['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
                signals.append("🚀 MACD GC")
                score += 3
            elif last['MACD'] > last['MACD_Signal']:
                # Trend continue
                pass
            
            # 3. RSI
            rsi = last['RSI']
            rsi_status = "中立"
            if rsi < 30:
                signals.append("💎 売られすぎ (RSI<30)")
                score += 2
                rsi_status = "底値圏"
            elif rsi > 70:
                signals.append("⚠️ 買われすぎ (RSI>70)")
                score -= 1 # Warning
                rsi_status = "過熱圏"
            
            # 4. Bollinger Bands Squeeze
            bb_width = (last['BB_Upper'] - last['BB_Lower']) / last['BB_Mid']
            if bb_width < 0.05: # Very tight
                signals.append("⚡ バンドスクイーズ (急動意警戒)")
                score += 1

            # Determine Recommendation
            recommendation = "様子見"
            style = "color: gray"
            
            if score >= 3:
                recommendation = "🔥 強気買い"
                style = "color: red; font-weight: bold"
            elif score >= 1 or (rsi < 30):
                recommendation = "🟢 買い検討"
                style = "color: green; font-weight: bold"
            elif score <= -1:
                recommendation = "🟣 売り/利確検討"
                style = "color: purple"
            
            if signals or score != 0: # Only list interesting ones
                results.append({
                    'コード': stock['code'],
                    '銘柄名': stock['name'],
                    '現在値': f"¥{info['current_price']:,.0f}",
                    '前日比': f"{info['change_percent']:+.2f}%",
                    '判定': recommendation,
                    'シグナル': ", ".join(signals),
                    'RSI': f"{rsi:.1f}",
                    'raw_score': score # For sorting
                })
                
        except Exception as e:
            print(f"Error scanning {stock['code']}: {e}")
            continue
            
    # Convert to DF and sort
    if results:
        res_df = pd.DataFrame(results)
        res_df = res_df.sort_values('raw_score', ascending=False)
        return res_df
    return pd.DataFrame()
