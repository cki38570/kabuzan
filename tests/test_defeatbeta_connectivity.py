
import sys
import os
import streamlit as st

# Mock streamlit secrets for the module if needed, or just set env var
# os.environ["HF_TOKEN"] = "st.secrets reference"

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.defeatbeta_client import get_client

def test_connection():
    env_token = os.environ.get("HF_TOKEN") or "NONE"
    print(f"Testing DefeatBeta Connection with Token: {env_token[:4]}...")
    
    client = get_client()
    
    # 1. Check basic connection
    print("\n1. Verifying Dataset Access...")
    if client.check_connection():
        print("   [SUCCESS] Connected to HuggingFace dataset.")
        try:
             # Check symbol format
             syms = client.con.execute(f"SELECT DISTINCT symbol FROM '{client.DATASET_URL}' WHERE symbol LIKE '7203%' LIMIT 5").fetchdf()
             print(f"   Toyota Symbols: {syms['symbol'].tolist()}")
        except:
             pass
    else:
        print("   [FAIL] Could not connect to dataset.")
        return

    # 2. Test Transcripts (Unique feature)
    ticker = "7203" # Toyota
    print(f"\n2. Fetching Transcripts for {ticker}...")
    df_transcripts = client.get_transcripts(ticker, limit=2)
    if not df_transcripts.empty:
        print(f"   [SUCCESS] Retrieved {len(df_transcripts)} transcripts.")
        print(f"   Latest: {df_transcripts.iloc[0]['year']} Q{df_transcripts.iloc[0]['quarter']} ({df_transcripts.iloc[0]['Date']})")
    else:
        print("   [WARNING] No transcripts found (might be valid for this ticker or auth issue).")

    # 3. Test Stock History (Data backup)
    print(f"\n3. Fetching Stock History for {ticker}...")
    df_hist = client.get_stock_history(ticker, limit=5)
    if not df_hist.empty:
        print(f"   [SUCCESS] Retrieved history. Latest close: {df_hist.iloc[-1]['Close']}")
    else:
        print("   [FAIL] No history data found.")

if __name__ == "__main__":
    test_connection()
