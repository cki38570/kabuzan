try:
    from google import genai
    from google.genai import types
    GENAI_V1_AVAILABLE = True
    print("google-genai (V1 SDK) available.")
except ImportError:
    GENAI_V1_AVAILABLE = False
    print("google-genai (V1 SDK) not available.")

import os
import time
import streamlit as st

# API Key - Load from secrets.toml (local) or Streamlit Cloud Secrets
# PRIORITY: st.secrets > os.getenv > None
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError, AttributeError):
    API_KEY = os.getenv("GEMINI_API_KEY")

# GENAI_AVAILABLE definition for other modules
GENAI_AVAILABLE = GENAI_V1_AVAILABLE and (API_KEY is not None)

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

def generate_gemini_analysis(ticker, price_info, indicators, credit_data, strategic_data, enhanced_metrics=None, patterns=None, extra_context=None, weekly_indicators=None, news_data=None):
    """
    Generate a professional stock analysis report using Gemini 1.5 Flash.
    Falls back to legacy SDK or mock if unavailable.
    """
    if enhanced_metrics is None:
        enhanced_metrics = {}
    if weekly_indicators is None:
        weekly_indicators = {}
    if news_data is None:
        news_data = []
        
    # [Prompt construction - same as before]
    prompt = f"""
    # Role
    あなたは「リスク管理を最優先するプロの機関投資家」兼「熟練のスイングトレーダー」です。
    提供された株価データとテクニカル指標に基づき、**論理的整合性の取れた**トレードシナリオを作成してください。

    # Mission
    ユーザーの資産を守り、かつ増やすために、勝率とリスクリワードのバランスが取れたトレードプラン（または「様子見」の判断）を提示すること。
    **トレンド判断と売買推奨の間に矛盾が生じることを絶対に避けてください。**

    # Critical Rules (絶対遵守事項)

    2. **総合判断スコア (Total Investment Score) の算出**
       - テクニカル（60%）とセンチメント（40%）を統合し、100点満点でスコアを算出してください。
       - 80点以上: 強い買い推奨
       - 60-79点: 買い検討
       - 40-59点: 中立・監視
       - 40点未満: 回避・売り検討

    3. **センチメント分析 (News Sentiment)**
       - 直近ニュースを解析し、「ポジティブ」「ネガティブ」「中立」を判定してください。
       - 各ニュースが株価に与える影響度を考慮してください。

    4. **価格設定の厳格化**
       - エントリー、利確、損切価格は、必ずテクニカル的な根拠に基づいて設定してください。

    5. **ステータスの明確化**
       - レポートの冒頭で、【BUY ENTRY】【SELL ENTRY】【MONITOR】【NO TRADE】のいずれかを明示してください。

    # Input Data (市場データ)
    - 銘柄: {ticker}
    - 現在値: ¥{price_info.get('current_price') or 0:,.1f}
    - 変化率: {price_info.get('change_percent') or 0:+.2f}%
    - 52週高値位置: {enhanced_metrics.get('price_position') or 50:.1f}% (高値: ¥{enhanced_metrics.get('52w_high') or 0:,.0f})
    
    ## テクニカル指標 (※計算済みデータ)
    - **【日足】**
      - トレンド: {indicators.get('trend_desc', 'N/A')}
      - SMA短期/中期/長期: ¥{indicators.get('sma_short', 0):,.0f} / ¥{indicators.get('sma_mid', 0):,.0f} / ¥{indicators.get('sma_long', 0):,.0f}
      - RSI(14): {indicators.get('rsi', 50):.1f} -> {indicators.get('rsi_status', '')}
      - MACD: {indicators.get('macd', 0):.2f} (Signal: {indicators.get('macd_signal', 0):.2f}) -> {indicators.get('macd_status', '')}
      - ボリンジャーバンド: {indicators.get('bb_status', '')} (幅: {indicators.get('bb_width', 0):.2f}%)
      - ATR: ¥{indicators.get('atr', 0):.0f}
    
    - **【週足 (大局)】**
      - トレンド: {weekly_indicators.get('trend_desc', 'N/A')}
      - RSI: {weekly_indicators.get('rsi', 50):.1f}
      - SMA(13/26/52): ¥{weekly_indicators.get('sma_short', 0):,.0f} / ¥{weekly_indicators.get('sma_mid', 0):,.0f} / ¥{weekly_indicators.get('sma_long', 0):,.0f}
    
    ## 検出パターン
    {_format_patterns_for_prompt(patterns)}
    
    ## 需給情報・財務概況 (Fundamentals)
    {_format_fundamentals_for_prompt(credit_data)}
    
    ## 直近ニュース (Sentiment Data)
    {_format_news_for_prompt(news_data)}

    ## その他の重要情報 (Context)
    {_format_extra_context(extra_context)}

    # Output Format (出力形式)
    以下のフォーマットに従って出力してください。**回答は必ず日本語で行ってください。**

    ---
    ## 📊 総合判定: [ここにステータスを入れる]
    ### 🎯 総合投資判断スコア: [00] / 100 点

    **【結論】**
    (「なぜそのスコア・判定なのか」を1行で要約。)

    **【思考プロセス】**
    1. **週足/大局判断**: (週足に基づく中期トレンド評価)
    2. **日足/テクニカル**: (日足の指標によるエントリー可否)
    3. **センチメント**: (ニュース面からの影響評価)

    **【トレードセットアップ】**
    (※具体的な価格根拠を含めて記述)
    - **エントリー推奨値**: [価格] 円
    - **利確目標 (TP)**: [価格] 円
    - **損切目安 (SL)**: [価格] 円
    - **リスクリワード比**: [数値]

    **【詳細分析レポート】**
    - **テクニカル点数**: [0-60]点
    - **センチメント判定**: [ポジティブ/中立/ネガティブ] ([0-40]点)
    - **特記事項**: (パターンの有無、決算日など)
    ---
    """
    
    error_details = []
    # Candidates for model name (tries from top)
    # Based on direct API check, 'gemini-flash-latest' and 'gemini-pro-latest' are confirmed available.
    MODEL_CANDIDATES = [
        'gemini-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-pro-latest',
        'gemini-2.0-flash',
        'gemini-2.0-flash-exp'
    ]

    # Attempt 1: New SDK (V1)
    client = get_gemini_client()
    if client:
        for model_name in MODEL_CANDIDATES:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    print(f"Success with V1 SDK: {model_name}")
                    return response.text
            except Exception as e:
                error_details.append(f"V1 SDK ({model_name}) Failed: {str(e)}")
    else:
        if not GENAI_V1_AVAILABLE:
            error_details.append("V1 SDK (google-genai) not installed.")
        if not API_KEY:
            error_details.append("API Key missing.")
    
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

def _format_fundamentals_for_prompt(credit_data):
    """Format fundamental data for the prompt."""
    if not credit_data or not credit_data.get('details'):
        return "- 財務データ: 取得不可"
    
    details = credit_data['details']
    def fmt(v, suffix=""):
        if v is None: return "N/A"
        if isinstance(v, (int, float)) and v >= 1e12: return f"{v/1e12:.2f}兆円"
        if isinstance(v, (int, float)) and v >= 1e8: return f"{v/1e8:.2f}億円"
        if isinstance(v, float): return f"{v:.2f}{suffix}"
        return f"{v}{suffix}"

    lines = [
        f"- 時価総額: {fmt(details.get('market_cap'))}",
        f"- PER (実績): {fmt(details.get('pe_ratio'), '倍')}",
        f"- PBR: {fmt(details.get('pb_ratio'), '倍')}",
        f"- 配立つ利回り: {fmt(details.get('dividend_yield'), '%')}",
        f"- ROE: {fmt(details.get('roe'))}",
        f"- セクター: {details.get('sector', 'N/A')}"
    ]
    return "\n".join(lines)

def _format_news_for_prompt(news_data):
    """Format news for inclusion in prompt."""
    if not news_data:
        return "直近の重要ニュースはありません。"
    
    result = []
    for n in news_data[:3]:
        result.append(f"- 【{n['publisher']}】{n['title']} ({n['provider_publish_time']})")
    
    return "\n".join(result)

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
    
    return "\n".join(lines) if lines else "特になし"
        
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

    # Based on direct API check, 'gemini-flash-latest' is confirmed available.
    MODEL_CANDIDATES = [
        'gemini-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-pro-latest',
        'gemini-2.0-flash',
        'gemini-2.0-flash-exp'
    ]

    client = get_gemini_client()
    if client:
        for model_name in MODEL_CANDIDATES:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"News Analysis V1 ({model_name}) Failed: {e}")
            
    return "ニュースのAI分析中にエラーが発生しました。接続可能なモデルが見つかりませんでした。"

    return "ニュースのAI分析中にエラーが発生しました。接続可能なモデルが見つかりませんでした。"
