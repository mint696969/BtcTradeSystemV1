
# BtcTradeSystem V1 — 情報収集ドメイン 設計仕様書（共有版）
最終更新: 2025-11-03 16:49:50 UTC+09:00
作成対象: Collector / Health（収集健全性）/ Ops-Audit（運用監査）
適用範囲: **メインPC単体運用**（将来の 収集専用PC+NAS 構成へ拡張可能なI/F で設計）

---

## 0. 目的と前提

- 本仕様は「チャットを跨いでも迷子にならない」ための **設計図** である。
- まずは **メインPC単体** で価値を証明（“光が見える”）。使い物にならない場合は撤退可能。
- 価値が確認できた場合に **収集専用PC + NAS** へスムーズに拡張できる **契約(I/F) 先行** 設計。
- 情報収集は「できて当たり前」。後続の **売買アシスト → 自動売買 → AI学習** を阻害しないデータ設計を最優先。
- **1ファイル1キャンバス**・**現物確認の上での変更**・**新規ファイルは2行ヘッダ（# path/# desc）** を厳守。

---

## 1. 成果物（完成像）

### 1.1 Collector（独立プロセス）
- 二重起動防止（Leader Lock, stale奪取あり）
- 取引所ごとのレート制御（優先度: 板/圧力 > 心理指標 > クロスアセット）
- 429/Retry-After 尊重、指数バックオフ、段階復帰、WS主系 + REST穴埋め
- 原子的ファイル出力（CSV置換 / JSONL追記+fsync）
- `status.json` を **最終形スキーマ** で継続更新（1–3s）
- Health からの `slow_down / restart / stop` 制御コマンドの受け口（本実装）

### 1.2 Health（ダッシュボード表示 + 設定タブ）
- 表示タブ: **取引所×エンドポイントの健全性カード**（OK/WARN/CRIT, 外因/内因タグ, ドリルダウン）
- 設定タブ: **表示順の並べ替え**・**閾値/自動アクション** を **プリセット＋Custom** で編集
- 自動アクション: 条件一致で Collector へ **slow_down / restart / stop** を発行（TTL/クールダウン設定）

### 1.3 Ops-Audit（運用監査）
- 初期出力の優先順位: **④データ品質(DQ) → ⑤リソース/コスト → ②インシデント時系列**
- 変更ジャーナル/日次オペレポは後付けで自動生成可能

### 1.4 可視化（後続：売買アシスト）—*収集仕様に影響する要件*のみ明記
- **S/H デュアル・チャネル**: System(S) と Human(H) を分離記録。学習は S-only + 良いHのみ採用。
- **信号・注文・約定** を同一タイムラインで重ね、 signal クリックで **評価ウィンドウ（t+5s/1m/5m）** 表示。

---

## 2. リポジトリ構成（平置き・機能集中・重複なし）

> 1機能=1フォルダに集約。サブフォルダは基本 `config/` のみ。ファイル名は唯一で迷わないこと。

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

## 3. 設定UIポリシー（プリセット＋Custom）

- すべての数値/組合せは **プルダウン（プリセット）→ Custom 選択で自由入力** の二段式。
- 単位は選択肢内に含め、誤入力を抑止（`5s`, `1/s`, `60/min` 等）。
- **Advancedトグル**で詳細パラメータを露出。
- **一時適用(Preview) → 保存** の二段適用。保存時に Ops-Audit へ **変更ジャーナル** を記録。

### 3.1 Collector 設定（設定タブ）
- 取引所ごとの: 有効化 / API Key（常時マスク・暗号化保存）/ 取得対象（板・trades…）/ 総レート上限 / endpoint優先度
- レート配分モード: `固定 / SLA / 適応(準備)`（最初は **SLA** が既定）
- 再試行・バックオフ: プリセット＋Custom

### 3.2 Health 設定（設定タブ）
- 表示順（取引所/endpoint の並べ替え）
- 閾値セット: `緩め / 標準 / 厳しめ / Custom`（age_sec, 連続違反, 復帰条件 などを束ねて管理）
- 自動アクション: `slow_down / restart / stop` 有効化、TTL/クールダウン設定

---

## 4. 主要I/F（契約・スキーマ）

### 4.1 status.json（**最終形を初手から採用**）
- 更新間隔: 1–3秒
- Health の第一ソース（mtimeフォールバックは緊急時のみ）

```json
{
  "updated_at": "ISO8601Z",
  "leader": { "host": "local", "since": "ISO8601Z", "active": true },
  "storage": { "primary": "up", "secondary": "idle", "secondary_path": null },
  "sync": { "pending": false, "last": { "at": null, "items": 0, "bytes": 0, "ok": true } },
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
- 受信手段: 初期は **ファイルキュー**（後日RPC差替え可）
- 重複防止: `cmd_id` と `ttl_s` で担保

```json
{ "cmd":"slow_down", "scope":"bitflyer.orderbook", "factor":0.5, "ttl_s":120, "cmd_id":"..." }
{ "cmd":"restart",   "scope":"bitflyer.trades",     "reason":"stale", "cmd_id":"..." }
{ "cmd":"stop",      "scope":"all",                 "reason":"manual", "cmd_id":"..." }
```

### 4.3 信号/注文/約定（S/H デュアル・チャネル）
> 可視化・評価・学習で共通利用。内部UTC、表示は Asia/Tokyo。

**signal**  
- `id, ts, channel(S/H), side, strength, rationale, features_digest(topK), model_info(id/version/params_hash), thresholds_name, market_context, rate_state, eval_targets=[5s,60s,300s]`

**order**  
- `id, signal_id, ts, side, qty, price_type, route(bitFlyer), status(pending/partial/canceled/filled)`

**fill**  
- `id, order_id, ts, avg_price, filled_qty, fee, slippage, pnl_mark(t+X)`

**eval（自動付与）**  
- `signal_id → { at_5s, at_60s, at_300s } = { direction(up/down/flat), pnl, mae, mfe, hit? }`

---

## 5. レート制御ポリシー（取引所ごと／Bを最終目標にCで運転）

- 優先度: **Retry-After最優先** ＞ 429既定待機 ＞ 内部安全則
- バケット: `exchange` を中核に `endpoint` 優先度で配分
- ディレート: 連続429で指数的に延伸、復帰は段階的（ヒステリシス）
- WS主系 + ドロップ時のみ REST 補完（短時間）
- **方式**: まず **C: SLA＋優先度キュー** を既定  
  並行して **B-1/B-2（情報利得メトリック計測→軽い自動調整）** を常時実行、データが溜まり次第 **Bへ昇格**。

---

## 6. Ops-Audit 初期出力（優先順位と目的）

1) **データ品質（DQ）** — 欠損率・連続欠損・REST補完成功率・SLA違反率（板は厳しめ）  
2) **リソース/コスト** — 取引所×endpoint の呼出回数・平均待機・降格滞在・429収束時間  
3) **インシデント時系列** — 重要イベント（SLA違反/WSドロップ/降格→復帰）と S/H の意思決定を一本化

> 変更ジャーナル / 日次オペレポは **後付け自動生成**。

---

## 7. UI/UX（数値入力・可視化・安全運用）

- **プルダウン＋Custom**（単位付き）/ **Advanced** / **Preview→保存** / **変更はOps-Auditに自動記録**
- **Health表示**は読み取り専用、**設定**で編集。カード順は設定に追従。
- **S/Hフィルタ**、signalツールチップに **根拠**、クリックで **評価ウィンドウ**。

---

## 8. 品質基準（受け入れ条件）

- **Collector**: 二重起動不可（stale時のみ奪取）、429/Retry-After追従、I/O破損0、status.jsonを1–3sで更新
- **Health**: 表示順と閾値が設定通り、自動アクションが Collector へ到達・効果
- **Ops-Audit**: DQ/Resource/Timeline が閲覧可能、主要イベントは相互に突合が取れる
- **可視化**: S/H分離表示・フィルタ、評価ウィンドウ、PNG/CSVエクスポート
- **学習準備**: S-only + 良いH抽出がフォーマット固定で出力可能

---

## 9. テスト計画（メインPC単体での検証）

- **多重起動**: 同時起動 → 2体目拒否／stale奪取の確認
- **429擬似**: 429+Retry-After → 待機→復帰（収束時間）
- **ネット断**: DNS/NET障害 → 待機モード降格→復帰
- **I/O障害**: 書込不可先 → WRITE_ERR → 停止 or 低頻度化
- **status.json**: age_sec・cause の健全推移、Health側の表示/閾値反映
- **Ops-Audit**: DQ/Resource/Timeline の指標が想定の範囲で出力

---

## 10. 将来拡張（収集専用PC+NAS への移行）

- `leader/storage/sync` ブロックへ **実値** を流し込む（NASロック / フェイルオーバ / 冪等同期）
- 制御ポートを **RPC/IPC** に差替（Health側は I/F不変）
- レート配分を **適応（B-3以降）** へ昇格（学習成果を接続）
- Ops-Audit に **日次/週次レポ** と **変更ジャーナル** を追加

---

## 11. 運用ルール（メモ）

- ダッシュボードは **薄い入口**（dashboard.py/settings.py は原則不改変）
- 変更提案は **1ファイル1キャンバス** + ①追加/②差替/③削除 フォーマット
- Secrets は常時マスク、コピー時はワンショット表示、保存は暗号化
- 重要な閾値変更や手動介入は **Ops-Audit** に必ず残る

---

## 付録A: 外因/内因タグ例（Health）
- 外因: `RATE_LIMIT / SRC_DOWN / NET_BLOCK / DNS_FAIL / AUTH_FAIL`
- 内因: `INTERNAL_ERR / WRITE_ERR / PARSE_ERR / TIMEOUT`

## 付録B: 既定SLAの目安（初期値）
- 板（orderbook mid）：**≤200ms**（95%tile）
- trades（秒足換算）：**≤500ms**
- 心理/クロス系列：**≤2s**

## 付録C: 評価ウィンドウ（初期）
- `t+5s / t+60s / t+300s`（設定で増減可）
