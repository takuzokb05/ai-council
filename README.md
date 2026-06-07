# AI COUNCIL

**複数の人格（職種・思想家・経営者）をもつ AI が、フェーズを踏んで“討論”するマルチエージェント議論エンジン。**
1 つの問いに対して、論理・共感・財務・法務…や、ソクラテス／ドラッカー／渋沢栄一といった偉人ペルソナが
発散→批判→収束の順で意見を戦わせ、議長が議事録に統合する。発言は 1 つずつストリーミング表示される。

> **English TL;DR** — A multi-agent deliberation engine. Distinct AI personas (roles + historical thinkers)
> debate a topic across phases (diverge → critique → converge); a chair synthesizes the minutes.
> **Bring your own LLM key (BYOK)** — this repo ships *no* API key. With no key it runs a free, deterministic
> **mock** mode so you can try the whole flow at zero cost. Backend: Python/FastAPI + SSE. Frontend: Next.js 15.

- 🆓 **キー無しで動く** — API キーを設定しなければ自動で **Mock**（決定的なサンプル応答）に落ちる。UX をゼロコストで試せる。
- 🔑 **BYOK（各自のキー持参）** — 本物の討論は利用者自身の API キーで動く。**このリポジトリにキーは含まれない／同梱しない**。Anthropic / OpenAI / Google(Gemini) の 1 社を選んで使う。
- 🧩 **ペルソナはデータ** — 46 体を YAML で同梱。コードを触らず YAML 追加だけで増やせる。
- 🧠 **設計でバグを根治** — 「人格混線・沈黙・均質化」というマルチエージェント討論の 3 大失敗を、プロンプト芸でなく**構造**で潰している（下記）。

---

## なぜ作ったか — マルチエージェント討論の「3 大バグ」を構造で根治

素朴に「複数の AI に順番に喋らせる」と、だいたい次の 3 つで破綻する。本実装はそれぞれを設計で潰している。

| 失敗 | 症状 | 本実装の根治 |
|---|---|---|
| **人格混線** | 途中から全員が同じ口調・主張に溶ける | 発言者から見て**自分の過去発言だけ `assistant`／他者は `【名前】` 付きの `user`** でコンテキストを組む（`core/context.py`）。文脈上「自分」と「他人」が常に分離される。 |
| **沈黙** | 司会の指名待ちで誰も喋らない／同じ人ばかり喋る | 発言順を LLM に委ねず **ラウンドロビン**で決め、各ラウンドで全パネリストが必ず 1 回発言する（`core/orchestrator.py`）。 |
| **均質化 (collapse)** | ラウンドを重ねるほど意見が同質化する | ペルソナ毎に `model`／`temperature` を変えられ、毎ターン反同調プロンプトと system 再注入を行う。 |

さらに **フェーズ進行**（発散→批判→収束）で議論に骨格を与え、**SSE ストリーミング**で「終わるまで何も見えない」を解消、**議長による議事録統合**で成果物を残す。

---

## アーキテクチャ（3 層）

```
core/   フレームワーク非依存の討論エンジン（テスト可能・UI/HTTP に依存しない）
  ├ personas.py      ペルソナ・レジストリ（dataclass + YAML ローダ）
  ├ context.py       人格混線を根治するコンテキスト構築
  ├ orchestrator.py  Council（フェーズ進行）＋ ラウンドロビン ＋ Turn
  └ llm_client.py    LLM 統一 IF（Anthropic / OpenAI / Gemini / Mock）

api/    薄い HTTP 層（FastAPI）。core の run() を SSE で配信
  ├ service.py       ドメインロジック（FastAPI 非依存・単体テスト可能）
  └ main.py          ルーティング（/health /personas /sessions …）

web/    Next.js 15 + Tailwind 4。SSE を購読し 1 発言ずつ表示（静的書き出し対応）
personas/  ペルソナ YAML（46 体）
presets/   編成プリセット（builtin）
tests/     run_tests.py（Mock で決定的・API キー不要）
```

---

## クイックスタート（API キー不要・Mock）

> 前提: Python 3.10+ / Node.js 20+（npm 同梱）。

```bash
# 1) バックエンド（リポジトリのルートで実行）
python -m pip install -r requirements.txt
python -m uvicorn api.main:app --port 8000        # キー未設定なら自動で Mock

# 2) フロントエンド（別ターミナル）
cd web
npm install
npm run dev                                        # http://localhost:3000
```

ブラウザで議題を入れて「討論を開始」。キーが無い状態では Mock（無料のサンプル応答）で全フローを体験できる。
ストリーミングのライブ感（1発言ずつ流れる様子）を Mock で見たいときは `.env` に `AI_TEAMS_MOCK_DELAY=0.2` を入れる。

エンジン単体の疎通（サーバ不要）:

```bash
python tests/run_tests.py     # 混線・沈黙・モデル上書き等を Mock で検証
```

---

## 本物の LLM で動かす（BYOK）

実 LLM を使うには **利用者自身の API キー**が要る。**このリポジトリはキーを同梱しない。**

- **ローカル/個人運用**: `.env` に `ANTHROPIC_API_KEY=...` を置く（`.env.example` 参照）。`.env` は `.gitignore` 済み。
- **共有/公開運用（BYOK）**: 環境変数 `AI_TEAMS_BYOK=1` を立てると、**サーバのキーを来訪者に一切使わせない**。
  来訪者は自分のキーを画面で入力し（ブラウザの localStorage のみに保存・サーバ非保存）、毎リクエストのヘッダで送る。
  キー未入力なら自動で Mock。あわせて `AI_TEAMS_READONLY=1`（編成 CRUD を 403）とレート制限の利用を推奨。

> 実 LLM を使うと API 利用料が発生する。討論はサーバ側のバックグラウンド実行（“プロデューサ”）で進むため、
> 開始後にブラウザを閉じても最後まで走りコストが出る（止めるには停止/終了操作が要る）点に注意。

主な環境変数は `.env.example` を参照。環境変数は歴史的経緯で `AI_TEAMS_` プレフィックスを使う（`AI_TEAMS_BYOK` 等）。

---

## 自前ホスト（公開する場合）

`web` を静的書き出し（`next build` → `web/out/`）し、**同じ uvicorn が静的 SPA を同一オリジンで同居配信**できる
（`api/main.py` 末尾で `web/out` があれば `/` にマウント）。Node 常駐も CORS 設定も不要。

公開時の最小ゲートは **BYOK（各自キー）＋ readonly ＋ レート制限**。長時間 SSE を通すトンネル
（例: cloudflared）と相性が良い（再接続は POST で叩く。GET ストリームをバッファするプロキシ対策）。

---

## ペルソナを追加する

`personas/` 配下に YAML を 1 ファイル足すだけ（再起動で読み込まれる）。効くのは YAML 内の
`category:` フィールドで、置くディレクトリは整理用（フィールドと一致していなくてよい）。

```yaml
id: my_persona              # 半角英小文字・数字・_・-
display_name: 私の参謀
# パネリスト: thinking / founders / philosophers
# 進行役（自動で編成に入る）: facilitation(司会) / chair(議長) / scribe(書記・発言しない)
category: thinking
description: "一行ティーザー（カードに表示）"
detail: "「詳細」で開く詳しい説明。どんな人か・何が持ち味か。"
system_prompt: |
  このペルソナの判断軸・口調・役割をここに書く。
```

役割の id ↔ 表示名: 司会=`moderator`(facilitation)、議長=`chair`、書記=`scribe`、調査役=`researcher`。
UI からの「自分のペルソナ」作成（このブラウザにのみ保存・サーバ非保存）にも対応。

---

## ステータス・既知の制限

- セッション状態はインメモリ（単一ワーカー前提）。永続化・マルチワーカー共有ストアは未実装。
- 実 LLM のモデル名は更新が速い。既定は環境変数で差し替え可能（コード変更不要）。

## 免責

- **著名人ペルソナ（スティーブ・ジョブズ、ソクラテス、渋沢栄一、イーロン・マスク 等。存命の人物も含む）は
  本人ではなく、公開された言動・思想に基づく解釈的な“演出”**です。特定個人の見解・発言を表すものではなく、
  事実の断定や捏造を意図したものではありません。
- 本プロジェクトは Anthropic / OpenAI / Google とは無関係の個人プロジェクトです。
- BYOK 利用時の API 利用料・利用規約の遵守は各利用者の責任です。

## ライセンス

[MIT](LICENSE)
