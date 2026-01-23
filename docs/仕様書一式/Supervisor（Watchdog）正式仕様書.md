Supervisor（Watchdog）正式仕様書（Collector）

（BtcTradeSystem NEXT / Phase1 確定版・統合版）

0. この文書の目的

本書は、Collector を 24/7で安定稼働させるための外部監視プロセス Supervisor（= Watchdog） の仕様を、他のGPT・他メンバーが読んでも運用と改修がブレない形で固定する。

1. 役割と責務境界（最重要）
1.1 Watchdog の責務

Collector の起動（ダミー/実）

環境変数注入（子プロセスへ明示的に渡す）

進捗監視（status.json の ts_unix/ts）

ハング検知（停滞）

異常時の kill → backoff → 再起動

多重起動防止（watchdog.lock）

ディスク安全弁（logs ドライブ残量）

監査ログ（supervisor_collector.log / .jsonl）

Phase1 テスト再現手順の固定（collector_watchdog_test.ps1）

1.2 Collector の責務

データ収集ロジック（API/取引所/エンドポイント）

status.json の生成/更新（進捗の唯一の根拠）

audit.jsonl 等の生成（Collector視点の監査）

2. ファイル配置（正準）
2.1 実体

Watchdog本体
./scripts/watchdog_collector.ps1

Phase1 検証ワンショット（運用ではなくテスト用）
./scripts/collector_watchdog_test.ps1

ダミーCollectorエントリ（Phase1）
./tmp/test_collector_entry.py

2.2 監視対象（Collector進捗）

"<BTC_TS_DATA_DIR>\collector\status.json"

3. 起動と停止（正準）
3.1 必須環境変数（正準）

BTC_TS_CONFIG_DIR = <config root>

BTC_TS_DATA_DIR = <data root>

BTC_TS_LOGS_DIR = <logs root>

PYTHONPATH = <repo>\btcts_next\src

3.2 起動コマンド

実運用（将来のPhase2で実Collector統合後に使用）
pwsh -File .\scripts\watchdog_collector.ps1

Phase1（ダミーCollectorで監視ロジック検証）
pwsh -File .\scripts\watchdog_collector.ps1 -UseDummyCollector

3.3 停止方法（Phase1 正準）

Ctrl + C（常駐プロセスであるためこれが正しい）

4. 多重起動防止（Lock / PID）
4.1 watchdog.lock（OS排他）

パス："<BTC_TS_LOGS_DIR>\watchdog.lock"

方式：FileShare.None による OSレベル排他

動作：ロック取得に失敗した場合は 「既に稼働中」 と判断して即終了

例：lock busy: E:\btc_ts\logs\watchdog.lock

4.2 watchdog.pid（参照用）

パス："<BTC_TS_LOGS_DIR>\watchdog.pid"

内容（最低限）

watchdog の PID

起動UTC

python実体パス

運用注意：watchdog.lock を手動削除する運用はしない。
「起動し直したい」のに lock busy になる場合は、まず「Watchdogが本当に生きているか」を確認し、死んでいるのに残っているなら原因を確定してから処置する（後述）。

5. 設定ファイル（watchdog.yaml）
5.1 既定の探索

ConfigPath が未指定なら："<BTC_TS_CONFIG_DIR>\watchdog.yaml"

5.2 Phase1でサポートするキー（トップレベル scalar + inline list）

schema_rev (int)

interval_sec (int) 既定 5

hang_timeout_sec (int) 既定 120

max_failures (int) 既定 5

backoff_sec (list) 既定 [10,30,60,120,300]

no_data_fail_limit (int) 既定 5

log_tail_lines (int) 既定 200（Phase1では保持のみ）

free_gb_warn (number) 既定 20

free_gb_stop (number) 既定 10

6. Collector 起動仕様
6.1 起動前チェック（Preflight）

Python で import btcts を実行し import 可否を確認

成功：preflight.btcts.ok

失敗：preflight.btcts.ng をログし、Collector起動せず停止

6.2 起動方式

Phase1（ダミー）：.\tmp\test_collector_entry.py

本番（実Collector）：btcts.collector.main を runpy.run_module で起動

6.3 子プロセスへ渡す環境（明示固定）

Watchdogは、子プロセスへ以下を 必ず明示注入する（手動起動との差を消すため）。

PYTHONPATH

BTC_TS_CONFIG_DIR

BTC_TS_DATA_DIR

BTC_TS_LOGS_DIR

6.4 stdout/stderr の採取

<BTC_TS_LOGS_DIR>\collector_stdout.log

<BTC_TS_LOGS_DIR>\collector_stderr.log

7. 監視ロジック（進捗・ハング検知）
7.1 進捗判定キー（正準）

status.json の ts_unix を優先

無ければ ts

どちらも無ければ「進捗判定不可」として ハング判定は行わない（安全側）

7.2 age_sec の定義

age_sec = now_utc - DateTime.UnixEpoch(ts_unix/ts)

7.3 ハング判定

age_sec >= hang_timeout_sec でハング扱い

7.4 ハング時の挙動

collector.hang をログ（age_sec, hang_sec, last_ok, fails）

Collector を kill

fails を +1

backoff 待機

再起動

8. 再起動制御（Backoff / 失敗上限）
8.1 backoff の決定

fails に応じて backoff_sec テーブルから選択
例：fails=1→10, 2→30, 3→60, 4→120, 5→300

8.2 停止条件（上限）

fails >= max_failures で Watchdog 自身が停止

ログ：watchdog.stop.too_many_fails

8.3 fails.reset（重要）

age_sec < hang_timeout_sec を観測した瞬間、fails を 0 に戻す

ログ：fails.reset prev=<n>

目的：一時的な失敗が累積して勝手に停止する事故を防ぐ

9. no_data 検知（補助）

status.json の message に以下が含まれる場合にカウント

no_data

startup grace

collector.no_data.detected をログ

count >= no_data_fail_limit で停止（Collector kill → Watchdog停止）

ログ：watchdog.stop.no_data_limit

10. ディスク安全弁（logsドライブ）

対象：BTC_TS_LOGS_DIR が属するドライブ残量

free_gb_warn 未満：guard.disk.warn

free_gb_stop 未満：Collector kill → Watchdog停止（guard.disk.stop）

11. ログ仕様（Supervisor視点）
11.1 出力

テキスト：<logs>\supervisor_collector.log

JSONL：<logs>\supervisor_collector.jsonl

11.2 代表イベント（固定）

watchdog.start

preflight.btcts.ok / preflight.btcts.ng

collector.start

collector.start.dummy

collector.start.real

collector.exited

collector.hang

collector.kill

fails.reset

backoff.sleep

watchdog.stop.too_many_fails

watchdog.stop.no_data_limit

guard.disk.warn / guard.disk.stop

watchdog.exit

12. stale lock（status.json.lock）の扱い（運用ルール固定）
12.1 対象

<BTC_TS_DATA_DIR>\collector\status.json.lock

12.2 Watchdog起動時の処置（安全条件付き）

起動時に 1回だけ stale 判定を行う

status.json から ts_unix/ts を取得できる場合のみ age を計算

age_sec >= hang_timeout_sec のときのみ lock を削除してよい

ログ：lock.stale.removed

status が読めない／tsが無い場合は削除しない（安全側）

ログ：lock.stale.check.skip

12.3 禁止事項

稼働中の lock を手動削除することは禁止
（多重起動、誤判定、ファイル破損の原因）

13. Phase1 テスト手順（監視ロジック最終確認）
13.1 目的

実Collector（API/取引所/endpoint）が無い現時点でも、Watchdog の監視・自己修復ループが正しいことを証明する。

13.2 正準コマンド（推奨）

pwsh -File .\scripts\collector_watchdog_test.ps1 -Dummy

13.3 期待ログ（合格判定）

collector.start.dummy ...

約120秒後に collector.hang ...

collector.kill ...

backoff.sleep sec=10（以降テーブル）

再度 collector.start.dummy ...

途中で fails.reset prev=1 が出る

13.4 重要：停止方法

Watchdog は常駐する。Ctrl + C で止めるのが正しい。

14. lock busy が出る件（運用として仕様に明記）
14.1 意味

lock busy: <...>\watchdog.lock は 「Watchdogが既に稼働中」 を意味する。

これは異常ではなく 多重起動防止が効いている正常動作。

14.2 取るべき行動（順序固定）

既に起動しているPowerShell（Watchdog）を探す（コンソールが残っていないか確認）

本当に止めたいなら、そのプロセスを Ctrl+C で終了

それでも起動できない場合のみ、watchdog.pid と実プロセスを突き合わせて原因を確定する
（「ファイルだけ消す」は原則禁止）

15. Phase1 完了定義（合格条件）

ダミーCollectorでハング検知できる

kill → backoff → 再起動が成立する

fails.reset が機能する

max_failures 未満なら自律運転が継続する

Ctrl+C で安全停止できる

supervisor_collector.log / jsonl が監査証跡として残る

16. Phase2 への前提（範囲外の明記）

実Collector（実API/endpoint/取引所）登録後に統合テストへ進む

サービス化（Windows Service / Task Scheduler）は Phase2 以降

Supervisor 自体の自己監視（Supervisor監視のSupervisor）は Phase2 以降

結論（設計思想の固定）

本Supervisorは 「Collectorを止めないために、止める」 を実装する。
Phase1 の目的は「監視ロジックの正当性」固定であり、それはダミー検証により満たされた。