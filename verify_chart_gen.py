import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.charts import create_lightweight_chart

def verify_chart_html():
    print("Verifying Chart HTML Generation...")
    
    # 1. Create Mock Data
    dates = pd.date_range(start='2024-01-01', periods=10)
    data = {
        'Open': np.random.rand(10) * 100,
        'High': np.random.rand(10) * 100 + 10,
        'Low': np.random.rand(10) * 100 - 10,
        'Close': np.random.rand(10) * 100,
        'Volume': np.random.randint(100, 1000, 10),
        'SMA_5': np.random.rand(10) * 100,
        'BBU_20_2.0': np.random.rand(10) * 100 + 20,
        'BBL_20_2.0': np.random.rand(10) * 100 - 20,
        'PSARl_0.02_0.2': np.random.rand(10) * 100 # Mock PSAR column
    }
    df = pd.DataFrame(data, index=dates)
    
    # Introduce NaN to test handling
    df.loc[df.index[5], 'SMA_5'] = np.nan
    
    try:
        # 2. Generate Chart HTML
        html = create_lightweight_chart(df, "Test Ticker", interval="1d")
        
        # 3. Assertions
        if not isinstance(html, str):
            print("❌ Error: Output is not a string (HTML).")
            return False
            
        if "<script>" not in html:
            print("❌ Error: HTML does not contain script tag.")
            return False
            
        if "null" not in html and "NaN" in html:
             print("❌ Error: NaN found in HTML, should be null.")
             # print(html) # Debug
             return False

        if "SMA_5" in html: # Should be part of the logic, checking for presence of data might be tricky without parsing
            # Simple check if the color for SMA (yellow) is there or the text
            pass

        print("✅ Chart HTML generated successfully.")
        print(f"Length: {len(html)} chars")
        return True
        
    except Exception as e:
        print(f"❌ Exception during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_chart_html()
