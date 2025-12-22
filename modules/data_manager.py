import pandas as pd
import yfinance as yf
import pandas_ta as ta
from diskcache import Cache
import os
import datetime
import traceback
from typing import Dict, Any, Optional, Tuple

# Internal modules
try:
    from modules.defeatbeta_client import get_client as get_defeatbeta_client
except ImportError:
    # Handle case where module might be imported from a different context
    def get_defeatbeta_client(token=None): return None

# Initialize disk cache
# Use /tmp for Streamlit Cloud or local .cache
if os.environ.get('STREAMLIT_RUNTIME_ENV') == 'cloud' or os.path.exists('/mount/src'):
    CACHE_DIR = '/tmp/kabuzan_cache'
else:
    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.cache')

try:
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
    cache = Cache(CACHE_DIR, size_limit=1024 * 1024 * 1024)
except Exception as e:
    print(f"Warning: Could not initialize diskcache at {CACHE_DIR}: {e}")
    # Fallback to dummy cache interface if diskcache fails
    class DummyCache:
        def get(self, key): return None
        def set(self, key, value): pass
    cache = DummyCache()

class DataManager:
    """
    Central data manager for Kabuzan.
    Implements hybrid data sourcing (yfinance + defeatbeta) and caching.
    """
    
    def __init__(self):
        self.defeatbeta = get_defeatbeta_client() # Lazy load or init
        
    def get_market_data(self, ticker_code: str, period: str = "1y", interval: str = "1d") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fetch market data (price, charts) primarily from yfinance.
        Uses Caching to reduce API calls.
        """
        if not str(ticker_code).endswith('.T') and str(ticker_code).isdigit():
            ticker_code = f"{ticker_code}.T"
            
        cache_key = f"market_data_{ticker_code}_{period}_{interval}"
        
        # Check Cache
        cached_data = cache.get(cache_key)
        if cached_data:
            # Basic validation of cached data
            df, meta, timestamp = cached_data
            if (datetime.datetime.now() - timestamp).total_seconds() < 300: # 5 min cache for price
                return df, meta
                
        try:
            # 1. Fetch from yfinance
            ticker = yf.Ticker(ticker_code)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                print(f"yfinance returned empty data for {ticker_code}")
                return pd.DataFrame(), {}
                
            # 2. Get Metadata (Current Price, Change)
            # Try fast info first, then history fallback
            info = ticker.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or df['Close'].iloc[-1]
            name = info.get('longName', ticker_code)
            
            if len(df) >= 2:
                prev_close = df['Close'].iloc[-2]
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100
            else:
                change = 0.0
                change_percent = 0.0
                
            meta = {
                'current_price': current_price,
                'change': change,
                'change_percent': change_percent,
                'name': name,
                'source': 'yfinance',
                'status': 'fresh'
            }
            
            # 3. Store in Cache
            cache.set(cache_key, (df, meta, datetime.datetime.now()))
            
            return df, meta
            
        except Exception as e:
            print(f"Error in get_market_data for {ticker_code}: {e}")
            traceback.print_exc()
            return pd.DataFrame(), {'error': str(e)}

    def get_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate technical indicators using pandas-ta.
        """
        # Default empty structure
        results = {
            'rsi': 50.0, 'rsi_status': "Data Lack",
            'macd': 0.0, 'macd_signal': 0.0, 'macd_status': "Data Lack",
            'bb_upper': 0.0, 'bb_lower': 0.0, 'bb_width': 0.0, 'bb_status': "Data Lack",
            'sma25': 0.0, 'sma75': 0.0, 'atr': 0.0, 'trend_desc': "Insufficient Data"
        }

        if df.empty or len(df) < 10:
            return results
            
        try:
            # Ensure columns are properly named and lowercase for pandas_ta if needed, 
            # though pandas_ta handles CamelCase.
            calc_df = df.copy()
            
            # Validation: Check if required columns exist
            required = ['Open', 'High', 'Low', 'Close']
            if not all(col in calc_df.columns for col in required):
                print(f"Missing columns for technicals: {list(calc_df.columns)}")
                return results

            # 1. RSI (14)
            calc_df.ta.rsi(length=14, append=True)
            if 'RSI_14' in calc_df.columns:
                rsi_val = calc_df['RSI_14'].iloc[-1]
                results['rsi'] = rsi_val
                if rsi_val > 70: results['rsi_status'] = "Overbought (買われすぎ)"
                elif rsi_val < 30: results['rsi_status'] = "Oversold (売られすぎ)"
                else: results['rsi_status'] = "Neutral (中立)"
            
            # 2. MACD (12, 26, 9)
            calc_df.ta.macd(fast=12, slow=26, signal=9, append=True)
            if 'MACD_12_26_9' in calc_df.columns:
                results['macd'] = calc_df['MACD_12_26_9'].iloc[-1]
                results['macd_signal'] = calc_df['MACDs_12_26_9'].iloc[-1]
                if results['macd'] > results['macd_signal']: results['macd_status'] = "Bullish Cross (買い優勢)"
                else: results['macd_status'] = "Bearish Cross (売り優勢)"
            
            # 3. Bollinger Bands (20, 2)
            calc_df.ta.bbands(length=20, std=2, append=True)
            if 'BBU_20_2.0' in calc_df.columns:
                results['bb_upper'] = calc_df['BBU_20_2.0'].iloc[-1]
                results['bb_lower'] = calc_df['BBL_20_2.0'].iloc[-1]
                price = calc_df['Close'].iloc[-1]
                results['bb_width'] = ((results['bb_upper'] - results['bb_lower']) / price) * 100 if price else 0
                results['bb_status'] = "Expansion" if results['bb_width'] > 5 else "Squeeze" if results['bb_width'] < 2 else "Normal"
            
            # 4. Moving Averages (SMA 25, 75)
            calc_df.ta.sma(length=25, append=True)
            calc_df.ta.sma(length=75, append=True)
            
            if 'SMA_25' in calc_df.columns:
                results['sma25'] = calc_df['SMA_25'].iloc[-1]
                price = calc_df['Close'].iloc[-1]
                sma75 = calc_df['SMA_75'].iloc[-1] if 'SMA_75' in calc_df.columns else 0
                results['sma75'] = sma75
                
                if price > results['sma25'] and results['sma25'] > sma75 and sma75 > 0:
                    results['trend_desc'] = "Strong Uptrend (強い上昇)"
                elif price < results['sma25'] and results['sma25'] < sma75 and sma75 > 0:
                    results['trend_desc'] = "Strong Downtrend (強い下落)"
                elif price > results['sma25']:
                    results['trend_desc'] = "Moderate Uptrend (緩やかな上昇)"
                else:
                    results['trend_desc'] = "Moderate Downtrend (緩やかな下落/調整)"
            
            # 5. ATR (14)
            calc_df.ta.atr(length=14, append=True)
            if 'ATRr_14' in calc_df.columns:
                results['atr'] = calc_df['ATRr_14'].iloc[-1]
                
            return results
            
        except Exception as e:
            print(f"Error calculating technicals: {e}")
            return results

    def get_financial_data(self, ticker_code: str) -> Dict[str, Any]:
        """
        Fetch detailed financial data.
        Primary: DefeatBeta (Deep Data)
        Fallback: yfinance (Basic Data)
        """
        data = {
            'source': 'yfinance_fallback', 
            'status': 'partial',
            'details': {}
        }
        
        # Ticker formatting
        if not str(ticker_code).endswith('.T'):
            target_ticker = f"{ticker_code}.T"
        else:
            target_ticker = ticker_code
            
        # Try DefeatBeta first (Mocked implementation for now as we build the client)
        # Real integration would call: self.defeatbeta.get_financials(target_ticker)
        # Here we simulate the fallback logic which is the user's priority requirement.
        
        try:
            # Placeholder for DefeatBeta call
            # details = self.defeatbeta.get_financials(target_ticker)
            # if details: return {'source': 'defeatbeta', 'status': 'complete', 'details': details}
            pass 
        except Exception:
            # Silent fail for auxiliary source
            pass
            
        # Fallback to yfinance
        try:
            ticker = yf.Ticker(target_ticker)
            info = ticker.info
            
            # Extract key metrics available in basic yfinance
            data['details'] = {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'dividend_yield': info.get('dividendYield'),
                'roe': info.get('returnOnEquity'),
                'sector': info.get('sector'),
            }
        except Exception as e:
            print(f"Financial data fetch failed: {e}")
            
        return data

# Singleton entry point
_data_manager = None

def get_data_manager():
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager
