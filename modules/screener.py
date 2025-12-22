import pandas as pd
import streamlit as st
from modules.data_manager import get_data_manager
from modules.analysis import calculate_indicators
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ticker Categories
CATEGORIES = {
    "主要大型株 (48)": [
        {'code': '7203', 'name': 'トヨタ'}, {'code': '9984', 'name': 'ソフトバンクG'},
        {'code': '6758', 'name': 'ソニーG'}, {'code': '6861', 'name': 'キーエンス'},
        {'code': '8306', 'name': '三菱UFJ'}, {'code': '9983', 'name': 'ファストリ'},
        {'code': '8035', 'name': '東エレク'}, {'code': '6723', 'name': 'ルネサス'},
        {'code': '6501', 'name': '日立'}, {'code': '4063', 'name': '信越化'},
        {'code': '7974', 'name': '任天堂'}, {'code': '8058', 'name': '三菱商'},
        {'code': '6098', 'name': 'リクルート'}, {'code': '8316', 'name': '三井住友'},
        {'code': '4568', 'name': '第一三共'}, {'code': '9432', 'name': 'NTT'},
        {'code': '6146', 'name': 'ディスコ'}, {'code': '8001', 'name': '伊藤忠'},
        {'code': '6920', 'name': 'レーザーテク'}, {'code': '4503', 'name': 'アステラス'},
        {'code': '8766', 'name': '東京海上'}, {'code': '7741', 'name': 'HOYA'},
        {'code': '6902', 'name': 'デンソー'}, {'code': '4543', 'name': 'テルモ'},
        {'code': '6367', 'name': 'ダイキン'}, {'code': '2914', 'name': 'JT'},
        {'code': '5401', 'name': '日本製鉄'}, {'code': '8053', 'name': '住友商'},
        {'code': '6594', 'name': 'ニデック'}, {'code': '4452', 'name': '花王'},
        {'code': '8802', 'name': '三菱地所'}, {'code': '8113', 'name': 'ユニチャーム'},
        {'code': '9020', 'name': 'JR東日本'}, {'code': '8411', 'name': 'みずほ'},
        {'code': '6702', 'name': '富士通'}, {'code': '9101', 'name': '日本郵船'},
        {'code': '7011', 'name': '三菱重工'}, {'code': '4901', 'name': '富士フイルム'},
        {'code': '7267', 'name': 'ホンダ'}, {'code': '7733', 'name': 'オリンパス'},
        {'code': '6273', 'name': 'SMC'}, {'code': '6981', 'name': '村田製'},
        {'code': '4502', 'name': '武田'}, {'code': '3382', 'name': 'セブン＆アイ'},
        {'code': '8031', 'name': '三井物'}, {'code': '9433', 'name': 'KDDI'},
        {'code': '6503', 'name': '三菱電'}, {'code': '9022', 'name': 'JR東海'}
    ],
    "日経225 (抜粋)": [
        {'code': '1925', 'name': '大和ハウス'}, {'code': '2502', 'name': 'アサヒ'},
        {'code': '2801', 'name': 'キッコマン'}, {'code': '3407', 'name': '旭化成'},
        {'code': '4324', 'name': '電通'}, {'code': '4519', 'name': '中外薬'},
        {'code': '4911', 'name': '資生堂'}, {'code': '5108', 'name': 'ブリヂストン'},
        {'code': '5201', 'name': 'AGC'}, {'code': '5713', 'name': '住友鉱'},
        {'code': '6301', 'name': 'コマツ'}, {'code': '6752', 'name': 'パナHD'},
        {'code': '7751', 'name': 'キヤノン'}, {'code': '8002', 'name': '丸紅'},
        {'code': '8604', 'name': '野村'}, {'code': '9202', 'name': 'ANA'},
        {'code': '9501', 'name': '東電HD'}, {'code': '9613', 'name': 'NTTデータ'}
    ],
    "グロース・注目株": [
        {'code': '2160', 'name': 'ジーエヌアイ'}, {'code': '5253', 'name': 'カバー'},
        {'code': '5595', 'name': 'QPS研究所'}, {'code': '9166', 'name': 'GENDA'},
        {'code': '4475', 'name': 'HENNGE'}, {'code': '4180', 'name': 'Appier'},
        {'code': '7014', 'name': '名村造船'}, {'code': '6526', 'name': 'ソシオネクスト'}
    ]
}

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
