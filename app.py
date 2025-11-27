import streamlit as st
import pandas as pd
from modules.styles import get_custom_css
from modules.data import get_stock_data, get_credit_data
from modules.analysis import calculate_indicators, generate_ai_report
from modules.charts import create_main_chart, create_credit_chart
from modules.notifications import check_price_alerts, show_alert_manager
from modules.recommendations import find_similar_stocks, get_recommendation_reason
from modules.backtest import backtest_strategy, format_backtest_results
from modules.patterns import enhance_ai_analysis_with_patterns
from modules.enhanced_metrics import calculate_advanced_metrics, format_metrics_display

# Page Config
st.set_page_config(
    page_title="株価AI分析ダッシュボード",
    layout="centered", 
    initial_sidebar_state="collapsed"
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

# --- Sidebar: Watchlist ---
if 'watchlist' not in st.session_state:
    # Default: Toyota, Softbank, Sony (Store as dicts for names)
    st.session_state.watchlist = [
        {'code': '7203', 'name': 'トヨタ自動車'}, 
        {'code': '9984', 'name': 'ソフトバンクG'}, 
        {'code': '6758', 'name': 'ソニーG'}
    ]

if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False
    st.session_state.comparison_tickers = []

with st.sidebar:
    st.header("👀 ウォッチリスト")
    new_ticker = st.text_input("追加", placeholder="コード (例: 7203)")
    if st.button("リストに追加"):
        if new_ticker:
            # Check if already exists
            exists = any(item['code'] == new_ticker for item in st.session_state.watchlist)
            if not exists:
                st.session_state.watchlist.append({'code': new_ticker, 'name': '読み込み中...'})
    
    st.markdown("---")
    selected_from_list = None
    
    # Display Watchlist
    for i, item in enumerate(st.session_state.watchlist):
        label = f"{item['name']} ({item['code']})"
        if st.button(label, key=f"btn_{item['code']}"):
            selected_from_list = item['code']
            
    if st.button("🗑️ リストをクリア"):
        st.session_state.watchlist = []
        st.rerun()
    
    st.markdown("---")
    st.header("⚙️ 機能")
    
    # Comparison Mode Toggle
    comparison_mode = st.checkbox("📊 銘柄比較モード", value=st.session_state.comparison_mode)
    if comparison_mode != st.session_state.comparison_mode:
        st.session_state.comparison_mode = comparison_mode
        st.rerun()

# --- Main Content ---
st.title("株価AI分析ダッシュボード")

# Search Input (Sync with Sidebar)
default_ticker = selected_from_list if selected_from_list else "7203"
ticker_input = st.text_input("🔍 銘柄コード検索 (例: 7203)", value=default_ticker)

# Comparison Mode
if st.session_state.comparison_mode:
    st.info("📊 比較モード: 複数の銘柄を同時に表示します")
    compare_input = st.text_input("比較する銘柄コード (カンマ区切り)", placeholder="例: 7203,9984,6758")
    if compare_input:
        tickers = [t.strip() for t in compare_input.split(',')]
        
        # Create comparison table
        comparison_data = []
        for ticker in tickers:
            df, info = get_stock_data(ticker)
            if df is not None and info is not None:
                df = calculate_indicators(df)
                last = df.iloc[-1]
                comparison_data.append({
                    '銘柄名': info['name'],
                    'コード': ticker,
                    '現在値': f"¥{info['current_price']:,.1f}",
                    '前日比': f"{info['change_percent']:.2f}%",
                    'RSI': f"{last['RSI']:.1f}",
                    '25日線': '上' if info['current_price'] > last['SMA25'] else '下'
                })
        
        if comparison_data:
            st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)

if ticker_input and not st.session_state.comparison_mode:
    # Fetch Data
    with st.spinner('AIが市場データを分析中...'):
        df, info = get_stock_data(ticker_input)
        
        if df is not None and info is not None:
            # Check for price alerts
            alerts = check_price_alerts(info['current_price'], ticker_input, info['name'])
            for alert_info in alerts:
                st.warning(alert_info['message'])
                # Auto-remove triggered alerts
                from modules.notifications import remove_alert
                remove_alert(alert_info['alert'])
            
            # Update Watchlist Name if it exists and was "読み込み中..."
            for item in st.session_state.watchlist:
                if item['code'] == ticker_input:
                    item['name'] = info['name']
            
            # Calculate Indicators
            df = calculate_indicators(df)
            
            # Fetch Credit Data
            credit_df = get_credit_data(ticker_input)
            
            # --- Tabs Layout ---
            tab1, tab2, tab3 = st.tabs(["📈 チャート", "🤖 AI分析", "📊 データ"])
            
            # Tab 1: Chart & Price
            with tab1:
                st.markdown(f"### {info['name']} ({ticker_input})")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    price_color = "#00ff00" if info['change'] >= 0 else "#ff0000"
                    sign = "+" if info['change'] >= 0 else ""
                    st.markdown(f"""
                    <div style="font-size: 3.5rem; font-weight: bold; color: white; line-height: 1.2;">
                        ¥{info['current_price']:,.1f}
                    </div>
                    <div style="font-size: 1.2rem; color: {price_color}; margin-bottom: 20px;">
                        前日比: {sign}{info['change']:,.1f} ({sign}{info['change_percent']:.2f}%) 
                        {'↗' if info['change'] >= 0 else '↘'}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Generate Report & Get Strategic Data
                report, strategic_data = generate_ai_report(df, credit_df, info['name'], info)
                
                fig_main = create_main_chart(df, info['name'], strategic_data)
                if fig_main:
                    st.plotly_chart(fig_main, use_container_width=True)

            # Tab 2: AI Analysis
            with tab2:
                st.markdown("### 🤖 Gemini AI アナリスト")
                
                # Enhanced Pattern Detection
                patterns = enhance_ai_analysis_with_patterns(df)
                
                # Display detected patterns
                if patterns['candlestick_patterns'] or patterns['chart_patterns']:
                    st.markdown("#### 🔍 検出されたパターン")
                    
                    for pattern in patterns['candlestick_patterns']:
                        emoji = "🟢" if pattern['type'] == 'bullish' else "🔴" if pattern['type'] == 'bearish' else "⚪"
                        st.info(f"{emoji} **{pattern['name']}**: {pattern['signal']}")
                    
                    for pattern in patterns['chart_patterns']:
                        emoji = "🟢" if pattern['type'] == 'bullish' else "🔴"
                        st.warning(f"{emoji} **{pattern['name']}**: {pattern['signal']}")
                
                st.markdown("---")
                
                # Backtesting Section
                st.markdown("### 📊 戦略バックテスト")
                with st.spinner('戦略を検証中...'):
                    backtest_results = backtest_strategy(df, strategic_data, days=30)
                    if backtest_results:
                        formatted_results = format_backtest_results(backtest_results)
                        st.markdown(formatted_results)
                        
                        # Show trade history if available
                        if backtest_results['trades']:
                            with st.expander("📋 取引履歴を表示"):
                                trades_df = pd.DataFrame(backtest_results['trades'])
                                trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date']).dt.strftime('%Y-%m-%d')
                                trades_df['exit_date'] = pd.to_datetime(trades_df['exit_date']).dt.strftime('%Y-%m-%d')
                                st.dataframe(trades_df[['entry_date', 'entry_price', 'exit_date', 'exit_price', 'profit_pct', 'reason']], 
                                           use_container_width=True)
                
                st.markdown("---")
                
                # AI Report
                st.markdown(f"""
                <div style="background-color: #112240; padding: 20px; border-radius: 10px; border: 1px solid #233554;">
                    {report}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Similar Stocks Recommendation
                st.markdown("### 🔍 類似銘柄の推薦")
                with st.spinner('類似銘柄を分析中...'):
                    similar_stocks = find_similar_stocks(ticker_input, df, top_n=5)
                    
                    if similar_stocks:
                        st.markdown("この銘柄と似た値動きをする銘柄:")
                        for stock in similar_stocks:
                            similarity_pct = stock['similarity'] * 100
                            reason = get_recommendation_reason(stock)
                            
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.markdown(f"**{stock['name']} ({stock['code']})**")
                                st.caption(reason)
                            with col2:
                                st.metric("類似度", f"{similarity_pct:.0f}%")
                            with col3:
                                if st.button("表示", key=f"view_{stock['code']}"):
                                    st.session_state.selected_ticker = stock['code']
                                    st.rerun()
                    else:
                        st.info("類似銘柄が見つかりませんでした。")
                
                st.markdown("---")
                # Alert Manager
                show_alert_manager(ticker_input, info['name'], info['current_price'])

            # Tab 3: Data
            with tab3:
                st.markdown("### 📈 パフォーマンス指標")
                
                # Calculate performance metrics
                perf_col1, perf_col2, perf_col3 = st.columns(3)
                
                week_ago = df.iloc[-5]['Close'] if len(df) >= 5 else df.iloc[0]['Close']
                month_ago = df.iloc[-20]['Close'] if len(df) >= 20 else df.iloc[0]['Close']
                
                week_change = ((info['current_price'] - week_ago) / week_ago) * 100
                month_change = ((info['current_price'] - month_ago) / month_ago) * 100
                
                with perf_col1:
                    st.metric("1週間", f"{week_change:+.2f}%")
                with perf_col2:
                    st.metric("1ヶ月", f"{month_change:+.2f}%")
                with perf_col3:
                    volatility = df['Close'].pct_change().std() * 100
                    st.metric("ボラティリティ", f"{volatility:.2f}%")
                
                st.markdown("---")
                
                # Enhanced Metrics Display
                enhanced_metrics = calculate_advanced_metrics(df, info['current_price'])
                if enhanced_metrics:
                    metrics_display = format_metrics_display(enhanced_metrics)
                    st.markdown(metrics_display)
                
                st.markdown("---")
                st.markdown("### 📊 信用需給データ")
                if credit_df is not None:
                    st.dataframe(credit_df, use_container_width=True, height=200)
                    fig_credit = create_credit_chart(credit_df)
                    if fig_credit:
                        st.plotly_chart(fig_credit, use_container_width=True)
                else:
                    st.info("信用データは現在取得できません。")
                
                st.markdown("### 📋 株価データ (直近10日)")
                # Safe Column Selection
                cols_to_show = ['Open', 'High', 'Low', 'Close']
                if 'Volume' in df.columns:
                    cols_to_show.append('Volume')
                st.dataframe(df.tail(10)[cols_to_show], use_container_width=True)
            
        else:
            st.error("銘柄が見つかりません。コードを確認してください。")
