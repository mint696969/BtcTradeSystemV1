# vNext Unified Watchdog 正式仕様書ドラフト

Last updated: 2026-03-27
Owner: GTP Partner New
Status: Draft / ready for operator review

---

## 0. 文書の位置づけ
本書は、旧 `Supervisor（Watchdog）正式仕様書` の思想を継承しつつ、
Collector vNext Unified runtime 向けに再定義した Watchdog 正式仕様ドラフトである。

本書が継承するのは主に以下の思想である。

- Watchdog は Collector 本体の外側に置く
- Collector と Watchdog の責務境界を明確に分ける
- 監視判断は内部メモリではなく、外から見える state を根拠にする
- 多重起動防止を前提にする
- supervisor 視点の audit を残す
- 安全側判定を優先する
- 「止めないために、止める」を許容する

一方で、旧仕様の具体実装はそのまま引き継がない。
とくに以下は vNext 向けに upgrade 対象とする。

- `status.json` 単独依存
- 即 kill 中心の停止モデル
- stale lock の広い掃除
- 文字列 message 解析による no_data 判定
- 単一 collector 前提の粗い監視モデル

---

## 1. 対象範囲
対象は Unified Collector runtime である。

vNext Unified runtime は少なくとも以下の要素を含む。

- REST lane
- WS Board lane
- WS Executions lane
- unified daemon
- unified scheduler / rate state / origin state / checkpoint
- supervisor request / supervisor status / daemon stop request

本書は、この Unified runtime に対する supervisor としての Watchdog を定義する。

---

## 2. 設計目的
Watchdog の目的は、Collector 本体に自己回復責務を持たせすぎず、
外部 supervisor として監視・停止・再起動・単一起動保証を担うことである。

主要目的は以下。

1. Unified daemon の単一起動保証
2. manual restart request の安全な実行
3. graceful stop を優先した restart orchestration
4. supervisor 視点の status / audit 可視化
5. stale request や起動競合による誤動作の抑制

---

## 3. 責務分離
### 3.1 Watchdog の責務
Watchdog は以下を担う。

- Unified daemon の起動
- Unified daemon の生存監視
- restart request の受理と実行
- graceful stop request の daemon への伝達
- timeout 時のみ force kill fallback
- backoff / max_failures に基づく supervisor 側の防御
- supervisor lock による単一起動保証
- supervisor status 出力
- supervisor audit 出力
- stale request の保守的無視

### 3.2 Collector daemon の責務
Unified daemon は以下を担う。

- REST / WS 収集の実行
- structured state の更新
- daemon status / daemon health の更新
- daemon stop request に対する graceful stop 応答
- lane 側 stop_event 伝播

### 3.3 UI の責務
UI は以下のみを担う。

- restart request を request file として書く
- supervisor status / request / daemon stop request を表示する
- pending request 中の再押下防止
- supervisor 非 RUNNING 時の warning 表示

UI は kill / start / restart 実行主体にならない。

---

## 4. 起動モデル
### 4.1 正規起動主体
Unified Collector の正規起動主体は Watchdog とする。

運用上の正規コマンドは以下。

```powershell
powershell -ExecutionPolicy Bypass -File C:\BtcTradeSystem\tools\run_collector_vnext_unified_watchdog.ps1
```

### 4.2 非推奨起動
以下は常用しない。

- `unified_daemon` の単独常用起動
- UI からの直接プロセス制御
- watchdog と standalone daemon の混在運用

理由は ownership 競合と lock 競合を避けるためである。

---

## 5. 多重起動防止
### 5.1 supervisor lock
Watchdog は `unified_supervisor.lock.json` を用いて単一起動を保証する。

### 5.2 daemon lock
Unified daemon は runtime family=`unified` の daemon lock を用いて単一起動を保証する。

### 5.3 stale lock の扱い
stale lock は PID 非生存が確認できた場合のみ最小限に掃除する。
Watchdog が広く lock を掃除する設計は採用しない。

---

## 6. state / request / status 契約
### 6.1 supervisor request
`unified_supervisor_request.json`

用途:
- UI など外部から watchdog に restart request を伝える

代表項目:
- `request_id`
- `action` (`restart`)
- `requested_at`
- `requested_by`
- `reason`

### 6.2 supervisor status
`unified_supervisor_status.json`

用途:
- watchdog の現在状態と直近 action を外部可視化する

代表項目:
- `mode`
- `last_action`
- `last_requested_at`
- `last_completed_at`
- `last_error`
- `daemon_pid`
- `request_ack_ts`
- `acked_request_id`
- `started_at`
- `last_seen_ts`
- `uptime_sec`
- `supervisor_pid`
- `runtime_family`
- `host_name`

### 6.3 daemon stop request
`unified_daemon_stop_request.json`

用途:
- watchdog から daemon へ graceful stop を要求する

代表項目:
- `action` (`stop`)
- `requested_at`
- `requested_by`
- `reason`
- `restart_requested`
- `supervisor_request`

### 6.4 daemon state
Unified daemon は少なくとも以下を出す。

- `unified_daemon_status.json`
- `unified_daemon_health.json`
- `unified_status.json`
- `unified_health.json`
- `unified_checkpoint.json`
- `unified_origin_status.json`
- `unified_executions_status.json`

UI と Watchdog は、内部メモリではなく、これらの state を判断材料にする。

---

## 7. restart 実行フロー
再起動は以下の順で行う。

1. UI が `unified_supervisor_request.json` を書く
2. Watchdog が request を検知する
3. Watchdog が request を ack し、`supervisor_status` を更新する
4. Watchdog が `unified_daemon_stop_request.json` を書く
5. daemon が loop 境界で stop request を観測する
6. daemon が STOPPING -> STOPPED を state に書いて終了する
7. Watchdog が backoff を挟む
8. Watchdog が新しい daemon を起動する
9. Watchdog が `last_completed_at` を含む RUNNING 状態へ戻る
10. request / stop request は最終的に残留させない

---

## 8. 停止モデル
### 8.1 基本方針
停止は `graceful-first` とする。

### 8.2 force kill の条件
以下のときのみ fallback として force kill を許容する。

- graceful stop timeout 超過
- daemon が停止に応答しない

### 8.3 採用しない方針
以下は中核にしない。

- `kill -> backoff -> restart` を標準系にすること
- 停止より先に kill を打つこと
- 書き込み中イベントを考慮しない再起動

---

## 9. stale request 対策
### 9.1 基本方針
古すぎる restart request は誤爆防止のため無視可能とする。

### 9.2 判定
request の `requested_at` から age を計算し、
`BTCTS_UNIFIED_REQUEST_MAX_AGE_SEC` を超える場合は stale とみなす。

### 9.3 動作
stale request は

- audit に `watchdog.restart.request.stale_ignored` を残す
- request file を消す
- supervisor status に `last_error` と `request_ack_ts` を残す
- restart は実行しない

---

## 10. supervisor mode 定義
代表 mode は以下。

- `STARTING`
- `RUNNING`
- `RESTART_REQUESTED`
- `GRACEFUL_STOPPING`
- `BACKOFF`
- `FAILED`
- `STOPPED`

これらは UI から可視化される前提とする。

---

## 11. audit
### 11.1 目的
Collector 側 audit と別に、supervisor 視点の出来事を追跡可能にする。

### 11.2 出力先
`unified_supervisor_audit.jsonl`

### 11.3 代表イベント
- `watchdog.start`
- `watchdog.start.daemon`
- `watchdog.observe.daemon_exited`
- `watchdog.restart.requested`
- `watchdog.restart.graceful_begin`
- `watchdog.restart.graceful_timeout`
- `watchdog.restart.force_kill`
- `watchdog.restart.completed`
- `watchdog.restart.request.stale_ignored`
- `watchdog.stop.too_many_fails`
- `watchdog.exception`
- `watchdog.exit`

---

## 12. UI 要件
UI は少なくとも以下を満たす。

1. restart button を持つ
2. button は request file を書くだけ
3. pending request 中は button を disable する
4. supervisor 非 RUNNING 時は warning を出す
5. request_id / ack / completed を可視化する
6. `started_at / last_seen_ts / uptime_sec` を可視化する
7. Collector タブ上段 summary は unified 正本に追従する

---

## 13. 実装済み到達点（2026-03-27 時点）
現時点で以下は実動確認済みである。

- watchdog を正規起動主体として起動できる
- UI から restart request を発行できる
- watchdog が request を受理できる
- daemon が restart される
- `daemon_pid` の切り替わりを確認済み
- `last_completed_at` / `acked_request_id` を確認済み
- pending request / daemon stop request が最終的に残留しない
- Collector タブ上段 summary の unified 追従化を確認済み

したがって、
「watchdog と UI 上から安全に再起動できる状態」
という今回の主ゴールは達成済みと判定する。

---

## 14. 未完了だが blocking ではない項目
以下は optional hardening / polish とする。

- disk guard
- restart policy の更なる厳密化
- API/WS イベント完全無欠損の深掘り証明
- UI 文言 polish
- health / daemon_health 責務の更なる整理
- origin continuity summary の追加改善

---

## 15. 運用上の注意
- standalone unified daemon と watchdog 起動を混在させない
- UI は restart 実行主体にならない
- stale request は残留運用しない
- supervisor status を見てから操作判断する
- 問題発生時は supervisor audit を優先確認する

---

## 16. 一文まとめ
vNext Unified Watchdog は、Collector 本体の外に置かれる supervisor であり、
UI から渡された restart request を安全側に処理し、graceful-first で Unified daemon を再起動し、
その過程を state と audit で外部可視化する。