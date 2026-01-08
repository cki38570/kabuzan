# デプロイおよび本番検証計画

この計画では、最新の変更をデプロイし、本番環境で正常に動作することを確認します。また、以前報告されていたウォッチリストの不具合（ソートエラー、名称読み込み中が続くなど）の最終チェックと修正を行います。

## Proposed Changes

### [Component: UI/App]

#### [MODIFY] [app.py](file:///c:/Users/GORO/Desktop/kabuzan/app.py)
- ウォッチリストのソートロジックの堅牢性向上。
- 不要なインポートの整理または遅延読み込みによるパフォーマンス改善の検討。

### [Component: AI/LLM]

#### [MODIFY] [llm.py](file:///c:/Users/GORO/Desktop/kabuzan/modules/llm.py)
- ユーザー指示に基づき、Geminiモデル名を `gemini-2.0-flash` 等の適切なものに更新（指示にある `gemini-2.5-flash` などの指定を確認しつつ適用）。

## Verification Plan

### Automated Tests
- なし（Streamlit Appのため）

### Manual Verification (Browser Tool)
1. **本番サイトアクセス**: [https://kabuzan-ai.streamlit.app/](https://kabuzan-ai.streamlit.app/) にアクセス。
2. **ウォッチリスト機能確認**:
    - 銘柄（例: 7203）を追加できるか。
    - 名称が正しく取得されるか（「読み込み中...」で止まらないか）。
    - 銘柄を削除できるか。
3. **AI分析実行**:
    - 銘柄を選択し、AI分析タブでレポートが生成されるか確認。
    - テクニカル指標、強気・弱気派の意見が正しく表示されるか。
4. **表示モード確認**:
    - ライトモード/ダークモード、またはモバイル表示での崩れがないか確認。

## フォルダ構成ルールへの準拠
- `docs/deployment_and_verification` フォルダを作成し、関連ドキュメントを保存します。
