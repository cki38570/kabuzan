import streamlit as st
import requests
import datetime
import os
import yfinance as yf
from modules.news import get_stock_news
from modules.llm import analyze_news_impact
from modules.line import send_line_message
from modules.templates import get_daily_report_template, get_alert_template

# Rate Limiting Cache
try:
    from diskcache import Cache
    # Cache stored in .cache_notifications directory
    notification_cache = Cache('./.cache_notifications')
except ImportError:
    notification_cache = None

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
    from modules.storage import storage
    st.markdown("### 🔔 通知設定")
    
    # Load settings from storage to persist state
    settings = storage.load_settings()
    current_notify_state = settings.get('notify_line', False)
    
    # Checkbox with persisted state
    notify_line = st.checkbox("LINE通知 (Messaging API)", value=current_notify_state)
    
    # Save if changed
    if notify_line != current_notify_state:
        settings['notify_line'] = notify_line
        storage.save_settings(settings)
        # Update session state immediately
        st.session_state.notify_line = notify_line
        st.toast(f"LINE通知を {'ON' if notify_line else 'OFF'} にしました")
    else:
        # Sync session state
        st.session_state.notify_line = notify_line

    if notify_line:
        # Auth Check with Fallback for GitHub Actions (Headless)
        channel_token = None
        try:
             channel_token = st.secrets.get("LINE_CHANNEL_ACCESS_TOKEN", "")
        except:
             pass
             
        if not channel_token:
             # Fallback to Environment Variable
             channel_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
             
        if not channel_token:
            st.error("⚠️ LINE認証情報未設定")
        else:
            # Mask token for security
            masked = channel_token[:4] + "*" * 4
            st.caption(f"✅ LINE有効 (Token: {masked})")
    
    # Advanced Features UI
    if notify_line:
        with st.expander("🛡️ PFガーディアン設定", expanded=False):
            # Settings are already loaded above
            
            p_target = st.number_input("利確目安 (%)", value=float(settings.get("profit_target", 10.0)), step=1.0)
            l_limit = st.number_input("損切目安 (%)", value=float(settings.get("stop_loss_limit", -5.0)), step=1.0)
            
            if st.button("設定を保存"):
                settings["profit_target"] = p_target
                settings["stop_loss_limit"] = l_limit
                if storage.save_settings(settings):
                    st.success("保存しました")
                else:
                    st.error("保存失敗")
    
    st.divider()
    if st.button("🧪 ストレージ接続テスト"):
        test_settings = settings.copy()
        test_settings['test_connection'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        results = []
        if storage.save_settings(test_settings):
            results.append("✅ 設定の書き込みに成功しました。")
        else:
            results.append("❌ 設定の書き込みに失敗しました。")
            
        if storage.save_notification_log("test_connection", test_settings['test_connection']):
            results.append("✅ 通知ログ(notifications_log)の書き込みに成功しました。")
        else:
            results.append("❌ 通知ログの書き込みに失敗しました。シートが存在するか確認してください。")
        
        for r in results: st.markdown(r)
        st.json(storage.load_settings())

def send_daily_report(manual=False):
    """Generate and send comprehensive daily report with Advanced Features."""
    if not st.session_state.get('notify_line'):
        if manual: st.error("LINE通知が有効になっていません。")
        return

    with st.spinner('高度な分析レポートを作成中...'):
        from modules.storage import storage
        from modules.data import get_next_earnings_date
        
        # 0. Load Data
        settings = storage.load_settings()
        profit_target = settings.get('profit_target', 10.0)
        stop_loss_limit = settings.get('stop_loss_limit', -5.0)
        
        indices = get_market_indices()
        portfolio_raw = storage.load_portfolio()
        portfolio = []
        alerts = storage.load_alerts()

        # Enrich portfolio with current prices
        if portfolio_raw:
            tickers = [p['code'] for p in portfolio_raw] # Note: portfolio.json uses 'code' not 'ticker'
            # Batch fetch could be better but sticking to loop for simplicity/robustness with existing code style
            # OR use yf.download for speed if list is long.
            # Let's use individual Ticker for consistency with other parts for now.
            for p in portfolio_raw:
                try:
                    ticker = p.get('code')
                    qty = float(p.get('quantity', 0))
                    avg_price = float(p.get('avg_price', 0))
                    
                    # Fetch price
                    stock = yf.Ticker(ticker)
                    # fast_info is faster
                    current_price = stock.fast_info.last_price
                    if not current_price:
                         hist = stock.history(period="1d")
                         if not hist.empty:
                             current_price = hist['Close'].iloc[-1]
                         else:
                             current_price = avg_price # Fallback
                    
                    val = current_price * qty
                    cost = avg_price * qty
                    pl = val - cost
                    pl_pct = (pl / cost * 100) if cost else 0
                    
                    p_enriched = p.copy()
                    p_enriched.update({
                        'ticker': ticker, # Ensure 'ticker' key exists as used later
                        'current_price': current_price,
                        'value': val,
                        'pl': pl,
                        'pl_pct': pl_pct,
                        'name': p.get('name', ticker)
                    })
                    portfolio.append(p_enriched)
                except Exception as e:
                    print(f"Error enriching {p.get('code')}: {e}")
                    # Keep raw but add defaults to avoid KeyError later
                    p_enriched = p.copy()
                    p_enriched.update({'ticker': p.get('code'), 'value': 0, 'pl':0, 'pl_pct':0})
                    portfolio.append(p_enriched)
        
        # 1. Market Overview
        # objects are already in correct format for template: {"Name": {"price": X, "change": Y}}
        market_data = indices
            
        # 2. Portfolio Guardian (Enhanced)
        portfolio_data = {}
        guardian_msg = ""
        portfolio_tickers = []
        
        if portfolio:
            total_val = sum(p['value'] for p in portfolio)
            total_pl = sum(p['pl'] for p in portfolio)
            portfolio_data = {"total_value": total_val, "total_pl": total_pl}
            portfolio_tickers = [p['ticker'] for p in portfolio]
            
            # Check individual positions for Guardian
            warnings = []
            goods = []
            for p in portfolio:
                pl_pct = p['pl_pct']
                if pl_pct >= profit_target:
                    goods.append(f"🎉 利確推奨: {p['name']} (+{pl_pct:.1f}%)")
                elif pl_pct <= stop_loss_limit:
                    warnings.append(f"🚑 損切検討: {p['name']} ({pl_pct:.1f}%)")
            
            if goods or warnings:
                guardian_msg = "\n🛡️ **ガーディアン通知**\n" + "\n".join(goods + warnings) + "\n"
        
        # 3. Sniper Alerts (Check Scenarios)
        # ... (Existing placeholder logic retained)
        # Ideally fetching data here.
 
        # 4. AI Scanner (News Impact Analysis)
        scanner_msg = ""
        try:
             # Fetch news for portfolio tickers
             news_map = {}
             if portfolio_tickers:
                 with st.spinner('📰 関連ニュースを収集中...'):
                     for ticker in portfolio_tickers[:5]: # Cap at 5 to save time/tokens
                         news = get_stock_news(ticker)
                         if news:
                             news_map[ticker] = news
                 
                 # Analyze Impact
                 if news_map:
                     ai_comment = analyze_news_impact(portfolio, news_map)
                     scanner_msg = f"\n🔭 **AI市場分析**\n{ai_comment}\n"
                 else:
                     scanner_msg = "\n🔭 **AI市場分析**\n特筆すべき関連ニュースはありませんでした。\n"
             else:
                 scanner_msg = "\n🔭 **AI市場分析**\nポートフォリオが空のため、分析をスキップしました。\n"
        except Exception as e:
            print(f"AI/News Error: {e}")
            scanner_msg = "\n⚠️ AI分析中にエラーが発生しました。\n"
 
        # 5. Earnings Alerts
        earnings_msg = ""
        today_date = datetime.datetime.now().date()
        for ticker in portfolio_tickers:
            edate = get_next_earnings_date(ticker)
            if edate:
                if isinstance(edate, datetime.datetime): edate = edate.date()
                elif isinstance(edate, str):
                    try: edate = datetime.datetime.strptime(edate, "%Y-%m-%d").date()
                    except: continue
                days = (edate - today_date).days
                if 0 <= days <= 7:
                    earnings_msg += f"⚠️ {ticker} 決算まであと{days}日 ({edate})\n"
 
        if earnings_msg:
            earnings_msg = "\n📅 **決算アラート**\n" + earnings_msg
 
        # Combine Analysis Text
        # We combine the text-based parts (Guardian, Earnings, Scanner, extra market info) into the analysis section
        # The main market indices and portfolio summary are now visual cards.
        
        analysis_text = f"{guardian_msg}{earnings_msg}{scanner_msg}".strip()
        if not analysis_text:
            analysis_text = "特筆すべきアラートはありません。"
 
        # Create Flex Message
        flex_message = get_daily_report_template(market_data, portfolio_data, analysis_text)
        
        # Send
        success, msg = send_line_message(payload_messages=[flex_message])
        if success:
            st.toast("高度な分析レポート(Flex)を送信しました！")
        else:
            st.error(f"送信失敗: {msg}")
 
def process_morning_notifications():
    """
    Run daily report check.
    Uses persistent storage to ensure report is sent only once per day.
    """
    from modules.storage import storage
    
    # 1. Load settings (Persisted)
    settings = storage.load_settings()
    notify_enabled = settings.get('notify_line', False)
    
    # Sync to session state for UI checkbox
    if 'notify_line' not in st.session_state:
        st.session_state.notify_line = notify_enabled
    
    # If notifications disabled, exit
    if not notify_enabled:
        return
    
    # 2. Check Time and Date
    # Time window guard: 9 AM to 11 PM JST
    now_jst = datetime.datetime.now()
    if not (9 <= now_jst.hour <= 23):
        print(f"Skipping daily report: Outside active hours (Current: {now_jst.hour}h JST).")
        return
 
    today = now_jst.strftime('%Y-%m-%d')
    # Ensure last_sent is compared as a string
    last_sent = str(settings.get('last_daily_report_date', ''))
    
    if last_sent == today:
        print(f"Skipping daily report: Already sent today ({today}).")
        return
        
    # 3. Send Report & Update Storage
    print(f"Triggering Daily Report for {today} (Last sent: {last_sent or 'Never'})...")
    send_daily_report(manual=False)
    
    # Save new date
    settings['last_daily_report_date'] = today
    if storage.save_settings(settings):
        print(f"Successfully updated last_daily_report_date to {today}")
    else:
        print(f"FAILED to update last_daily_report_date to {today}")
    
    # Sync session state
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
    Check for extended technical signals and send notifications if enabled.
    Includes persistent rate limiting via Google Sheets to prevent spam 
    even after environment restarts.
    """
    if not st.session_state.get('notify_line'):
        return None
        
    rsi = indicators.get('rsi', 50)
    bb_low = indicators.get('bb_lower', 0)
    bb_up = indicators.get('bb_upper', 0)
    bb_mid = indicators.get('bb_mid', p*0.01 if (p:=price) else 1)
    
    signals = []
    
    # 1. RSI Extremes
    if rsi <= 25:
        signals.append("💎 RSI超売られすぎ (25以下)")
    elif rsi >= 80:
        signals.append("🔥 RSI超買われすぎ (80以上)")
        
    # 2. Bollinger Band Squeeze
    if bb_mid > 0:
        bandwidth = (bb_up - bb_low) / bb_mid
        if bandwidth < 0.05:
            signals.append("⚡ バンドスクイーズ (変動予兆)")
            
    # 3. Key Levels
    if price <= bb_low * 0.99:
        signals.append("💧 バンド下限ブレイク (逆張り検討)")
 
    # Send Notification Logic
    if signals:
        signal_text = "\n".join(signals)
        message = (
            f"\n【⚡ シグナル検知: {ticker}】\n"
            f"銘柄: {name}\n"
            f"現在値: ¥{price:,.0f}\n\n"
            f"{signal_text}\n\n"
            f"詳細分析を確認してください。"
        )
        
        # Rate Limit Check (Persistent via Storage)
        # 1 Hour Cooldown per Ticker
        should_send = True
        cache_key = f"signal_{ticker}"
        
        from modules.storage import storage
        log = storage.load_notification_log()
        last_sent_str = log.get(cache_key)
        
        import time
        now = time.time()
        
        if last_sent_str:
            try:
                last_sent = float(last_sent_str)
                if (now - last_sent) < 3600:
                    should_send = False
            except: pass
        
        if should_send:
            success, res = send_line_message(message)
            if success:
                storage.save_notification_log(cache_key, str(now))
                st.toast(f"LINE通知: {signal_text}", icon="📲")
        
        return signals
    return None
