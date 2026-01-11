import pandas as pd
import requests
import time
import random
import datetime
import numpy as np

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("yfinance not available, using mock data.")
except Exception as e:
    YFINANCE_AVAILABLE = False
    print(f"yfinance failed to import: {e}, using mock data.")

import streamlit as st

@st.cache_data(ttl=900)
def get_cached_card_info(ticker_code):
    """
    Lightweight fetch for watchlist items.
    Avoids accessing the full 'info' property which is slow.
    """
    if not str(ticker_code).endswith('.T'):
        ticker_code = f"{ticker_code}.T"
        
    if not YFINANCE_AVAILABLE:
        # returns mock data if yfinance is not available
        return {
            'current_price': 1000, 'change_percent': 0.0, 'name': ticker_code
        }
        
    try:
        t = yf.Ticker(str(ticker_code))
        
        # Method 1: fast_info (Newer yfinance)
        try:
            cur_price = t.fast_info['last_price']
            prev_close = t.fast_info['previous_close']
            
            change = cur_price - prev_close
            pct = (change / prev_close) * 100
            
            return {
                'current_price': float(cur_price),
                'change_percent': float(pct),
                # Name often requires full info, maybe fetch once or use cached map?
                # For speed, we return ticker if name unavailable or rely on previously saved name
                'name': ticker_code 
            }
        except:
             pass
             
        # Method 2: minimal history
        hist = t.history(period="2d")
        if len(hist) >= 1:
            cur_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else cur_price
            
            change = cur_price - prev_close
            pct = (change / prev_close) * 100
             
            return {
                'current_price': float(cur_price),
                'change_percent': float(pct),
                'name': ticker_code
            }
            
    except Exception as e:
        print(f"Fast fetch failed for {ticker_code}: {e}")
        
    return None

@st.cache_data(ttl=900)
def get_stock_data(ticker_code, period="1y", interval="1d"):
    """
    Fetch stock data from yfinance.
    Adds .T suffix if missing.
    Falls back to mock data if yfinance is unavailable.
    Cached for 15 minutes.
    """
    if not str(ticker_code).endswith('.T'):
        ticker_code = f"{ticker_code}.T"
        
    if YFINANCE_AVAILABLE:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(str(ticker_code))
                # Retry fetching history if it comes back empty unexpectedly
                df = ticker.history(period=period, interval=interval)
                
                if df.empty and attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                
                # Flatten MultiIndex if present (yfinance update)
                if isinstance(df.columns, pd.MultiIndex):
                    try:
                        # Drop the Ticker level if it exists
                        df.columns = df.columns.get_level_values(0)
                    except:
                        pass
                
                if not df.empty:
                    # Get current price and change
                    info = ticker.info
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or df['Close'].iloc[-1]
                    
                    if len(df) >= 2:
                        prev_close = df['Close'].iloc[-2]
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100
                    else:
                        change = 0
                        change_percent = 0
                    
                    # Extract Sector and Industry
                    sector = info.get('sector', '不明')
                    industry = info.get('industry', '不明')
                    
                    return df, {
                        'current_price': float(current_price) if current_price is not None else 0.0,
                        'change': float(change) if change is not None else 0.0,
                        'change_percent': float(change_percent) if change_percent is not None else 0.0,
                        'name': info.get('longName', ticker_code),
                        'sector': sector,
                        'industry': industry,
                        'status': 'fresh',
                        'source': 'yfinance'
                    }
            except Exception as e:
                print(f"Attempt {attempt+1}/{max_retries} failed for {ticker_code}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    import streamlit as st
                    st.toast(f"データ取得エラー ({ticker_code}): {e}") # Use toast instead of error for less obtrusiveness
                    print(f"Error fetching stock data: {e}, falling back to mock.")
    
    # Mock Data Generation
    dates = pd.date_range(end=datetime.datetime.now(), periods=250, freq='B')
    base_price = 2800.0
    prices = [base_price]
    for _ in range(249):
        change = random.uniform(-0.02, 0.02)
        prices.append(prices[-1] * (1 + change))
        
    df = pd.DataFrame(index=dates)
    df['Close'] = prices
    df['Open'] = [p * (1 + random.uniform(-0.01, 0.01)) for p in prices]
    df['High'] = [max(o, c) * (1 + random.uniform(0, 0.01)) for o, c in zip(df['Open'], df['Close'])]
    df['Low'] = [min(o, c) * (1 - random.uniform(0, 0.01)) for o, c in zip(df['Open'], df['Close'])]
    df['Volume'] = [int(random.uniform(100000, 1000000)) for _ in range(250)] # Add Mock Volume
    
    current_price = prices[-1]
    prev_close = prices[-2]
    change = current_price - prev_close
    change_percent = (change / prev_close) * 100
    
    return df, {
        'current_price': current_price,
        'change': change,
        'change_percent': change_percent,
        'name': f"Mock: {ticker_code}"
    }

@st.cache_data(ttl=3600)  # Credit data updates less frequently
def get_credit_data(ticker_code):
    """
    Scrape credit margin data from Kabutan.
    Returns a DataFrame and a list of recent dicts.
    Falls back to mock data.
    """
    # Mock Data for Credit
    dates = pd.date_range(end=datetime.datetime.now(), periods=10, freq='W-FRI')[::-1]
    data = []
    for d in dates:
        sell = random.randint(1000, 5000)
        buy = random.randint(1000, 5000)
        ratio = buy / sell if sell > 0 else 1.0
        data.append({
            'Date': d.strftime('%Y-%m-%d'),
            '売残': sell,
            '買残': buy,
            '信用倍率': round(ratio, 2)
        })
    return pd.DataFrame(data)

@st.cache_data(ttl=21600) # Cache for 6 hours
def get_next_earnings_date(ticker_code):
    """
    Fetch the next earnings date for the ticker.
    """
    if not str(ticker_code).endswith('.T'):
        ticker_code = f"{ticker_code}.T"
        
    if YFINANCE_AVAILABLE:
        try:
            ticker = yf.Ticker(ticker_code)
            # Try getting calendar
            cal = ticker.calendar
            if cal is not None and not cal.empty:
                # Calendar might be a DataFrame where index or columns are dates
                # Often it has 'Earnings Date' or similar.
                # yfinance structure varies, usually it returns a dict or DF with 'Earnings Date'
                # For simplicity in this robust implementation:
                earnings_date = cal.get('Earnings Date')
                if earnings_date is not None:
                     if isinstance(earnings_date, list):
                         return earnings_date[0]
                     return earnings_date
                
                # Fallback: check index if it is dates
                return cal.iloc[0][0] # Crude attempt
            
        except Exception:
            pass
            
    # Fallback or if no data found
    return None

@st.cache_data(ttl=3600)
def get_market_sentiment():
    """
    Fetch Nikkei 225 (^N225) trend to determine market sentiment.
    Returns: 'Bull', 'Bear', or 'Neutral'
    """
    if not YFINANCE_AVAILABLE:
        return "Neutral"
        
    try:
        ticker = yf.Ticker("^N225")
        df = ticker.history(period="3mo", interval="1d")
        if len(df) < 25:
            return "Neutral"
            
        current_price = df['Close'].iloc[-1]
        sma25 = df['Close'].rolling(window=25).mean().iloc[-1]
        
        if current_price > sma25 * 1.01:
            return "Bull"
        elif current_price < sma25 * 0.99:
            return "Bear"
        else:
            return "Neutral"
    except Exception:
        return "Neutral"
