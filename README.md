# proactive-agent-ux

従来のチャット型 AI エージェントとの差別化として、**ユーザーの意図を先読みして提案する
プロアクティブ型 UI** を持つ AI エージェントの最小プロトタイプ。
①先読み提案 ②進捗の可視化 ③ワンクリック実行 の体験を重視（バックエンドは簡易モック）。

## 差別化ポイント

1. **提案理由の可視化** — すべての先読み提案に「なぜ提案したか（reason）」を必ず添える。
   理由のない提案は生成しない（`test_every_suggestion_has_reason_and_oneclick_action` で担保）。
   ユーザーは AI の予測根拠を見て納得した上で採否を判断できる。
2. **ワンクリック実行** — 各提案にワンクリック実行アクションを付与。押すと実行が
   **ステップに分解されて進捗表示**され、体感的に「今何をしているか」が分かる。

## 3つの体験

| # | 体験 | 実装 |
|---|------|------|
| ① | 先読み提案（理由つき） | `backend/suggester.py`（文脈→ルールで意図予測） |
| ② | 進捗の可視化 | `backend/progress.py` + `frontend/.../ProgressView.jsx` |
| ③ | ワンクリック実行 | `frontend/.../ProactiveSuggestion.jsx` |

## クイックスタート

```bash
# フロント: ビルド不要。ブラウザで frontend/index.html を開くだけで動作(React CDN)
open frontend/index.html      # or ダブルクリック

# バックエンド(任意): 実提案APIを使う場合
pip install fastapi uvicorn
uvicorn backend.mock_agent_api:app --reload

# ロジックのデモ / テスト
python demo.py
python -m pytest -q
```

Vite で本格ビルドする場合は `frontend/src/`（App.jsx / components）をそのまま利用可能。

## 構成

```
backend/
  suggester.py       # ① 先読み提案エンジン(理由つき・確信度順)
  progress.py        # ② 進捗の可視化(ステップ状態遷移)
  mock_agent_api.py  # 簡易モックAPI(/suggest, /execute, /progress)
frontend/
  index.html         # ビルド不要のスタンドアロンdemo(React CDN)
  src/App.jsx, components/ProactiveSuggestion.jsx, ProgressView.jsx  # Vite用ソース
tests/               # 理由必須・確信度順・進捗完了を検証
```
