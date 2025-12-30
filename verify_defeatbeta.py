
import os
import sys
import pandas as pd
import duckdb

# Add path to find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.defeatbeta_client import get_client

def test_defeatbeta():
    print("--- Starting DefeatBeta Verification ---")
    
    # 1. Initialize Client
    try:
        client = get_client(token=None)
        print("✅ Client initialized.")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return

    # 2. Check Connection & Debug Symbols
    print("\nChecking connection and sampling symbols...")
    try:
        # Sample symbols to see format (e.g., 'AAPL', '7203.T', 'JP:7203')
        query = f"SELECT DISTINCT symbol FROM '{client.DATASET_URL}' LIMIT 10"
        symbols = client.con.execute(query).fetchdf()
        print(f"✅ Connection Successful. Sample symbols:\n{symbols}")
    except Exception as e:
        print(f"❌ Connection/Query failed: {e}")
        return

    # 3. Fetch Stock History (7203.T)
    ticker = "7203"
    print(f"\nFetching history for {ticker}...")
    df = client.get_stock_history(ticker, limit=5)
    
    if not df.empty:
        print(f"✅ History Data Fetched ({len(df)} rows):")
        print(df.head())
    else:
        print("❌ History fetch returned empty.")

    # 4. Fetch Transcripts
    print(f"\nFetching transcripts for {ticker}...")
    transcripts = client.get_transcripts(ticker, limit=1)
    
    if not transcripts.empty:
        print(f"✅ Transcripts Fetched ({len(transcripts)} rows):")
        print(transcripts[['quarter', 'year', 'Date']])
    else:
        print("❌ Transcripts fetch returned empty (This might be normal if no data for ticker).")

    print("\n--- Verification Finished ---")

if __name__ == "__main__":
    test_defeatbeta()
