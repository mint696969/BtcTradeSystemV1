# Phase1 CC 最終テスト（自動終了・短時間検査）

## 目的
- Collector の scheduler 周り（status.json / rate_state.json / audit.jsonl）を
  **安全に短時間で再現・検証**する。
- Ctrl+C に依存しない（結果がブレない）テストを実行する。

---

## 1) test_collector_entry.py とは
- Collector Scheduler の疑似テスト用エントリ
- ダミー endpoint を 1つだけ登録し、指定モードで runner を動かす
- **BTC_TS_TEST_RUN_SEC により必ず自動終了できる（hangでも止められる）**

### 主な用途
- watchdog / supervisor の “hang 検知” や “status 更新” の挙動確認
- audit.jsonl が期待通り出るか（イベント名のブレ検知）
- rate_state.json の更新頻度・内容が壊れていないか
- 「Ctrl+C で止めると結果がブレる」問題の回避

### 実行モード（環境変数）
- `BTC_TS_TEST_MODE_FORCE` : ok | skip | error | hang | ok_then_hang | ok_then_error
  - watchdog が mode を注入しても FORCE が最優先
- `BTC_TS_TEST_HANG_SEC` : hang の sleep 秒数（例: 9999）
- `BTC_TS_TEST_RUN_SEC` : **プロセスを強制終了する秒数（最重要）**
- `BTC_TS_TEST_EXIT_CODE` : 自動終了時のexit code（既定0）
- tick/status/rate_state 間隔:
  - `BTC_TS_TEST_TICK_SEC`
  - `BTC_TS_TEST_STATUS_EVERY_SEC`
  - `BTC_TS_TEST_RATE_STATE_EVERY_SEC`
  - `BTC_TS_TEST_STARTUP_GRACE_SEC`
  - `BTC_TS_TEST_NO_DATA_CHECK_EVERY_SEC`

---

## 2) test_phase1_cc_checks.ps1 とは
- 直近 N秒の実行で、
  - audit.jsonl の増分行数
  - supervisor jsonl の増分行数
  - rate_state/status の書き込み回数
  - 429/hold の発生
  - status.json の更新（mtime）
  を集計して **短時間で“危険兆候”を数値確認するスクリプト**

### 主な用途
- 「動いてる風」ではなく “書き込み/監査が死んでない” を確認
- 多重起動の疑いがある時のログ診断（pid/starts の増え方確認）
- Phase1完了前の最終スモーク（30〜60秒で終わる）

---

## 3) 最終テスト（これだけやればOK）
### 前提
- logs ディレクトリが存在すること
- 旧 test プロセスが残っていないこと（多重起動回避）

### コマンド（PowerShell）
1) hang 自動終了（30s）
2) ok_then_hang 自動終了（15s）
3) cc_checks で監査・更新頻度を確認（10s）
4) stderr log を tail

（※このセットで「止まらない」「Ctrl+C依存」の問題を排除できる）

---

## 4) 注意点（事故防止）
- `BTC_TS_TEST_RUN_SEC` 未指定で `hang` を動かすと **止まらない**
- watchdog/supervisor を別途動かしている場合、ログが混ざるため
  **テスト前に旧プロセス掃除を必ず行う**
- “テストの正準” は上記の最終テストコマンド。改変は禁止（必要なら追記で）
