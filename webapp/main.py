from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
import sys

# Add parent directory to path to import modules if needed (for later)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Kabuzan HTMX")

# Mount static files
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

# Templates
templates = Jinja2Templates(directory="webapp/templates")

# Mock data loader (will replace with real modules later)
def load_watchlist():
    try:
        with open("watchlist.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.get("/")
async def read_root(request: Request):
    watchlist = load_watchlist()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "watchlist": watchlist,
        "title": "Kabuzan | Watchlist"
    })

import yfinance as yf
from datetime import datetime, timedelta

# Simple in-memory cache: {ticker: (data, timestamp)}
# In production, use Redis or nicer caching
STOCK_CACHE = {}
CACHE_DURATION = 300 # 5 minutes

def get_real_stock_data(ticker_code: str):
    """Fetch real data from yfinance with caching."""
    if not ticker_code.endswith(".T") and ticker_code.isdigit():
        ticker_code = f"{ticker_code}.T"
        
    now = datetime.now()
    if ticker_code in STOCK_CACHE:
        data, timestamp = STOCK_CACHE[ticker_code]
        if (now - timestamp).total_seconds() < CACHE_DURATION:
            return data

    try:
        # Fetch data
        ticker = yf.Ticker(ticker_code)
        # Get 5 days to ensure we have previous close even on weekends/holidays
        hist = ticker.history(period="5d", interval="1d")
        
        if hist.empty:
            return None
            
        current_price = hist['Close'].iloc[-1]
        
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[-2]
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
        else:
            change = 0.0
            change_percent = 0.0
            
        result = {
            "price": int(current_price),
            "change": int(change),
            "percent": change_percent
        }
        
        STOCK_CACHE[ticker_code] = (result, now)
        return result
        
    except Exception as e:
        print(f"Error fetching {ticker_code}: {e}")
        return None

@app.get("/components/stock-card/{ticker}")
async def get_stock_card(request: Request, ticker: str):
    """
    HTMX component: Returns just the HTML for a single stock card.
    Fetches LIVE data from yfinance.
    """
    data = get_real_stock_data(ticker)
    
    if data:
        price = data["price"]
        change = data["change"]
        percent = data["percent"]
    else:
        # Fallback or error state
        price = 0
        change = 0
        percent = 0
    
    return templates.TemplateResponse("components/stock_card.html", {
        "request": request,
        "ticker": ticker,
        "price": price,
        "change": change,
        "percent": percent
    })
