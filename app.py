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
    st.header("⚙️ メニュー")
    
    # 1. Main Navigation / Analysis Settings
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

    # 2. Watchlist (Mobile Cards)
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
                exists = any(item['code'] == new_ticker for item in st.session_state.watchlist)
                if not exists:
                    st.session_state.watchlist.append({'code': new_ticker, 'name': '読み込み中...'})
                    save_watchlist(st.session_state.watchlist)
                    st.rerun()
    
    # Init Cache
    if 'analysis_cache' not in st.session_state:
        st.session_state.analysis_cache = {}

# Ensure session state for active ticker
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = ""

    # Sort watchlist
    st.session_state.watchlist.sort(key=lambda x: x['code'])
    
    import yfinance as yf
    
    # Caching function for watchlist card data to improve performance
    @st.cache_data(ttl=300) # Cache for 5 minutes
    def get_cached_card_info(code):
        try:
             fetch_code = f"{code}.T" if code.isdigit() and len(code) == 4 else code
             t = yf.Ticker(fetch_code)
             # Use fast_info to avoid heavy network calls if possible
             curr = t.fast_info.last_price
             prev = t.fast_info.previous_close
             
             if curr and prev:
                 chg = curr - prev
                 pct = (chg / prev) * 100
                 return curr, chg, pct
             else:
                 # Fallback to history if fast_info fails
                 hist = t.history(period="2d")
                 if len(hist) >= 2:
                     curr = hist['Close'].iloc[-1]
                     prev = hist['Close'].iloc[-2]
                     chg = curr - prev
                     pct = (chg / prev) * 100
                     return curr, chg, pct
        except Exception as e:
             pass
        return 0, 0, 0
    
    # Render Cards
    for item in st.session_state.watchlist:
        clean_name = item['name'].replace('Mock: ', '')
        code = item['code']
        
        # Use cached fetch for card info
        curr, chg, pct = get_cached_card_info(code)
        
        # Use new Card Component
        if render_stock_card(code, clean_name, curr, chg, pct, key=f"card_{code}"):
            st.session_state.active_ticker = code
            st.rerun()

    if st.button("🗑️ リストをクリア", key="clear_wl"):
        st.session_state.watchlist = []
        save_watchlist(st.session_state.watchlist)
        st.session_state.active_ticker = "" # Clear active ticker too
        st.rerun()
    
    st.markdown("---")
    # Notification Settings (Persisted)
    show_notification_settings()

# --- Global Data ---
# Load settings for process_morning_notifications inside
process_morning_notifications() 
settings = storage.load_settings()
last_notified = settings.get('last_daily_report_date', 'Never')
st.sidebar.caption(f"📅 Last Report: {last_notified}")
if last_notified == 'Never' and settings.get('notify_line'):
    st.sidebar.warning("⚠️ ストレージへの保存が未完了です。設定から接続テストを行ってください。")

market_trend = get_market_sentiment()
market_badge_color = "#00ff00" if market_trend == "Bull" else "#ff4b4b" if market_trend == "Bear" else "#808080"

# --- Main Content ---

# Feature 4: Quick Select UX (Buttons removed as requested)


# ⚠️ IMPORTANT: We use a callback or session value to sync this
# If user types in box, we strictly take that using on_change or simple processing
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
# Sync back just in case (e.g. if code modifies active_ticker elsewhere)
if ticker_input != st.session_state.active_ticker:
    st.session_state.active_ticker = ticker_input

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

if ticker_input and not st.session_state.comparison_mode:
    # Sanitize input: remove .0 if present
    ticker_input = str(ticker_input).replace(".0", "")
    
    try:
        if ticker_input in st.session_state.analysis_cache:
            # Load from Cache
            cache = st.session_state.analysis_cache[ticker_input]
            df, info = cache['df'], cache['info']
            indicators, weekly_indicators = cache['indicators'], cache['weekly_indicators']
            news_data = cache['news_data']
            macro_context, transcript_data = cache['macro_context'], cache['transcript_data']
            df_weekly = cache['df_weekly']
        else:
            # Fetch New Data
            with st.spinner('AIが市場データを分析中...'):
                dm = get_data_manager()
                df, info = dm.get_market_data(ticker_input)
                indicators = dm.get_technical_indicators(df, interval="1d")
                
                # Prepare weekly indicators for AI analysis
                df_weekly, _ = dm.get_market_data(ticker_input, interval="1wk")
                weekly_indicators = dm.get_technical_indicators(df_weekly, interval="1wk") if not df_weekly.empty else {}
            
            # Fetch News Data for sentiment analysis
            news_data = get_stock_news(ticker_input)
        
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
                
                market_text = "上昇トレンド" if market_trend == "Bull" else "下落トレンド" if market_trend == "Bear" else "中立"
                st.markdown(f"**市場地合い (日経225)**: <span style='color:{market_badge_color}; font-weight:bold;'>{market_text}</span>", unsafe_allow_html=True)

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

                # Technical calculation (Old logic for charts if needed, but we use pre-calc for AI)
                # Actually, DataManager already calculated everything we need for AI.
                # But the charts might need the specific columns from calculate_indicators.
                df = calculate_indicators(df, params) 
                
                credit_data = dm.get_financial_data(ticker_input)
                
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
                
                report_raw = generate_gemini_analysis(
                    ticker_input, info, indicators, credit_data, strategic_data, 
                    enhanced_metrics=enhanced_metrics, patterns=patterns,
                    extra_context=extra_context, weekly_indicators=weekly_indicators,
                    news_data=news_data, macro_data=macro_context,
                    transcript_data=transcript_data, relative_strength=relative_strength,
                    backtest_results=backtest_results
                )
                
                # Parse AI Result
                report_data = {}
                try:
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', report_raw, re.DOTALL)
                    if json_match:
                        report_data = json.loads(json_match.group(1))
                    else:
                        report_data = json.loads(report_raw)
                except:
                    pass

            # --- Portfolio Quick Add (Moved Top) ---
            with st.expander("💰 ポートフォリオに追加", expanded=False):
                 with st.form("portfolio_quick_add"):
                    p_col1, p_col2 = st.columns(2)
                    p_qty = p_col1.number_input("株数", min_value=0, step=100)
                    p_p = p_col2.number_input("単価", min_value=0.0, value=float(info['current_price']))
                    if st.form_submit_button("ポートフォリオに反映"):
                        add_to_portfolio(ticker_input, info['name'], p_qty, p_p)
                        st.success(f"{info['name']} を追加しました")
                        st.rerun()

            # --- Main Content via Tabs ---
            tab_ai, tab_chart, tab_data = st.tabs(["🤖 AI分析", "📈 チャート", "📊 データ・詳細"])

            with tab_ai:
                 # 1. Summary Dashboard
                st.markdown("### 📊 Decision Center")
                total_score = report_data.get('total_score', 0)
                status = report_data.get('status', 'NEUTRAL')
                accent_color = "#10b981" if "BUY" in status else "#f43f5e" if "SELL" in status else "#64748b"
                t_score = report_data.get('transcript_score', 0)
                stars = "★" * int(t_score) + "☆" * (5 - int(t_score)) if t_score else "N/A"
                
                badge_html = f"<div style='background: #ff4b4b; color: white; padding: 4px 12px; border-radius: 50px; display: inline-block; font-size: 0.8rem; font-weight: bold; margin-left: 10px; box-shadow: 0 0 10px rgba(255,75,75,0.5); vertical-align: middle; margin-top: -10px;'>🔥 出来高急増！</div>" if strategic_data.get('volume_spike') else ""
                dashboard_html = f"<div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%); padding: 24px; border-radius: 20px; border: 1px solid {accent_color}66; margin-bottom: 25px; backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.3);'><div style='display: flex; justify-content: space-between; align-items: flex-start;'><div><span style='font-size: 0.8rem; color: #8892b0; text-transform: uppercase; letter-spacing: 2px;'>Gemini Analyst</span><br/><span style='font-size: 2.5rem; font-weight: 900; color: {accent_color}; text-shadow: 0 0 10px {accent_color}33;'>{status}</span>{badge_html}</div><div style='text-align: right;'><span style='font-size: 0.8rem; color: #8892b0;'>AI SCORE</span><br/><span style='font-size: 3rem; font-weight: 1000; color: {accent_color};'>{total_score}<small style='font-size: 1rem; color: #8892b0;'>/100</small></span></div></div></div>"
                st.markdown(dashboard_html, unsafe_allow_html=True)
                
                # 2. AI Reasoning
                with st.container(): # Use container instead of expander for main view
                    if report_data:
                        st.markdown(f"### {report_data['headline']}")
                        st.markdown(report_data['analysis_body'])
                        if report_data.get('transcript_reason'):
                             st.info(f"💬 **決算自信度 ({stars}):** {report_data['transcript_reason']}")
                             
                with st.expander("🔄 バックテスト結果"):
                     st.markdown(format_backtest_results(backtest_results))
                     if report_data.get('backtest_feedback'):
                          st.warning(f"💡 AIの反省: {report_data['backtest_feedback']}")

            with tab_chart:
                 # Lightweight Charts (No Plotly)
                 st.markdown(f"**{info['name']} ({ticker_input})** | {info.get('sector', '')}")
                 
                 chart_daily = create_lightweight_chart(df, info['name'], strategic_data, interval="1d")
                 if chart_daily:
                     st.markdown("##### 日足")
                     chart_daily.load()
                 
                 if not df_weekly.empty:
                     chart_weekly = create_lightweight_chart(df_weekly, info['name'], strategic_data, interval="1wk")
                     if chart_weekly:
                         st.markdown("##### 週足")
                         chart_weekly.load()

            with tab_data:
                 tcol1, tcol2, tcol3 = st.columns(3)
                 tcol1.metric("RSI", f"{indicators.get('rsi', 0):.1f}")
                 tcol2.metric("地合い差分", f"{relative_strength['diff']:+.1f}%")
                 tcol3.metric("現在値", f"¥{info['current_price']:,.0f}")
                 
                 if credit_data:
                    st.markdown("#### 信用残推移")
                    c_chart_data = create_credit_chart(credit_data)
                    if c_chart_data is not None:
                        st.bar_chart(c_chart_data)
                 
            st.markdown("#### 関連ニュース")
            if news_data:
                for n in news_data[:5]:
                    st.markdown(f"• **[{n['title']}]({n['link']})**")
                    st.caption(f"{n.get('publisher', '')} | {n.get('published', '')}")
            else:
                st.info("ニュースはありません")
            
            st.markdown("#### クイックスキャン")
            category = st.selectbox("カテゴリ", list(SCREENER_CATEGORIES.keys()), key="fold_scan_mini")
            if st.button("🚀 スキャン実行"):
                scan_result = scan_market(category_name=category)
                if not scan_result.empty:
                   st.dataframe(scan_result[['銘柄名', 'コード', '判定', 'RSI']])
            else:
                st.error(f"銘柄コード {ticker_input} のデータを取得できませんでした。")
    except Exception as e:
        import traceback
        st.error(f"エラーが発生しました: {e}")
        st.code(traceback.format_exc())

# Sidebar Watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = load_watchlist()

# Footer
st.markdown("---")
st.caption("© 2026 Kabuzan | Pixel Fold Optimized Terminal")
