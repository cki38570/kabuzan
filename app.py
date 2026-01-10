import streamlit as st
import pandas as pd
from modules.styles import get_custom_css
from modules.ui import get_card_css, render_stock_card
from modules.data import get_stock_data, get_credit_data, get_next_earnings_date, get_market_sentiment
from modules.analysis import calculate_indicators, calculate_trading_strategy, calculate_relative_strength
import datetime
import traceback
from modules.charts import create_credit_chart, create_lightweight_chart
from modules.notifications import (
    check_price_alerts, 
    show_alert_manager, 
    show_notification_settings, 
    process_morning_notifications,
    send_line_message,
    check_technical_signals
)
from modules.recommendations import find_similar_stocks, get_recommendation_reason
from modules.backtest import backtest_strategy, format_backtest_results
from modules.patterns import enhance_ai_analysis_with_patterns
from modules.enhanced_metrics import calculate_advanced_metrics, format_metrics_display
from modules.portfolio import add_to_portfolio, remove_from_portfolio, get_portfolio_df
from modules.exports import generate_report_text
from modules.screener import scan_market
from modules.llm import API_KEY, GENAI_AVAILABLE, generate_gemini_analysis
from modules.data_manager import get_data_manager
from modules.news import get_stock_news
from modules.constants import SCREENER_CATEGORIES, QUICK_TICKERS, DEFAULT_WATCHLIST
import json
import os

from modules.storage import storage

def load_watchlist():
    return storage.load_watchlist()

def save_watchlist(watchlist):
    storage.save_watchlist(watchlist)

# Page Config
st.set_page_config(
    page_title="株価AI分析",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# PWA Meta Tags
pwa_meta = """
<link rel="manifest" href="/app/static/manifest.json">
<meta name="theme-color" content="#0a192f">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="株価AI">
<link rel="apple-touch-icon" href="/app/static/icon-192.png">
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/app/static/service-worker.js')
      .then(reg => console.log('Service Worker registered'))
      .catch(err => console.log('Service Worker registration failed'));
  });
}
</script>
"""
st.markdown(pwa_meta, unsafe_allow_html=True)

# Inject Custom CSS (Base + Mobile/Card UI)
st.markdown(get_custom_css(), unsafe_allow_html=True)
st.markdown(get_card_css(), unsafe_allow_html=True)

# --- Sidebar: Navigation & Settings ---
with st.sidebar:
    st.header(" Kabuzan Menu")
    
    # NEW: Navigation Menu
    page = st.radio("移動", ["🏠 ホーム", "🚀 クイックスキャン", "💰 ポートフォリオ", "⚙️ 設定"], index=0)
    
    st.divider()

    # 1. Analysis Settings (Available on all pages for now, or only Home)
    if page == "🏠 ホーム":
        with st.expander("🛠️ 分析・表示設定", expanded=False):
            st.caption("テクニカル指標のパラメータ")
            params = {}
            params['sma_short'] = st.number_input("短期移動平均 (日)", 3, 20, 5)
            params['sma_mid'] = st.number_input("中期移動平均 (日)", 10, 50, 25)
            params['sma_long'] = st.number_input("長期移動平均 (日)", 50, 200, 75)
            params['rsi_period'] = st.number_input("RSI期間", 5, 30, 14)
            params['bb_window'] = st.number_input("ボリンジャー期間", 10, 50, 20)
            
            st.divider()
            if 'comparison_mode' not in st.session_state:
                st.session_state.comparison_mode = False
            
            # Comparison Mode Toggle
            comparison_mode = st.checkbox("📊 銘柄比較モード", value=st.session_state.comparison_mode)
            if comparison_mode != st.session_state.comparison_mode:
                st.session_state.comparison_mode = comparison_mode
                st.rerun()
    else:
        # Default params if not on home
        params = {'sma_short': 5, 'sma_mid': 25, 'sma_long': 75, 'rsi_period': 14, 'bb_window': 20}

    # 2. Watchlist (Mobile Cards) - Always Visible
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = load_watchlist()
        if not st.session_state.watchlist:
            st.session_state.watchlist = DEFAULT_WATCHLIST

    st.markdown("---")
    st.header("👀 ウォッチリスト")
    
    # Add Ticker
    with st.form("add_ticker_form", clear_on_submit=True):
        col_mn1, col_mn2 = st.columns([3, 1])
        new_ticker = col_mn1.text_input("追加", placeholder="コード (例: 7203)", label_visibility="collapsed")
        if col_mn2.form_submit_button("＋"):
            if new_ticker:
                # Normalize ticker
                clean_ticker = str(new_ticker).strip()
                if clean_ticker.endswith(".0"):
                    clean_ticker = clean_ticker[:-2]
                    
                if clean_ticker.isdigit() and len(clean_ticker) == 4:
                    clean_ticker = f"{clean_ticker}.T"
                
                exists = any(item.get('code') == clean_ticker for item in st.session_state.watchlist if isinstance(item, dict))
                if not exists:
                    st.session_state.watchlist.append({'code': clean_ticker, 'name': clean_ticker})
                    save_watchlist(st.session_state.watchlist)
                    st.toast(f"✅ {clean_ticker} を追加しました")
                    st.rerun()
    
    # --- The FOLLOWING UI elements must be OUTSIDE the st.form to use st.button/st.rerun correctly ---

    # Init Cache
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}

    # Ensure session state for active ticker
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = ""

    # Sort watchlist safely
    if 'watchlist' in st.session_state and isinstance(st.session_state.watchlist, list):
        try:
            st.session_state.watchlist.sort(key=lambda x: str(x.get('code', '') if isinstance(x, dict) else ''))
        except Exception as e:
            st.error(f"Watchlist sorting error: {e}")
    
    import yfinance as yf
    
    # Caching function for watchlist card data to improve performance
    @st.cache_data(ttl=300) # Cache for 5 minutes
    def get_cached_card_info(code):
        try:
            # Normalize code if it's a 4-digit string
            ticker_code = str(code)
            if ticker_code.isdigit() and len(ticker_code) == 4:
                ticker_code = f"{ticker_code}.T"
                
            t = yf.Ticker(ticker_code)
            # Use fast_info to avoid heavy network calls if possible
            curr = 0
            prev = 0
            name = None

            try:
                # Get Name first
                info = t.info
                name = info.get('longName') or info.get('shortName')
            except: pass

            try:
                # Some objects might be missing attributes in some yfinance versions/states
                if hasattr(t, 'fast_info'):
                    curr = t.fast_info.last_price
                    prev = t.fast_info.previous_close
            except: pass
            
            # Use history as fallback if fast_info fails or returns None
            if curr is None or prev is None or curr == 0:
                try:
                    hist = t.history(period="2d")
                    if len(hist) >= 2:
                        curr = hist['Close'].iloc[-1]
                        prev = hist['Close'].iloc[-2]
                    elif len(hist) == 1:
                        curr = hist['Close'].iloc[-1]
                        prev = curr # Change will be 0
                except: pass

            # Ensure they are floats and not None
            curr = float(curr) if curr is not None else 0.0
            prev = float(prev) if prev is not None else 0.0

            if curr != 0 and prev != 0:
                chg = curr - prev
                pct = (chg / prev) * 100
                return curr, chg, pct, name or str(code)
            elif curr != 0:
                return curr, 0.0, 0.0, name or str(code)
        except Exception as e:
             # st.error/warning inside cached function is generally not recommended, but helps during debug
             pass
        return 0, 0, 0, str(code) # Fallback: return code as name if info fails
    
    # Render Cards
    updated_wl = False
    for item in st.session_state.watchlist:
        # Heal if item is a string (legacy/corrupted data)
        if isinstance(item, str):
            item = {'code': item, 'name': item}
        
        if not isinstance(item, dict):
            continue
            
        code = str(item.get('code', 'Unknown'))
        name = item.get('name')
        if name is None or name == '読み込み中...':
            name = code
            
        # Use cached fetch for card info
        curr, chg, pct, fetched_name = get_cached_card_info(code)
        
        # Sync name if it was missing or loading
        if fetched_name and (name == code or name == '読み込み中...'):
            item['name'] = fetched_name
            updated_wl = True
            name = fetched_name

        if name and isinstance(name, str) and name.startswith('Mock: '):
            clean_name = name[6:]
        else:
            clean_name = str(name)
        
        # Use new Card Component
        try:
            if render_stock_card(code, clean_name, curr, chg, pct, key=f"card_{code}"):
                st.session_state.active_ticker = code
                st.rerun()
        except Exception as e:
            st.error(f"Error rendering card for {code}: {e}")
            
    if updated_wl:
        save_watchlist(st.session_state.watchlist)

    if st.button("🗑️ リストをクリア", key="clear_wl"):
        st.session_state.watchlist = []
        save_watchlist([])
        st.session_state.active_ticker = ""
        st.rerun()
    
# --- Global Data ---
# Load settings for process_morning_notifications inside
process_morning_notifications() 
settings = storage.load_settings()
last_notified = settings.get('last_daily_report_date', 'Never')
st.sidebar.caption(f"📅 Last Report: {last_notified}")

market_trend = get_market_sentiment()
market_badge_color = "#00ff00" if market_trend == "Bull" else "#ff4b4b" if market_trend == "Bear" else "#808080"


# --- Page Views ---

def render_home(params):
    st.title("🏠 ホーム / AI分析")
    dm = get_data_manager() # Initialize dm early to avoid scope errors
    
    # 1. Ticker Input
    def update_ticker_from_input():
        st.session_state.active_ticker = st.session_state.ticker_input_widget

    ticker_input = st.text_input(
        "コード入力", 
        value=st.session_state.active_ticker, 
        placeholder="例: 7203", 
        label_visibility="collapsed",
        key="ticker_input_widget",
        on_change=update_ticker_from_input
    )
    # Sync back just in case
    if ticker_input != st.session_state.active_ticker:
        st.session_state.active_ticker = ticker_input

    # 2. Comparison Mode
    if st.session_state.comparison_mode:
        st.info("📊 比較モード: 複数の銘柄を同時に表示します")
        compare_input = st.text_input("比較する銘柄コード (カンマ区切り)", placeholder="例: 7203,9984,6758")
        if compare_input:
            tickers = [t.strip() for t in compare_input.split(',')]
            comparison_data = []
            for ticker in tickers:
                df, info = get_stock_data(ticker)
                if df is not None and info is not None:
                    df = calculate_indicators(df, params)
                    last = df.iloc[-1]
                    comparison_data.append({
                        '銘柄名': info['name'],
                        'コード': ticker,
                        '現在値': f"¥{info['current_price']:,.1f}",
                        '前日比': f"{info['change_percent']:.2f}%",
                        'RSI': f"{last['RSI']:.1f}",
                    })
            if comparison_data:
                st.dataframe(pd.DataFrame(comparison_data), width='stretch')
        return

    # 3. Normal Analysis
    if ticker_input:
        # Sanitize input: remove .0 if present
        ticker_input = str(ticker_input)
        if ticker_input.endswith(".0"):
            ticker_input = ticker_input[:-2]
        
        try:
            if ticker_input in st.session_state.analysis_cache:
                # Load from Cache
                cache = st.session_state.analysis_cache[ticker_input]
                df, info = cache['df'], cache['info']
                indicators, weekly_indicators = cache['indicators'], cache['weekly_indicators']
                news_data = cache['news_data']
                macro_context, transcript_data = cache['macro_context'], cache['transcript_data']
                df_weekly = cache['df_weekly']
                earnings_date = cache.get('earnings_date') # Retrieve earnings_date from cache
            else:
                # Fetch New Data
                with st.spinner('AIが市場データを分析中...'):
                    df, info = dm.get_market_data(ticker_input)
                    indicators, df = dm.get_technical_indicators(df, interval="1d")
                    
                    # Prepare weekly indicators for AI analysis
                    df_weekly, _ = dm.get_market_data(ticker_input, interval="1wk")
                    if not df_weekly.empty:
                        weekly_indicators, df_weekly = dm.get_technical_indicators(df_weekly, interval="1wk")
                    else:
                        weekly_indicators = {}
                
                # Fetch News Data for sentiment analysis
                news_data = get_stock_news(ticker_input)
            
                # Get earnings date
                try:
                    earnings_date = info.get('earnings_date')
                except:
                    earnings_date = None
            
                # v3.0: Fetch Macro context and Transcripts
                macro_context = dm.get_macro_context()
                transcript_data = dm.defeatbeta.get_transcripts(ticker_input) if dm.defeatbeta else pd.DataFrame()
                
                if df is not None and not df.empty:
                    st.session_state.analysis_cache[ticker_input] = {
                        'df': df, 'info': info, 'indicators': indicators, 
                        'weekly_indicators': weekly_indicators, 'news_data': news_data,
                        'macro_context': macro_context, 'transcript_data': transcript_data,
                        'df_weekly': df_weekly
                    }
            
            if df is not None and not df.empty:
                # Data Status Display
                status_map = {"fresh": "🟢 Live", "cached": "🟡 Cached", "fallback": "🔴 Fallback"}
                status_text = status_map.get(info.get('status'), "⚪ Unknown")
                st.caption(f"Data Status: {status_text} (Source: {info.get('source')})")

                # Technical Signal Check (RSI + BB)
                check_technical_signals(ticker_input, info['current_price'], indicators, info['name'])

                alerts = check_price_alerts(info['current_price'], ticker_input, info['name'])
                for alert_info in alerts:
                    st.warning(alert_info['message'])
                    from modules.notifications import remove_alert
                    remove_alert(alert_info['alert'])
                
                for item in st.session_state.watchlist:
                    if item['code'] == ticker_input:
                        if item['name'] != info['name']:
                            item['name'] = info['name']
                            save_watchlist(st.session_state.watchlist)
                
                # Market Trend Visualization
                trend_color = "#10b981" if market_trend == "Bull" else "#f43f5e" if market_trend == "Bear" else "#64748b"
                trend_icon = "📈" if market_trend == "Bull" else "📉" if market_trend == "Bear" else "➡"
                trend_text = "強気相場 (上昇トレンド)" if market_trend == "Bull" else "弱気相場 (下落トレンド)" if market_trend == "Bear" else "中立 (方向感なし)"
                
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, {trend_color}22 0%, rgba(0,0,0,0) 100%); 
                            border-left: 5px solid {trend_color}; padding: 10px 15px; border-radius: 5px; margin-bottom: 15px;">
                    <span style="font-size: 0.9rem; color: #aaa;">🇯🇵 日経平均トレンド</span><br/>
                    <span style="font-size: 1.2rem; font-weight: bold; color: {trend_color};">{trend_icon} {trend_text}</span>
                </div>
                """, unsafe_allow_html=True)

                # Feature: Mock Warning
                if not API_KEY or not GENAI_AVAILABLE:
                    st.error("⚠️ **AI API未稼働**: APIキーが設定されていないか、制限によりモック（ダミーデータ）による分析を表示しています。")

                # Feature 2: Earnings Alert
                earnings_date = get_next_earnings_date(ticker_input)
                if earnings_date:
                    # Calculate days until earnings
                    today = datetime.datetime.now().date()
                    if isinstance(earnings_date, datetime.datetime):
                        e_date = earnings_date.date()
                    else:
                        e_date = pd.to_datetime(earnings_date).date()
                        
                    days_left = (e_date - today).days
                    if 0 <= days_left <= 7:
                         st.error(f"⚠️ **決算発表が近いです！** (予定日: {e_date} / 残り{days_left}日) \n持ち越しには十分注意してください。")
                    else:
                         st.caption(f"📅 次回決算予定: {e_date} (残り{days_left}日)")

                # Technical calculation
                df = calculate_indicators(df, params) 
                
                financial_data = dm.get_financial_data(ticker_input)
                credit_df = get_credit_data(ticker_input)
                
                # --- Pre-calculation for Dashboard ---
                strategic_data = calculate_trading_strategy(df, settings=settings)
                relative_strength = calculate_relative_strength(df, macro_context)
                backtest_results = backtest_strategy(df, strategic_data)
                
                # AI Analysis Triggered immediately to show results on Dashboard
                extra_context = {
                    'earnings_date': earnings_date,
                    'market_trend': market_trend
                }
                patterns = enhance_ai_analysis_with_patterns(df)
                enhanced_metrics = calculate_advanced_metrics(df, info['current_price'])
                
                # Load AI Analysis History for feedback loop
                past_history = storage.load_ai_analysis_history(ticker_input)

                # Generate AI Analysis
                report_raw, ai_cost, analysis_error = generate_gemini_analysis(
                    ticker_input, info, indicators, financial_data, strategic_data, 
                    enhanced_metrics=enhanced_metrics, patterns=patterns,
                    extra_context=extra_context, weekly_indicators=weekly_indicators,
                    news_data=news_data, macro_data=macro_context,
                    transcript_data=transcript_data, relative_strength=relative_strength,
                    backtest_results=backtest_results,
                    past_history=past_history,
                    credit_df=credit_df
                )
                
                # Parse AI Result
                report_data = {}
                if report_raw:
                try:
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', report_raw, re.DOTALL)
                    if json_match:
                        report_data = json.loads(json_match.group(1))
                    else:
                        report_data = json.loads(report_raw)
                    
                    # Normalize confidence keys
                    if 'confidence' in report_data and 'confidence_score' not in report_data:
                        report_data['confidence_score'] = report_data['confidence']
                    elif 'confidence_score' in report_data and 'confidence' not in report_data:
                        report_data['confidence'] = report_data['confidence_score']
                        
                except Exception as e:
                    # Fallback on parse error
                    report_data = {
                        "status": "ERROR",
                        "total_score": 0,
                        "headline": "解析エラー",
                        "final_reasoning": f"AIデータのパースに失敗しました。詳細: {e}\nRaw: {str(report_raw)[:200]}..."
                    }
                else:
                    if analysis_error:
                         report_data = {
                            "status": "ERROR",
                            "total_score": 0,
                            "headline": "AI分析エラー",
                            "final_reasoning": f"AI分析実行中にエラーが発生しました: {analysis_error}"
                        }
                    elif not report_raw:
                         report_data = {
                            "status": "WAITING",
                            "total_score": 50,
                            "headline": "準備中",
                            "final_reasoning": "AI分析を準備しています..."
                        }
                
                # Save AI Analysis Log to storage (Memory)
                if report_data.get('status'):
                    storage.save_ai_analysis_log(
                        ticker_input, 
                        report_data.get('total_score', 50), 
                        report_data.get('status'), 
                        info['current_price']
                    )

                # --- Main Content via Tabs ---
                # Changed order as requested: Chart -> AI -> Data
                tab_chart, tab_ai, tab_data = st.tabs(["📈 チャート", "🤖 AI分析", "📊 データ・詳細"])

                with tab_chart:
                     st.markdown(f"**{info['name']} ({ticker_input})** | {info.get('sector', '')}")
                     
                     # Chart Mode Toggle
                     chart_range = st.radio("期間", ["日足", "週足"], horizontal=True, label_visibility="collapsed")
                     
                     if chart_range == "日足":
                         chart_daily = create_lightweight_chart(df, info['name'], strategic_data, interval="1d")
                         if chart_daily:
                             st.markdown("##### 日足チャート")
                             chart_daily.load()
                     else: # Weekly
                         if not df_weekly.empty:
                             chart_weekly = create_lightweight_chart(df_weekly, info['name'], strategic_data, interval="1wk")
                             if chart_weekly:
                                 st.markdown("##### 週足チャート")
                                 chart_weekly.load()
                         else:
                             st.warning("週足データがありません")

                with tab_ai:
                     # 1. Summary Dashboard
                    st.markdown("### 📊 Decision Center")
                    
                    status = report_data.get('status', 'NEUTRAL')
                    total_score = report_data.get('total_score', 0)
                    
                    # Status Styling
                    if "BUY" in status:
                        status_color = "#10b981" # Emerald Green
                        status_icon = "🚀"
                        status_ja = "買い推奨 (BUY)"
                    elif "SELL" in status:
                        status_color = "#f43f5e" # Rose Red
                        status_icon = "🚨"
                        status_ja = "売り推奨 (SELL)"
                    else:
                        status_color = "#94a3b8" # Slate
                        status_icon = "👀"
                        status_ja = "様子見 (NEUTRAL)"

                    badge_html = f"<div style='background: #f59e0b; color: black; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; display: inline-block; vertical-align: top; margin-left: 5px;'>🔥 出来高急増</div>" if strategic_data.get('volume_spike') else ""

                    dashboard_html = f"""
                    <div style="background: linear-gradient(135deg, {status_color}15 0%, rgba(0,0,0,0) 100%); 
                                border: 1px solid {status_color}44; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-size: 0.8rem; color: #cbd5e1; letter-spacing: 1px;">GEMINI ANALYST JUDGEMENT</div>
                                <div style="font-size: 2.2rem; font-weight: 900; color: {status_color}; text-shadow: 0 0 15px {status_color}33;">
                                    {status_icon} {status}
                                </div>
                                <div style="font-size: 1rem; color: {status_color}; font-weight: bold;">{status_ja} {badge_html}</div>
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <div style="text-align: right; background: {status_color}10; padding: 10px 15px; border-radius: 12px; border: 1px solid {status_color}33;">
                                    <div style="font-size: 0.7rem; color: #cbd5e1;">CONFIDENCE</div>
                                    <div style="font-size: 1.8rem; font-weight: 800; color: #60a5fa; line-height: 1;">
                                        {report_data.get('confidence', report_data.get('confidence_score', 0))}<span style="font-size: 0.8rem; color: #64748b;">%</span>
                                    </div>
                                </div>
                                <div style="text-align: right; background: {status_color}10; padding: 10px 15px; border-radius: 12px; border: 1px solid {status_color}33;">
                                    <div style="font-size: 0.7rem; color: #cbd5e1;">AI SCORE</div>
                                    <div style="font-size: 1.8rem; font-weight: 800; color: {status_color}; line-height: 1;">
                                        {total_score}<span style="font-size: 0.8rem; color: #64748b;">/100</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(dashboard_html, unsafe_allow_html=True)
                    
                    # 2. Action Plan Cards (Visual Enhancement)
                    action_plan = report_data.get('action_plan', {})
                    if action_plan:
                        st.markdown("#### 🎯 戦略アクションプラン")
                        
                        # Use a 3-column minimalist layout with theme colors
                        c_entry, c_target, c_stop = st.columns(3)
                        
                        def price_card(label, price, color, subtext=""):
                            # Handle None case safely
                            display_price = 0
                            if price is not None:
                                try:
                                    display_price = float(price)
                                except:
                                    display_price = 0
                                    
                            return f"""
                            <div style="background: {color}15; border-left: 5px solid {color}; padding: 12px; border-radius: 8px; border: 1px solid {color}33;">
                                <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 3px;">{label}</div>
                                <div style="font-size: 1.4rem; font-weight: 800; color: {color}; line-height: 1;">¥{display_price:,.0f}</div>
                                <div style="font-size: 0.7rem; color: #64748b; margin-top: 5px;">{subtext}</div>
                            </div>
                            """

                        with c_entry:
                            st.markdown(price_card("エントリー目安", action_plan.get('buy_limit', 0), "#10b981", "想定買付価格"), unsafe_allow_html=True)
                        with c_target:
                            st.markdown(price_card("利確ターゲット", action_plan.get('sell_limit', 0), "#fbbf24", "目標利益"), unsafe_allow_html=True)
                        with c_stop:
                            st.markdown(price_card("損切りライン", action_plan.get('stop_loss', 0), "#f43f5e", "リスク許容限界"), unsafe_allow_html=True)
                        
                        st.info(f"💡 **推奨アクション**: {action_plan.get('recommended_action', 'N/A')}\n\n_{action_plan.get('rationale', '')}_")

                    # 3. AI Reasoning (Expert Committee Results)
                    st.divider()
                    
                    # Headline and Key Details
                    headline = report_data.get('headline', 'AI分析レポート')
                    st.markdown(f"### {headline}")

                    if 'sector_analysis' in report_data:
                        st.markdown(f"**🏢 セクター分析**: {report_data['sector_analysis']}")
                    
                    with st.expander("🔍 専門家別の詳細分析", expanded=True):
                        if 'technical_detail' in report_data:
                            st.markdown(f"**📏 テクニカル分析**: {report_data['technical_detail']}")
                        if 'macro_sentiment_detail' in report_data:
                            st.markdown(f"**🌐 地合い・需給相関**: {report_data['macro_sentiment_detail']}")
                        if report_data.get('memory_feedback'):
                            st.info(f"🧠 **過去の反省**: {report_data['memory_feedback']}")
                    
                    # Bull vs Bear (Reinforced with quantitative reasoning)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.success(f"**🐂 強気派 (Bull)**\n\n{report_data.get('bull_view', 'データ不足')}")
                    with c2:
                        st.error(f"**🐻 弱気派 (Bear)**\n\n{report_data.get('bear_view', 'データ不足')}")
                    
                    # Final Conclusion
                    st.markdown("#### 💬 最終統合判断")
                    st.markdown(report_data.get('final_reasoning', '現在、詳細な分析を生成できませんでした。'))

                    t_score = report_data.get('transcript_score', 0)
                    stars = "★" * int(t_score) + "☆" * (5 - int(t_score)) if t_score else "N/A"
                    if report_data.get('transcript_reason'):
                            st.caption(f"決算自信度 ({stars}): {report_data['transcript_reason']}")
                            
                    with st.expander("🔄 バックテスト結果"):
                            st.markdown(format_backtest_results(backtest_results))
                            if report_data.get('backtest_feedback'):
                                st.warning(f"💡 AIの反省: {report_data['backtest_feedback']}")

                with tab_data:
                     tcol1, tcol2, tcol3 = st.columns(3)
                     tcol1.metric("RSI", f"{indicators.get('rsi', 0) if indicators else 0:.1f}")
                     tcol2.metric("地合い差分", f"{relative_strength.get('diff', 0):+.1f}%")
                     tcol3.metric("現在値", f"¥{info.get('current_price', 0):,.0f}")
                     
                     if credit_df is not None and not credit_df.empty:
                        st.markdown("#### 信用残推移")
                        c_chart_data = create_credit_chart(credit_df)
                        if c_chart_data is not None:
                            st.bar_chart(c_chart_data)
                     
                     st.markdown("#### 関連ニュース")
                     if news_data:
                        for n in news_data[:5]:
                            st.markdown(f"• **[{n['title']}]({n['link']})**")
                            st.caption(f"{n.get('publisher', '')} | {n.get('published', '')}")
                     else:
                        st.info("ニュースはありません")
            else:
                st.error(f"銘柄コード {ticker_input} のデータを取得できませんでした。")
        except Exception as e:
            import traceback
            st.error(f"エラーが発生しました: {e}")
            st.code(traceback.format_exc())

def render_scanner():
    st.title("🚀 クイックスキャン")
    st.write("市場全体を高速スキャンし、チャンスのある銘柄を抽出します。")
    
    category = st.selectbox("カテゴリ", list(SCREENER_CATEGORIES.keys()), key="full_scan_cat")
    if st.button("🚀 スキャン実行", type="primary"):
        with st.spinner(f"{category} をスキャン中..."):
            scan_result = scan_market(category_name=category)
            if not scan_result.empty:
               st.success(f"{len(scan_result)} 件の銘柄がヒットしました")
               # Safe column selection
               display_cols = ['銘柄名', 'コード', '判定', '現在値', 'RSI', '出来高倍率']
               available_cols = [c for c in display_cols if c in scan_result.columns]
               st.dataframe(
                   scan_result[available_cols], 
                   width='stretch'
               )
            else:
                st.info("条件に一致する銘柄は見つかりませんでした。")

def render_portfolio():
    st.title("💰 ポートフォリオ")
    
    # Add Form
    with st.expander("➕ 銘柄を追加", expanded=True):
         with st.form("portfolio_main_add"):
            c1, c2, c3 = st.columns(3)
            p_code = c1.text_input("コード", placeholder="7203")
            p_qty = c2.number_input("株数", min_value=0, step=100)
            p_p = c3.number_input("取得単価", min_value=0.0)
            
            if st.form_submit_button("追加"):
                if p_code:
                    # Try to fetch name
                    dummy_df, dummy_info = get_stock_data(p_code)
                    name = dummy_info.get('name', p_code) if dummy_info else p_code
                    add_to_portfolio(p_code, name, p_qty, p_p)
                    st.success(f"{name} を追加しました")
                    st.rerun()

    # List
    st.subheader("保有資産一覧")
    pf_df = get_portfolio_df()
    if not pf_df.empty:
        # Calculate current logic if possible, otherwise just show cached
        st.dataframe(pf_df, width='stretch')
        
        # Remove Logic
        st.divider()
        rm_target = st.text_input("削除する銘柄コード")
        if st.button("削除"):
            remove_from_portfolio(rm_target)
            st.success("削除しました")
            st.rerun()
    else:
        st.info("ポートフォリオは空です。")

def render_settings():
    st.title("⚙️ 設定")
    show_notification_settings()
    
    st.subheader("システム情報")
    if API_KEY:
        st.success("✅ Gemini APIキー設定済み")
    else:
        st.error("❌ Gemini APIキー未設定")

# --- Routing ---
if page == "🏠 ホーム":
    render_home(params)
elif page == "🚀 クイックスキャン":
    render_scanner()
elif page == "💰 ポートフォリオ":
    render_portfolio()
elif page == "⚙️ 設定":
    render_settings()

# Footer
st.markdown("---")
st.caption("© 2026 Kabuzan | Pixel Fold Optimized Terminal")
