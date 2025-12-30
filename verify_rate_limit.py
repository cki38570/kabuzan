
import streamlit as st
import time
import shutil
import os

# Mock secrets and session state
st.secrets = {"LINE_CHANNEL_ACCESS_TOKEN": "mock_token"}
st.session_state.notify_line = True

# Mock st.toast
if not hasattr(st, 'toast'):
    st.toast = lambda x, icon=None: print(f"🍞 Toast: {x}")

# Clean cache before start
if os.path.exists('./.cache_notifications'):
    shutil.rmtree('./.cache_notifications')

from modules.notifications import check_technical_signals

# Mock indicators (Strong Buy Signal)
indicators = {
    'rsi': 20, # Oversold -> Signal
    'bb_lower': 1000,
    'bb_upper': 1200,
    'bb_mid': 1100
}

print("--- Test 1: First Call (Should Send) ---")
# Mock send_line_message in modules.notifications by monkeypatching?
# Or just rely on print in send_line_message if I mock that module.
# Let's mock the internal function.
import modules.notifications
original_send = modules.notifications.send_line_message

def mock_send(msg, payload_messages=None):
    print(f"📨 SENDING LINE: {msg[:50]}...")
    return True, "OK"

modules.notifications.send_line_message = mock_send

# Call 1
check_technical_signals("TEST", 900, indicators, "Test Stock")

print("\n--- Test 2: Immediate Second Call (Should BLOCK) ---")
check_technical_signals("TEST", 900, indicators, "Test Stock")

print("\n--- Test 3: Different Ticker (Should Send) ---")
check_technical_signals("TEST2", 900, indicators, "Test Stock 2")

print("\n--- Test Finished ---")
modules.notifications.send_line_message = original_send
