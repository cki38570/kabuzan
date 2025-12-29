import pandas as pd
import yfinance as yf
import pandas_ta as ta
from diskcache import Cache
import os
import datetime
import traceback
from typing import Dict, Any, Optional, Tuple
import random

# Internal modules
try:
    from modules.defeatbeta_client import get_client as get_defeatbeta_client
except ImportError:
    # Handle case where module might be imported from a different context
    def get_defeatbeta_client(token=None): return None

# Initialize disk cache
if os.environ.get('STREAMLIT_RUNTIME_ENV') == 'cloud' or os.path.exists('/mount/src'):
    CACHE_DIR = '/tmp/kabuzan_cache'
else:
    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.cache')

# FMP API Key
import requests
try:
    import streamlit as st
    FMP_API_KEY = st.secrets.get("FMP_API_KEY")
except:
    FMP_API_KEY = os.getenv("FMP_API_KEY")

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
        self.defeatbeta = get_defeatbeta_client() 
        self.fmp_key = FMP_API_KEY

    def _fetch_from_fmp(self, ticker_code: str, period: str = "1y", interval: str = "1d") -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
        """Helper to fetch data from Financial Modeling Prep (FMP)."""
        if not self.fmp_key:
            return None, None
            
        # FMP ticker format for Japan is often '7203:JP' (Google style) or '7203.TSE'
        clean_ticker = str(ticker_code).split('.')[0]
        
        # Try primary suffix (:JP) which is common for FMP
        fmp_ticker = f"{clean_ticker}.T" # Default fallback
        
        try:
            candidates = [f"{clean_ticker}.T", f"{clean_ticker}:JP", f"{clean_ticker}.TSE"]
            
            # Simple check for US tickers
            if ticker_code.isalpha():
                candidates = [ticker_code]

            response = None
            for cand in candidates:
                hist_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{cand}?apikey={self.fmp_key}"
                try:
                    res = requests.get(hist_url, timeout=5)
                    if res.status_code == 200:
                        response = res
                        fmp_ticker = cand # Update to working ticker
                        break
                    elif res.status_code == 403:
                        # Silently ignore 403 forbidden to reduce log spam
                        # print(f"FMP Free Tier limitation for {cand} (403 Forbidden)")
                        pass
                except:
                    continue
            
            if not response or response.status_code != 200:
                return None, None
                
            data = response.json()
            if not data or 'historical' not in data:
                return None, None
                
            df = pd.DataFrame(data['historical'])
            df['Date'] = pd.to_datetime(df['date'])
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            # Map FMP columns to yfinance-style
            df = df.rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low', 
                'close': 'Close', 'volume': 'Volume'
            })[['Open', 'High', 'Low', 'Close', 'Volume']]

            # 2. Real-time Quote
            quote_url = f"https://financialmodelingprep.com/api/v3/quote/{fmp_ticker}?apikey={self.fmp_key}"
            q_res = requests.get(quote_url, timeout=10)
            meta = {}
            if q_res.status_code == 200:
                q_data = q_res.json()
                if q_data:
                    q = q_data[0]
                    meta = {
                        'current_price': q.get('price'),
                        'change': q.get('change'),
                        'change_percent': q.get('changesPercentage'),
                        'name': q.get('name'),
                        'source': 'fmp',
                        'status': 'fresh'
                    }
            
            if not meta and not df.empty:
                # Fallback meta from historical
                last = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else last
                meta = {
                    'current_price': last['Close'],
                    'change': last['Close'] - prev['Close'],
                    'change_percent': ((last['Close'] - prev['Close']) / prev['Close'] * 100) if prev['Close'] else 0,
                    'name': fmp_ticker,
                    'source': 'fmp_historical',
                    'status': 'fresh'
                }
                
            return df, meta
        except Exception as e:
            # print(f"FMP fetch error: {e}")
            return None, None

    def _generate_mock_data(self, ticker_code: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate Mock Data when all APIs fail."""
        dates = pd.date_range(end=datetime.datetime.now(), periods=250, freq='B')
        base_price = 1000.0 + random.uniform(-200, 200)
        prices = [base_price]
        for _ in range(249):
            change = random.uniform(-0.02, 0.02)
            prices.append(prices[-1] * (1 + change))
            
        df = pd.DataFrame(index=dates)
        df['Close'] = prices
        df['Open'] = [p * (1 + random.uniform(-0.01, 0.01)) for p in prices]
        df['High'] = [max(o, c) * (1 + random.uniform(0, 0.01)) for o, c in zip(df['Open'], df['Close'])]
        df['Low'] = [min(o, c) * (1 - random.uniform(0, 0.01)) for o, c in zip(df['Open'], df['Close'])]
        df['Volume'] = [int(random.uniform(100000, 1000000)) for _ in range(250)]
        
        current_price = prices[-1]
        prev_close = prices[-2]
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100
        
        return df, {
            'current_price': current_price,
            'change': change,
            'change_percent': change_percent,
            'name': f"Mock: {ticker_code} (Rate Limited)",
            'source': 'mock',
            'status': 'fallback'
        }

    def get_market_data(self, ticker_code: str, period: str = "1y", interval: str = "1d") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fetch market data (price, charts) primarily from yfinance.
        Uses Caching to reduce API calls.
        Falls back to Mock Data if Rate Limited.
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
            # 1. Try FMP (Priority 1)
            # Only try FMP if not explicitly known to fail? Just retry, we silenced the logs.
            df_fmp, meta_fmp = self._fetch_from_fmp(ticker_code, period, interval)
            if df_fmp is not None and not df_fmp.empty:
                cache.set(cache_key, (df_fmp, meta_fmp, datetime.datetime.now()))
                return df_fmp, meta_fmp

            # 2. Try yfinance (Priority 2)
            ticker = yf.Ticker(ticker_code)
            
            # Explicit try-catch for history
            try:
                df = ticker.history(period=period, interval=interval)
            except Exception as e:
                 print(f"yfinance history fetch failed: {e}")
                 df = pd.DataFrame()

            if df.empty:
                # If history failed, we should probably fallback to Mock immediately or check why
                # But let's verify if 'info' call below also fails or if we can salvage something?
                # Usually if history fails, everything is toast.
                # Fallback to Mock
                return self._generate_mock_data(ticker_code)
                
            # 2. Get Metadata (Current Price, Change)
            # Try fast info first, then history fallback
            # WRAP THIS IN TRY-BLOCK specifically for Rate Limit
            try:
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or df['Close'].iloc[-1]
                name = info.get('longName', ticker_code)
            except Exception as e:
                # Likely Rate Limited here
                print(f"yfinance info fetch failed (Rate Limit suspected): {e}")
                # Fallback to calculating from DF if we have DF
                if not df.empty:
                    current_price = df['Close'].iloc[-1]
                    name = f"{ticker_code} (Data Only)"
                else:
                    return self._generate_mock_data(ticker_code)
            
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
            print(f"Error fetching market data: {e}")
            # traceback.print_exc() # Reduce noise
            # Final Fallback to Mock Data
            return self._generate_mock_data(ticker_code)
        
    def get_macro_context(self) -> Dict[str, Any]:
        """
        Fetch macro indicators (USD/JPY, Nikkei 225) to provide market context.
        """
        cache_key = "macro_context"
        cached = cache.get(cache_key)
        if cached:
            data, timestamp = cached
            if (datetime.datetime.now() - timestamp).total_seconds() < 3600: # 1 hour cache
                return data
        
        context = {}
        try:
            # Nikkei 225
            n225 = yf.Ticker("^N225")
            n225_hist = n225.history(period="1mo")
            if not n225_hist.empty:
                current = n225_hist['Close'].iloc[-1]
                prev = n225_hist['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                context['n225'] = {
                    'price': current,
                    'change_pct': change,
                    'trend': 'Bull' if change > 0 else 'Bear'
                }
            
            # USD/JPY
            usdjpy = yf.Ticker("JPY=X")
            usdjpy_hist = usdjpy.history(period="1mo")
            if not usdjpy_hist.empty:
                current = usdjpy_hist['Close'].iloc[-1]
                prev = usdjpy_hist['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                context['usdjpy'] = {
                    'price': current,
                    'change_pct': change,
                    'trend': 'Weak Yen' if change > 0 else 'Strong Yen'
                }
                
            cache.set(cache_key, (context, datetime.datetime.now()))
            return context
        except Exception as e:
            print(f"Error fetching macro context: {e}")
            return {}

    def get_technical_indicators(self, df: pd.DataFrame, interval: str = "1d") -> Dict[str, Any]:
        """
        Calculate technical indicators using pandas-ta.
        """
        # Default empty structure
        results = {
            'rsi': 50.0, 'rsi_status': "Data Lack",
            'macd': 0.0, 'macd_signal': 0.0, 'macd_status': "Data Lack",
            'bb_upper': 0.0, 'bb_lower': 0.0, 'bb_width': 0.0, 'bb_status': "Data Lack",
            'sma_short': 0.0, 'sma_mid': 0.0, 'sma_long': 0.0, 'atr': 0.0, 'trend_desc': "Insufficient Data"
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
            
            # 4. Moving Averages
            if interval == "1wk":
                ma_short_len, ma_mid_len, ma_long_len = 13, 26, 52  # 13週, 26週, 52週
            else:
                ma_short_len, ma_mid_len, ma_long_len = 5, 25, 75   # 5日, 25日, 75日
            
            calc_df.ta.sma(length=ma_short_len, append=True)
            calc_df.ta.sma(length=ma_mid_len, append=True)
            calc_df.ta.sma(length=ma_long_len, append=True)
            
            ma_short_col = f'SMA_{ma_short_len}'
            ma_mid_col = f'SMA_{ma_mid_len}'
            ma_long_col = f'SMA_{ma_long_len}'
            
            if ma_mid_col in calc_df.columns:
                results['sma_short'] = calc_df[ma_short_col].iloc[-1]
                results['sma_mid'] = calc_df[ma_mid_col].iloc[-1]
                price = calc_df['Close'].iloc[-1]
                sma_long = calc_df[ma_long_col].iloc[-1] if ma_long_col in calc_df.columns else 0
                results['sma_long'] = sma_long
                
                if price > results['sma_mid'] and results['sma_mid'] > sma_long and sma_long > 0:
                    results['trend_desc'] = "Strong Uptrend (強い上昇)"
                elif price < results['sma_mid'] and results['sma_mid'] < sma_long and sma_long > 0:
                    results['trend_desc'] = "Strong Downtrend (強い下落)"
                elif price > results['sma_mid']:
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
            
        # Try FMP Financials (Priority 1)
        if self.fmp_key:
            try:
                clean_ticker = str(ticker_code).split('.')[0]
                fmp_ticker = f"{clean_ticker}.T"
                # Get Key Metrics
                metrics_url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{fmp_ticker}?apikey={self.fmp_key}"
                res = requests.get(metrics_url, timeout=10)
                if res.status_code == 200:
                    metrics = res.json()
                    if metrics:
                        m = metrics[0]
                        data['details'].update({
                            'market_cap': m.get('marketCapTTM'),
                            'pe_ratio': m.get('peRatioTTM'),
                            'pb_ratio': m.get('priceToBookRatioTTM'),
                            'dividend_yield': m.get('dividendYieldTTM', 0) * 100 if m.get('dividendYieldTTM') else 0,
                            'roe': m.get('roeTTM'),
                        })
                        data['source'] = 'fmp'
                        data['status'] = 'complete'
                
                # Get Profile for Sector/Name
                profile_url = f"https://financialmodelingprep.com/api/v3/profile/{fmp_ticker}?apikey={self.fmp_key}"
                p_res = requests.get(profile_url, timeout=10)
                if p_res.status_code == 200:
                    profile = p_res.json()
                    if profile:
                        p = profile[0]
                        data['details']['sector'] = p.get('sector')
                        data['details']['name'] = p.get('companyName')
            except Exception as e:
                pass # Silently fail for financials

        # Try DefeatBeta (Priority 2) - For Credit Margin Data mostly
        try:
            # Real integration would call: self.defeatbeta.get_financials(target_ticker)
            if self.defeatbeta:
                db_data = self.defeatbeta.get_company_info(ticker_code)
                if db_data:
                    # Merge or update from DefeatBeta (especially credit/margin)
                    data['details'].update(db_data)
                    if data['source'] == 'yfinance_fallback':
                        data['source'] = 'defeatbeta'
        except Exception:
            pass
            
        # Fallback to yfinance
        try:
            ticker = yf.Ticker(target_ticker)
            
            try:
                 info = ticker.info
            except Exception:
                 info = {}

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
            # print(f"Financial data fetch failed: {e}")
            pass
            
        return data

# Singleton entry point
_data_manager = None

def get_data_manager():
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager
