import pandas as pd
import numpy as np
from modules.analysis import calculate_trading_strategy

def test_stop_loss_logic():
    # 模擬データの作成
    data = {
        'Close': [1000] * 100,
        'High': [1010] * 100,
        'Low': [990] * 100,
        'SMA5': [1000] * 100,
        'SMA25': [980] * 100,
        'SMA75': [950] * 100,
        'BB_Upper': [1050] * 100,
        'BB_Lower': [950] * 100,
        'ATR': [20] * 100 # ATRを20に設定
    }
    df = pd.DataFrame(data)
    
    # テストケース1: 通常のATR損切り (ATR 20 * 2.0 = 40)
    # エントリー価格は約1000なので、損切りは 1000 - 40 = 960。
    # 固定制限 -5% (= 950) より浅いので、ATRが採用されるはず。
    settings_normal = {'stop_loss_limit': -5.0}
    res_normal = calculate_trading_strategy(df, settings=settings_normal)
    print(f"--- Normal Case (Low Volatility) ---")
    print(f"Entry: {res_normal['entry_price']}, SL: {res_normal['stop_loss']}, Source: {res_normal['sl_source']}, HighRisk: {res_normal['is_high_risk']}")
    assert res_normal['sl_source'] == "ATR", "Should use ATR source"
    
    # テストケース2: ボラティリティが高い場合 (ATR 50 * 2.0 = 100)
    # エントリー価格は約1000なので、ATR損切りは 1000 - 100 = 900。
    # 固定制限 -5% (= 950) より深いので、固定値 950 が採用されるはず。
    df_high_vol = df.copy()
    df_high_vol['ATR'] = 50
    res_high = calculate_trading_strategy(df_high_vol, settings=settings_normal)
    print(f"\n--- High Volatility Case (Guardrail Triggered) ---")
    print(f"Entry: {res_high['entry_price']}, SL: {res_high['stop_loss']}, Source: {res_high['sl_source']}, HighRisk: {res_high['is_high_risk']}")
    assert res_high['sl_source'] == "Fixed Limit (-5%)", "Should use Fixed Limit source"
    assert res_high['is_high_risk'] == True, "Should be marked as high risk"

    print("\n✅ Verification scripts passed!")

if __name__ == "__main__":
    test_stop_loss_logic()
