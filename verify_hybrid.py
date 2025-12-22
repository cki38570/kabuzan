import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_manager import get_data_manager
import pandas as pd

def test_data_manager():
    print("--- Starting Hybrid Data Manager Verification ---")
    dm = get_data_manager()
    
    ticker = "7203" # Toyota
    print(f"\n1. Testing Market Data Fetch for {ticker}...")
    df, meta = dm.get_market_data(ticker)
    
    if not df.empty:
        print(f"[OK] DataFrame received. Shape: {df.shape}")
        print(f"[OK] Metadata: {meta}")
    else:
        print("[FAIL] No data received.")
        
    print(f"\n2. Testing Technical Indicators Calculation...")
    techs = dm.get_technical_indicators(df)
    if techs:
        print(f"[OK] Technicals calculated: {list(techs.keys())[:5]}...")
        print(f"    RSI: {techs.get('rsi')}")
        print(f"    MACD Status: {techs.get('macd_status')}")
    else:
        print("[FAIL] Technical calculation failed.")
        
    print(f"\n3. Testing Financial Data Fallback...")
    # This should fallback to yfinance as defeatbeta is mocked to fail/empty currently
    fin_data = dm.get_financial_data(ticker)
    print(f"    Source: {fin_data.get('source')}")
    print(f"    Status: {fin_data.get('status')}")
    print(f"    Details: {fin_data.get('details')}")
    
    if fin_data.get('source') == 'yfinance_fallback':
         print("[OK] Fallback logic working correctly.")
    else:
         print("[WARN] unexpected source.")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    test_data_manager()
