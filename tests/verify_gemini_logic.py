import sys
import os
import time
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

def test_exponential_backoff_logic():
    print("--- Testing Exponential Backoff Logic ---")
    
    # Mocking the client and models
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Analysis result"
    
    # Simulate 429 error twice, then success
    mock_client.models.generate_content.side_effect = [
        Exception("Resource has been exhausted (e.g. check quota) - 429"),
        Exception("429 RESOURCE_EXHAUSTED"),
        mock_response
    ]
    
    from modules.llm import generate_gemini_analysis
    
    # Minimal data for analysis
    price_info = {'current_price': 1000, 'change_percent': 1.5}
    indicators = {'trend_desc': 'Up', 'sma_short': 1000, 'sma_mid': 950, 'sma_long': 900, 'rsi': 55, 'atr': 20}
    credit_data = {'details': {'market_cap': 100000000}}
    strategic_data = {'entry_price': 1000, 'target_price': 1100, 'stop_loss': 950}
    weekly_indicators = {'trend_desc': 'Up', 'sma_short': 900, 'sma_mid': 850, 'sma_long': 800}
    
    with patch('modules.llm.get_gemini_client', return_value=mock_client), \
         patch('time.sleep', return_value=None) as mock_sleep:
        
        print("Calling generate_gemini_analysis...")
        result = generate_gemini_analysis("TEST", price_info, indicators, credit_data, strategic_data, weekly_indicators=weekly_indicators)
        
        print(f"Result: {result[:50]}...")
        
        # Verify retries and backoff
        assert mock_client.models.generate_content.call_count == 3
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(2) # 2^0 * 2
        mock_sleep.assert_any_call(4) # 2^1 * 2
        
        print("LOGIC TEST PASSED!")

if __name__ == "__main__":
    try:
        test_exponential_backoff_logic()
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
