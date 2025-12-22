import sys
import os
from unittest.mock import MagicMock
import pandas as pd
import datetime

# Mock missing dependencies
mock_cache_lib = MagicMock()
mock_cache_instance = MagicMock()
mock_cache_instance.get.return_value = None # Force cache miss
mock_cache_lib.Cache.return_value = mock_cache_instance
sys.modules['diskcache'] = mock_cache_lib

sys.modules['yfinance'] = MagicMock()
sys.modules['pandas_ta'] = MagicMock()

# Import our code
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.data_manager import DataManager

def verify_logic_integrity():
    print("=== Logic Integrity Verification ===")
    dm = DataManager()
    
    # 1. Test get_market_data flow
    ticker = "7203"
    print(f"\n[1] Testing Market Data Flow: {ticker}")
    import yfinance as yf
    
    # Create a real-looking DataFrame for technicals to process
    dates = pd.date_range(start='2023-01-01', periods=100)
    mock_hist = pd.DataFrame({
        'Open': [100.0] * 100,
        'High': [105.0] * 100,
        'Low': [95.0] * 100,
        'Close': [102.0] * 100,
        'Volume': [1000] * 100
    }, index=dates)
    
    yf.Ticker.return_value.history.return_value = mock_hist
    yf.Ticker.return_value.info = {'currentPrice': 104, 'longName': 'Toyota'}
    
    df, meta = dm.get_market_data(ticker)
    
    if meta.get('name') == 'Toyota' and meta.get('current_price') == 104:
        print("[PASS] get_market_data logic correct (Mocked yf)")
    else:
        print("[FAIL] get_market_data metadata mismatch")

    # 2. Test Technical Calculation Flow Setup
    print("\n[2] Testing Technical Integration Setup")
    # DataManager.get_technical_indicators expects certain columns
    # Even if pandas_ta is mocked, we check if the code handles the dataframe correctly
    techs = dm.get_technical_indicators(mock_hist)
    # Result will be largely empty because pandas_ta is mocked and doesn't add cols
    # But it shouldn't crash.
    print(f"Technicals result keys: {list(techs.keys())}")
    
    # 3. Test Financial Fallback logic
    print("\n[3] Testing Financial Fallback logic")
    fin = dm.get_financial_data("7203")
    if fin['source'] == 'yfinance_fallback' and fin['status'] == 'partial':
        print("[PASS] Financial fallback logic triggered correctly")
    
    print("\n=== Integrity Check Complete ===")

if __name__ == "__main__":
    verify_logic_integrity()
