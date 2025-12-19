try:
    from google import genai
    from google.genai import types
    GENAI_V1_AVAILABLE = True
    print("google-genai (V1 SDK) available.")
except ImportError:
    GENAI_V1_AVAILABLE = False
    print("google-genai (V1 SDK) not available.")

try:
    import google.generativeai as old_genai
    GENAI_LEGACY_AVAILABLE = True
    print("google-generativeai (Legacy SDK) available.")
except ImportError:
    GENAI_LEGACY_AVAILABLE = False
    print("google-generativeai (Legacy SDK) not available.")

import os
import time

import streamlit as st

# API Key - Load from secrets.toml (local) or Streamlit Cloud Secrets
# PRIORITY: st.secrets > os.getenv > None
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    API_KEY = os.getenv("GEMINI_API_KEY")

# GENAI_AVAILABLE definition for other modules
GENAI_AVAILABLE = (GENAI_V1_AVAILABLE or GENAI_LEGACY_AVAILABLE) and (API_KEY is not None)

if not API_KEY:
    print("Warning: GEMINI_API_KEY not found in secrets.toml or environment variables.")

def get_gemini_client():
    """Returns a V1 Client if available."""
    if not GENAI_V1_AVAILABLE or not API_KEY:
        return None
    try:
        client = genai.Client(api_key=API_KEY)
        return client
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")
        return None

def generate_gemini_analysis(ticker, price_info, indicators, credit_data, strategic_data, enhanced_metrics=None, patterns=None, extra_context=None):
    """
    Generate a professional stock analysis report using Gemini 1.5 Flash.
    Falls back to legacy SDK or mock if unavailable.
    """
    if enhanced_metrics is None:
        enhanced_metrics = {}
        
    # [Prompt construction - same as before]
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
    - 現在値: ¥{price_info.get('current_price') or 0:,.1f}
    - 変化率: {price_info.get('change_percent') or 0:+.2f}%
    - 52週高値位置: {enhanced_metrics.get('price_position') or 50:.1f}% (高値: ¥{enhanced_metrics.get('52w_high') or 0:,.0f})
    
    ## テクニカル指標
    - トレンド (SMA): {strategic_data.get('trend_desc', '')}
    - RSI(14): {indicators.get('rsi') or 50:.1f} ({indicators.get('rsi_status', '')})
    - MACD: {indicators.get('macd_status', '')}
    - ボリンジャーバンド: {indicators.get('bb_status', '')} (幅: {enhanced_metrics.get('bb_width') or 0:.2f}%)
    - ATR(14): ¥{indicators.get('atr') or 0:.0f}
    
    ## アルゴリズム提案値 (参考)
    ※以下の値はあくまで参考値です。プロの視点で再評価・修正してください。
    - 提案トレンド: {strategic_data.get('strategy_msg', '')}
    - 算出エントリー: ¥{strategic_data.get('entry_price') or 0:,.0f}
    - 算出ターゲット: ¥{strategic_data.get('target_price') or 0:,.0f}
    - 算出損切: ¥{strategic_data.get('stop_loss') or 0:,.0f}
    
    ## 検出パターン
    {_format_patterns_for_prompt(patterns)}
    
    ## 需給情報
    {credit_data}

    ## その他の重要情報 (Context)
    {_format_extra_context(extra_context)}

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
    
    error_details = []

    # Attempt 1: New SDK (V1)
    client = get_gemini_client()
    if client:
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            error_details.append(f"V1 SDK Failed: {str(e)}")
    else:
        if not GENAI_V1_AVAILABLE:
            error_details.append("V1 SDK (google-genai) not installed.")
        if not API_KEY:
            error_details.append("API Key missing.")

    # Attempt 2: Legacy SDK フォールバック
    if GENAI_LEGACY_AVAILABLE and API_KEY:
        try:
            old_genai.configure(api_key=API_KEY)
            model = old_genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_details.append(f"Legacy SDK Failed: {str(e)}")
    
    # Fallback to Mock
    debug_info = " | ".join(error_details) if error_details else "Unknown Error"
    return _create_mock_report(strategic_data, enhanced_metrics, indicators, credit_data, error_info=debug_info)

def _create_mock_report(strategic_data, enhanced_metrics, indicators, credit_data, error_info=None):
    """Helper to create strict format mock report."""
    trend_status = "MONITOR (監視)"
    conclusion = "方向感が乏しため、明確なシグナルが出るまで静観を推奨します。"
    
    # Simple logic to make mock dynamic
    if enhanced_metrics.get('roc_5d', 0) > 2 and indicators.get('rsi', 50) < 70:
            trend_status = "BUY ENTRY"
            conclusion = "短期上昇モメンタムが発生しており、押し目でのエントリーが有効です。"
    elif enhanced_metrics.get('roc_5d', 0) < -2:
            trend_status = "NO TRADE"
            conclusion = "下落トレンド中につき、底打ちを確認するまで様子見を推奨。"

    debug_tag = f"\n> [!CAUTION]\n> **AI Analysis Failure**: {error_info}\n" if error_info else ""

    return f"""
<!-- MOCK REPORT due to API failure -->
{debug_tag}
## 📊 戦略判定: 🛡️ {trend_status}

**【結論】**
{conclusion}

**【トレードセットアップ】**
- **エントリー推奨値**: ¥{strategic_data.get('entry_price') or 0:,.0f}
  - (根拠: アルゴリズム算出値に基づく参考価格)
- **利確目標 (TP)**: ¥{strategic_data.get('target_price') or 0:,.0f}
  - (根拠: ボリンジャーバンド+2σ付近)
- **損切目安 (SL)**: ¥{strategic_data.get('stop_loss') or 0:,.0f}
  - (根拠: 直近サポートライン割れ)
- **リスクリワード比**: {strategic_data.get('risk_reward') or 0:.2f}

**【テクニカル詳細分析】**
1. **トレンド環境**:
   - SMA判定: {strategic_data.get('trend_desc', 'N/A')}
   - トレンド強度: {enhanced_metrics.get('trend_strength', 0):.1f}

2. **オシレーター評価**:
   - RSI(14): {indicators.get('rsi') or 50:.1f} ({indicators.get('rsi_status', '')})
   - MACD: {indicators.get('macd_status', '')}
   - ボリンジャーバンド: {indicators.get('bb_status', '')}

3. **需給・ファンダ**:
   - {credit_data}
"""

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

def _format_extra_context(context):
    """Format extra context like Earnings and Market Trend."""
    if not context:
        return "特になし"
    
    lines = []
    if 'earnings_date' in context and context['earnings_date']:
        lines.append(f"- **次回決算日**: {context['earnings_date']} (決算またぎのリスクに注意)")
    
    if 'market_trend' in context:
        trend = context['market_trend']
        desc = "上昇トレンド（追い風）" if trend == "Bull" else "下落トレンド（向かい風）" if trend == "Bear" else "中立"
        lines.append(f"- **市場全体の地合い (日経平均)**: {desc}")
        
def analyze_news_impact(portfolio_items, news_data_map):
    """
    Analyze the impact of recent news on portfolio holdings using Gemini.
    """
    if not GENAI_AVAILABLE:
        return "AI分析が利用できないため、要約をスキップします。"
    
    if not portfolio_items:
        return "ポートフォリオが空です。"

    portfolio_str = "\n".join([f"- {item['name']} ({item['ticker']}): {item['shares']}株" for item in portfolio_items])
    
    news_str = ""
    for ticker, news_list in news_data_map.items():
        if news_list:
            news_str += f"\n【{ticker} 関連ニュース】\n"
            for n in news_list[:3]:
                news_str += f"- {n['title']} ({n['publisher']})\n"

    if not news_str:
        return "関連ニュースが見つかりませんでした。"

    prompt = f"""
    あなたはプロの証券アナリストです。以下の保有銘柄と最新ニュースに基づき、
    1. 各ニュースが保有株に与える影響（ポジティブ/ネガティブ/中立）
    2. 今後の投資活動に対する簡潔なアドバイス
    を、忙しいユーザーのために重要度順に要約してください。

    # 保有銘柄
    {portfolio_str}

    # 最新ニュース
    {news_str}

    # 出力形式
    - 絵文字を使い、親しみやすくかつプロフェッショナルなトーンで。
    - LINEで読みやすいよう、要点を箇条書きで短くまとめてください。
    """

    client = get_gemini_client()
    if client:
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"News Analysis V1 Failed: {e}")
            
    if GENAI_LEGACY_AVAILABLE and API_KEY:
        try:
            old_genai.configure(api_key=API_KEY)
            model = old_genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"News Analysis Legacy Failed: {e}")

    return "ニュースのAI分析中にエラーが発生しました。"
