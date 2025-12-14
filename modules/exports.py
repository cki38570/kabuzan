from datetime import datetime

def generate_report_text(ticker, name, report_content, strategic_data, indicators):
    """
    Generate a formatted text report for download.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    text = f"""
==================================================
株価AI分析レポート
==================================================
作成日時: {timestamp}
銘柄: {name} ({ticker})

【戦略的概要】
判断: {strategic_data.get('trend_desc', 'N/A')}
推奨アクション: {strategic_data.get('action_msg', 'N/A')}
--------------------------------------------------
エントリー推奨: ¥{strategic_data.get('entry_price', 0):,}
利確目標:       ¥{strategic_data.get('target_price', 0):,}
損切目安:       ¥{strategic_data.get('stop_loss', 0):,}
リスクリワード: {strategic_data.get('risk_reward', 0):.2f}
--------------------------------------------------

【テクニカル指標】
RSI: {indicators.get('rsi', 0):.1f} ({indicators.get('rsi_status', '-')})
MACD: {indicators.get('macd_status', '-')}
Bバンド: {indicators.get('bb_status', '-')}

【AI詳細分析】
{report_content}

==================================================
※本レポートはAIによる自動生成です。投資判断は自己責任で行ってください。
"""
    return text.strip()
