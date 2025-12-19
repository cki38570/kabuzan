import json
import os
import pandas as pd
from datetime import datetime

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    """Load portfolio from local JSON file."""
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    try:
        with open(PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading portfolio: {e}")
        return []

def save_portfolio(portfolio_data):
    """Save portfolio to local JSON file."""
    try:
        with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
            json.dump(portfolio_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving portfolio: {e}")
        return False

def add_to_portfolio(code, name, quantity, avg_price):
    """Add or update a stock position in the portfolio."""
    portfolio = load_portfolio()
    
    # Check if exists, update if so
    found = False
    for item in portfolio:
        if item['code'] == code:
            # Simple weighted average for multiple buys could be implemented here
            # For now, we overwrite or update quantity
            # Let's say we update quantity and average price
            total_cost_old = item['quantity'] * item['avg_price']
            total_cost_new = quantity * avg_price
            new_qty = item['quantity'] + quantity
            new_avg = (total_cost_old + total_cost_new) / new_qty
            
            item['quantity'] = new_qty
            item['avg_price'] = new_avg
            item['name'] = name # Update name just in case
            found = True
            break
    
    if not found:
        portfolio.append({
            'code': code,
            'name': name,
            'quantity': quantity,
            'avg_price': avg_price,
            'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    save_portfolio(portfolio)

def remove_from_portfolio(code):
    """Remove a stock from the portfolio."""
    portfolio = load_portfolio()
    portfolio = [p for p in portfolio if p['code'] != code]
    save_portfolio(portfolio)

def get_portfolio_df(current_prices):
    """
    Calculate portfolio performance.
    current_prices: dict {code: price}
    """
    portfolio = load_portfolio()
    if not portfolio:
        return pd.DataFrame(), 0, 0
    
    rows = []
    total_invested = 0
    total_value = 0
    
    for item in portfolio:
        code = item['code']
        qty = item['quantity']
        avg = item['avg_price']
        current = current_prices.get(code, avg) # Fallback to avg if price not found
        
        invested = qty * avg
        value = qty * current
        profit = value - invested
        profit_pct = (profit / invested) * 100 if invested > 0 else 0
        
        total_invested += invested
        total_value += value
        
        rows.append({
            '銘柄名': item['name'],
            'コード': code,
            '保有株数': qty,
            '平均取得単価': avg,
            '現在値': current,
            '取得額': invested,
            '評価額': value,
            '損益': profit,
            '損益率': profit_pct
        })
        
    df = pd.DataFrame(rows)
    return df, total_invested, total_value

def get_portfolio_data():
    """Returns a simple list of portfolio items for news analysis."""
    portfolio = load_portfolio()
    return [{'ticker': p['code'], 'name': p['name'], 'shares': p['quantity']} for p in portfolio]
