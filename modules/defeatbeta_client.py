import duckdb
import pandas as pd
import requests
import os
from typing import Optional, Dict, Any, Union
import streamlit as st

class DefeatBetaClient:
    """
    Custom client to fetch stock data from HuggingFace dataset using DuckDB.
    Replaces the broken defeatbeta-api library.
    """
    
    DATASET_URL = "https://huggingface.co/datasets/bwzheng2010/yahoo-finance-data/resolve/main/data/stock_prices.parquet"
    TRANSCRIPTS_URL = "https://huggingface.co/datasets/bwzheng2010/yahoo-finance-data/resolve/main/data/stock_earning_call_transcripts.parquet"
    
    def __init__(self, token: Optional[str] = None):
        # Allow token injection, otherwise check env var or Streamlit secrets
        self.token = token or os.environ.get("HF_TOKEN")
        if not self.token and hasattr(st, "secrets"):
            try:
                self.token = st.secrets["HF_TOKEN"]
            except KeyError:
                pass
                
        if not self.token:
            print("WARNING: No HuggingFace token provided. Public access might be restricted.")
            
        self.con = duckdb.connect(database=':memory:')
        
        # Configure DuckDB for HTTP access
        try:
            self.con.execute("INSTALL httpfs;") 
            self.con.execute("LOAD httpfs;")
        except Exception as e:
            print(f"Warning loading httpfs: {e}")
        
        if self.token:
            # Simple and robust way for all versions
            try:
                self.con.execute(f"SET http_headers = {{'Authorization': 'Bearer {self.token}'}};")
            except Exception as e:
                print(f"Warning: Could not set http_headers: {e}")

    def get_stock_history(self, ticker_code: str, limit: int = 365) -> pd.DataFrame:
        """
        Fetch historical stock data for a given ticker.
        Returns a DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        if not ticker_code.endswith(".T"):
            ticker_code = f"{ticker_code}.T"
            
        try:
            # Direct SQL query on the remote parquet file
            # This is much faster than downloading the whole file
            query = f"""
                SELECT 
                    report_date as Date, 
                    open as Open, 
                    high as High, 
                    low as Low, 
                    close as Close, 
                    volume as Volume 
                FROM '{self.DATASET_URL}' 
                WHERE symbol = '{ticker_code}'
                ORDER BY report_date DESC
                LIMIT {limit}
            """
            
            df = self.con.execute(query).fetchdf()
            
            if df.empty:
                print(f"No data found for {ticker_code}")
                return pd.DataFrame()
                
            # Sort by Date ascending for typical charting use
            df = df.sort_values('Date')
            
            # Ensure Date is datetime
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching data via DuckDB: {e}")
            return pd.DataFrame()

    def check_connection(self) -> bool:
        """Verify connection to the dataset."""
        try:
            query = f"SELECT count(*) FROM '{self.DATASET_URL}' LIMIT 1"
            res = self.con.execute(query).fetchone()
            return True
        except Exception as e:
            print(f"Connection check failed: {e}")
            return False

    def get_transcripts(self, ticker_code: str, limit: int = 5) -> pd.DataFrame:
        """
        Fetch earnings call transcripts for a given ticker.
        """
        if not ticker_code.endswith(".T"):
            ticker_code = f"{ticker_code}.T"
            
        try:
            query = f"""
                SELECT 
                    symbol,
                    fiscal_quarter as quarter,
                    fiscal_year as year,
                    report_date as Date,
                    transcripts as Content
                FROM '{self.TRANSCRIPTS_URL}' 
                WHERE symbol = '{ticker_code}'
                ORDER BY report_date DESC
                LIMIT {limit}
            """
            
            df = self.con.execute(query).fetchdf()
            return df
            
        except Exception as e:
            print(f"Error fetching transcripts: {e}")
            return pd.DataFrame()

# Singleton instance for easy import if needed, though dependency injection is better
_client_instance = None

def get_client(token: Optional[str] = None):
    global _client_instance
    if _client_instance is None:
        _client_instance = DefeatBetaClient(token=token)
    return _client_instance
