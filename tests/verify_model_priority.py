
import sys
import os
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

from modules.llm import generate_gemini_analysis

def test_gemini_2_5_priority():
    print("--- Testing Gemini 2.5 Priority ---")
    
    # Mocking the client and models
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Analysis result from Gemini 2.5"
    
    # When generate_content is called, we check the model name
    def side_effect(model, contents):
        print(f"DEBUG: gemini client called with model='{model}'")
        if model == 'gemini-2.5-flash':
            return mock_response
        else:
            raise Exception("Using fallback model")

    mock_client.models.generate_content.side_effect = side_effect
    
    # Data arguments
    price_info = {'current_price': 1000}
    
    # We need to mock get_gemini_client to return our mock_client
    # We also need to patch GENAI_AVAILABLE to be True in case likely not set without key
    with patch('modules.llm.get_gemini_client', return_value=mock_client), \
         patch('modules.llm.GENAI_AVAILABLE', True), \
         patch('modules.llm.GENAI_V1_AVAILABLE', True), \
         patch('modules.llm.API_KEY', 'dummy_key'):
        
        print("Calling generate_gemini_analysis...")
        # Just passing minimal required args
        result = generate_gemini_analysis("TEST", price_info, {}, {}, {}, {})
        
        print(f"Result: {result[:50]}...")
        
        # Verify that gemini-2.5-flash was called
        # We know it was called if we got "Analysis result from Gemini 2.5"
        if "Analysis result from Gemini 2.5" in result:
             print("SUCCESS: Gemini 2.5 Flash was used.")
        else:
             print("FAILURE: Gemini 2.5 Flash was NOT used or failed.")

if __name__ == "__main__":
    test_gemini_2_5_priority()
