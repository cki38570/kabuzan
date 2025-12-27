import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# Try importing the connection, if fails (dev env without install), fallback to local
try:
    from streamlit_gsheets import GSheetsConnection
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

WATCHLIST_FILE = "watchlist.json"
PORTFOLIO_FILE = "portfolio.json"

class StorageManager:
    """
    Manages data persistence via Google Sheets or local JSON.
    """
    def __init__(self):
        self.use_gsheets = False
        self.conn = None
        
        # Check if secrets are available for simple validation
        if GSHEETS_AVAILABLE and "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            try:
                self.conn = st.connection("gsheets", type=GSheetsConnection)
                self.use_gsheets = True
                print("Using Google Sheets for storage.")
            except Exception as e:
                print(f"Failed to connect to Google Sheets: {e}. Falling back to local.")
        else:
            print("Google Sheets credentials not found. Using local storage.")

    def _load_local(self, filename):
        if not os.path.exists(filename):
            return []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def _save_local(self, filename, data):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving local: {e}")
            return False

    def load_watchlist(self):
        if self.use_gsheets:
            try:
                # Expecting a worksheet named 'watchlist'
                # If it doesn't exist or is empty, handle gracefully
                df = self.conn.read(worksheet="watchlist", ttl=0)
                if df.empty:
                    return []
                return df.to_dict('records')
            except Exception as e:
                print(f"GSheets load error (watchlist): {e}")
                # If error (e.g. worksheet missing), try creating empty or fallback
                return []
        else:
            return self._load_local(WATCHLIST_FILE)

    def save_watchlist(self, data):
        # data is list of dicts
        if self.use_gsheets:
            try:
                df = pd.DataFrame(data)
                self.conn.update(worksheet="watchlist", data=df)
                return True
            except Exception as e:
                print(f"GSheets save error (watchlist): {e}")
                return False
        else:
            return self._save_local(WATCHLIST_FILE, data)

    def load_portfolio(self):
        if self.use_gsheets:
            try:
                df = self.conn.read(worksheet="portfolio", ttl=0)
                if df.empty:
                    return []
                # Convert numeric types if needed, though read usually handles it
                return df.to_dict('records')
            except Exception as e:
                print(f"GSheets load error (portfolio): {e}")
                return []
        else:
            return self._load_local(PORTFOLIO_FILE)

    def save_portfolio(self, data):
        if self.use_gsheets:
            try:
                df = pd.DataFrame(data)
                # Ensure all columns are present to avoid schema issues if possible
                self.conn.update(worksheet="portfolio", data=df)
                return True
            except Exception as e:
                print(f"GSheets save error (portfolio): {e}")
                return False
        else:
            return self._save_local(PORTFOLIO_FILE, data)

# Singleton instance
storage = StorageManager()
