import os
import sys

# Ensure we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.notifications import send_daily_report, process_morning_notifications
    from modules.line import send_line_message
    from modules.storage import storage
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

import traceback

def main():
    print("--- Starting Auto Monitor Bot (Debug Mode) ---")
    
    try:
        # Debug: Check Env Vars (Masked)
        token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
        print(f"LINE_TOKEN: {'Found' if token else 'Missing'} ({len(token) if token else 0} chars)")
        
        url = os.environ.get("SPREADSHEET_URL")
        print(f"SHEET_URL: {'Found' if url else 'Missing'}")
        
        key = os.environ.get("GCP_SERVICE_ACCOUNT_KEY")
        print(f"GCP_KEY: {'Found' if key else 'Missing'} ({len(key) if key else 0} chars)")
        
        import streamlit as st
        # --- MOCK STREAMLIT UI FUNCTIONS FOR HEADLESS MODE ---
        if not hasattr(st, 'session_state'):
            class MockSessionState(dict):
                def __getattr__(self, key):
                    try:
                        return self[key]
                    except KeyError:
                        raise AttributeError(key)
                def __setattr__(self, key, value):
                    self[key] = value
            st.session_state = MockSessionState()
        st.session_state.notify_line = True 
        
        class MockSpinner:
            def __init__(self, text): self.text = text
            def __enter__(self): print(f"[Spinner] {self.text}")
            def __exit__(self, exc_type, exc_val, exc_tb): pass

        st.spinner = MockSpinner
        st.toast = lambda x, **kwargs: print(f"[Toast] {x}")
        st.error = lambda x, **kwargs: print(f"[Error] {x}")
        st.warning = lambda x, **kwargs: print(f"[Warning] {x}")
        st.success = lambda x, **kwargs: print(f"[Success] {x}")
        st.markdown = lambda x, **kwargs: print(f"[Markdown] {x}")
        
        # Run report (Managed)
        process_morning_notifications()
        print("Daily check processed.")
        
    except Exception:
        print("!!! CRITICAL ERROR !!!")
        traceback.print_exc()
        sys.exit(1)

    print("--- Finished ---")

if __name__ == "__main__":
    main()
