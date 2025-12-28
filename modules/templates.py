
"""
Templates for LINE Flex Messages.
Provides structured layouts for different notification types.
"""

def create_header_component(title, color="#000000"):
    return {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": title,
                "weight": "bold",
                "size": "xl",
                "color": color
            }
        ]
    }

def create_market_row(name, price, change):
    change_color = "#D32F2F" if change < 0 else "#2E7D32" # Red for down, Green for up
    change_icon = "▼" if change < 0 else "▲"
    return {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {"type": "text", "text": name, "size": "sm", "color": "#555555", "flex": 2},
            {"type": "text", "text": f"{price:,.0f}", "size": "sm", "color": "#111111", "align": "end", "flex": 2},
            {"type": "text", "text": f"{change_icon}{abs(change):,.0f}", "size": "sm", "color": change_color, "align": "end", "flex": 2}
        ]
    }

def get_daily_report_template(market_data, portfolio_data, analysis_text):
    """
    Constructs a Flex Message bubble for the daily report.
    """
    
    # 1. Header
    header = {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {"type": "text", "text": "📊 株山AI 朝刊", "weight": "bold", "size": "xl", "color": "#ffffff"},
            {"type": "text", "text": "本日の市場とポートフォリオ", "size": "xs", "color": "#eeeeee"}
        ],
        "backgroundColor": "#2768C1",
        "paddingAll": "20px"
    }

    # 2. Market Section
    market_rows = []
    if market_data:
        market_rows.append({"type": "text", "text": "市場概況", "weight": "bold", "size": "sm", "margin": "md"})
        market_rows.append({"type": "separator", "margin": "sm"})
        for name, data in market_data.items():
            market_rows.append(create_market_row(name, data['price'], data['change']))

    # 3. Portfolio Section
    portfolio_rows = []
    if portfolio_data:
        portfolio_rows.append({"type": "separator", "margin": "lg"})
        portfolio_rows.append({"type": "text", "text": "ポートフォリオ", "weight": "bold", "size": "sm", "margin": "md"})
        
        total_val = portfolio_data.get('total_value', 0)
        total_pl = portfolio_data.get('total_pl', 0)
        pl_color = "#D32F2F" if total_pl < 0 else "#2E7D32"
        
        portfolio_rows.append({
            "type": "box", 
            "layout": "horizontal", 
            "contents": [
                {"type": "text", "text": "評価額計", "size": "sm", "color": "#555555"},
                {"type": "text", "text": f"¥{total_val:,.0f}", "size": "md", "weight": "bold", "align": "end"}
            ]
        })
        portfolio_rows.append({
            "type": "box", 
            "layout": "horizontal", 
            "contents": [
                {"type": "text", "text": "含み損益", "size": "sm", "color": "#555555"},
                {"type": "text", "text": f"¥{total_pl:+,.0f}", "size": "md", "weight": "bold", "color": pl_color, "align": "end"}
            ]
        })

    # 4. Analysis / Message
    analysis_ui = []
    if analysis_text:
        analysis_ui.append({"type": "separator", "margin": "lg"})
        analysis_ui.append({"type": "text", "text": "AIコメント", "weight": "bold", "margin": "md", "size": "sm"})
        analysis_ui.append({"type": "text", "text": analysis_text, "wrap": True, "size": "xs", "color": "#666666", "maxLines": 5})

    # 5. Footer (Link)
    # Note: Replace with actual app URL if available
    footer = {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "button",
                "action": {"type": "uri", "label": "アプリで詳細を見る", "uri": "https://kabuzan-app.streamlit.app/"},
                "style": "primary",
                "color": "#2768C1",
                "height": "sm"
            }
        ]
    }

    body_contents = market_rows + portfolio_rows + analysis_ui

    bubble = {
        "type": "bubble",
        "header": header,
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": body_contents
        },
        "footer": footer
    }

    return {
        "type": "flex",
        "altText": "株山AI 朝刊レポート",
        "contents": bubble
    }

def get_alert_template(ticker, name, current_price, condition, limit_price):
    """
    Template for price alerts and guardian alerts.
    """
    color = "#D32F2F" if condition == "allowance" else "#F57F17" # Red for loss cut/danger, Orange for alert
    title = "損切アラート" if condition == "loss_cut" else "利確チャンス" if condition == "profit" else "価格アラート"
    
    header_color = "#D32F2F" if "損切" in title else "#2E7D32" if "利確" in title else "#F9A825"

    return {
        "type": "flex",
        "altText": f"【アラート】{name}",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "🔔 " + title, "weight": "bold", "color": "#FFFFFF"}
                ],
                "backgroundColor": header_color
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"{name} ({ticker})", "weight": "bold", "size": "lg"},
                    {"type": "separator", "margin": "md"},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {"type": "text", "text": "現在値", "size": "sm", "color": "#555555"},
                            {"type": "text", "text": f"¥{current_price:,.0f}", "size": "xl", "align": "end", "weight": "bold"}
                        ]
                    },
                     {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "設定条件", "size": "xs", "color": "#999999"},
                            {"type": "text", "text": f"{limit_price}円 {'以下' if '損切' in title or '下' in title else '以上'}", "size": "xs", "align": "end", "color": "#999999"}
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button", 
                        "action": {"type": "uri", "label": "チャートを確認", "uri": f"https://kabuzan-app.streamlit.app/?ticker={ticker}"},
                        "style": "secondary"
                    }
                ]
            }
        }
    }
