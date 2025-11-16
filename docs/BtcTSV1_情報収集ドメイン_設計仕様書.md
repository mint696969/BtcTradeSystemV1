# BtcTradeSystem V1 — 情報収集ドメイン 設計仕様書（共有版）

最終更新: 2025-11-03 16:49:50 UTC+09:00
作成対象: Collector / Health（収集健全性）/ Ops-Audit（運用監査）
適用範囲: **メイン PC 単体運用**（将来の 収集専用 PC+NAS 構成へ拡張可能な I/F で設計）

---

## 0. 目的と前提

- 本仕様は「チャットを跨いでも迷子にならない」ための **設計図** である。
- まずは **メイン PC 単体** で価値を証明（“光が見える”）。使い物にならない場合は撤退可能。
- 価値が確認できた場合に **収集専用 PC + NAS** へスムーズに拡張できる **契約(I/F) 先行** 設計。
- 情報収集は「できて当たり前」。後続の **売買アシスト → 自動売買 → AI 学習** を阻害しないデータ設計を最優先。
- **1 ファイル 1 キャンバス**・**現物確認の上での変更**・**新規ファイルは 2 行ヘッダ（# path/# desc）** を厳守。

---

## 1. 成果物（完成像）

### 1.1 Collector（独立プロセス）

- 二重起動防止（Leader Lock, stale 奪取あり）
- 取引所ごとのレート制御（優先度: 板/圧力 > 心理指標 > クロスアセット）
- 429/Retry-After 尊重、指数バックオフ、段階復帰、WS 主系 + REST 穴埋め
- 原子的ファイル出力（CSV 置換 / JSONL 追記+fsync）
- `status.json` を **最終形スキーマ** で継続更新（1–3s）
- Health からの `slow_down / restart / stop` 制御コマンドの受け口（本実装）

### 1.2 Health（ダッシュボード表示 + 設定タブ）

- 表示タブ: **取引所 × エンドポイントの健全性カード**（OK/WARN/CRIT, 外因/内因タグ, ドリルダウン）
- 設定タブ: **表示順の並べ替え**・**閾値/自動アクション** を **プリセット＋ Custom** で編集
- 自動アクション: 条件一致で Collector へ **slow_down / restart / stop** を発行（TTL/クールダウン設定）

### 1.3 Ops-Audit（運用監査）

- 初期出力の優先順位: **④ データ品質(DQ) → ⑤ リソース/コスト → ② インシデント時系列**
- 変更ジャーナル/日次オペレポは後付けで自動生成可能

### 1.4 可視化（後続：売買アシスト）—*収集仕様に影響する要件*のみ明記

- **S/H デュアル・チャネル**: System(S) と Human(H) を分離記録。学習は S-only + 良い H のみ採用。
- **信号・注文・約定** を同一タイムラインで重ね、 signal クリックで **評価ウィンドウ（t+5s/1m/5m）** 表示。

---

## 2. リポジトリ構成（平置き・機能集中・重複なし）

> 1 機能=1 フォルダに集約。サブフォルダは基本 `config/` のみ。ファイル名は唯一で迷わないこと。

```
features/
  collector/
    collector_entry.py         # 起動/停止の入口（独立プロセス）
    collector_scheduler.py     # 間隔管理・起動停止
    collector_rate.py          # 取引所バケット＋endpoint優先度
    collector_status.py        # status.json 最終形スキーマ出力
    collector_io.py            # CSV置換/JSONL追記+fsync
    collector_control.py       # slow_down/restart/stop 受け口
    collector_errors.py        # 例外型と正規化
    bitflyer_public.py         # 取引所APIラッパ（例）
    binance_public.py          # （例）
    okx_public.py              # （例）
    bybit_public.py            # （例）
    config/
      collector_def.yaml       # 既定（追跡対象）

  health/
    health_entry.py            # 評価の起動点
    health_eval.py             # status.json → 外因/内因・SLO判定
    health_actions.py          # Collector制御の実行
    ui_health.py               # 表示（読取専用）
    set_health.py              # 設定（表示順/閾値/アクション）
    config/
      health_def.yaml          # 既定（追跡対象）

  ops_audit/
    ops_audit_writer.py        # 運用イベント記録（再起動/降格/復帰…）
    ops_audit_reports.py       # DQ/Resource/Timeline の集計
    ui_ops_audit.py            # 任意の可視化
    config/
      ops_audit_def.yaml       # 既定（追跡対象）

config/
  ui/
    collector.yaml             # 現在値（追跡外）
    health.yaml                # 現在値（追跡外）
  secrets.ini                  # API/秘密（追跡外・常時マスク）
```

---

## 3. 設定 UI ポリシー（プリセット＋ Custom）

- すべての数値/組合せは **プルダウン（プリセット）→ Custom 選択で自由入力** の二段式。
- 単位は選択肢内に含め、誤入力を抑止（`5s`, `1/s`, `60/min` 等）。
- **Advanced トグル**で詳細パラメータを露出。
- **一時適用(Preview) → 保存** の二段適用。保存時に Ops-Audit へ **変更ジャーナル** を記録。

### 3.1 Collector 設定（設定タブ）

- 取引所ごとの: 有効化 / API Key（常時マスク・暗号化保存）/ 取得対象（板・trades…）/ 総レート上限 / endpoint 優先度
- レート配分モード: `固定 / SLA / 適応(準備)`（最初は **SLA** が既定）
- 再試行・バックオフ: プリセット＋ Custom

### 3.2 Health 設定（設定タブ）

- 表示順（取引所/endpoint の並べ替え）
- 閾値セット: `緩め / 標準 / 厳しめ / Custom`（age_sec, 連続違反, 復帰条件 などを束ねて管理）
- 自動アクション: `slow_down / restart / stop` 有効化、TTL/クールダウン設定

---

## 4. 主要 I/F（契約・スキーマ）

### 4.1 status.json（**最終形を初手から採用**）

- 更新間隔: 1–3 秒
- Health の第一ソース（mtime フォールバックは緊急時のみ）

```json
{
  "updated_at": "ISO8601Z",
  "leader": { "host": "local", "since": "ISO8601Z", "active": true },
  "storage": { "primary": "up", "secondary": "idle", "secondary_path": null },
  "sync": {
    "pending": false,
    "last": { "at": null, "items": 0, "bytes": 0, "ok": true }
  },
  "items": [
    {
      "exchange": "bitflyer",
      "topic": "orderbook",
      "last_ok": "ISO8601Z",
      "age_sec": 0.18,
      "cause": null,
      "retries": 0,
      "notes": "ok",
      "source": "runtime"
    }
  ]
}
```

### 4.2 制御コマンド（Health → Collector）

- 受信手段: 初期は **ファイルキュー**（後日 RPC 差替え可）
- 重複防止: `cmd_id` と `ttl_s` で担保

```json
{ "cmd":"slow_down", "scope":"bitflyer.orderbook", "factor":0.5, "ttl_s":120, "cmd_id":"..." }
{ "cmd":"restart",   "scope":"bitflyer.trades",     "reason":"stale", "cmd_id":"..." }
{ "cmd":"stop",      "scope":"all",                 "reason":"manual", "cmd_id":"..." }
```

### 4.3 信号/注文/約定（S/H デュアル・チャネル）

> 可視化・評価・学習で共通利用。内部 UTC、表示は Asia/Tokyo。

**signal**

- `id, ts, channel(S/H), side, strength, rationale, features_digest(topK), model_info(id/version/params_hash), thresholds_name, market_context, rate_state, eval_targets=[5s,60s,300s]`

**order**

- `id, signal_id, ts, side, qty, price_type, route(bitFlyer), status(pending/partial/canceled/filled)`

**fill**

- `id, order_id, ts, avg_price, filled_qty, fee, slippage, pnl_mark(t+X)`

**eval（自動付与）**

- `signal_id → { at_5s, at_60s, at_300s } = { direction(up/down/flat), pnl, mae, mfe, hit? }`

---

## 5. レート制御ポリシー（取引所ごと／B を最終目標に C で運転）

- 優先度: **Retry-After 最優先** ＞ 429 既定待機 ＞ 内部安全則
- バケット: `exchange` を中核に `endpoint` 優先度で配分
- ディレート: 連続 429 で指数的に延伸、復帰は段階的（ヒステリシス）
- WS 主系 + ドロップ時のみ REST 補完（短時間）
- **方式**: まず **C: SLA ＋優先度キュー** を既定  
  並行して **B-1/B-2（情報利得メトリック計測 → 軽い自動調整）** を常時実行、データが溜まり次第 **B へ昇格**。

---

## 6. Ops-Audit 初期出力（優先順位と目的）

1. **データ品質（DQ）** — 欠損率・連続欠損・REST 補完成功率・SLA 違反率（板は厳しめ）
2. **リソース/コスト** — 取引所 ×endpoint の呼出回数・平均待機・降格滞在・429 収束時間
3. **インシデント時系列** — 重要イベント（SLA 違反/WS ドロップ/降格 → 復帰）と S/H の意思決定を一本化

> 変更ジャーナル / 日次オペレポは **後付け自動生成**。

---

## 7. UI/UX（数値入力・可視化・安全運用）

- **プルダウン＋ Custom**（単位付き）/ **Advanced** / **Preview→ 保存** / **変更は Ops-Audit に自動記録**
- **Health 表示**は読み取り専用、**設定**で編集。カード順は設定に追従。
- **S/H フィルタ**、signal ツールチップに **根拠**、クリックで **評価ウィンドウ**。

---

## 8. 品質基準（受け入れ条件）

- **Collector**: 二重起動不可（stale 時のみ奪取）、429/Retry-After 追従、I/O 破損 0、status.json を 1–3s で更新
- **Health**: 表示順と閾値が設定通り、自動アクションが Collector へ到達・効果
- **Ops-Audit**: DQ/Resource/Timeline が閲覧可能、主要イベントは相互に突合が取れる
- **可視化**: S/H 分離表示・フィルタ、評価ウィンドウ、PNG/CSV エクスポート
- **学習準備**: S-only + 良い H 抽出がフォーマット固定で出力可能

---

## 9. テスト計画（メイン PC 単体での検証）

- **多重起動**: 同時起動 → 2 体目拒否／stale 奪取の確認
- **429 擬似**: 429+Retry-After → 待機 → 復帰（収束時間）
- **ネット断**: DNS/NET 障害 → 待機モード降格 → 復帰
- **I/O 障害**: 書込不可先 → WRITE_ERR → 停止 or 低頻度化
- **status.json**: age_sec・cause の健全推移、Health 側の表示/閾値反映
- **Ops-Audit**: DQ/Resource/Timeline の指標が想定の範囲で出力

---

## 10. 将来拡張（収集専用 PC+NAS への移行）

- `leader/storage/sync` ブロックへ **実値** を流し込む（NAS ロック / フェイルオーバ / 冪等同期）
- 制御ポートを **RPC/IPC** に差替（Health 側は I/F 不変）
- レート配分を **適応（B-3 以降）** へ昇格（学習成果を接続）
- Ops-Audit に **日次/週次レポ** と **変更ジャーナル** を追加

---

## 11. 運用ルール（メモ）

- ダッシュボードは **薄い入口**（dashboard.py/settings.py は原則不改変）
- 変更提案は **1 ファイル 1 キャンバス** + ① 追加/② 差替/③ 削除 フォーマット
- Secrets は常時マスク、コピー時はワンショット表示、保存は暗号化
- 重要な閾値変更や手動介入は **Ops-Audit** に必ず残る

---

## 付録 A: 外因/内因タグ例（Health）

- 外因: `RATE_LIMIT / SRC_DOWN / NET_BLOCK / DNS_FAIL / AUTH_FAIL`
- 内因: `INTERNAL_ERR / WRITE_ERR / PARSE_ERR / TIMEOUT`

## 付録 B: 既定 SLA の目安（初期値）

- 板（orderbook mid）：**≤200ms**（95%tile）
- trades（秒足換算）：**≤500ms**
- 心理/クロス系列：**≤2s**

## 付録 C: 評価ウィンドウ（初期）

- `t+5s / t+60s / t+300s`（設定で増減可）

---

📌【追記案】情報収集ドメイン設計仕様書 — GPT/検証対応のための設計補遺
付録：将来の GPT 解析・売買検証に対応するための設計補遺

（2025-11-15 更新）

本システムにおける Collector / Health / Audit / Strategy の各モジュールを、
将来の「検証・再現性のある学習補助・GPT 分析」に安全に接続できるよう、
以下の 3 点を“設計上の固定方針”として追加する。

1. \*\*status.json の正準スキーマを固定する（後続すべての土台）

Collector が出力する status.json は、本システム全体で共有される
「唯一のリアルタイム状態表現」であり、今後変更しない“契約”として以下のスキーマを採用する。

status.json 仕様（正準）

leader:
id: string # リーダー識別子（hostname / pid 等）
since: iso8601 # リーダー就任時刻
stale_sec: number # 交代判定用の staleness

storage:
data_root: string
logs_root: string
note: string # 補足（NAS 切替等）

sync:
ts_now: iso8601
ts_status_written: iso8601
latency_ms: number # collector→fs 書き込み遅延の目安

items: # exchange-topic ごとの状態

- exchange: string
  topic: string # ticker / orderbook / trades
  last_ok: iso8601 # 最後に正常応答を得た時刻
  age_sec: number # 今の staleness
  cause: string|null # stale / io_err / 429 等の原因
  retries: number # 連続リトライ数
  source: string # ws / rest / fs など
  notes: string|null # 補足情報

目的

Health / Ops-Audit / GPT ケース生成のすべてが、このスキーマを前提にする。

後からフィールドが揺れると影響が大きいため、この段階で固定しておく。

2. Decision（売買決定）を「1 決定 = 決定＋理由＋結果」の 1 レコードで必ず保持する

将来の検証・再現性確保・GPT 解析のため、
売買シグナル／オーダー判断は必ず「決定ユニット」として以下の項目を持つ。

decision_id: string
ts_decision: iso8601

symbol: string
venue: string # bitflyer / binance 等

side: string # buy / sell
qty: number
price_plan: string # limit(X) / market / postonly など

strategy_name: string

params_snapshot_id: string # その時点のパラメータセットの ID/ハッシュ

reason_code: string # ma_cross_up / volatility_spike など
reason_note: string # 簡潔な判断説明（自然言語）

market_snapshot: # Collector 情報の要約
volatility: number
spread: number
depth_factors: { ... } # 必要なら

result:
exit_ts: iso8601
exit_reason: string # takeprofit / stoploss / timeout
pnl: number
slippage_ticks: number|null
mfe: number|null
mae: number|null

review_status: string # pending / in_progress / done
reviewed_at: iso8601|null
review_notes_ref: string|null # Markdown メモのパス

目的

「なぜそのタイミングでそのシグナルが出たか」を後で解釈できる。

「その売買指示は正しかったか」を GPT と検証できる。

パラメータ調整のための“事後分析の素材”が一箇所に揃う。

3. GPT 解析用の“検証ケース”は Collector 本体では生成しない

GPT や機械学習のための解析単位（期間ウインドウ／事故ケース／決定ユニット etc）は、
Collector 自体が生成せず、別レイヤー（tools/ または research/）で派生生成するものとする。

基本方針
Collector：raw ＋ status.json ＋ dev_audit を出すだけ
↓
tools/gpt_case_builder：検証ケース（jsonl / md）を生成
↓
GPT / 検証 UI：解析・要約・ラベリング・調整案作成

理由

Collector を肥大化させず責務を明確に分離するため。

GPT 用のケース構造は将来進化するため、Collector に埋め込むべきではない。

運用監査（Ops-Audit）とも干渉しない。

付記：将来拡張の方針（抜粋）

endpoints_def / exchanges_def には将来のラベル（prio / SLA / importance）を入れる余地を残す。

RateController は「collector 内唯一のレート制御点」とする。

運用監査（Ops-Audit）は Dev-Audit と分離し、専用スキーマ・専用 Writer を後で実装する。

GPT 用の解析はリアルタイムではなく バッチ or ユニット ID 単位 とする。

✔ この追記を入れておけば、後戻りはほぼ発生しない

この 3 点だけ仕様書に追記しておけば：

Health

Collector

Ops-Audit

Strategy

GPT 解析

パラメータチューニング

Decision 検証

どれを後で作っても 構造を壊す必要がなくなるため、
今の段階で決める「最低限の設計固定」になっています。
