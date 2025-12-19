import pandas as pd
import numpy as np

def backtest_strategy(df, strategic_data, days=30):
    """
    Backtest the AI trading strategy over the last N days.
    Returns performance metrics and trade history.
    """
    if df is None or len(df) < days:
        return None
    
    # Get recent data
    recent_df = df.tail(days).copy()
    
    # Extract strategy parameters
    target_price = strategic_data.get('target_price', 0)
    stop_loss = strategic_data.get('stop_loss', 0)
    
    # Simulate trades
    trades = []
    in_position = False
    entry_price = 0
    entry_date = None
    
    for idx, row in recent_df.iterrows():
        current_price = row['Close']
        
        if not in_position:
            # Check for entry signal (simplified: buy when price is near support)
            # In real scenario, this would be based on actual buy zone
            support_level = strategic_data.get('stop_loss', current_price * 0.95)
            
            # Entry: Price is within 2% of support and RSI < 50
            if 'RSI' in row and not pd.isna(row['RSI']):
                if current_price <= support_level * 1.02 and row['RSI'] < 50:
                    in_position = True
                    entry_price = current_price
                    entry_date = idx
        else:
            # Check for exit signal
            exit_triggered = False
            exit_reason = ""
            exit_price = current_price
            
            # Take profit
            if target_price and target_price > 0 and current_price >= target_price:
                exit_triggered = True
                exit_reason = "利確"
                exit_price = target_price
            
            # Stop loss
            elif stop_loss and stop_loss > 0 and current_price <= stop_loss:
                exit_triggered = True
                exit_reason = "損切"
                exit_price = stop_loss
            
            if exit_triggered:
                profit = exit_price - entry_price
                profit_pct = (profit / entry_price) * 100
                
                trades.append({
                    'entry_date': entry_date,
                    'entry_price': entry_price,
                    'exit_date': idx,
                    'exit_price': exit_price,
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'reason': exit_reason
                })
                
                in_position = False
    
    # Calculate metrics
    if not trades:
        return {
            'total_trades': 0,
            'win_rate': 0,
            'avg_profit': 0,
            'avg_loss': 0,
            'total_return': 0,
            'max_drawdown': 0,
            'trades': []
        }
    
    trades_df = pd.DataFrame(trades)
    
    winning_trades = trades_df[trades_df['profit'] > 0]
    losing_trades = trades_df[trades_df['profit'] <= 0]
    
    win_rate = (len(winning_trades) / len(trades_df)) * 100 if len(trades_df) > 0 else 0
    avg_profit = winning_trades['profit_pct'].mean() if len(winning_trades) > 0 else 0
    avg_loss = losing_trades['profit_pct'].mean() if len(losing_trades) > 0 else 0
    total_return = trades_df['profit_pct'].sum()
    
    # Calculate max drawdown
    cumulative_returns = trades_df['profit_pct'].cumsum()
    running_max = cumulative_returns.expanding().max()
    drawdown = cumulative_returns - running_max
    max_drawdown = drawdown.min() if len(drawdown) > 0 else 0
    
    return {
        'total_trades': len(trades_df),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'win_rate': win_rate,
        'avg_profit': avg_profit,
        'avg_loss': avg_loss,
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'trades': trades
    }

def format_backtest_results(results):
    """
    Format backtest results for display.
    """
    if results is None or results['total_trades'] == 0:
        return "📊 過去30日間で取引シグナルが発生しませんでした。"
    
    report = f"""
### 📊 戦略バックテスト結果 (過去30日)

**取引実績**
- 総取引回数: {results['total_trades']}回
- 勝ちトレード: {results['winning_trades']}回
- 負けトレード: {results['losing_trades']}回

**パフォーマンス**
- 勝率: {results['win_rate']:.1f}%
- 平均利益: {results['avg_profit']:.2f}%
- 平均損失: {results['avg_loss']:.2f}%
- 累積リターン: {results['total_return']:.2f}%
- 最大ドローダウン: {results['max_drawdown']:.2f}%

**評価**: {'✅ 良好' if results['win_rate'] > 60 and results['total_return'] > 0 else '⚠️ 要改善' if results['total_return'] > 0 else '❌ 損失'}
    """
    
    return report.strip()
