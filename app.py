import streamlit as st
import pandas as pd
from modules.styles import get_custom_css
from modules.data import get_stock_data, get_credit_data, get_next_earnings_date, get_market_sentiment
from modules.analysis import calculate_indicators, calculate_trading_strategy
import datetime
from modules.charts import create_main_chart, create_credit_chart
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
import json
import os

WATCHLIST_PATH = "watchlist.json"

def load_watchlist():
    if os.path.exists(WATCHLIST_PATH):
        try:
            with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_watchlist(watchlist):
    try:
        with open(WATCHLIST_PATH, "w", encoding="utf-8") as f:
            json.dump(watchlist, f, ensure_ascii=False, indent=2)
    except:
        pass

# Page Config
st.set_page_config(
    page_title="株価AI分析",
    layout="wide", # Changed to wide for better dashboard view
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

# Inject Custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# --- Sidebar: Analysis Settings ---
with st.sidebar:
    st.header("🛠️ 分析設定")
    with st.expander("テクニカル指標設定"):
        params = {}
        params['sma_short'] = st.number_input("短期移動平均 (日)", 3, 20, 5)
        params['sma_mid'] = st.number_input("中期移動平均 (日)", 10, 50, 25)
        params['sma_long'] = st.number_input("長期移動平均 (日)", 50, 200, 75)
        params['rsi_period'] = st.number_input("RSI期間", 5, 30, 14)
        params['bb_window'] = st.number_input("ボリンジャー期間", 10, 50, 20)

# --- Sidebar: Watchlist ---
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = load_watchlist()
    if not st.session_state.watchlist:
        st.session_state.watchlist = [
            {'code': '7203', 'name': 'トヨタ自動車'}, 
            {'code': '9984', 'name': 'ソフトバンクG'}, 
            {'code': '6758', 'name': 'ソニーG'}
        ]

if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False

with st.sidebar:
    st.markdown("---")
    st.header("👀 ウォッチリスト")
    new_ticker = st.text_input("追加", placeholder="コード (例: 7203)")
    if st.button("リストに追加"):
        if new_ticker:
            exists = any(item['code'] == new_ticker for item in st.session_state.watchlist)
            if not exists:
                st.session_state.watchlist.append({'code': new_ticker, 'name': '読み込み中...'})
                save_watchlist(st.session_state.watchlist)
    
    selected_from_list = None
    for item in st.session_state.watchlist:
        # Cleanup name if it contains 'Mock:'
        clean_name = item['name'].replace('Mock: ', '')
        label = f"{clean_name} ({item['code']})"
        if st.button(label, key=f"btn_{item['code']}"):
            selected_from_list = item['code']
            
    if st.button("🗑️ リストをクリア"):
        st.session_state.watchlist = []
        save_watchlist(st.session_state.watchlist)
        st.rerun()
    
    st.markdown("---")
    st.header("⚙️ 機能")
    
    comparison_mode = st.checkbox("📊 銘柄比較モード", value=st.session_state.comparison_mode)
    if comparison_mode != st.session_state.comparison_mode:
        st.session_state.comparison_mode = comparison_mode
        st.rerun()

    st.markdown("---")
    st.markdown("---")
    show_notification_settings()

# --- Global Data ---
market_trend = get_market_sentiment()
process_morning_notifications()
market_badge_color = "#00ff00" if market_trend == "Bull" else "#ff4b4b" if market_trend == "Bear" else "#808080"

# --- Main Content ---
default_ticker = selected_from_list if selected_from_list else ""

# Feature 4: Quick Select UX
st.markdown("### 🔍 銘柄検索")
col_q1, col_q2, col_q3, col_q4, col_q5 = st.columns(5)
quick_tickers = [
    {'code': '7203', 'name': 'トヨタ'},
    {'code': '9984', 'name': 'SBG'},
    {'code': '6920', 'name': 'レーザー'},
    {'code': '8306', 'name': 'UFJ'},
    {'code': '1570', 'name': '日経レバ'}
]

clicked_quick = None
# Create quick select buttons
if col_q1.button(f"{quick_tickers[0]['name']}", type="primary"): clicked_quick = quick_tickers[0]['code']
if col_q2.button(f"{quick_tickers[1]['name']}"): clicked_quick = quick_tickers[1]['code']
if col_q3.button(f"{quick_tickers[2]['name']}"): clicked_quick = quick_tickers[2]['code']
if col_q4.button(f"{quick_tickers[3]['name']}"): clicked_quick = quick_tickers[3]['code']
if col_q5.button(f"{quick_tickers[4]['name']}"): clicked_quick = quick_tickers[4]['code']

if clicked_quick:
    default_ticker = clicked_quick

ticker_input = st.text_input("コード入力", value=default_ticker, placeholder="例: 7203", label_visibility="collapsed")

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
    with st.spinner('AIが市場データを分析中...'):
        dm = get_data_manager()
        df, info = dm.get_market_data(ticker_input)
        indicators = dm.get_technical_indicators(df, interval="1d")
        
        # Prepare weekly indicators for AI analysis
        df_weekly, _ = dm.get_market_data(ticker_input, interval="1wk")
        weekly_indicators = dm.get_technical_indicators(df_weekly, interval="1wk") if not df_weekly.empty else {}
        
        # Fetch News Data for sentiment analysis
        news_data = get_stock_news(ticker_input)
        
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
            
            # Fast Strategy Calculation for lines
            strategic_data = calculate_trading_strategy(df)
            
            # --- Tabs Layout ---
            tab_titles = ["📈 チャート", "🤖 AI分析", "💰 ポートフォリオ", "🔍 市場スキャン", "📊 データ"]
            tabs = st.tabs(tab_titles)
            tab1, tab2, tab3, tab4, tab5 = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4]
            
            # Tab 1: Chart
            with tab1:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {info['name']} ({ticker_input})")
                with col2:
                     price_color = "#00ffbd" if info['change'] >= 0 else "#ff4b4b"
                     st.markdown(f"<div style='text-align:right; font-size: 1.5rem; color:{price_color}'>¥{info['current_price']:,.0f}</div>", unsafe_allow_html=True)
                
                # Multi-Timeframe Tabs for Charts
                chart_daily_tab, chart_weekly_tab = st.tabs(["日足 (Daily)", "週足 (Weekly)"])
                
                with chart_daily_tab:
                    fig_main = create_main_chart(df, info['name'], strategic_data, interval="1d")
                    st.plotly_chart(fig_main, use_container_width=True, key="chart_daily")
                
                with chart_weekly_tab:
                    # Fetch weekly data
                    df_weekly, meta_weekly = dm.get_market_data(ticker_input, interval="1wk")
                    if not df_weekly.empty:
                        # Calculate indicators for weekly
                        df_weekly_calc = calculate_indicators(df_weekly, params) 
                        fig_weekly = create_main_chart(df_weekly_calc, info['name'], interval="1wk")
                        st.plotly_chart(fig_weekly, use_container_width=True, key="chart_weekly")
                    else:
                        st.warning("週足データを取得できませんでした。")
                
                # Performance Metrics
                st.markdown("#### パフォーマンス概要")
                perf_col1, perf_col2, perf_col3 = st.columns(3)
                week_ago = df.iloc[-5]['Close'] if len(df) >= 5 else df.iloc[0]['Close']
                month_ago = df.iloc[-20]['Close'] if len(df) >= 20 else df.iloc[0]['Close']
                week_change = ((info['current_price'] - week_ago) / week_ago) * 100
                month_change = ((info['current_price'] - month_ago) / month_ago) * 100
                
                perf_col1.metric("1週間", f"{week_change:+.2f}%")
                perf_col2.metric("1ヶ月", f"{month_change:+.2f}%")
                perf_col3.metric("ボラティリティ", f"{df['Close'].pct_change().std() * 100:.2f}%")

            # Tab 2: AI Analysis
            with tab2:
                st.markdown("### 🤖 Gemini AI アナリスト")
                
                # --- Fundamental Briefing Section ---
                if credit_data and credit_data.get('details'):
                    details = credit_data['details']
                    def format_large_number(num):
                        if not num: return "N/A"
                        if num >= 1e12: return f"{num/1e12:.1f}兆円"
                        if num >= 1e8: return f"{num/1e8:.1f}億円"
                        return f"{num:,.0f}円"

                    st.markdown("#### 💎 銘柄概況 (Fundamentals)")
                    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
                    f_col1.metric("時価総額", format_large_number(details.get('market_cap')))
                    f_col2.metric("PER (実績)", f"{details.get('pe_ratio', 0):.1f}倍" if details.get('pe_ratio') else "N/A")
                    f_col3.metric("PBR", f"{details.get('pb_ratio', 0):.2f}倍" if details.get('pb_ratio') else "N/A")
                    f_col4.metric("配当利回り", f"{details.get('dividend_yield', 0):.2f}%" if details.get('dividend_yield') else "N/A")
                    st.divider()
                
                # Pass Extra Context to AI
                extra_context = {
                    'earnings_date': earnings_date,
                    'market_trend': market_trend
                }
                
                # Use the new structured analysis from modules/llm.py directly
                patterns = enhance_ai_analysis_with_patterns(df)
                enhanced_metrics = calculate_advanced_metrics(df, info['current_price'])
                
                report = generate_gemini_analysis(
                    ticker_input, 
                    info, 
                    indicators, 
                    credit_data, 
                    strategic_data, 
                    enhanced_metrics=enhanced_metrics,
                    patterns=patterns,
                    extra_context=extra_context,
                    weekly_indicators=weekly_indicators,
                    news_data=news_data
                )
                
                # Sentiment Score Extraction for UI Display
                import re
                score_match = re.search(r'総合投資判断スコア:\s*(\d+)', report)
                total_score = int(score_match.group(1)) if score_match else None
                
                if total_score is not None:
                    score_color = "#64ffda" if total_score >= 80 else "#00d4ff" if total_score >= 60 else "#ffff00" if total_score >= 40 else "#ff4b4b"
                    st.markdown(f"""
                    <div style='background-color: rgba(10, 25, 47, 0.7); padding: 20px; border-radius: 10px; border: 1px solid {score_color}; margin-bottom: 20px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span style='font-size: 1.2rem; font-weight: bold; color: #ccd6f6;'>📊 AI 総合投資判断スコア</span>
                            <span style='font-size: 2.5rem; font-weight: bold; color: {score_color};'>{total_score}<small style='font-size: 1rem;'> / 100</small></span>
                        </div>
                        <div style='background-color: #233554; height: 12px; border-radius: 6px; margin-top: 10px;'>
                            <div style='background-color: {score_color}; width: {total_score}%; height: 12px; border-radius: 6px; transition: width 1s ease-in-out;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display News Brief in the AI tab
                if news_data:
                    with st.expander("📰 関連ニュース一覧"):
                        for n in news_data:
                            st.markdown(f"**[{n['publisher']}]({n['link']})**: {n['title']}  \n<small>{n['provider_publish_time']}</small>", unsafe_allow_html=True)
                
                # Export Button
                last_row = df.iloc[-1]
                simple_indicators = {
                    'rsi': last_row['RSI'],
                    'rsi_status': "過熱" if last_row['RSI'] > 70 else "底値" if last_row['RSI'] < 30 else "中立",
                    'macd_status': "GC" if last_row['MACD'] > last_row['MACD_Signal'] else "DC",
                    'bb_status': "BW" if last_row['Close'] > last_row['BB_Upper'] else "Normal"
                }
                report_text = generate_report_text(ticker_input, info['name'], report, strategic_data, simple_indicators)
                st.download_button(
                    label="📥 レポートをダウンロード (TXT)",
                    data=report_text,
                    file_name=f"report_{ticker_input}.txt",
                    mime="text/plain"
                )
                
                # Display detected patterns
                patterns = enhance_ai_analysis_with_patterns(df)
                all_patterns = patterns.get('candlestick_patterns', []) + patterns.get('chart_patterns', [])
                
                if all_patterns:
                    st.markdown("#### 🔍 検出されたパターン")
                    for p in all_patterns:
                        p_type = p.get('type', 'neutral')
                        icon = '🟢' if p_type == 'bullish' else '🔴' if p_type == 'bearish' else '⚪'
                        st.info(f"{icon} **{p['name']}**: {p['signal']}")
                
                # Feature: Technical Strength Meter
                st.markdown("#### ⚖️ テクニカル強度スコア")
                last_row = df.iloc[-1]
                score = 0
                # SMA Score (Trend)
                if last_row['SMA5'] > last_row['SMA25']: score += 25
                if last_row['SMA25'] > last_row['SMA75']: score += 25
                # RSI Score (Momentum)
                if 40 < last_row['RSI'] < 60: score += 25
                elif 30 < last_row['RSI'] <= 40 or 60 <= last_row['RSI'] < 70: score += 15
                # MACD Score
                if last_row['MACD'] > last_row['MACD_Signal']: score += 25
                
                score_color = "green" if score >= 75 else "orange" if score >= 50 else "red"
                st.markdown(f"""
                <div style='background-color: #1a1a1a; padding: 10px; border-radius: 5px; border-left: 5px solid {score_color};'>
                    <span style='font-size: 1.2rem;'>総合スコア: <b>{score} / 100</b></span>
                    <div style='background-color: #333; height: 10px; border-radius: 5px; margin-top: 5px;'>
                        <div style='background-color: {score_color}; width: {score}%; height: 10px; border-radius: 5px;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"<div style='background-color: #112240; padding: 15px; border-radius: 8px; margin-top: 15px;'>{report}</div>", unsafe_allow_html=True)
                
                # Feature: Backtest Integration
                st.markdown("---")
                st.markdown("### 📊 戦略バックテスト")
                backtest_results = backtest_strategy(df, strategic_data)
                st.markdown(format_backtest_results(backtest_results))
                
                st.markdown("---")
                show_alert_manager(ticker_input, info['name'], info['current_price'])
                
            # Tab 3: Portfolio
            with tab3:
                st.markdown("### 💰 ポートフォリオ管理")
                
                # Feature: Position Size Calculator
                with st.expander("🧮 適正ポジショニング計算機"):
                    col_calc1, col_calc2 = st.columns(2)
                    total_capital = col_calc1.number_input("運用資金 (円)", min_value=0, value=1000000, step=100000)
                    risk_per_trade = col_calc2.number_input("1トレードの許容損失 (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
                    
                    if strategic_data.get('entry_price') and strategic_data.get('stop_loss'):
                        entry = strategic_data['entry_price']
                        stop = strategic_data['stop_loss']
                        risk_per_share = abs(entry - stop)
                        
                        if risk_per_share and risk_per_share > 0:
                            allowed_loss = total_capital * (risk_per_trade / 100)
                            suggested_qty = int(allowed_loss / risk_per_share)
                            # Align to 100 shares (Standard in Japan)
                            suggested_qty_standard = (suggested_qty // 100) * 100
                            
                            st.info(f"""
                            **計算結果:**
                            - 1トレードの許容損失額: ¥{allowed_loss:,.0f}
                            - 1株あたりのリスク: ¥{risk_per_share:,.0f}
                            - 推奨購入株数: **{suggested_qty:,}株** (単元株ベース: {suggested_qty_standard:,}株)
                            - 想定投資額: ¥{suggested_qty * entry:,.0f}
                            """)
                        else:
                            st.warning("損切り価格とエントリー価格が同一です。")
                    else:
                        st.warning("戦略データ（エントリー・損切価格）が取得できないため計算できません。")

                # Input Form
                with st.form("portfolio_add"):
                    col1, col2, col3 = st.columns(3)
                    p_qty = col1.number_input("保有株数", min_value=0, step=100)
                    p_price = col2.number_input("平均取得単価", min_value=0.0, step=10.0, value=float(info['current_price']))
                    submitted = col3.form_submit_button("ポートフォリオに追加/更新")
                    if submitted and p_qty > 0:
                        add_to_portfolio(ticker_input, info['name'], p_qty, p_price)
                        st.success(f"{info['name']} をポートフォリオに追加しました")
                        st.rerun()

                # Display Logic
                current_prices = {ticker_input: info['current_price']}
                port_df, total_inv, total_val = get_portfolio_df(current_prices)
                
                if not port_df.empty:
                    # Summary Metrics
                    total_pl = total_val - total_inv
                    m1, m2, m3 = st.columns(3)
                    m1.metric("総投資額", f"¥{total_inv:,.0f}")
                    m2.metric("評価額合計", f"¥{total_val:,.0f}")
                    m3.metric("総損益", f"¥{total_pl:,.0f}", delta=f"{(total_pl/total_inv)*100:.1f}%" if total_inv else "0%")
                    
                    st.dataframe(port_df, width='stretch')
                    
                    del_code = st.selectbox("削除する銘柄", port_df['コード'].tolist())
                    if st.button("選択した銘柄を削除"):
                        remove_from_portfolio(del_code)
                        st.warning(f"{del_code} を削除しました")
                        st.rerun()
                else:
                    st.info("ポートフォリオは空です。上部のフォームから追加してください。")

            # Tab 4: Screener (NEW)
            with tab4:
                 st.markdown("### 🔍 市場スクリーニング")
                 st.caption("対象となる銘柄群を選択してスキャンを実行します。")
                 
                 from modules.screener import CATEGORIES
                 category = st.selectbox("銘柄カテゴリ", list(CATEGORIES.keys()))
                 
                 if st.button("🚀 スキャン開始"):
                     progress_text = f"{category} をスキャン中..."
                     my_bar = st.progress(0, text=progress_text)
                     
                     scan_result = scan_market(category_name=category, progress_bar=my_bar)
                     my_bar.empty()
                     
                     if not scan_result.empty:
                         st.success(f"{len(scan_result)}件の注目銘柄を検出しました！")
                         st.dataframe(
                             scan_result[['銘柄名', 'コード', '現在値', '前日比', '判定', 'シグナル', 'RSI']], 
                             use_container_width=True
                         )
                         st.info("💡 コードをコピーして検索バーに入力すると詳細分析が可能です。")
                     else:
                         st.warning("現在、特定のシグナル条件に合致する銘柄はありませんでした。")

            # Tab 5: Data
            with tab5:
                st.markdown("### 📊 詳細データ")
                enhanced_metrics = calculate_advanced_metrics(df, info['current_price'])
                if enhanced_metrics:
                    st.markdown(format_metrics_display(enhanced_metrics))
                
                if credit_data and credit_data.get('details'):
                     st.markdown("#### 信用需給・財務概況")
                     # st.json(credit_data['details']) # Replaced with cleaner display
                     details = credit_data['details']
                     
                     def format_val(v):
                         if isinstance(v, float): return f"{v:.2f}"
                         if isinstance(v, (int, float)) and v > 1000000:
                            if v >= 1e12: return f"{v/1e12:.2f}兆円"
                            return f"{v/1e8:.2f}億円"
                         return str(v)

                     # Show as a table for better readability on mobile
                     detail_df = pd.DataFrame([
                         {"項目": k, "値": format_val(v)} for k, v in details.items() if v is not None
                     ])
                     st.table(detail_df)
                
                st.markdown("#### 時系列データ")
                st.dataframe(df.tail(10), width='stretch')

        else:
            st.error("銘柄が見つかりません。")
