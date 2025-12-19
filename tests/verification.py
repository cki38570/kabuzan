import sys
import os
# Add current directory to path
sys.path.append(os.getcwd())

print("--- 1. Testing Imports ---")
try:
    from modules.llm import GENAI_AVAILABLE, API_KEY
    print(f"GENAI_AVAILABLE: {GENAI_AVAILABLE}")
    print(f"API_KEY focus: {'Found' if API_KEY else 'Not Found'}")
except ImportError as e:
    print(f"FAILED to import modules.llm: {e}")
except Exception as e:
    print(f"Unexpected error in modules.llm: {e}")

try:
    import pandas as pd
    from modules.charts import create_main_chart
    print("modules.charts imported successfully.")
except ImportError as e:
    print(f"FAILED to import modules.charts: {e}")

print("\n--- 2. Testing Strategy Return (Downtrend) ---")
try:
    from modules.analysis import calculate_trading_strategy
    import pandas as pd
    import numpy as np
    
    # Mock DF with downtrend
    df = pd.DataFrame({
        'Close': [1000, 950, 900, 850, 800],
        'High': [1010, 960, 910, 860, 810],
        'Low': [990, 940, 890, 840, 790],
        'Open': [1000, 950, 900, 850, 800]
    })
    # Add dummy indicators
    df['SMA5'] = df['Close'].rolling(5).mean()
    df['SMA25'] = df['Close'] * 1.1 # Dummy SMA25 above price
    df['SMA75'] = df['Close'] * 1.2 # Dummy SMA75 above price
    df['BB_Upper'] = df['Close'] * 1.3
    df['BB_Lower'] = df['Close'] * 0.9
    df['ATR'] = 10
    
    strategy = calculate_trading_strategy(df)
    print(f"Downtrend Entry Price: {strategy.get('entry_price')}")
    print(f"Downtrend Target Price: {strategy.get('target_price')}")
    print(f"Downtrend Stop Loss: {strategy.get('stop_loss')}")
    
    if strategy.get('entry_price') is not None:
        print("✅ Entry point is now correctly returned in downtrend.")
    else:
        print("❌ Entry point is still None in downtrend.")
        
except Exception as e:
    print(f"Error testing strategy: {e}")

print("\n--- 3. Testing New Modules ---")
try:
    from modules.news import get_stock_news
    from modules.line import send_line_notification
    print("New modules imported successfully.")
except ImportError as e:
    print(f"FAILED to import new modules: {e}")

print("\nVerification Complete.")
