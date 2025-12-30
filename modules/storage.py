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

# Try importing gspread for headless mode
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

WATCHLIST_FILE = "watchlist.json"
PORTFOLIO_FILE = "portfolio.json"

class StorageManager:
    """
    Manages data persistence via Google Sheets (Streamlit or Headless) or local JSON.
    """
    def __init__(self):
        self.use_gsheets = False
        self.conn = None
        self.mode = "local" # local, streamlit, headless
        
        # 1. Check for Streamlit Secrets (App Mode)
        if GSHEETS_AVAILABLE:
            try:
                # Naive check if we are in streamlit context/have secrets
                if hasattr(st, "secrets") and "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
                    self.conn = st.connection("gsheets", type=GSheetsConnection)
                    self.use_gsheets = True
                    self.mode = "streamlit"
                    # print("Using Google Sheets (Streamlit Mode).")
                    return
            except Exception as e:
                pass
        
        # 2. Check for Env Vars (Headless Mode / GitHub Actions)
        # We expect GCP_SERVICE_ACCOUNT_KEY (json string) and SPREADSHEET_URL/ID
        if GSPREAD_AVAILABLE:
            gcp_key_json = os.environ.get("GCP_SERVICE_ACCOUNT_KEY")
            sheet_url = os.environ.get("SPREADSHEET_URL")
            
            if gcp_key_json and sheet_url:
                try:
                    # Parse JSON string
                    # If it's a file path, load it. If json string, parse it.
                    if gcp_key_json.startswith("{"):
                        creds_dict = json.loads(gcp_key_json)
                    elif os.path.exists(gcp_key_json):
                        with open(gcp_key_json) as f:
                            creds_dict = json.load(f)
                    else:
                        raise ValueError("Invalid Key")
                        
                    scopes = [
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ]
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                    self.gc = gspread.authorize(creds)
                    self.sh = self.gc.open_by_url(sheet_url)
                    
                    self.use_gsheets = True
                    self.mode = "headless"
                    print("Using Google Sheets (Headless Mode).")
                    return
                except Exception as e:
                    print(f"Headless setup failed: {e}")

        print("Using local storage.")

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
            
    # --- Helper for GSpread ---
    def _read_ws_headless(self, ws_name):
        try:
            ws = self.sh.worksheet(ws_name)
            data = ws.get_all_records()
            return data
        except:
            return []

    def _update_ws_headless(self, ws_name, df):
        try:
            ws = self.sh.worksheet(ws_name)
            ws.clear()
            # gspread with pandas: set headers and data
            # set_with_dataframe is from gspread-dataframe package, but we might not have it.
            # Manual way:
            params = [df.columns.values.tolist()] + df.values.tolist()
            ws.update(params)
            return True
        except Exception as e:
            print(f"CRITICAL: Headless Google Sheets update error for {ws_name}: {e}")
            traceback.print_exc()
            return False

    def load_watchlist(self):
        if self.mode == "streamlit":
            try:
                df = self.conn.read(worksheet="watchlist", ttl=0)
                if df.empty: return []
                return df.to_dict('records')
            except: return []
        elif self.mode == "headless":
            return self._read_ws_headless("watchlist")
        else:
            return self._load_local(WATCHLIST_FILE)

    def save_watchlist(self, data):
        if self.mode == "streamlit":
            try:
                df = pd.DataFrame(data)
                self.conn.update(worksheet="watchlist", data=df)
                return True
            except: return False
        elif self.mode == "headless":
            return self._update_ws_headless("watchlist", pd.DataFrame(data))
        else:
            return self._save_local(WATCHLIST_FILE, data)

    def load_portfolio(self):
        if self.mode == "streamlit":
            try:
                df = self.conn.read(worksheet="portfolio", ttl=0)
                if df.empty: return []
                return df.to_dict('records')
            except: return []
        elif self.mode == "headless":
            return self._read_ws_headless("portfolio")
        else:
            return self._load_local(PORTFOLIO_FILE)

    def save_portfolio(self, data):
        if self.mode == "streamlit":
            try:
                df = pd.DataFrame(data)
                self.conn.update(worksheet="portfolio", data=df)
                return True
            except: return False
        elif self.mode == "headless":
            return self._update_ws_headless("portfolio", pd.DataFrame(data))
        else:
            return self._save_local(PORTFOLIO_FILE, data)

    def load_alerts(self):
        filename = "alerts.json"
        if self.mode == "streamlit":
            try:
                df = self.conn.read(worksheet="alerts", ttl=0)
                if df.empty: return []
                return df.to_dict('records')
            except: return []
        elif self.mode == "headless":
            return self._read_ws_headless("alerts")
        else:
            return self._load_local(filename)

    def save_alerts(self, data):
        filename = "alerts.json"
        if self.mode == "streamlit":
            try:
                df = pd.DataFrame(data)
                self.conn.update(worksheet="alerts", data=df)
                return True
            except: return False
        elif self.mode == "headless":
            return self._update_ws_headless("alerts", pd.DataFrame(data))
        else:
            return self._save_local(filename, data)

    def load_settings(self):
        filename = "settings.json"
        defaults = {"profit_target": 10.0, "stop_loss_limit": -5.0}
        
        # Helper to parse list of dicts to dict
        def parse_kv(records):
            s = defaults.copy()
            for rec in records:
                k = rec['key']
                v = rec['value']
                
                # Handle common boolean strings from GSheets/CSV
                if isinstance(v, str):
                    if v.upper() == 'TRUE': v = True
                    elif v.upper() == 'FALSE': v = False
                
                # Handle GSheets auto-detected date objects if they occur
                if hasattr(v, 'strftime'): # Likely a datetime/date object
                    v = v.strftime('%Y-%m-%d')

                try:
                    if isinstance(v, bool):
                        s[k] = v
                    else:
                        # Attempt to convert to float if it looks like a number
                        f_val = float(v)
                        # If it's a whole number, keep as float (consistency)
                        s[k] = f_val
                except (ValueError, TypeError):
                    # Keep as string or original type (e.g. for dates or titles)
                    s[k] = v
            return s

        if self.mode == "streamlit":
            try:
                df = self.conn.read(worksheet="settings", ttl=0)
                if df.empty: return defaults
                return parse_kv(df.to_dict('records'))
            except: return defaults
        elif self.mode == "headless":
            data = self._read_ws_headless("settings")
            return parse_kv(data)
        else:
            data = self._load_local(filename)
            return {**defaults, **data} if data else defaults

    def save_settings(self, settings_dict):
        filename = "settings.json"
        # CRITICAL: Convert all values to strings to prevent GSheets mixed-type errors
        data_list = [{"key": k, "value": str(v)} for k, v in settings_dict.items()]
        
        if self.mode == "streamlit":
            try:
                df = pd.DataFrame(data_list)
                self.conn.update(worksheet="settings", data=df)
                return True
            except: return False
        elif self.mode == "headless":
            return self._update_ws_headless("settings", pd.DataFrame(data_list))
        else:
            return self._save_local(filename, settings_dict)

# Singleton instance
storage = StorageManager()
