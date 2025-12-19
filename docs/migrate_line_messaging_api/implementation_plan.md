# LINE Messaging APIへの移行計画

LINE Notifyのサービス終了（2025年3月31日）に伴い、LINE Messaging APIを使用した通知機能へ移行します。

## ユーザーレビューが必要な事項
- **必要な認証情報の取得 (最新手順対応)**: 
  ご指摘の通り、現在は公式アカウント作成後に Messaging API を有効にする流れとなっています。その設定が完了している場合、以下の情報を LINE Developers コンソールから取得いただけます。
  1. **Channel Access Token (long-lived)**: LINE Developers コンソールの対象チャネル内「Messaging API設定」タブの一番下にある「発行」ボタンで取得できます。
  2. **Your User ID**: 同じく「Messaging API設定」タブ内の「Your user ID」項目に記載されている `U` から始まる文字列です。
  ※これらの値が揃い次第、`modules/notifications.py` の実装と `secrets.toml` への設定を行います。

## 変更内容

### 1. 通知機能の刷新

#### [MODIFY] [notifications.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/notifications.py)
- **新しい通知関数の追加**: `send_line_message(text)` を実装します。これは LINE Messaging API のプッシュメッセージエンドポイントを使用します。
- **定数の定義**: `LINE_CHANNEL_ACCESS_TOKEN` と `LINE_USER_ID` をコード冒頭で設定（secretsから取得）します。
- **既存処理の更新**: `process_morning_notifications` 内で、LINE Notify 用の `send_line_notification` を呼び出している箇所を、新しい `send_line_message` に置き換えます。

### 2. メインアプリとの連携

#### [MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)
- **インポートの追加**: `modules.notifications` から `send_line_message` をインポートし、他で必要になった際に呼び出せるようにします。

## 検証計画

### 手動検証
1. 「テスト通知を送信」ボタンを Messaging API 用に更新し、実際にスマホの LINE アプリにメッセージが届くか確認します。
2. 朝のニュース要約ロジックを走らせ、プッシュメッセージとして届くかを確認します。
