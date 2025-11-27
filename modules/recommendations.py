import pandas as pd
import numpy as np
from modules.data import get_stock_data
from modules.analysis import calculate_indicators

# Major Japanese stocks for comparison (TOPIX Core 30)
MAJOR_STOCKS = {
    '7203': 'トヨタ自動車',
    '9984': 'ソフトバンクG',
    '6758': 'ソニーG',
    '9433': 'KDDI',
    '8306': '三菱UFJ',
    '6861': 'キーエンス',
    '6954': 'ファナック',
    '7974': '任天堂',
    '4063': '信越化学',
    '6098': 'リクルート',
    '4502': '武田薬品',
    '4503': 'アステラス',
    '6501': '日立',
    '6902': 'デンソー',
    '7267': 'ホンダ',
    '7201': '日産自動車',
    '8058': '三菱商事',
    '8001': '伊藤忠',
    '9020': 'JR東日本',
    '9022': 'JR東海'
}

def calculate_correlation(df1, df2, days=60):
    """
    Calculate correlation between two stock price series.
    Returns correlation coefficient (-1 to 1).
    """
    try:
        # Use last N days
        prices1 = df1['Close'].tail(days).pct_change().dropna()
        prices2 = df2['Close'].tail(days).pct_change().dropna()
        
        # Align indices
        common_idx = prices1.index.intersection(prices2.index)
        if len(common_idx) < 20:  # Need minimum data points
            return 0.0
        
        correlation = prices1.loc[common_idx].corr(prices2.loc[common_idx])
        return correlation if not np.isnan(correlation) else 0.0
    except:
        return 0.0

def calculate_volatility_similarity(df1, df2):
    """
    Calculate how similar the volatility is between two stocks.
    Returns similarity score (0 to 1).
    """
    try:
        vol1 = df1['Close'].pct_change().std()
        vol2 = df2['Close'].pct_change().std()
        
        # Similarity based on ratio (closer to 1 = more similar)
        ratio = min(vol1, vol2) / max(vol1, vol2) if max(vol1, vol2) > 0 else 0
        return ratio
    except:
        return 0.0

def find_similar_stocks(ticker, df, top_n=5):
    """
    Find stocks similar to the given ticker.
    Returns list of dicts with ticker, name, and similarity score.
    """
    similar_stocks = []
    
    for code, name in MAJOR_STOCKS.items():
        if code == ticker:
            continue
        
        # Fetch comparison stock data
        comp_df, comp_info = get_stock_data(code)
        if comp_df is None or len(comp_df) < 30:
            continue
        
        # Calculate similarity metrics
        correlation = calculate_correlation(df, comp_df)
        vol_similarity = calculate_volatility_similarity(df, comp_df)
        
        # Combined similarity score (weighted average)
        # Correlation is more important than volatility similarity
        similarity = (correlation * 0.7 + vol_similarity * 0.3)
        
        # Only include if reasonably similar (correlation > 0.3)
        if correlation > 0.3:
            similar_stocks.append({
                'code': code,
                'name': name,
                'similarity': similarity,
                'correlation': correlation,
                'vol_similarity': vol_similarity
            })
    
    # Sort by similarity score
    similar_stocks.sort(key=lambda x: x['similarity'], reverse=True)
    
    return similar_stocks[:top_n]

def get_recommendation_reason(similarity_data):
    """
    Generate human-readable reason for recommendation.
    """
    corr = similarity_data['correlation']
    vol_sim = similarity_data['vol_similarity']
    
    reasons = []
    
    if corr > 0.7:
        reasons.append("値動きが非常に似ています")
    elif corr > 0.5:
        reasons.append("値動きが似ています")
    
    if vol_sim > 0.8:
        reasons.append("ボラティリティが近い")
    
    if not reasons:
        reasons.append("相関性があります")
    
    return "、".join(reasons)
