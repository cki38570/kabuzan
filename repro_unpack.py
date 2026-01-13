import pandas as pd
import sys
import os

# Mock dependencies to avoid network/cache issues
from unittest.mock import MagicMock
sys.modules['diskcache'] = MagicMock()
sys.modules['yfinance'] = MagicMock()
sys.modules['pandas_ta'] = MagicMock()

# Import DataManager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.data_manager import DataManager

def test_return_types():
    dm = DataManager()
    
    # Create a dummy DataFrame
    df = pd.DataFrame({
        'Open': [100.0] * 20,
        'High': [105.0] * 20,
        'Low': [95.0] * 20,
        'Close': [102.0] * 20,
        'Volume': [1000] * 20
    })
    
    print("Testing get_technical_indicators with valid DF...")
    res = dm.get_technical_indicators(df)
    print(f"Return type: {type(res)}")
    print(f"Return length: {len(res)}")
    
    # Unpack as in app.py
    try:
        indicators, out_df, *_ = dm.get_technical_indicators(df)
        print(f"Unpacked indicators type: {type(indicators)}")
        print(f"Unpacked out_df type: {type(out_df)}")
        if not out_df.empty:
            print("out_df.empty check passed")
    except Exception as e:
        print(f"Unpacking failed: {e}")

    print("\nTesting get_technical_indicators with EMPTY DF...")
    empty_df = pd.DataFrame()
    res_empty = dm.get_technical_indicators(empty_df)
    print(f"Return type (empty): {type(res_empty)}")
    print(f"Return value (empty): {res_empty}")
    
    try:
        indicators, out_df, *_ = dm.get_technical_indicators(empty_df)
        print(f"Unpacked out_df type (empty): {type(out_df)}")
        print(f"out_df is DataFrame: {isinstance(out_df, pd.DataFrame)}")
        # This is where it might fail if out_df is a string
        print(f"out_df.empty: {out_df.empty}")
    except Exception as e:
        print(f"Unpacking empty failed: {e}")

if __name__ == "__main__":
    test_return_types()
