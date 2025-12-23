# 📱 株価AI分析アプリ

Gemini AI搭載の日本株分析ツール。リアルタイムデータ、テクニカル分析、AI推奨を統合したモバイルファーストのWebアプリケーション。

🔗 **Live Demo**: [https://kabuzan.streamlit.app](https://kabuzan.streamlit.app)

## ✨ 主な機能

### 📊 データ分析
- **マルチタイムフレーム対応** - 日足と週足をボタン一つで切り替え表示
- **リアルタイム株価表示** - yfinance APIによる最新データ
- **20+の詳細指標** - 52週高値/安値、ボラティリティ、出来高分析、モメンタム指標
- **テクニカル指標** - MA（日足: 5/25/75, 週足: 13/26/52）、RSI、MACD、ボリンジャーバンド、ATR
- **信用需給データ** - 信用倍率、買い残・売り残

### 🤖 AI分析
- **統合投資判断スコア** - テクニカル(60%)とセンチメント(40%)を統合した100点満点スコアリング
- **ニュース感情分析** - 関連ニュースの「ポジティブ・ネガティブ・中立」をAIが判定
- **Gemini AI統合** - 週足トレンドを考慮した800文字以上の詳細分析レポート
- **戦略的シナリオ** - 具体的なエントリー価格、利確・損切ライン

### 📈 トレード支援
- **LINE通知連携** - RSI売られすぎやボリンジャーバンド接触時などの重要シグナルをLINE Notifyで通知
- **チャートレンジセレクター** - 1ヶ月、3ヶ月、6ヶ月、1年、すべての期間を瞬時に切り替え
- **エントリーポイント表示** - チャート上に最適なエントリー価格を表示
- **バックテスト機能** - 過去30日の戦略検証（勝率、平均損益）
- **ウォッチリスト** - お気に入り銘柄の管理

### 📱 モバイル対応
- **PWA対応** - ホーム画面に追加してネイティブアプリのように使用可能
- **Android最適化** - タッチ操作に最適化されたUI
- **ダークテーマ** - 目に優しいデザイン

## 🚀 技術スタック

- **Frontend**: Streamlit
- **Data**: yfinance, pandas, numpy
- **Charts**: Plotly
- **AI**: Google Gemini API
- **Deployment**: Streamlit Cloud

## 📦 ローカル実行

### 必要要件
- Python 3.9+
- pip

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/cki38570/kabuzan.git
cd kabuzan

# 依存関係をインストール
pip install -r requirements.txt

# アプリを起動
streamlit run app.py
```

ブラウザで `http://localhost:8501` を開く

### 環境変数

Gemini APIを使用する場合、環境変数を設定：

```bash
export GEMINI_API_KEY="your_api_key_here"
```

または、Streamlit Secretsに設定（`.streamlit/secrets.toml`）：

```toml
GEMINI_API_KEY = "your_api_key_here"
```

## 🎯 使い方

1. **銘柄検索**: 銘柄コード（例: 7203）を入力
2. **チャート確認**: ローソク足チャート、移動平均線、エントリーポイントを確認
3. **AI分析**: 詳細な分析レポートと具体的な推奨を確認
4. **データ確認**: 詳細市場データとバックテスト結果を確認

## 📱 PWA化（スマホ）

### Android
1. Chromeでアプリを開く
2. メニュー（︙）→「ホーム画面に追加」
3. アイコン名を設定して追加

## 🔄 アップデート方法

```bash
# コードを修正後
git add .
git commit -m "Update: 修正内容"
git push

# Streamlit Cloudが自動的に再デプロイ（1-2分）
```

## 📊 スクリーンショット

（TODO: スクリーンショットを追加）

## 🤝 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📄 ライセンス

MIT License

## 👤 作成者

GORO ([@cki38570](https://github.com/cki38570))

## 🙏 謝辞

- [yfinance](https://github.com/ranaroussi/yfinance) - 株価データ取得
- [Streamlit](https://streamlit.io/) - Webアプリフレームワーク
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI分析エンジン
