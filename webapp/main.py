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

# Import DataManager
from modules.data_manager import get_data_manager

@app.get("/components/stock-card/{ticker}")
async def get_stock_card(request: Request, ticker: str):
    """
    HTMX component: Returns just the HTML for a single stock card.
    Fetches LIVE data using the Hybrid DataManager.
    """
    dm = get_data_manager()
    
    # 1. Get Market Data (Price, Change)
    # yfinance (Primary) with Caching
    df, meta = dm.get_market_data(ticker)
    
    if not df.empty and meta:
        price = meta["current_price"]
        change = meta["change"]
        percent = meta["change_percent"]
        source_status = meta.get("status", "fresh")
    else:
        # Error state
        price = 0
        change = 0
        percent = 0
        source_status = "error"
    
    # 2. Get Technicals (Optional for Card, but good for tooltip/color coding)
    # techs = dm.get_technical_indicators(df)
    
    return templates.TemplateResponse("components/stock_card.html", {
        "request": request,
        "ticker": ticker,
        "price": price,
        "change": change,
        "percent": percent,
        "source_status": source_status
    })
