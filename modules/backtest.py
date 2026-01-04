import pandas as pd
import numpy as np

def backtest_strategy(df, strategic_data=None, days=30):
    """
    Backtest the AI trading strategy over the last N days.
    Eliminates look-ahead bias by calculating levels at each point in time.
    """
    if df is None or len(df) < days:
        return None
    
    # Get recent data and ensure indicators are present
    recent_df = df.tail(days + 20).copy() # Buffer for indicators if needed
    
    # Simulated settings (can be refined)
    sl_limit_pct = -5.0 
    
    trades = []
    in_position = False
    entry_price = 0
    entry_date = None
    current_target = 0
    current_stop_loss = 0
    
    # Iterate through days
    for idx, row in recent_df.iterrows():
        # Skip if we don't have enough indicators for this row
        needed = ['SMA5', 'SMA25', 'SMA75', 'BB_Upper', 'BB_Lower', 'ATR', 'RSI']
        if not all(col in row.index for col in needed) or pd.isna(row['SMA75']):
            continue
            
        current_price = row['Close']
        
        if not in_position:
            # --- Entry Logic (Consistent with analysis.py) ---
            sma5, sma25, sma75 = row['SMA5'], row['SMA25'], row['SMA75']
            rsi = row['RSI']
            bb_low = row['BB_Lower']
            atr = row['ATR']
            
            # Trend Check
            is_uptrend = (sma5 > sma25) or (current_price > sma25)
            
            # Entry Signal: Near support (SMA25 or BB_Low) and RSI not overbought
            support_level = max([sma25, bb_low]) if max([sma25, bb_low]) < current_price else current_price * 0.98
            
            if is_uptrend and current_price <= support_level * 1.02 and rsi < 60:
                in_position = True
                entry_price = current_price
                entry_date = idx
                
                # Calculate Target/SL at the moment of entry
                current_target = row['BB_Upper']
                
                # ATR-based SL logic
                atr_sl = entry_price - (2.0 * atr)
                fixed_sl = entry_price * (1 + (sl_limit_pct / 100))
                current_stop_loss = max(atr_sl, fixed_sl) # Tighter/Safer one
                
        else:
            # --- Exit Logic ---
            exit_triggered = False
            exit_reason = ""
            exit_price = current_price
            
            # Take profit
            if current_price >= current_target:
                exit_triggered = True
                exit_reason = "利確"
                exit_price = current_target
            
            # Stop loss
            elif current_price <= current_stop_loss:
                exit_triggered = True
                exit_reason = "損切"
                exit_price = current_stop_loss
            
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
            'total_trades': 0, 'win_rate': 0, 'avg_profit': 0, 'avg_loss': 0,
            'total_return': 0, 'max_drawdown': 0, 'trades': []
        }
    
    trades_df = pd.DataFrame(trades)
    winning_trades = trades_df[trades_df['profit'] > 0]
    losing_trades = trades_df[trades_df['profit'] <= 0]
    
    win_rate = (len(winning_trades) / len(trades_df)) * 100
    avg_profit = winning_trades['profit_pct'].mean() if not winning_trades.empty else 0
    avg_loss = losing_trades['profit_pct'].mean() if not losing_trades.empty else 0
    total_return = trades_df['profit_pct'].sum()
    
    # Cumulative returns for drawdown calc
    trades_df['cum_return'] = (1 + trades_df['profit_pct'] / 100).cumprod()
    running_max = trades_df['cum_return'].cummax()
    drawdown = (trades_df['cum_return'] - running_max) / running_max
    max_drawdown = drawdown.min() * 100 if not drawdown.empty else 0
    
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
