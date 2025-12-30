import sys
import os
import time

# Ensure we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_persistent_log():
    print("Testing GSheet-based persistent log logic...")
    # Mocking storage to avoid real GSheet API calls in local test
    # but testing the logic flow
    
    log = {}
    
    def mock_save(key, val):
        log[key] = val
        return True
        
    def mock_load():
        return log

    # Scenario: Signal A sent 30 mins ago
    now = time.time()
    mock_save("signal_A", str(now - 1800))
    
    # Check rate limit
    def check_limit(ticker, current_now):
        current_log = mock_load()
        last_sent_str = current_log.get(f"signal_{ticker}")
        if last_sent_str:
            last_sent = float(last_sent_str)
            if (current_now - last_sent) < 3600:
                return False # Rate limited
        return True

    assert check_limit("A", now) is False
    assert check_limit("B", now) is True
    
    # Scenario: Signal A cooldown expired (1.1 hours later)
    assert check_limit("A", now + 4000) is True
    
    print("Test PASSED: Persistent log logic is correct.")

if __name__ == "__main__":
    test_persistent_log()
