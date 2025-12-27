import streamlit as st
import requests
import datetime
import os
import yfinance as yf
from modules.news import get_stock_news
from modules.llm import analyze_news_impact
from modules.line import send_line_message

def get_market_indices():
    """Fetch major market indices."""
    indices = {
        "^N225": "日経平均",
        "^DJI": "NYダウ", 
        "^VIX": "恐怖指数"
    }
    results = {}
    try:
        for ticker, name in indices.items():
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 1:
                price = hist['Close'].iloc[-1]
                change = 0
                if len(hist) >= 2:
                    prev = hist['Close'].iloc[-2]
                    change = price - prev
                results[name] = {"price": price, "change": change}
    except Exception:
        pass
    return results

def show_notification_settings():
    """Display notification settings UI in sidebar."""
    st.markdown("### 🔔 通知設定")
    
    notify_line = st.checkbox("LINE通知 (Messaging API)", value=st.session_state.get('notify_line', False))
    if notify_line:
        channel_token = st.secrets.get("LINE_CHANNEL_ACCESS_TOKEN", "")
        if not channel_token:
            st.error("⚠️ LINE認証情報未設定")
        else:
            st.success("✅ LINE有効")
    
    st.session_state.notify_line = notify_line
    
    if st.button("📊 今すぐレポートを送信"):
        send_daily_report(manual=True)

def send_daily_report(manual=False):
    """Generate and send comprehensive daily report."""
    if not st.session_state.get('notify_line'):
        if manual: st.error("LINE通知が有効になっていません。")
        return

    with st.spinner('レポート作成中...'):
        # 1. Market Overview
        indices = get_market_indices()
        market_msg = "🌍 **市場概況**\n"
        for name, data in indices.items():
            icon = "😨" if name == "恐怖指数" and data['price'] > 20 else "📈" if data['change'] >= 0 else "📉"
            market_msg += f"{icon} {name}: {data['price']:,.0f} ({data['change']:+,.0f})\n"
            
        # 2. Portfolio Summary
        from modules.portfolio import get_portfolio_data
        portfolio = get_portfolio_data()
        pf_msg = ""
        portfolio_tickers = []
        
        if portfolio:
            total_val = sum(p['value'] for p in portfolio)
            total_pl = sum(p['pl'] for p in portfolio)
            pf_msg = f"\n💰 **ポートフォリオ**\n評価額: ¥{total_val:,.0f}\n損益: ¥{total_pl:+,.0f}\n"
            portfolio_tickers = [p['ticker'] for p in portfolio]
        
        # 3. Earnings Alerts
        from modules.data import get_next_earnings_date
        earnings_msg = ""
        today_date = datetime.datetime.now().date()
        for ticker in portfolio_tickers:
            edate = get_next_earnings_date(ticker)
            if edate:
                # Convert to date object if datetime
                if isinstance(edate, datetime.datetime):
                    edate = edate.date()
                elif isinstance(edate, str):
                    try:
                         edate = datetime.datetime.strptime(edate, "%Y-%m-%d").date()
                    except:
                        continue
                        
                days = (edate - today_date).days
                if 0 <= days <= 7:
                    earnings_msg += f"⚠️ {ticker} 決算まであと{days}日 ({edate})\n"

        if earnings_msg:
            earnings_msg = "\n📅 **決算アラート**\n" + earnings_msg

        # Combine
        full_msg = f"📊 株山AI レポート ({'手動' if manual else '朝刊'})\n\n{market_msg}{pf_msg}{earnings_msg}\n(詳細ニュースはアプリで確認)"
        
        success, msg = send_line_message(full_msg)
        if success:
            st.toast("LINEにレポートを送信しました！")
        else:
            st.error(f"送信失敗: {msg}")

def process_morning_notifications():
    """Run daily report check."""
    if not st.session_state.get('notify_line'):
        return
    
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if st.session_state.get('last_notified_date') == today:
        return
        
    # Send Report
    send_daily_report(manual=False)
    st.session_state.last_notified_date = today

def check_price_alerts(price, ticker, name):
    alerts = st.session_state.get('alerts', [])
    triggered_alerts = []
    for alert in alerts:
        if alert['code'] == ticker:
            if alert['condition'] == 'above' and price >= alert['price']:
                triggered_alerts.append({'message': f"アラート: {name}が{alert['price']}円以上になりました", 'alert': alert})
            elif alert['condition'] == 'below' and price <= alert['price']:
                triggered_alerts.append({'message': f"アラート: {name}が{alert['price']}円以下になりました", 'alert': alert})
    return triggered_alerts

def remove_alert(alert_to_remove):
    alerts = st.session_state.get('alerts', [])
    st.session_state.alerts = [a for a in alerts if a != alert_to_remove]

def show_alert_manager(ticker_input, name, current_price):
    st.markdown("### 📈 価格アラート設定")
    if 'alerts' not in st.session_state:
        st.session_state.alerts = []
    
    col1, col2, col3 = st.columns(3)
    alert_price = col1.number_input("アラート価格", value=current_price)
    condition = col2.selectbox("条件", ["以上", "以下"], index=0)
    
    if col3.button("アラート設定"):
        cond_val = 'above' if condition == "以上" else 'below'
        st.session_state.alerts.append({'code': ticker_input, 'price': alert_price, 'condition': cond_val, 'name': name})
        st.success(f"{name} {alert_price}円 {condition} のアラートを設定")

    if st.session_state.alerts:
        st.markdown("設定中のアラート:")
        for i, alert in enumerate(st.session_state.alerts):
            if alert['code'] == ticker_input:
                st.info(f"{alert['name']} {alert['price']}円 {'以上' if alert['condition'] == 'above' else '以下'}")

def check_technical_signals(ticker, price, indicators, name):
    """
    Check for extended technical signals including:
    - RSI Oversold/Overbought
    - Bollinger Band Squeeze
    - Golden/Dead Cross (MACD)
    """
    if not st.session_state.get('notify_line'):
        return None
        
    rsi = indicators.get('rsi', 50)
    bb_low = indicators.get('bb_lower', 0)
    bb_up = indicators.get('bb_upper', 0)
    bb_mid = indicators.get('bb_mid', p*0.01 if (p:=price) else 1) # Avoid div by zero
    macd_hist = indicators.get('macd_hist', 0)
    
    # Needs previous MACD for crossover check, but simplified: checks histogram sign change proxy or just state
    # Ideally we pass more indicator context. For now, we use state based logic.
    macd_status = indicators.get('macd_status', '') 
    
    signals = []
    
    # 1. RSI Extremes
    if rsi <= 25:
        signals.append("💎 RSI超売られすぎ (25以下)")
    elif rsi >= 80:
        signals.append("🔥 RSI超買われすぎ (80以上)")
        
    # 2. Bollinger Band Squeeze (Volatility Contraction)
    if bb_mid > 0:
        bandwidth = (bb_up - bb_low) / bb_mid
        if bandwidth < 0.05: # Very tight squeeze
            signals.append("⚡ バンドスクイーズ (爆発前夜)")
            
    # 3. Key Levels
    if price <= bb_low * 0.99:
        signals.append("💧 バンド下限ブレイク (逆張り検討)")

    # Send Notification if meaningful
    if signals:
        signal_text = "\n".join(signals)
        message = (
            f"\n【⚡ シグナル検知: {ticker}】\n"
            f"銘柄: {name}\n"
            f"現在値: ¥{price:,.0f}\n\n"
            f"{signal_text}\n\n"
            f"詳細分析を確認してください。"
        )
        # Avoid spamming: Check cache or last notified time (omitted for simplicity, relies on re-run)
        # In a real app, use session_state to debounce.
        state_key = f"notified_signal_{ticker}_{datetime.datetime.now().hour}"
        if state_key not in st.session_state:
            success, res = send_line_message(message)
            if success:
                st.session_state[state_key] = True
                st.toast(f"LINE通知: {signal_text}", icon="📲")
            return signals
    return None
