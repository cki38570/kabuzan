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

def get_stock_data(ticker_code, period="1y", interval="1d"):
    """
    Fetch stock data from yfinance.
    Adds .T suffix if missing.
    Falls back to mock data if yfinance is unavailable.
    """
    if not str(ticker_code).endswith('.T'):
        ticker_code = f"{ticker_code}.T"
    
    if YFINANCE_AVAILABLE:
        try:
            ticker = yf.Ticker(ticker_code)
            df = ticker.history(period=period, interval=interval)
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
                    
                return df, {
                    'current_price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'name': info.get('longName', ticker_code)
                }
        except Exception as e:
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
