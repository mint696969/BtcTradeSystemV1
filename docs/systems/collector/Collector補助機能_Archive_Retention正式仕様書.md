# Collector補助機能 仕様書ドラフト

Last updated: 2026-03-29
Owner: GTP Partner New
Status: Draft / docs配置用

---

## 0. 文書の位置づけ
本書は Collector vNext に付随する補助機能としての Archive / Retention サブシステムの正式仕様ドラフトである。

対象は以下。

- Hot -> Cold Archive Copy
- Verified Retention / GC
- Archive Worker の起動・停止
- Archive state / audit / UI diagnostics

本機能は Collector 本体の収集責務とは分離された周辺運用サブシステムであり、Collector の安全なリアルタイム収集を妨げずに長期保管を成立させることを目的とする。

---

## 1. 背景
Collector はリアルタイム収集性能を優先し、Hot ストレージへ append-only で書き込む。
一方、長期保管・分析・AI 学習・再処理の観点では、Hot ストレージを正本の長期置き場とし続けるのは望ましくない。

そのため、保存を二層化する。

- Hot: `D:\btc_ts_hot`
- Cold: `E:\btc_ts`

Collector は Hot のみへ書き込み、補助機能が別プロセスで Cold へ複製し、十分古い Hot データだけを保守的に整理する。

---

## 2. 目的
### 2.1 Collector 非干渉
Collector の収集・書き込み性能を最優先し、Archive / Retention は別プロセスで動かす。

### 2.2 欠損防止
Hot 側からの削除は、Cold 側に安全に存在確認できたものだけを対象とする。

### 2.3 連続性維持
過去から最新までの連続した履歴を壊さない。

### 2.4 専用機移植性
Collector 専用機へそのまま移植しやすい構造と起動形を持つ。

### 2.5 可観測性
Archive / Retention の動作は state / audit / UI で外から観測できるようにする。

---

## 3. 必須原則
### 3.1 Collector は書くだけ
Collector 本体は Hot 側へ append-only で書くことだけを責務とする。

### 3.2 Watchdog に混ぜない
Watchdog は daemon の起動・監視・restart のみに責務を限定し、Archive / Retention は持たない。

### 3.3 copy と delete を分離
削除は copy の成功確認後にのみ実行可能とし、実装責務も分離する。

### 3.4 active file を触らない
Collector が書き込み中の可能性がある最新 file や最新日付領域は copy / delete 対象にしない。

### 3.5 小分け低優先度
一斉コピー・一斉削除を避け、少量ずつ、低優先度で進める。

---

## 4. 責務分離
### 4.1 Collector
責務:
- raw / canonical / state / logs の書き込み
- Hot 側 append-only 記録

非責務:
- Cold への archive copy
- Hot 側 retention delete
- archive state / audit の更新

### 4.2 Unified Watchdog
責務:
- unified daemon の起動
- 生存監視
- graceful restart / stop 要求処理

非責務:
- archive copy
- archive GC

### 4.3 Archive Worker
責務:
- Hot -> Cold copy
- verified GC
- archive state 出力
- archive audit 出力
- graceful stop request への応答

### 4.4 Stack Launcher
責務:
- unified watchdog と archive worker の同時起動
- stack 停止時の archive worker graceful stop request 出力

---

## 5. 配置
Collector に近いが Collector 本体とは混ぜない構造を採用する。

```text
btcts_next/src/btcts/collector_vnext/archive/
    __init__.py
    config.py
    planner.py
    gc_job.py
    state.py
    audit.py
    worker.py
```

launcher は `tools/` に置く。

```text
tools/run_collector_vnext_archive_worker.ps1
tools/run_collector_vnext_stack.ps1
```

---

## 6. 起動・停止モデル
### 6.1 起動
Collector スタック起動時に、以下を別プロセスで同時起動する。

- unified watchdog
- archive worker

概念図:

```text
collector_stack_launcher
 ├─ unified_watchdog
 │   └─ unified_daemon
 └─ archive_worker
```

### 6.2 停止
stack 停止時は archive worker に stop request を出し、現在の 1 work unit を終えてから停止する。
即 kill を基本動作にしない。

### 6.3 UI restart との関係
Collector タブの restart は daemon / watchdog 系の運転制御であり、archive worker の再起動までは責務に含めない。

---

## 7. 対象ストレージ
### 7.1 Hot
- `D:\btc_ts_hot`
- Collector のリアルタイム書き込み先
- 低遅延・高頻度書き込みを優先

### 7.2 Cold
- `E:\btc_ts`
- 長期保管の正本
- AI 学習・再解析・研究・証跡確認の基盤

---

## 8. 対象 prefix
初期対象は少なくとも以下。

- `data/market_data`
- `data/collector_raw`
- `state/collector_vnext`
- `logs/collector_vnext`

ただし GC は初期段階では `data/*` のみを対象とし、state/logs の削除は行わない。

---

## 9. Copy 仕様
### 9.1 copy-only
copy phase は Hot -> Cold の複製のみを行い、削除はしない。

### 9.2 active file 非対象
以下は copy 対象から除外または後回しとする。

- 当日 date ディレクトリ
- 安定化待ち file
- 直近更新 file

### 9.3 基本単位
`data/*` 系は `date=YYYY-MM-DD` 配下の file 単位で評価する。
Cold 側未存在でも、date dir 丸ごと copy ではなく stable file 単位でコピーする。

### 9.4 制御
少なくとも以下を持つ。

- `scan_interval_sec`
- `stable_age_sec`
- `copy_min_age_days`
- `max_files_per_cycle`
- `max_bytes_per_cycle`

---

## 10. Verified GC 仕様
### 10.1 初期条件
GC は保守的に開始する。

- 当日: 対象外
- 前日: 対象外
- 一昨日以前: 候補

### 10.2 delete 条件
削除対象は以下を満たす file のみ。

1. Hot 側 file が stable である
2. Cold 側に同パス file が存在する
3. `cold_size >= hot_size`
4. retention age を超えている

### 10.3 dry-run
GC は `gc_enabled=true` かつ `gc_dry_run=true` で候補抽出のみを行える。
この場合、audit/state 上は候補件数を可視化するが、Hot 側実体は削除しない。

### 10.4 実 delete
`gc_enabled=true` かつ `gc_dry_run=false` の時のみ Hot 側 file を削除する。
運用上は少量件数で短時間確認し、その後安全側設定へ戻すことを推奨する。

### 10.5 一括削除禁止
`max_delete_files_per_cycle` を持ち、一度に大量削除しない。

---

## 11. state 仕様
### 11.1 copy state
- `archive_copy_state.json`

代表項目:
- `mode`
- `started_at`
- `last_scan_ts`
- `last_plan_count`
- `last_copied_files`
- `last_copied_bytes`
- `last_error`

### 11.2 gc state
- `archive_gc_state.json`

代表項目:
- `mode`
- `started_at`
- `enabled`
- `dry_run`
- `last_scan_ts`
- `last_plan_count`
- `last_deleted_files`
- `last_deleted_bytes`
- `last_error`
- `plan_sample`

### 11.3 停止時 state
archive worker 停止時は copy / gc の両 state を整合した mode に更新する。

- `STOPPING`
- `STOPPED`
- `FAILED`

---

## 12. audit 仕様
- `logs/collector_vnext/archive_audit.jsonl`

代表 event:
- `archive.worker.start`
- `archive.worker.stop`
- `archive.copy.begin`
- `archive.copy.completed`
- `archive.copy.error`
- `archive.gc.begin`
- `archive.gc.completed`
- `archive.gc.error`

UI の recent copy / recent delete は `begin` イベントの `plan_sample` を基に表示する。

---

## 13. UI 仕様
Collector タブ内に `Archive / Retention Diagnostics` を持つ。

表示要素:
- Copy Mode
- GC Mode
- GC Enabled
- GC Dry Run
- Remaining Hot Files
- archive_started_at
- copy_last_scan_ts
- gc_last_scan_ts
- Latest Copy 5
- Latest Delete 5
- Hot D drive remaining data files (latest 50)

Health タブではなく Collector タブに置く理由は、本機能が取得データの健全性ではなく、Collector 運用補助・保管整理機能だからである。

---

## 14. 安全運用ルール
### 14.1 実 delete テスト後の復帰
実 delete テスト後は launcher を安全側に戻す。

推奨安全設定:
- `BTCTS_ARCHIVE_GC_ENABLED=true`
- `BTCTS_ARCHIVE_GC_DRY_RUN=true`
- `BTCTS_ARCHIVE_MAX_DELETE_FILES_PER_CYCLE=32`（運用方針により調整可）

### 14.2 実 delete テスト時
短時間だけ以下へ切り替える。

- `BTCTS_ARCHIVE_GC_DRY_RUN=false`
- `BTCTS_ARCHIVE_MAX_DELETE_FILES_PER_CYCLE=5`

確認後は安全側へ戻す。

### 14.3 収集優先
Collector の収集に異常兆候が出た場合、Archive / Retention を優先停止できること。

---

## 15. 2026-03-29 時点の到達点
実装到達点:
- archive worker 常駐
- Hot -> Cold copy
- GC dry-run
- 実 delete テスト
- 安全側設定への復帰
- Collector タブ diagnostics 表示
- watchdog とは責務分離済み

---

## 16. 今後の拡張候補
- hash / manifest による stronger verify
- state/logs の retention policy
- archive worker lock / single-instance guard
- UI 文言 polish（dry-run 時の `deleted_files` 表現改善）
- prefix / exchange ごとの fair scheduling 強化
- GPT 用 slice / export 補助機能

---

## 17. 一文まとめ
Collector は Hot 側へ書くだけに徹し、Archive Worker が別プロセスで Hot -> Cold を安全複製し、Verified GC が十分古い Hot データだけを保守的に整理する。Watchdog には archive 責務を混ぜず、Collector タブ Diagnostics で運用確認可能とする。