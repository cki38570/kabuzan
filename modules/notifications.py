import streamlit as st

def show_notification_settings():
    """Display notification settings UI in sidebar."""
    st.markdown("### 🔔 通知設定 (シミュレーション)")
    
    notify_line = st.checkbox("LINE通知", value=st.session_state.get('notify_line', False))
    if notify_line:
        st.session_state.line_token = st.text_input("LINE Notify Token", type="password", 
                                                  value=st.session_state.get('line_token', ''),
                                                  placeholder="トークンを入力 (任意)")
        
    notify_email = st.checkbox("メール通知", value=st.session_state.get('notify_email', False))
    if notify_email:
        st.session_state.email_addr = st.text_input("メールアドレス", 
                                                  value=st.session_state.get('email_addr', ''),
                                                  placeholder="example@mail.com")
        
    st.session_state.notify_line = notify_line
    st.session_state.notify_email = notify_email
    
    if st.button("テスト通知を送信"):
        send_test_notification()

def send_test_notification():
    """Simulate sending a notification."""
    methods = []
    if st.session_state.get('notify_line'):
        methods.append("LINE")
    if st.session_state.get('notify_email'):
        methods.append("メール")
    
    if not methods:
        st.warning("通知方法が選択されていません。")
        return
        
    st.toast(f"🔔 {'/'.join(methods)}にテスト通知を送信しました！", icon="✅")
    
    # Simulation Logic
from modules.line import send_line_notification
from modules.news import get_stock_news
from modules.llm import analyze_news_impact
import datetime
import os
import json

def process_morning_notifications():
    """
    Check if morning notification was already sent today.
    If not, analyze news for portfolio and send to LINE.
    """
    if not st.session_state.get('notify_line') or not st.session_state.get('line_token'):
        return
    
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if st.session_state.get('last_notified_date') == today:
        return
    
    # Check if it's "morning" (e.g., 6:00 - 10:00) - For simulation, we just check if it's the first run of the day
    with st.spinner('朝のニュース分析を送信中...'):
        from modules.portfolio import get_portfolio_data
        portfolio = get_portfolio_data()
        
        if not portfolio:
            return
            
        news_data_map = {}
        for item in portfolio:
            news = get_stock_news(item['ticker'])
            news_data_map[item['ticker']] = news
            
        summary = analyze_news_impact(portfolio, news_data_map)
        
        full_msg = f"\n☀️ おはようございます！本日のニュース要約です。\n\n{summary}"
        success, msg = send_line_notification(full_msg, st.session_state.line_token)
        
        if success:
            st.session_state.last_notified_date = today
            st.toast("☀️ 朝の要約通知をLINEに送信しました！")
        else:
            st.error(f"LINE通知エラー: {msg}")

def check_and_notify(ticker, price, alert_price, condition):
    """
    Check price condition and trigger notification if met.
    Returns True if notification sent.
    """
    triggered = False
    
    if condition == 'above' and price >= alert_price:
        triggered = True
    elif condition == 'below' and price <= alert_price:
        triggered = True
        
    if triggered:
        msg = f"🔔 アラート: {ticker} が {alert_price}円 {'以上' if condition == 'above' else '以下'} になりました！ (現在: {price}円)"
        st.toast(msg, icon="🚨")
        # In real implementation: send_line(msg), send_email(msg)
        return True
    
    return False

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
