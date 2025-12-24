import sys
import os
import streamlit as st

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_manager import get_data_manager
from modules.llm import generate_gemini_analysis
import json
import re

def test_real_gemini_analysis():
    print("--- Testing Real Gemini Analysis with New Prompt ---")
    dm = get_data_manager()
    ticker = "7203"
    df, info = dm.get_market_data(ticker)
    indicators = dm.get_technical_indicators(df)
    df_weekly, _ = dm.get_market_data(ticker, interval="1wk")
    weekly_indicators = dm.get_technical_indicators(df_weekly, interval="1wk")
    credit_data = dm.get_financial_data(ticker)
    
    # We use empty dicts for extras to keep it simple
    report_raw = generate_gemini_analysis(
        ticker, info, indicators, credit_data, 
        strategic_data={'entry_price': info['current_price']}, 
        weekly_indicators=weekly_indicators,
        enhanced_metrics={}, 
        patterns={}
    )
    
    print("\n[AI RAW REPORT RESPONSE]")
    print(report_raw)
    
    # Parse check
    try:
        json_match = re.search(r'```json\s*(.*?)\s*```', report_raw, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            data = json.loads(report_raw)
            
        print("\n✅ JSON Parsing SUCCESS.")
        print(f"Status: {data.get('status')}")
        setup = data.get('setup', {})
        print(f"Trade Plan: Entry={setup.get('entry_price')}, TP={setup.get('target_price')}, SL={setup.get('stop_loss')}")
        
        # Check for technical evidence
        reasoning = data.get('final_reasoning', '')
        if any(str(v) in reasoning for v in [indicators.get('rsi'), indicators.get('sma_mid')]):
             print("✅ Technical evidence presence verified in reasoning.")
        else:
             print("⚠️ Technical evidence (numerical) might be missing in reasoning, but check manually.")
             
    except Exception as e:
        print(f"\n❌ JSON Parsing FAILED: {e}")

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is required for this test.")
    else:
        test_real_gemini_analysis()
