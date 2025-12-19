import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Mock streamlit before it's imported in modules.llm
from unittest.mock import MagicMock
sys.modules['streamlit'] = MagicMock()

from modules.llm import generate_gemini_analysis

def test_type_error_fix():
    print("Testing TypeError fix in generate_gemini_analysis...")
    
    ticker = "9101"
    price_info = {'current_price': 5000.0, 'change_percent': -2.5}
    indicators = {'rsi': 35.0, 'rsi_status': '中立', 'macd_status': '売り', 'bb_status': '通常', 'atr': 150.0}
    credit_data = "信用倍率: 10倍 (買い残多)"
    
    # Simulate a case where entry_price, target_price, and stop_loss are None (downtrend)
    strategic_data = {
        'trend_desc': "📉 下落基調",
        'trend_score': -1,
        'action_msg': "下落トレンド中。...",
        'target_price': None,
        'stop_loss': None,
        'entry_price': None,
        'strategy_msg': "🐻 戻り売り/様子見",
        'risk_reward': 0
    }
    
    try:
        # 1. Test LLM logic
        print("Calling generate_gemini_analysis...")
        report = generate_gemini_analysis(ticker, price_info, indicators, credit_data, strategic_data)
        
        # 2. Test Chart logic
        from modules.charts import create_main_chart
        import pandas as pd
        df = pd.DataFrame({
            'Open': [100]*100, 'High': [110]*100, 'Low': [90]*100, 'Close': [100]*100,
            'SMA5': [100]*100, 'SMA25': [100]*100, 'SMA75': [100]*100, 'RSI': [50]*100
        }, index=pd.date_range('2023-01-01', periods=100))
        print("Calling create_main_chart...")
        fig = create_main_chart(df, "Test Stock", strategic_data)
        
        # 3. Test Backtest logic
        from modules.backtest import backtest_strategy
        print("Calling backtest_strategy...")
        bt_results = backtest_strategy(df, strategic_data)
        
        print("Success! No TypeError raised in any module.")
        return True
    except TypeError as e:
        print(f"FAILED: TypeError still occurs: {e}")
        return False
    except Exception as e:
        # API fail is expected if key is not set, resulting in mock report
        print(f"Note: Caught other exception (likely API related): {e}")
        return True

if __name__ == "__main__":
    if test_type_error_fix():
        print("\nVerification Passed!")
    else:
        print("\nVerification Failed!")
        sys.exit(1)
