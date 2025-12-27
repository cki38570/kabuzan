import os
import sys

# Ensure we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.notifications import send_daily_report
    from modules.line import send_line_message
    from modules.storage import storage
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def main():
    print("--- Starting Auto Monitor Bot ---")
    
    # 1. Check Credentials
    line_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not line_token:
        print("Error: LINE_CHANNEL_ACCESS_TOKEN not found in environment.")
        return

    # 2. Check Storage Connection
    if storage.mode == "local":
        print("Warning: Running in LOCAL storage mode. This might not be intended for GitHub Actions unless you committed json files.")
        # If we are in Actions, we expect 'headless' mode (gspread) usually.
        # But if user forgot SPREADSHEET_URL, it falls back to local.
    else:
        print(f"Storage Mode: {storage.mode}")

    # 3. Execute Report & Checks
    # We trigger the same logic as "Manual Report Send" but automated
    print("Generating report...")
    try:
        # Hack: The original function checks st.session_state.get('notify_line')
        # In this script, we don't have a real session state.
        # However, modules/notifications.py imports 'send_line_message' from 'modules.line'.
        # We need to bypass the 'if not notify_line' check in send_daily_report?
        # Actually send_daily_report checks `st.session_state`.
        # Since this is a specialized script, we should probably refactor send_daily_report to be cleaner,
        # OR we just mock st.session_state.
        
        import streamlit as st
        if not hasattr(st, 'session_state'):
            st.session_state = {}
            
        # Mock session state to enable notifications
        st.session_state['notify_line'] = True 
        
        # Run report
        send_daily_report(manual=True)
        print("Report generation triggered.")
        
    except Exception as e:
        print(f"Error during reporting: {e}")
        # Send error notification to clear confusion
        send_line_message(f"⚠️ 自動監視ボットのエラー: {e}")

    print("--- Finished ---")

if __name__ == "__main__":
    main()
