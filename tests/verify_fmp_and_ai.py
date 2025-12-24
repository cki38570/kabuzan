import sys
import os
import pandas as pd
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_manager import get_data_manager
from modules.llm import generate_gemini_analysis

def verify_data_manager_fallback():
    print("--- Verifying DataManager Fallback ---")
    dm = get_data_manager()
    
    # Test with a known ticker
    ticker = "7203" # Toyota
    df, info = dm.get_market_data(ticker)
    
    print(f"Ticker: {ticker}")
    print(f"Data Source: {info.get('source')}")
    print(f"Status: {info.get('status')}")
    print(f"Current Price: {info.get('current_price')}")
    
    if not df.empty:
        print("✅ Market Data fetch SUCCESS.")
    else:
        print("❌ Market Data fetch FAILED.")

    financials = dm.get_financial_data(ticker)
    print(f"Financials Source: {financials.get('source')}")
    print(f"Financials Metadata: {financials.get('details').keys()}")
    
    if financials.get('details'):
        print("✅ Financial Data fetch SUCCESS.")
    else:
        print("❌ Financial Data fetch FAILED.")

def verify_llm_prompt_structure():
    print("\n--- Verifying AI Analysis Prompt Structure (Mocked) ---")
    
    # Mock data
    ticker = "7203"
    price_info = {'current_price': 2800.0, 'change_percent': 1.2, 'name': 'Toyota'}
    indicators = {'trend_desc': 'Strong Uptrend', 'sma_short': 2750, 'sma_mid': 2600, 'sma_long': 2400, 'rsi': 55, 'atr': 50}
    credit_data = {'details': {'market_cap': 30000000000000}}
    strategic_data = {'entry_price': 2780}
    weekly = {'trend_desc': 'Bullish'}
    
    with patch('modules.llm.get_gemini_client') as mock_client_init:
        mock_client = MagicMock()
        mock_client_init.return_value = mock_client
        
        # Simulate a structured JSON response from Gemini
        mock_response = MagicMock()
        mock_response.text = '```json\n{\n  "status": "BUY ENTRY",\n  "total_score": 85,\n  "conclusion": "テクニカル強気に加え、RSI 55と適度な過熱感で、更なる上昇が期待されます。",\n  "bull_view": "SMA25が2600円でサポートし、RSI 55から買い余力あり。",\n  "bear_view": "ATR 50からボラティリティ増大がリスク。",\n  "final_reasoning": "週足・日足ともに上昇トレンドで、押し目買いの好機。",\n  "setup": {\n    "entry_price": 2780,\n    "target_price": 2950,\n    "stop_loss": 2680,\n    "risk_reward": 1.7\n  },\n  "details": {\n    "technical_score": 50,\n    "sentiment_score": 35,\n    "sentiment_label": "ポジティブ",\n    "notes": "決算発表まで余裕あり。需給も良好。" \n  }\n}\n```'
        mock_client.models.generate_content.return_value = mock_response
        
        report = generate_gemini_analysis(ticker, price_info, indicators, credit_data, strategic_data, weekly_indicators=weekly, enhanced_metrics={}, patterns={})
        
        print("Generated Report (Simulated Content):")
        print(report)
        
        if '"status": "BUY ENTRY"' in report and '"setup":' in report:
            print("\n✅ AI Output structure verified.")
        else:
            print("\n❌ AI Output structure verification FAILED.")

if __name__ == "__main__":
    verify_data_manager_fallback()
    verify_llm_prompt_structure()
