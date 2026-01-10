import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.analysis import calculate_indicators

def verify_analysis():
    print("Verifying Analysis Columns...")
    
    # 1. Create Mock Data
    dates = pd.date_range(start='2024-01-01', periods=100)
    data = {
        'Open': np.random.rand(100) * 100,
        'High': np.random.rand(100) * 100 + 10,
        'Low': np.random.rand(100) * 100 - 10,
        'Close': np.random.rand(100) * 100,
        'Volume': np.random.randint(100, 1000, 100)
    }
    df = pd.DataFrame(data, index=dates)
    
    try:
        # 2. Calculate Indicators
        df = calculate_indicators(df, interval="1d")
        
        # 3. Check Columns
        print("--- Columns ---")
        for c in sorted(df.columns):
            print(c)
        print("----------------")
        
        required = ['SMA_5', 'RSI_14']
        # Check BBU loosely
        bbu_cols = [c for c in df.columns if 'BBU' in c]
        if bbu_cols:
             print(f"✅ Found BBU columns: {bbu_cols}")
        else:
             print("❌ No BBU columns found!")

        psar_cols = [c for c in df.columns if c.startswith('PSAR')]
            
        if psar_cols:
            print(f"✅ PSAR columns found: {psar_cols}")
        else:
            print("❌ PSAR columns missing.")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_analysis()
