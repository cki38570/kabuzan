import streamlit as st
from datetime import datetime

def check_price_alerts(current_price, ticker_code, ticker_name):
    """
    Check if current price triggers any alerts.
    Returns list of triggered alerts.
    """
    if 'price_alerts' not in st.session_state:
        st.session_state.price_alerts = []
    
    triggered = []
    for alert in st.session_state.price_alerts:
        if alert['ticker'] != ticker_code:
            continue
            
        if alert['type'] == 'above' and current_price >= alert['price']:
            triggered.append({
                'message': f"🔔 {ticker_name} が目標価格 ¥{alert['price']:,} を突破しました！ (現在: ¥{current_price:,.1f})",
                'alert': alert
            })
        elif alert['type'] == 'below' and current_price <= alert['price']:
            triggered.append({
                'message': f"⚠️ {ticker_name} が警戒価格 ¥{alert['price']:,} を下回りました！ (現在: ¥{current_price:,.1f})",
                'alert': alert
            })
    
    return triggered

def add_price_alert(ticker_code, ticker_name, price, alert_type):
    """
    Add a price alert.
    alert_type: 'above' or 'below'
    """
    if 'price_alerts' not in st.session_state:
        st.session_state.price_alerts = []
    
    st.session_state.price_alerts.append({
        'ticker': ticker_code,
        'ticker_name': ticker_name,
        'price': price,
        'type': alert_type,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
    })

def remove_alert(alert):
    """Remove a specific alert"""
    if 'price_alerts' not in st.session_state:
        return
    
    st.session_state.price_alerts = [
        a for a in st.session_state.price_alerts 
        if not (a['ticker'] == alert['ticker'] and 
                a['price'] == alert['price'] and 
                a['type'] == alert['type'])
    ]

def show_alert_manager(ticker_code, ticker_name, current_price):
    """
    Display alert management UI in sidebar or expander.
    """
    st.markdown("### 🔔 価格アラート設定")
    
    col1, col2 = st.columns(2)
    with col1:
        alert_price = st.number_input(
            "目標価格 (円)", 
            min_value=0.0, 
            value=float(current_price * 1.05),
            step=10.0,
            key=f"alert_price_{ticker_code}"
        )
    with col2:
        alert_type = st.selectbox(
            "条件",
            options=['above', 'below'],
            format_func=lambda x: '以上になったら通知' if x == 'above' else '以下になったら通知',
            key=f"alert_type_{ticker_code}"
        )
    
    if st.button("アラート追加", key=f"add_alert_{ticker_code}"):
        add_price_alert(ticker_code, ticker_name, alert_price, alert_type)
        st.success(f"アラートを追加しました: ¥{alert_price:,}")
    
    # Show existing alerts
    if 'price_alerts' in st.session_state:
        ticker_alerts = [a for a in st.session_state.price_alerts if a['ticker'] == ticker_code]
        if ticker_alerts:
            st.markdown("**設定中のアラート:**")
            for i, alert in enumerate(ticker_alerts):
                condition = "以上" if alert['type'] == 'above' else "以下"
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"¥{alert['price']:,} {condition}")
                with col2:
                    if st.button("削除", key=f"del_alert_{ticker_code}_{i}"):
                        remove_alert(alert)
                        st.rerun()
