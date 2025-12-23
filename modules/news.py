import yfinance as yf
import streamlit as st
import datetime

@st.cache_data(ttl=1800)  # 30分キャッシュ
def get_stock_news(ticker_code):
    """
    yfinanceを使用して最新のニュースを取得する。
    """
    if not str(ticker_code).endswith('.T') and str(ticker_code).isdigit():
        ticker_code = f"{ticker_code}.T"
        
    try:
        ticker = yf.Ticker(ticker_code)
        news = ticker.news
        if not news:
            return []
            
        formatted_news = []
        for n in news[:5]: # 最新5件
            formatted_news.append({
                'title': n.get('title'),
                'publisher': n.get('publisher'),
                'link': n.get('link'),
                'provider_publish_time': datetime.datetime.fromtimestamp(n.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M')
            })
        return formatted_news
    except Exception as e:
        print(f"Error fetching news for {ticker_code}: {e}")
        return []
