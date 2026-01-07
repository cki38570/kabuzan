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

def generate_gemini_analysis(ticker, price_info, indicators, credit_data, strategic_data, enhanced_metrics=None, patterns=None, extra_context=None, weekly_indicators=None, news_data=None, macro_data=None, transcript_data=None, relative_strength=None, backtest_results=None, past_history=None, credit_df=None):
    """
    Generate a professional stock analysis report using a 'Virtual Investment Committee' flow.
    Integrates detailed evidence-based Bull/Bear logic and feedback from past predictions.
    """
    if price_info is None: price_info = {}
    if indicators is None: indicators = {}
    if macro_data is None: macro_data = {}
    if transcript_data is None: transcript_data = pd.DataFrame()
    if relative_strength is None: relative_strength = {}
    if weekly_indicators is None: weekly_indicators = {}
    if news_data is None: news_data = []

    # Prepare historical feedback if available
    history_context = ""
    if past_history:
        history_context = f"""
        ## 過去の分析フィードバック (Memory Feedback)
        前回分析日: {past_history.get('date')}
        前回判定: {past_history.get('status')} (スコア: {past_history.get('score')})
        当時の価格: ¥{past_history.get('price'):,.1f}
        現在の価格: ¥{price_info.get('current_price', 0):,.1f}
        **反省タスク**: 前回の予測が当たっていたか検証し、その傾向（強気すぎた、あるいはリスクを見落としていた等）を今回の分析に活かしてください。
        """
        
    # Advanced Prompt: Virtual Investment Committee
    prompt = f"""
    # Role: 仮想投資戦略会議 (Virtual Investment Committee)
    最高峰のヘッジファンドにおける「投資委員会」として、以下の3名の専門家による独立した分析と、最終決定プロセスを経てレポートを作成してください。

    {history_context}

    # Stage 1: 専門家別分析 (Specialized Insights)
    
    ## 1. テクニカル分析担当 (Technical Specialist)
    - 指標の具体的な数値（RSI, 移動平均乖離率, ボリンジャーバンドの位置, ATR）に基づき、論理的にトレンドを定義せよ。
    - **厳守**: 単に「上昇傾向」とするのではなく、「RSIが{indicators.get('rsi')}であり過熱圏に近づいているため、一時的な押し目が必要」といった具体的な根拠を示せ。
    
    ## 2. 需給・市場心理担当 (Supply/Demand Expert)
    - 信用倍率、出来高倍率、地合い（日経平均・ドル円）との相関から、上値の重さや底堅さを分析せよ。
    - **マクロ環境連携**: ドル円が{macro_data.get('usdjpy', {}).get('price', 'N/A')} ({macro_data.get('usdjpy', {}).get('trend', 'N/A')}) であることが、この銘柄の輸出/輸入採算や株価にどう影響するか言語化せよ。
    
    ## 3. ファンダメンタル・材料担当 (Fundamental/News Analyst)
    - PBR/PERの見地、直近ニュース、決算説明会の内容から、中長期的な価値を評価せよ。
    - 決算説明会の書き起こしデータ（Transcript）がある場合は、経営陣のトーンや具体的な成長戦略に必ず言及すること。

    # Stage 2: 深層自己反省 (Bull/Bear Deep Reflection)
    テクニカル・需給・ファンダすべての情報を統合し、以下の2名に**徹底的な論理バトル**を行わせてください。
    1. **強気派 (Bull)**: 200〜300文字で、具体的な指標数値を根拠に、なぜ今「買い」なのかを論証せよ。
    2. **弱気派 (Bear)**: 200〜300文字で、潜在的リスクやテクニカルの弱点、マクロ懸念を根拠に、なぜ今「見送り/売り」なのかを反論せよ。
    **条件**: 「期待できる」といった抽象的な表現を禁じ、「SMA25が下向きである」「信用買残が過去平均より30%多い」といった定量的根拠を必ず含めること。

    # Stage 3: 最終投資判断 (Final Directive)
    以下の計算された戦略データを参考にしつつも、AI独自のリスク評価を加えて最終的なアクションプランを決定してください。
    - 計算された戦略目安: {strategic_data}

    # Input Data
    - 銘柄: {ticker}
    - 現在値: ¥{price_info.get('current_price') or 0:,.1f} ({price_info.get('change_percent') or 0:+.2f}%)
    - 日足テクニカル: RSI:{indicators.get('rsi')}, MACD:{indicators.get('macd_status')}, BB:{indicators.get('bb_status')}
    - 週足テクニカル: {_format_indicators_for_prompt(weekly_indicators, "週足")}
    - 市場環境: 日経平均 ¥{macro_data.get('n225', {}).get('price', 'N/A')}, ドル円 ¥{macro_data.get('usdjpy', {}).get('price', 'N/A')}
    - 相対比較: {relative_strength.get('status', 'N/A')} ({relative_strength.get('desc', 'N/A')})
    - ファンダメンタルズ: {_format_fundamentals_for_prompt(credit_data)}
    - 需給 (信用残): {_format_credit_for_prompt(credit_df)}
    - ニュース: {_format_news_for_prompt(news_data)}
    - 決算説明会 (Transcript): {_format_transcripts_for_prompt(transcript_data)}
    - 過去のバックテスト成績: {_format_backtest_for_prompt(backtest_results)}

    # Output Format (Strict JSON)
    # 重要: 各テキストフィールド（sector_analysis, technical_detail, macro_sentiment_detail, bull_view, bear_view, final_reasoning）は、
    # 決して一言で終わらせず、背景・根拠・展望を含めて200〜300文字程度で非常に詳細に論理を展開してください。
    # 確信度 (confidence_score) は0-100で、データの鮮度やシグナルの合致度から算定せよ。
    ```json
    {{
        "status": "【BUY ENTRY / SELL ENTRY / NEUTRAL】",
        "total_score": 0-100,
        "confidence_score": 0-100,
        "headline": "結論を一言で",
        "sector_analysis": "セクター内での立ち位置やバリュエーション評価（詳細かつ論理的に）",
        "technical_detail": "日足・週足のマルチタイムフレーム分析に基づく具体的かつ網羅的な分析結果",
        "macro_sentiment_detail": "需給とマクロ（ドル円等）の相関および市場心理の深掘り分析",
        "bull_view": "強気派の論理的根拠（200-300文字、定量的数値を3つ以上含めること）",
        "bear_view": "弱気派の論理的根拠（200-300文字、定量的数値を3つ以上含めること）",
        "memory_feedback": "過去の分析との答え合わせ結果と今回の修正点（あれば）",
        "final_reasoning": "全専門家の意見を統合した最終根拠（250-300文字程度で極めて詳細に記述）",
        "transcript_score": 1-5,
        "transcript_reason": "決算説明会や定性的材料に基づく自信度の根拠（100文字程度）",
        "backtest_feedback": "精度向上したバックテスト結果に基づく戦略の妥当性評価",
        "action_plan": {{
            "recommended_action": "具体的アクション",
            "buy_limit": 数値,
            "sell_limit": 数値,
            "stop_loss": 数値,
            "rationale": "価格設定の具体的・論理的根拠（支持線・抵抗線の具体的数値や戦略計算値を参照）"
        }}
    }}
    ```
    """
    
    error_details = []
    # Stable Model Candidates (Updated to 3.0/2.5 per user request)
    MODEL_CANDIDATES = [
        'gemini-2.5-flash',
        'gemini-3-flash'
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
        "confidence_score": 30,
        "headline": "AI分析エラーによる簡易リポート",
        "conclusion": conclusion,
        "technical_detail": "ルールベースによるテクニカル判定のみを生成しています。",
        "macro_sentiment_detail": "市場ニュースとの相関分析をスキップしました。",
        "bull_view": "テクニカル指標の一部に下げ止まりの兆候が見られるが、確定的な反転サインではない。",
        "bear_view": "短期的な移動平均線が下向きであり、地合いの悪化が継続するリスクがある。",
        "final_reasoning": f"AI分析エラー({error_info})のため、暫定的な判定を表示しています。",
        "action_plan": {
            "recommended_action": "様子見",
            "buy_limit": strategic_data.get('entry_price', 0),
            "sell_limit": strategic_data.get('target_price', 0),
            "stop_loss": strategic_data.get('stop_loss', 0),
            "rationale": "AI分析不能のため、テクニカル計算値を指値目安としています。"
        }
    }

    return f"```json\n{json.dumps(mock_json, ensure_ascii=False, indent=4)}\n```"

def _format_indicators_for_prompt(indicators, label="日足"):
    """Format technical indicators for the prompt."""
    if not indicators:
        return f"{label}データ不足"
    
    lines = [
        f"RSI: {indicators.get('rsi', 'N/A')}",
        f"MACD: {indicators.get('macd_status', 'N/A')}",
        f"BB: {indicators.get('bb_status', 'N/A')}",
        f"トレンド: {indicators.get('trend_desc', 'N/A')}"
    ]
    return ", ".join(lines)

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
        f"- 配当利回り: {fmt(details.get('dividend_yield'), '%')}",
        f"- ROE: {fmt(details.get('roe'))}",
        f"- セクター: {details.get('sector', 'N/A')}"
    ]
    return "\n".join(lines)

def _format_credit_for_prompt(credit_df):
    """Format credit margin data for the prompt."""
    if credit_df is None or credit_df.empty:
        return "- 信用残データ: なし"

    try:
        latest = credit_df.iloc[0] # assuming sorted latest first in data.py logic
        
        # Check if we have multiple points for trend
        trend = ""
        if len(credit_df) >= 2:
            prev = credit_df.iloc[1]
            if latest['信用倍率'] > prev['信用倍率']:
                trend = "(悪化傾向)"
            elif latest['信用倍率'] < prev['信用倍率']:
                trend = "(改善傾向)"
        
        return f"""
        - 信用倍率: {latest.get('信用倍率', 'N/A')}倍 {trend}
        - 信用売残: {latest.get('売残', 0):,}
        - 信用買残: {latest.get('買残', 0):,}
        """
    except Exception as e:
        return f"- 信用残データ: 書式エラー ({e})"

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

def _format_backtest_for_prompt(results):
    """Format backtest results for AI consumption."""
    if not results or not isinstance(results, dict):
        return "直近のバックテストデータはありません。"
    
    lines = [
        f"- **勝率**: {results.get('win_rate', 0):.1f}%",
        f"- **総取引数**: {results.get('total_trades', 0)}回",
        f"- **平均利益率**: {results.get('avg_profit', 0):.2f}%",
        f"- **リスクリワード比**: {results.get('risk_reward', 0):.2f}",
        f"- **総損益**: {results.get('total_pl', 0):.2f}%"
    ]
    return "### 過去30日の運用成績（バックテスト）\n" + "\n".join(lines)
        
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
        'gemini-2.5-flash',
        'gemini-3-flash'
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
