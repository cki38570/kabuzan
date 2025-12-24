
import requests
import json
import sys

# Provided API KEY (normally load from secrets, but using directly for this specific test as provided by user)
API_KEY = "4Xee6GBSKSrERfIEgvUxt8bYfJ3BNFtW"

def test_fmp_symbol(symbol_base, suffix_label, suffix):
    ticker = f"{symbol_base}{suffix}"
    print(f"\n--- Testing Ticker: {ticker} ({suffix_label}) ---")
    
    endpoints = {
        "Profile": f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={API_KEY}",
        "Quote": f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={API_KEY}",
        "Historical": f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={API_KEY}"
    }
    
    for name, url in endpoints.items():
        try:
            print(f"  > Fetching {name}...")
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if not data:
                    print(f"    [EMPTY] 200 OK but empty list/dict.")
                elif isinstance(data, dict) and 'Error Message' in data:
                     print(f"    [ERROR] {data['Error Message']}")
                else:
                    snippet = str(data)[:100]
                    print(f"    [SUCCESS] Found data. Node type: {type(data)} | {snippet}...")
            elif resp.status_code == 403:
                print(f"    [FORBIDDEN] 403 (Likely Premium Only)")
            else:
                print(f"    [FAIL] Status: {resp.status_code}")
        except Exception as e:
            print(f"    [EXCEPTION] {e}")

if __name__ == "__main__":
    base = "7203"
    variations = {
        "No Suffix": "",
        ".T (yfinance style)": ".T",
        ".TSE": ".TSE",
        ":JP": ":JP",
        "TYO: (Google style)": "TYO:"
    }
    
    print(f"Testing FMP Connectivity with Key: {API_KEY[:4]}...")
    
    for label, suffix in variations.items():
        # Handle prefix case like TYO:7203
        if suffix.endswith(":"):
            # Skip for now, FMP usually uses suffix
            continue
        else:
            test_fmp_symbol(base, label, suffix)

