# path: ./docs/開発メモ/supervisor_spec.md

# desc: Collector を24/7運用するための Supervisor（Watchdog）仕様書ドラフト。再起動条件・安全弁・多重起動防止・ログ根拠を固定する。

# BtcTradeSystem NEXT — Supervisor（Watchdog）仕様書（ドラフト）

制定: 2026-01-22
対象: Windows / PowerShell 運用

## 0. 目的とスコープ

Supervisor は Collector を **24時間連続稼働**させるための「自己修復」機構である。

* 監視（生存確認）
* 異常時の再起動（自己修復）
* 運用事故の防止（安全弁：多重起動・再起動ループ・ディスク逼迫）

非スコープ（Phase1）

* 通知（Slack/メール等）
* 自動原因分析（ログ解析や推論）
* Collector の内部ロジック変更（Supervisorは外から守る）

## 1. 前提（正準）

### 1.1 Collector 起動正準

* 正準起動: `python -m btcts.collector.main`
* そのため Supervisor は以下を必須として扱う

  * `PYTHONPATH` に `./btcts_next/src` が含まれる
  * `BTC_TS_CONFIG_DIR / BTC_TS_DATA_DIR / BTC_TS_LOGS_DIR` が本番正準を指す

### 1.2 監視根拠（進捗の証拠）

監視は「プロセスが居る」ではなく **進捗がある**ことを見る。

* 最優先: `<DATA_DIR>/collector/status.json` の `ts_unix` が更新され続けること
* 補助: `<DATA_DIR>/collector/rate_state.json` の `ts` が更新され続けること
* 補助: `<LOGS_DIR>/audit.jsonl` が増加すること（存在する場合）

status.json の必須フィールド（最低限）

* `ts_unix` : float（UNIX秒）
* `ts_iso`  : str（UTC ISO / Z）
* `mode`    : str（例: RUNNING / ERROR / STOPPED）
* `items`   : list（常に list）

## 2. 異常判定

### 2.1 “止まった”（ハング）判定

* `status.ts_unix` が `hang_timeout_sec` 以上更新されない → ハング
* 推奨初期値: `hang_timeout_sec = 120`

補足:

* 一時的なAPI遅延・瞬断・抑制（CRIT hold）に耐えつつ、停止を早めに拾う。

### 2.2 “落ちた”判定

* Collector プロセスが存在しない
* もしくは pidfile があるが PID が不在（stale）

### 2.3 “no_data” 判定

* Collector が no_data を理由に例外終了する設計を維持する。
* Supervisor は no_data を **再起動対象**として扱う。
* no_data が `no_data_fail_limit` 回以上連続した場合は停止（恒久障害疑い）

  * 推奨初期値: `no_data_fail_limit = 5`

## 3. 再起動ポリシー

### 3.1 再起動の基本

* 異常を検知したら `Stop → Clean → Start` の順で再起動する。
* Stop は Windows 前提で確実性を最優先（段階的に強制）

### 3.2 バックオフ（再起動ループ対策）

* 連続失敗回数に応じて待機を増やす（上限あり）
* 推奨: `10s → 30s → 60s → 120s → 300s (cap=300s)`

### 3.3 連続失敗停止

* 連続失敗 `max_failures` 回で Supervisor 自身が停止する
* 推奨初期値: `max_failures = 5`

停止時はログに以下を残す

* 停止理由（hang/no_data/exit/guard）
* 直近の status.json（可能なら全文）
* 直近の audit.jsonl 末尾N行（存在する場合）

## 4. 多重起動防止（安全弁）

Supervisor 自体の多重起動防止

* `watchdog.lock` を取得できない場合は即終了

Collector の多重起動防止

* 既存の `btcts.collector.control` のロック＋pidfile方針を尊重する。
* Supervisor が外側でも PID を二重に起動しない（pidfile確認）。

## 5. ディスク逼迫停止（安全弁）

* `BTC_TS_LOGS_DIR` が存在するドライブの空き容量を監視
* 推奨初期値:

  * WARN: free < 20GB
  * STOP: free < 10GB

STOP では Collector を停止し Supervisor も停止する（書けない状態で動かさない）。

## 6. 設定（watchdog.yaml）

Supervisor は設定で運用値を固定する（コード直埋め禁止）。

例:

```yaml
schema_rev: 1
interval_sec: 5
hang_timeout_sec: 120
max_failures: 5
backoff_sec: [10, 30, 60, 120, 300]
no_data_fail_limit: 5
log_tail_lines: 200
free_gb_warn: 20
free_gb_stop: 10
paths:
  status_json: "<DATA_DIR>/collector/status.json"
  rate_state_json: "<DATA_DIR>/collector/rate_state.json"
  audit_jsonl: "<LOGS_DIR>/audit.jsonl"
  pidfile: "<LOGS_DIR>/collector.pid"
  supervisor_lock: "<LOGS_DIR>/watchdog.lock"
```

## 7. 成功条件（Phase 1）

* Collector が落ちる / ハングする / no_data になる状況を疑似テストで再現し、Supervisor が復旧できる
* 多重起動しない
* ディスク逼迫時に停止できる
* 監視根拠（status.ts_unix 更新）が運用で安定して観測できる
