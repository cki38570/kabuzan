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
import pandas as pd
import json

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

def generate_gemini_analysis(ticker, price_info, indicators, credit_data, strategic_data, enhanced_metrics=None, patterns=None, extra_context=None, weekly_indicators=None, news_data=None, macro_data=None, transcript_data=None):
    """
    Generate a highly advanced professional stock analysis report using Gemini.
    Implements Self-Reflection (Bull/Bear perspectives) and Macro/Transcript integration.
    Returns structured JSON if possible, otherwise Markdown.
    """
    if macro_data is None:
        macro_data = {}
    if transcript_data is None:
        transcript_data = pd.DataFrame()
        
    # Advanced Prompt with Self-Reflection and Macro/Transcript Context
    prompt = f"""
    # Role
    あなたは「世界トップクラスのヘッジファンド・シニア戦略アナリスト」です。
    機関投資家レベルの、多角的かつ論理的な投資判断を提供してください。

    # Self-Reflection Task (深層思考プロセス)
    分析において、以下の2人のエキスパートの徹底的な対話を経て、最終結論（シニアアナリストとしてのあなた）を導き出してください：
    1. **強気派アナリスト (Bull)**: 
       - テクニカルの上昇サイン、好材料、マクロの追い風を最大評価する。
       - 「なぜ今買うべきか」のポジティブな根拠を構築する。
    2. **弱気派アナリスト (Bear)**: 
       - 上値抵抗線、需給の悪化（信用残）、潜在的なマクロリスク、ニュースの裏側を厳しく指摘する。
       - 「なぜ今買うべきではないか」「最悪のシナリオは何か」を突きつける。

    # Strategic Analysis Priorities
    - **時価総額と流動性**: 時価総額に基づき、値動きの軽重や機関投資家の参入可能性を考慮せよ。
    - **財務の質 (ROE/PBR/利回り)**: 単なる割安さではなく、資本効率(ROE)と株主還元のバランスから真の価値を評価せよ。
    - **マクロと個別株の相関**: 日経平均やドル円のトレンドが、この銘柄にどのようなベータ（連動性）をもたらすか分析せよ。
    - **イベントリスク (決算)**: 直近の決算日が近い場合、その不確実性を最大の考慮事項とせよ。

    # Mission
    曖昧さを排除し、「期待値（勝率×利益幅）」が最大化される、具体的かつ実行可能なエントリー・利確・損切戦略を提示すること。

    # Signal & Trade Plan Requirements (必須事項)
    - **明確な判定**: 「BUY ENTRY」「SELL ENTRY」「NEUTRAL (様子見)」のいずれかを断定せよ。理由なき「様子見」は避け、テクニカル的根拠に基づいて判断せよ。
    - **トレードプラン**: エントリー価格、利確ターゲット、損切ラインを、現在のボラティリティ(ATR)や主要な抵抗/支持線から論理的に算出せよ。
    - **テクニカル数値の義務化**: 判断の根拠として、必ず「RSIが〇〇で乖離している」「SMA25が〇〇円で上値を抑えている」など、提供された数値を引用せよ。

    # Input Data (市場データ)
    - 銘柄: {ticker}
    - 現在値: ¥{price_info.get('current_price') or 0:,.1f}
    - 変化率: {price_info.get('change_percent') or 0:+.2f}%
    
    ## テクニカル指標
    - 【日足】: {indicators.get('trend_desc', 'N/A')}, SMA(5/25/75): {indicators.get('sma_short')}/{indicators.get('sma_mid')}/{indicators.get('sma_long')}, RSI: {indicators.get('rsi')}, ATR: {indicators.get('atr')}
    - 【週足】: {weekly_indicators.get('trend_desc', 'N/A')}, SMA(13/26/52): {weekly_indicators.get('sma_short')}/{weekly_indicators.get('sma_mid')}/{weekly_indicators.get('sma_long')}
    
    ## マクロ経済環境
    - 日経平均平均 (^N225): {macro_data.get('n225', {}).get('price', 'N/A')} ({macro_data.get('n225', {}).get('change_pct', 0):+.2f}%, {macro_data.get('n225', {}).get('trend', 'N/A')})
    - ドル円 (USD/JPY): {macro_data.get('usdjpy', {}).get('price', 'N/A')} ({macro_data.get('usdjpy', {}).get('change_pct', 0):+.2f}%, {macro_data.get('usdjpy', {}).get('trend', 'N/A')})
    
    ## 検出パターン
    {_format_patterns_for_prompt(patterns)}
    
    ## 需給・ファンダ (Supply/Demand)
    {_format_fundamentals_for_prompt(credit_data)}
    
    ## 直近ニュース (Sentiment)
    {_format_news_for_prompt(news_data)}

    ## 決算説明会文字起こし要約 (Transcripts)
    {_format_transcripts_for_prompt(transcript_data)}

    # Output Format (Structured JSON)
    必ず以下の構造のJSON形式で出力してください。Markdownのコードブロック（```json ... ```）で囲んでください。
    {{
        "status": "【BUY ENTRY / SELL ENTRY / NEUTRAL】",
        "total_score": 0-100,
        "conclusion": "要約された結論（1行）",
        "bull_view": "強気派の詳細な視点（テクニカル数値を含む）",
        "bear_view": "弱気派の詳細な視点（テクニカル数値を含む）",
        "final_reasoning": "シニアアナリストとして両者を統合した、多角的な最終判断根拠",
        "setup": {{
            "entry_price": 数値,
            "target_price": 数値,
            "stop_loss": 数値,
            "risk_reward": 数値
        }},
        "details": {{
            "technical_score": 0-60,
            "sentiment_score": 0-40,
            "sentiment_label": "ポジティブ/中立/ネガティブ",
            "notes": "特記事項（決算日、マクロ要因、需給の数値的懸念等）"
        }}
    }}
    """
    
    error_details = []
    # Stable Model Candidates (2025 Free Tier Optimized)
    MODEL_CANDIDATES = [
        'gemini-3-flash-preview',
        'gemini-2.5-flash-lite',
        'gemini-2.5-flash'
    ]

    # Use V1 SDK if available
    client = get_gemini_client()
    if client:
        for model_name in MODEL_CANDIDATES:
            max_retries = 3
            base_delay = 2  # Initial delay in seconds
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if response and response.text:
                        print(f"Success with Gemini API: {model_name} (Attempt {attempt+1})")
                        return response.text
                except Exception as e:
                    err_msg = str(e)
                    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limit hit (429). Retrying {model_name} in {delay}s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        error_details.append(f"Gemini {model_name} Failed: {err_msg}")
                        break # Try next model if it's not a rate limit error
    else:
        if not GENAI_V1_AVAILABLE:
            error_details.append("V1 SDK (google-genai) not installed.")
        if not API_KEY:
            error_details.append("API Key missing.")
    
    # Fallback to Mock
    debug_info = " | ".join(error_details) if error_details else "Unknown Error"
    return _create_mock_report(strategic_data, enhanced_metrics, indicators, credit_data, error_info=debug_info)

def _create_mock_report(strategic_data, enhanced_metrics, indicators, credit_data, error_info=None):
    """Helper to create strict format mock report in JSON."""
    trend_status = "NEUTRAL"
    conclusion = "方向感が乏しため、明確なシグナルが出るまで静観を推奨します。"
    
    if enhanced_metrics.get('roc_5d', 0) > 2 and indicators.get('rsi', 50) < 70:
            trend_status = "BUY ENTRY"
            conclusion = "短期上昇モメンタムが発生しており、押し目でのエントリーが有効です。"
    elif enhanced_metrics.get('roc_5d', 0) < -2:
            trend_status = "SELL ENTRY"
            conclusion = "下落トレンド中につき、底打ちを確認するまで様子見を推奨。"

    mock_json = {
        "status": trend_status,
        "total_score": 50,
        "conclusion": conclusion,
        "bull_view": "テクニカル指標の一部に下げ止まりの兆候が見られるが、確定的な反転サインではない。",
        "bear_view": "短期的な移動平均線が下向きであり、地合いの悪化が継続するリスクがある。",
        "final_reasoning": f"AI分析エラー({error_info})のため、暫定的なテクニカル判断のみを表示しています。",
        "setup": {
            "entry_price": strategic_data.get('entry_price', 0),
            "target_price": strategic_data.get('target_price', 0),
            "stop_loss": strategic_data.get('stop_loss', 0),
            "risk_reward": strategic_data.get('risk_reward', 0)
        },
        "details": {
            "technical_score": 30,
            "sentiment_score": 20,
            "sentiment_label": "中立",
            "notes": f"エラー情報: {error_info}"
        }
    }

    return f"```json\n{json.dumps(mock_json, ensure_ascii=False, indent=4)}\n```"

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
    for n in news_data[:2]: # Trim to top 2 for token saving
        result.append(f"- 【{n['publisher']}】{n['title']} ({n['provider_publish_time']})")
    
    return "\n".join(result)

def _format_transcripts_for_prompt(transcript_data):
    """Format transcript snippets for inclusion in prompt."""
    if transcript_data is None or transcript_data.empty:
        return "過去の決算説明会データはありません。"
    
    result = []
    for _, row in transcript_data.iterrows():
        content = str(row['Content'])[:1000] # Reduced from 1500 to 1000 for token saving
        result.append(f"### {row['year']} Q{row['quarter']} (公開日: {row['Date']})\n{content}...")
    
    return "\n\n".join(result)
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
            for n in news_list[:2]: # Trim to top 2 for token saving
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

    # Consistently use the same stable candidates for news as well
    MODEL_CANDIDATES = [
        'gemini-3-flash-preview',
        'gemini-2.5-flash-lite',
        'gemini-2.5-flash'
    ]

    client = get_gemini_client()
    if client:
        for model_name in MODEL_CANDIDATES:
            max_retries = 3
            base_delay = 2
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if response and response.text:
                        return response.text
                except Exception as e:
                    err_msg = str(e)
                    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limit hit (429). Retrying {model_name} in {delay}s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"News Analysis V1 ({model_name}) Failed: {e}")
                        break
            
    return "ニュースのAI分析中にエラーが発生しました。接続可能なモデルが見つかりませんでした。"

    return "ニュースのAI分析中にエラーが発生しました。接続可能なモデルが見つかりませんでした。"
