import sys
import os
import pandas as pd
import numpy as np

# Add current directory to path
sys.path.append(os.getcwd())

print("--- 1. Testing Integrity & Consistency in analysis.py ---")
try:
    from modules.analysis import calculate_trading_strategy
    
    # CASE: Strong Downtrend (Should NOT suggest normal Buy)
    df_bear = pd.DataFrame({
        'Close': [1000, 950, 900, 850, 800],
        'High': [1010, 960, 910, 860, 810],
        'Low': [990, 940, 890, 840, 790],
        'Open': [1000, 950, 900, 850, 800],
        'Volume': [100, 100, 100, 100, 100]
    })
    df_bear['SMA5'] = df_bear['Close'].rolling(5).mean()
    df_bear['SMA25'] = df_bear['Close'] + 100 # Definitely above
    df_bear['SMA75'] = df_bear['Close'] + 200 # Definitely above
    df_bear['BB_Upper'] = df_bear['Close'] + 50
    df_bear['BB_Lower'] = df_bear['Close'] - 50
    df_bear['ATR'] = 10
    
    strategy = calculate_trading_strategy(df_bear)
    print(f"Strategy for Downtrend: {strategy['strategy_msg']}")
    if "様子見" in strategy['strategy_msg'] or "戻り売り" in strategy['strategy_msg']:
        print("✅ Algorithmic strategy correctly identifies Downtrend Caution.")
    else:
        print("❌ Algorithmic strategy failed to identify Downtrend Caution.")

except Exception as e:
    print(f"Error in Integrity Test: {e}")

print("\n--- 2. Checking llm.py Exports ---")
try:
    from modules.llm import GENAI_AVAILABLE, API_KEY
    print(f"GENAI_AVAILABLE: {GENAI_AVAILABLE}")
    print(f"API_KEY: {'Present' if API_KEY else 'Missing'}")
    print("✅ modules.llm exports are healthy.")
except ImportError as e:
    print(f"❌ ImportError in modules.llm: {e}")

print("\n--- 3. Checking for NameError in charts.py (Previous Fix) ---")
try:
    from modules.charts import create_main_chart
    # Dry run with dummy data
    df_dummy = pd.DataFrame({'Open':[100], 'High':[110], 'Low':[90], 'Close':[105], 'RSI':[50], 'SMA5':[100]})
    df_dummy.index = [pd.Timestamp.now()]
    fig = create_main_chart(df_dummy, "Test Stock", strategic_data={'target_price': 120, 'stop_loss': 80, 'entry_price': 100})
    if fig:
        print("✅ charts.py is healthy and free of NameError: pd.")
except Exception as e:
    print(f"❌ charts.py Error: {e}")

print("\nVerification Complete.")
