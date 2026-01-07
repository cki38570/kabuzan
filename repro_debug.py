import sys
import os
import pandas as pd
import json

# Add current directory to path
sys.path.append(os.getcwd())

from modules.data_manager import get_data_manager
from modules.analysis import calculate_indicators, calculate_trading_strategy

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        return super().default(obj)

def debug_ticker(ticker):
    print(f"\n=== Debugging {ticker} ===")
    dm = get_data_manager()
    
    # 1. Market Data
    df, info = dm.get_market_data(ticker)
    print(f"Market Data Info: {info}")
    if df.empty:
        print("Market Data DF is empty!")
    else:
        print(f"Market Data Rows: {len(df)}")
        
    # 2. Technical Indicators
    params = {'sma_short': 5, 'sma_mid': 25, 'sma_long': 75, 'rsi_period': 14, 'bb_window': 20}
    df_calc = calculate_indicators(df, params)
    print(f"Calculated Columns: {df_calc.columns.tolist()}")
    
    # 3. Strategic Data
    strategic_data = calculate_trading_strategy(df_calc)
    print(f"Strategic Data: {json.dumps(strategic_data, indent=2, ensure_ascii=False, cls=CustomEncoder)}")
    
    # 4. Financial Data
    fin_data = dm.get_financial_data(ticker)
    print(f"Financial Data Details: {json.dumps(fin_data.get('details', {}), indent=2, ensure_ascii=False, cls=CustomEncoder)}")

if __name__ == "__main__":
    debug_ticker("7203") # Toyota
    # debug_ticker("9984") # SoftBank
