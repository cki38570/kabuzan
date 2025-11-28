# 📱 株価AI分析アプリ

Gemini AI搭載の日本株分析ツール。リアルタイムデータ、テクニカル分析、AI推奨を統合したモバイルファーストのWebアプリケーション。

🔗 **Live Demo**: [https://kabuzan.streamlit.app](https://kabuzan.streamlit.app)

## ✨ 主な機能

### 📊 データ分析
- **リアルタイム株価表示** - yfinance APIによる最新データ
- **20+の詳細指標** - 52週高値/安値、ボラティリティ、出来高分析、モメンタム指標
- **テクニカル指標** - MA、RSI、MACD、ボリンジャーバンド、ATR
- **信用需給データ** - 信用倍率、買い残・売り残

### 🤖 AI分析
- **Gemini AI統合** - 800文字以上の詳細分析レポート
- **パターン認識** - ローソク足・チャートパターンの自動検出
- **類似銘柄推薦** - 相関分析による類似株の提案
- **戦略的シナリオ** - 具体的なエントリー価格、利確・損切ライン

### 📈 トレード支援
- **エントリーポイント表示** - チャート上に最適なエントリー価格を表示
- **バックテスト機能** - 過去30日の戦略検証（勝率、平均損益）
- **価格アラート** - 目標価格到達時の通知
- **ウォッチリスト** - お気に入り銘柄の管理
- **銘柄比較モード** - 複数銘柄の同時比較

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
