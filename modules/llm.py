try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("google-generativeai not available (Python < 3.9?). Using mock.")

import os
import time

# API Key - Use environment variable for cloud deployment
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDL-fH2-9ADc61okQm6WtRyHFunoH_tyP4")

def configure_genai():
    if not GENAI_AVAILABLE:
        return False
    try:
        genai.configure(api_key=API_KEY)
        return True
    except Exception as e:
        print(f"Failed to configure Gemini: {e}")
        return False

def generate_gemini_analysis(ticker, price_info, indicators, credit_data, strategic_data, enhanced_metrics=None, patterns=None):
    """
    Generate a professional stock analysis report using Gemini 1.5 Pro.
    Falls back to mock if unavailable.
    """
    if not configure_genai():
        # Enhanced Mock Fallback
        time.sleep(2)
        return f"""
### 🧠 Gemini AI Analyst Report (Enhanced Mock)

**総合判断**: **{strategic_data.get('trend_desc', '').split(':')[0].replace('**', '')}** 

#### 📊 市場ポジション分析
現在の株価は52週レンジの**{enhanced_metrics.get('price_position', 50):.1f}%**の位置にあり、{
'高値圏で推移しています。利益確定の動きに注意が必要です' if enhanced_metrics.get('price_position', 50) > 70 else
'安値圏で推移しています。反発の可能性を探るべきタイミングです' if enhanced_metrics.get('price_position', 50) < 30 else
'中間レンジで推移しており、方向感を見極める局面です'
}。

52週高値（¥{enhanced_metrics.get('52w_high', 0):,.0f}）からは**{enhanced_metrics.get('52w_high_pct', 0):.1f}%**、
52週安値（¥{enhanced_metrics.get('52w_low', 0):,.0f}）からは**{enhanced_metrics.get('52w_low_pct', 0):+.1f}%**の位置です。

#### 🔥 モメンタム評価
- **短期（5日）**: {enhanced_metrics.get('roc_5d', 0):+.2f}% - {'強い上昇モメンタム' if enhanced_metrics.get('roc_5d', 0) > 2 else '弱い動き' if abs(enhanced_metrics.get('roc_5d', 0)) < 1 else '下落圧力'}
- **中期（10日）**: {enhanced_metrics.get('roc_10d', 0):+.2f}%
- **長期（20日）**: {enhanced_metrics.get('roc_20d', 0):+.2f}%

モメンタムの方向性から判断すると、{
'短期的な過熱感が見られます。調整局面に入る可能性があります' if enhanced_metrics.get('roc_5d', 0) > 5 else
'安定したトレンドが継続しています' if abs(enhanced_metrics.get('roc_5d', 0) - enhanced_metrics.get('roc_10d', 0)) < 2 else
'モメンタムの減速が見られます。トレンド転換の兆候に注意してください'
}。

#### 📈 テクニカル詳細分析
**RSI**: {indicators.get('rsi', 50):.1f} ({enhanced_metrics.get('rsi_trend', 'N/A')})
- RSIは{
'70を超えており、買われ過ぎの水準です。短期的な調整リスクが高まっています' if indicators.get('rsi', 50) > 70 else
'30を下回っており、売られ過ぎの水準です。反発の可能性が高まっています' if indicators.get('rsi', 50) < 30 else
'50付近で中立的な水準です。明確な方向感は出ていません' if 45 < indicators.get('rsi', 50) < 55 else
'健全な範囲内で推移しています'
}。

**MACD**: {enhanced_metrics.get('macd_cross', 'none')}
- {
'ゴールデンクロスが発生しました。買いシグナルとして注目すべきポイントです' if enhanced_metrics.get('macd_cross') == 'golden' else
'デッドクロスが発生しました。売りシグナルとして警戒が必要です' if enhanced_metrics.get('macd_cross') == 'dead' else
'クロスは発生していません。現在のトレンドが継続する可能性が高いです'
}。

**ボリンジャーバンド**: 幅{enhanced_metrics.get('bb_width', 0):.2f}%
- BB幅から判断すると、{
'ボラティリティが拡大しています。大きな値動きが予想されます' if enhanced_metrics.get('bb_width', 0) > 10 else
'ボラティリティが縮小しています（スクイーズ）。ブレイクアウトが近い可能性があります' if enhanced_metrics.get('bb_width', 0) < 5 else
'通常のボラティリティ範囲です'
}。

#### 💹 出来高分析
当日出来高は平均の**{enhanced_metrics.get('volume_ratio', 1):.2f}倍**で、{
'異常な出来高急増が見られます。重要な転換点の可能性があります' if enhanced_metrics.get('volume_ratio', 1) > 2 else
'出来高が減少しています。トレンドの勢いが弱まっている兆候です' if enhanced_metrics.get('volume_ratio', 1) < 0.7 else
'平均的な出来高で推移しています'
}。

#### 🎯 戦略的推奨
{strategic_data.get('action_msg', '')}

**利確目標**: ¥{strategic_data.get('target_price', 0):,.0f}
- この目標は{
'ボリンジャーバンドの上限付近に設定されており、妥当な水準です' if enhanced_metrics.get('bb_position', 50) < 80 else
'やや楽観的な設定です。段階的な利益確定を推奨します'
}。

**損切ライン**: ¥{strategic_data.get('stop_loss', 0):,.0f}
- ATR（¥{enhanced_metrics.get('atr', 0):,.0f}）を考慮すると、{
'適切な損切位置です。このラインは厳守してください' if enhanced_metrics.get('atr_pct', 0) < 3 else
'ボラティリティが高いため、損切幅を広めに取ることも検討してください'
}。

#### ⚠️ リスク要因
- 年率ボラティリティ: **{enhanced_metrics.get('volatility_annual', 0):.1f}%**
- トレンド強度: **{enhanced_metrics.get('trend_strength', 0):.1f}**

{
'ボラティリティが高く、リスクの高い銘柄です。ポジションサイズを抑えることを推奨します' if enhanced_metrics.get('volatility_annual', 0) > 40 else
'ボラティリティは標準的な範囲です' if enhanced_metrics.get('volatility_annual', 0) > 20 else
'ボラティリティが低く、安定した値動きが期待できます'
}。
        """

    # Construct Enhanced Prompt
    prompt = f"""
    あなたは世界トップクラスのヘッジファンドで働く、伝説的な日本人テクニカルアナリストです。
    20年以上の経験を持ち、数々の市場の転換点を的確に予測してきました。
    
    以下の詳細な市場データに基づき、プロフェッショナルな視点で「{ticker}」の徹底的な分析レポートを作成してください。
    
    ## 基本情報
    - 現在値: ¥{price_info.get('current_price', 0):,.1f} (前日比: {price_info.get('change_percent', 0):+.2f}%)
    - 52週高値: ¥{enhanced_metrics.get('52w_high', 0):,.0f} (現在値との乖離: {enhanced_metrics.get('52w_high_pct', 0):.1f}%)
    - 52週安値: ¥{enhanced_metrics.get('52w_low', 0):,.0f} (現在値との乖離: {enhanced_metrics.get('52w_low_pct', 0):+.1f}%)
    - 価格位置: 52週レンジの{enhanced_metrics.get('price_position', 50):.1f}%
    
    ## モメンタム指標
    - 5日ROC: {enhanced_metrics.get('roc_5d', 0):+.2f}%
    - 10日ROC: {enhanced_metrics.get('roc_10d', 0):+.2f}%
    - 20日ROC: {enhanced_metrics.get('roc_20d', 0):+.2f}%
    
    ## テクニカル指標（詳細）
    - RSI(14): {indicators.get('rsi', 50):.1f} (トレンド: {enhanced_metrics.get('rsi_trend', 'N/A')}, 平均: {enhanced_metrics.get('rsi_avg', 50):.1f})
    - MACD: {enhanced_metrics.get('macd', 0):.2f} (シグナル: {enhanced_metrics.get('macd_signal', 0):.2f}, ヒストグラム: {enhanced_metrics.get('macd_histogram', 0):.2f})
    - MACDクロス: {enhanced_metrics.get('macd_cross', 'none')}
    - ボリンジャーバンド幅: {enhanced_metrics.get('bb_width', 0):.2f}% (価格位置: {enhanced_metrics.get('bb_position', 50):.1f}%)
    - 移動平均線配列: {enhanced_metrics.get('ma_alignment', 'neutral')}
    - トレンド強度: {enhanced_metrics.get('trend_strength', 0):.1f}
    
    ## ボラティリティ
    - 日次ボラティリティ: {enhanced_metrics.get('volatility_daily', 0)*100:.2f}%
    - 年率ボラティリティ: {enhanced_metrics.get('volatility_annual', 0):.1f}%
    - ATR(14): ¥{enhanced_metrics.get('atr', 0):,.0f} ({enhanced_metrics.get('atr_pct', 0):.2f}%)
    
    ## 出来高分析
    - 平均出来高(20日): {enhanced_metrics.get('avg_volume_20d', 0):,.0f}
    - 当日出来高: {enhanced_metrics.get('current_volume', 0):,.0f}
    - 出来高比率: {enhanced_metrics.get('volume_ratio', 1):.2f}x
    - 出来高トレンド: {enhanced_metrics.get('volume_trend', 'N/A')}
    
    ## 検出されたパターン
    {_format_patterns_for_prompt(patterns) if patterns else '特になし'}
    
    ## アルゴリズム算出の戦略シナリオ
    - トレンド判定: {strategic_data.get('trend_desc', '')}
    - 推奨アクション: {strategic_data.get('action_msg', '')}
    - 利確目標: ¥{strategic_data.get('target_price', 0):,.0f}
    - 損切ライン: ¥{strategic_data.get('stop_loss', 0):,.0f}
    - リスクリワード比: {strategic_data.get('risk_reward', 0):.2f}
    
    ## 指示（必ず守ること）
    1. **結論ファースト**: 最初に「強気」「弱気」「中立」のいずれかを明確に断言し、その根拠を3つ挙げてください。
    
    2. **市場ポジション分析**: 52週レンジ内での現在位置を評価し、「高値圏」「安値圏」「中間レンジ」のどこにいるかを明示してください。
    
    3. **モメンタム評価**: 短期・中期・長期のROCから、モメンタムの方向性と強さを詳細に分析してください。
       - モメンタムが加速しているか減速しているか
       - トレンド転換の兆候はあるか
    
    4. **テクニカル詳細分析**: 各指標を単に羅列するのではなく、「なぜその数値が重要か」を文脈で語ってください。
       - RSI: 過熱感、ダイバージェンス、トレンドの持続性
       - MACD: クロスの信頼性、ヒストグラムの変化
       - ボリンジャーバンド: スクイーズ、エクスパンション、バンドウォーク
       - 移動平均線: パーフェクトオーダー、デッドクロス、支持/抵抗
    
    5. **出来高分析**: 出来高の変化が価格トレンドをどう裏付けているか、または矛盾しているかを指摘してください。
    
    6. **パターン評価**: 検出されたパターンの信頼性を評価し、過去の統計的な成功率も考慮してください。
    
    7. **戦略シナリオの評価**: アルゴリズムが算出した戦略を批判的に評価してください。
       - 利確目標は妥当か（楽観的すぎないか、保守的すぎないか）
       - 損切ラインは適切か（ATRやボラティリティを考慮して）
       - リスクリワード比は魅力的か
    
    8. **リスク要因**: 見落とされがちなリスクを3つ挙げてください。
    
    9. **具体的なアクションプラン**: 
       - 「今すぐ買うべきか、押し目を待つべきか」
       - 「エントリーする場合の具体的な価格レンジ」
       - 「ポジションサイズの推奨（全力か、分割か）」
    
    10. **口調**: 冷静沈着、論理的、かつ断定的なプロフェッショナルな口調。「〜と思われる」ではなく「〜である」「〜と判断する」を使用。
    
    11. **フォーマット**: Markdown形式で見やすく構造化。見出しは###から開始。
    
    12. **文字数**: 最低800文字以上の詳細なレポートを作成してください。
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini generation failed: {e}")
        return None

def _format_patterns_for_prompt(patterns):
    """Format detected patterns for inclusion in prompt."""
    if not patterns:
        return "特になし"
    
    result = []
    for p in patterns.get('candlestick_patterns', []):
        result.append(f"- {p['name']}: {p['signal']}")
    for p in patterns.get('chart_patterns', []):
        result.append(f"- {p['name']}: {p['signal']}")
    
    return "\n".join(result) if result else "特になし"
