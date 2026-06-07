# web/ — AI COUNCIL フロントエンド（Next.js 15 + Tailwind 4）

`api/`（FastAPI + SSE）を購読し、討論を**1発言ずつストリーミング表示**する。
絵文字は使わず、アバターは**モノグラム＋カテゴリ色**。レスポンシブ（lg 以上は 3 レーン、未満は討論を全画面＋左右ドロワー）。

## 画面構成（3 レーン）

```
ヘッダー: AI COUNCIL                              ● 状態
┌──────────┬─────────────────────┬────────────┐
│ 編成(左)  │   討論(中央・主役)     │ 成果(右)    │
│ ペルソナ  │  議題 / 発言タイムライン │ 議事録・調査 │
│ 選択      │  入力バー(⌘/Ctrl+Enter)│ (議長の統合) │
└──────────┴─────────────────────┴────────────┘
```

## 起動（API と 2 プロセス）

```bash
# 1) バックエンド（別ターミナル・リポジトリルートで）
python -m uvicorn api.main:app --port 8000

# 2) フロント
cd web
npm install
npm run dev          # http://localhost:3000
```

開発時はフロントの API 呼び出し先を `NEXT_PUBLIC_API_BASE`（既定 `http://localhost:8000`）で指定する。
本番は `next build`（`output: "export"`）で `web/out/` に静的書き出しし、**同じ uvicorn が同一オリジンで同居配信**する
（`NEXT_PUBLIC_API_BASE=` 空＝相対パス）。Next.js の rewrites は使わない（SSE をバッファするプロキシ対策として、
ストリームは `fetch` + `ReadableStream` で自前パースし、再接続は POST で叩く）。

## 構成

| パス | 役割 |
|---|---|
| `app/page.tsx` | 3 レーンのページ本体・状態管理・SSE ハンドリング |
| `lib/sse.ts` | `fetch` + `ReadableStream` で SSE を自前パース（EventSource は POST 不可のため） |
| `lib/types.ts` | API と共有する型・表示ラベル |
| `lib/config.ts` | BYOK キー・履歴などの localStorage 管理 |
| `components/PersonaPicker.tsx` | 左：カテゴリ別ペルソナ選択（説明・「詳細」展開つき） |
| `components/Timeline.tsx` | 中央：発言タイムライン（追従スクロール・「最新へ」） |
| `components/MinutesPanel.tsx` / `ResearchNotes.tsx` | 右：議事録・調べたこと |
| `components/KeyEntry.tsx` | BYOK：各自の API キー入力（localStorage のみ・サーバ非保存） |
| `app/globals.css` | デザイントークン（@theme） |

実 LLM は **BYOK**（各自のキー）。キー未入力時は API 側が自動で Mock に落ちるため、キー無しでも全フローを試せる。
