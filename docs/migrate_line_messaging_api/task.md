# LINE Messaging API 実装の柔軟性向上タスク

- [ ] `modules/notifications.py` の修正
    - [ ] `Channel ID` と `Channel Secret` からアクセストークンを動的に取得する `get_line_access_token()` 関数の実装
    - [ ] `send_line_message(text)` の改良
        - [ ] アクセストークンが定数でない場合、動的取得を試みる
        - [ ] `User ID` が不明な場合、`broadcast` エンドポイントを使用して「自分（およびフォロワー全般）」に届くようにする
- [ ] `secrets.toml` 設定項目の更新
    - [ ] ユーザーに `LINE_CHANNEL_ID` と `LINE_CHANNEL_SECRET` を設定してもらうよう案内
- [ ] 動作確認
    - [ ] 動的トークン取得が成功するか
    - [ ] ブロードキャスト送信が成功するか（シミュレーション or ログ）
