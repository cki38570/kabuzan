# 新機能追加の実装計画：マルチタイムフレーム・センチメント・LINE連携

この計画では、以下の3つのステップを通じてアプリの分析機能と利便性を大幅に強化します。

## 1. マルチタイムフレーム分析とUI改善
大局的なトレンド把握と、直感的なUI操作を可能にします。

### Proposed Changes
- **[MODIFY] [modules/data_manager.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/data_manager.py)**
    - `get_market_data` に `interval` 引数を追加し、週足（`1wk`）に対応。
    - 週足用のテクニカル指標（13週・26週移動平均、RSI）の計算ロジックを追加。
- **[MODIFY] [modules/charts.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/charts.py)**
    - チャートにレンジセレクター（1m, 3m, 1y, All）を追加。
    - ダークモードに適したプロフェッショナルな配色（グリッド線、背景色）に微調整。
- **[MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)**
    - チャート表示部分をタブ分け（日足/週足）し、両方の視点から分析可能にする。
- **[MODIFY] [modules/llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)**
    - 週足データをプロンプトに含め、「大局トレンドに基づくタイミング示唆」を行うよう調整。

---

## 2. センチメント分析（ニュース連携）
Geminiを活用してニュースの影響を数値化します。

### Proposed Changes
- **[NEW] [modules/news.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/news.py)**
    - `yfinance` を通じて最新のニュース記事を取得する機能を実装。
- **[MODIFY] [modules/llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)**
    - 取得したニュースを解析し、「ポジティブ・ネガティブ・中立」を判定するロジックを追加。
    - テクニカルとセンチメントを統合した「総合判断スコア（100点満点）」の提供。
- **[MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)**
    - 画面にセンチメント・スコア（ゲージ風表示）を追加。

---

## 3. LINE Webhook / Notify 通知
特定のチャンスを逃さないための自動通知システムを導入します。

### Proposed Changes
- **[MODIFY] [modules/notifications.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/notifications.py)**
    - シグナル検知関数（RSI < 30 かつ ボリバン下限タッチ等）の実装。
- **[MODIFY] [modules/line.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/line.py)**
    - LINE Notify API を使用したメッセージ送信機能。
    - `st.secrets` からトークンを安全に取得。

---

## ユーザー確認事項
> [!IMPORTANT]
> - LINE通知を利用するには、[LINE Notify](https://notify-bot.line.me/ja/) からアクセストークンを取得し、Streamlitの `secrets.toml` に `LINE_NOTIFY_TOKEN` として保存する必要があります。
> - 週足データの表示により、初期ロード時間がわずかに増加する可能性があります（キャッシュでカバー予定）。

## 検証計画
### 自動テスト
- `modules/news.py` の単体テスト（ニュースが正しく取得できるか）。
- `modules/data_manager.py` の週足指標計算の検証。

### 手動検証
- ブラウザで日足・週足のタブを切り替え、レンジセレクターが正常に動作するか確認。
- ニュースが表示され、それに基づくAI分析が生成されるか確認。
- （テスト用シグナルを発生させて）LINEに通知が届くか確認。
