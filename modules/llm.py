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
    if enhanced_metrics is None:
        enhanced_metrics = {}
        
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

**🎯 推奨エントリー価格**: ¥{strategic_data.get('entry_price', 0):,.0f}
- この価格帯は、サポートラインとテクニカル指標から算出した最適なエントリーポイントです。

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

    # Construct Enhanced Prompt with Strict Persona
    prompt = f"""
    # Role
    あなたは「リスク管理を最優先するプロの機関投資家」兼「熟練のスイングトレーダー」です。
    提供された株価データとテクニカル指標に基づき、**論理的整合性の取れた**トレードシナリオを作成してください。

    # Mission
    ユーザーの資産を守り、かつ増やすために、勝率とリスクリワードのバランスが取れたトレードプラン（または「様子見」の判断）を提示すること。
    **トレンド判断と売買推奨の間に矛盾が生じることを絶対に避けてください。**

    # Critical Rules (絶対遵守事項)

    1. **トレンド順張り原則 (Trend Alignment)**
       - 全体的なトレンド判断が「下落（Bearish）」の場合、安易な「買い（Long）」推奨をしてはいけません。
       - 下落トレンド中の「買い」は、RSIのダイバージェンスや強力な長期サポートラインでの反発確認など、明確な「底打ちシグナル」が出ている場合のみ提案し、それ以外は**「様子見（WAIT）」**と判定してください。

    2. **エントリー価格の厳格化**
       - 「現在価格」で適当にエントリーさせないでください。
       - エントリー価格は、必ずテクニカル的な根拠（移動平均線、ボリンジャーバンド±2σ、水平線、フィボナッチ等）がある価格帯に設定してください。
       - **「下落中のナイフ」をつかませないでください。** 反発確認後のエントリーを前提としてください。

    3. **リスクリワード (R/R) の計算定義**
       - リスクリワードは以下の式で正確に算出してください。
         `R/R = (利確目標値 - エントリー価格) ÷ (エントリー価格 - 損切目安値)`
       - **R/Rが 1.5 を下回るトレードは「推奨しない（NO TRADE）」と判定してください。** 旨味が少なすぎます。

    4. **ステータスの明確化**
       - レポートの冒頭で、現在のステータスを以下から1つ選択して明示してください。
         - 【BUY ENTRY】: 上昇トレンド中、または明確な押し目。直ちに指値検討可。
         - 【SELL ENTRY】: 空売り推奨（可能な場合）。
         - 【MONITOR (監視)】: トレンド転換待ち、または条件が揃うのを待つ段階。価格はあくまで「監視候補」とする。
         - 【NO TRADE (静観)】: トレンドレス、またはボラティリティ過多で危険。

    # Input Data (市場データ)
    - 銘柄: {ticker}
    - 現在値: ¥{price_info.get('current_price', 0):,.1f}
    - 変化率: {price_info.get('change_percent', 0):+.2f}%
    - 52週高値位置: {enhanced_metrics.get('price_position', 50):.1f}% (高値: ¥{enhanced_metrics.get('52w_high', 0):,.0f})
    
    ## テクニカル指標
    - トレンド (SMA): {strategic_data.get('trend_desc', '')}
    - RSI(14): {indicators.get('rsi', 50):.1f} ({indicators.get('rsi_status', '')})
    - MACD: {indicators.get('macd_status', '')}
    - ボリンジャーバンド: {indicators.get('bb_status', '')} (幅: {enhanced_metrics.get('bb_width', 0):.2f}%)
    - ATR(14): ¥{indicators.get('atr', 0):.0f}
    
    ## アルゴリズム提案値 (参考)
    ※以下の値はあくまで参考値です。プロの視点で再評価・修正してください。
    - 提案トレンド: {strategic_data.get('strategy_msg', '')}
    - 算出エントリー: ¥{strategic_data.get('entry_price', 0):,.0f}
    - 算出ターゲット: ¥{strategic_data.get('target_price', 0):,.0f}
    - 算出損切: ¥{strategic_data.get('stop_loss', 0):,.0f}
    
    ## 検出パターン
    {_format_patterns_for_prompt(patterns)}
    
    ## 需給情報
    {credit_data}

    # Output Format (出力形式)

    以下のフォーマットに従って出力してください。Markdownを使用してください。

    ---
    ## 📊 戦略判定: [ここにステータスを入れる (例: 🛡️ MONITOR / 🟢 BUY ENTRY)]

    **【結論】**
    (ここに、「なぜその判定なのか」を1行で要約。例:「下落トレンド継続中のため、直近安値での反発を確認するまで静観を推奨」)

    **【トレードセットアップ】**
    ※ステータスが「MONITOR」や「NO TRADE」の場合、以下の価格は「監視ライン」として提示すること。

    - **エントリー推奨値**: [価格] 円
      - (根拠: 25日移動平均線のサポート、前回高値ライン 等)
    - **利確目標 (TP)**: [価格] 円 (+[％]%)
      - (根拠: ボリンジャーバンド+2σ、直近高値 等)
    - **損切目安 (SL)**: [価格] 円 (-[％]%)
      - (根拠: 直近安値割れ、75日線ブレイク 等)
    - **リスクリワード比**: [数値] (計算式に基づく正確な値)

    **【テクニカル詳細分析】**
    1. **トレンド環境**: (パーフェクトオーダーの有無、ダウ理論によるトレンド判定)
    2. **オシレーター評価**: (RSIやMACDが示す過熱感やダイバージェンスの有無)
    3. **需給・ファンダ**: (信用倍率や出来高から読み取れる相場心理)

    ---
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
