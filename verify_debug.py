import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run():
    try:
        print("Importing modules...")
        import streamlit as st
        
        # Mock Session State FIRST
        if not hasattr(st, 'session_state'):
            class MockSession(dict):
                def __getattr__(self, key): return self.get(key)
                def __setattr__(self, key, val): self[key] = val
            st.session_state = MockSession()
        
        # Mock Secrets if needed (empty dict)
        if not hasattr(st, 'secrets'):
            st.secrets = {}

        from modules.notifications import process_morning_notifications
        
        print("Running process_morning_notifications...")
        process_morning_notifications()
        print("Done.")
        
    except Exception:
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print("Error occurred. Check error_log.txt")

if __name__ == "__main__":
    run()
