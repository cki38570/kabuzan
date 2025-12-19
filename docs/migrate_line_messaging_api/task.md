# LINE Messaging APIへの移行タスク

- [ ] `modules/notifications.py` の修正
    - [ ] `LINE_CHANNEL_ACCESS_TOKEN` と `LINE_USER_ID` の定数定義 (st.secretsから取得)
    - [ ] `send_line_message(text)` 関数の実装 (requestsを使用)
    - [ ] 既存の `process_morning_notifications` 内の通知ロジックを新関数に置き換え
- [ ] `app.py` の修正
    - [ ] `send_line_message` のインポート追加
- [ ] 認証情報の保存
    - [ ] `.streamlit/secrets.toml` に `LINE_CHANNEL_ACCESS_TOKEN` と `LINE_USER_ID` を追加 (ユーザーから取得後)
- [ ] 設定UIの更新
    - [ ] `show_notification_settings` から LINE Notify 関連の入力（トークン等）を削除または Messaging API 用に更新（今回は定数を使うため、UIでの入力は不要になる可能性があるが、確認が必要）
- [ ] 動作確認
    - [ ] 実際に通知が送信されるか（シミュレーションまたはログ確認）
