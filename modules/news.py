import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def get_stock_news(ticker_code):
    """
    Fetch recent news related to the ticker using yfinance.
    """
    if not str(ticker_code).endswith('.T'):
        ticker_code = f"{ticker_code}.T"
    
    try:
        ticker = yf.Ticker(ticker_code)
        news = ticker.news
        if not news:
            return []
        
        formatted_news = []
        for n in news[:5]: # Get top 5 news
            formatted_news.append({
                'title': n.get('title'),
                'publisher': n.get('publisher'),
                'link': n.get('link'),
                'provider_publish_time': n.get('providerPublishTime')
            })
        return formatted_news
    except Exception as e:
        print(f"Error fetching news for {ticker_code}: {e}")
        return []
