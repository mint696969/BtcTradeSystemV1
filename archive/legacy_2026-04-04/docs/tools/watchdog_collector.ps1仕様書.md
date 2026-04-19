# path: ./archive/legacy_2026-04-04/docs/tools/watchdog_collector.ps1仕様書.md
# desc: Archived note, specification, report, or reference document.

watchdog_collector.ps1 仕様書（Phase1 / Supervisor）
1. 目的

watchdog_collector.ps1 は Collector を 24/7 運用する Supervisor。
以下を監視し、異常時に kill → backoff → 再起動を行う。

Collector プロセスの終了（Exit）

status.json の更新停滞（ハング検知：ts_unix / ts）

status.message 上の no_data 系の連続（保険）

ディスク空き容量の不足（安全弁）

多重起動防止（lock）

実行ログは テキスト（.log） と JSONL（.jsonl） を常時生成し、Health/検証ツールが参照できる形に固定する。

2. 正準パス

スクリプト本体

C:\BtcTradeSystem\scripts\watchdog_collector.ps1

Phase1 ダミー Collector（UseDummyCollector 時）

C:\BtcTradeSystem\tools\test_collector_entry.py

※実際にログ上は C:\BtcTradeSystem\scripts\..\tools\test_collector_entry.py として記録される（実体は同一）

3. 必須環境変数（実行前に必ずセット）
ENV	内容	例
BTC_TS_CONFIG_DIR	watchdog.yaml の配置ディレクトリ / Collector config ルート	C:\BtcTradeSystem\tmp\wd_test\config
BTC_TS_DATA_DIR	Collector data ルート（status.json の参照元にもなる）	C:\BtcTradeSystem\tmp\wd_test\data
BTC_TS_LOGS_DIR	watchdog 自身の logs ルート	C:\BtcTradeSystem\tmp\wd_test\logs

任意：

PYTHONPATH（優先して使用。未設定の場合は自動推定）
推奨: C:\BtcTradeSystem\btcts_next\src

4. 起動方法（正準）
4.1 ダミー Collector で起動（Phase1 テスト）
$env:BTC_TS_CONFIG_DIR="C:\BtcTradeSystem\tmp\wd_test\config"
$env:BTC_TS_DATA_DIR  ="C:\BtcTradeSystem\tmp\wd_test\data"
$env:BTC_TS_LOGS_DIR  ="C:\BtcTradeSystem\tmp\wd_test\logs"

Remove-Item "C:\BtcTradeSystem\tmp\wd_test" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $env:BTC_TS_CONFIG_DIR,$env:BTC_TS_DATA_DIR,$env:BTC_TS_LOGS_DIR -Force | Out-Null

& "C:\BtcTradeSystem\scripts\watchdog_collector.ps1" -UseDummyCollector

4.2 本番 Collector で起動（UseDummyCollector なし）
& "C:\BtcTradeSystem\scripts\watchdog_collector.ps1"

5. 設定ファイル（watchdog.yaml）
5.1 既定の場所

省略時：$env:BTC_TS_CONFIG_DIR\watchdog.yaml

-ConfigPath が渡されればそれを優先。

5.2 許可形式

PowerShell 標準のみで読む簡易 YAML。
許可されるのは トップレベル scalar と inline list のみ。

5.3 設定キー（既定値）
key	default	説明
schema_rev	1	設定スキーマ版
interval_sec	5	監視ループ間隔
hang_timeout_sec	120	status 停滞でハング扱いする秒数
max_failures	5	連続失敗で watchdog 停止する閾値
backoff_sec	[10,30,60,120,300]	再起動前の待ち（失敗回数に応じて段階）
no_data_fail_limit	5	no_data 連続で停止する閾値
log_tail_lines	200	予約（Phase1では未使用だが保持）
free_gb_warn	20	空き容量警告（logs ドライブ）
free_gb_stop	10	空き容量停止（logs ドライブ）

未知キーは無視（安全側）。

6. 監視対象と判定ロジック
6.1 多重起動防止（lock）

BTC_TS_LOGS_DIR\watchdog.lock を FileShare.None でオープンできた場合のみ起動継続。

開けない場合は lock busy で例外終了。

可能なら実行中 watchdog の pwsh.exe を Win32_Process.CommandLine から列挙し、ヒントとして例外文に含める。

6.2 監視対象 status.json

パス：$env:BTC_TS_DATA_DIR\collector\status.json

参照キー：

ts_unix があれば優先

なければ ts

ハング判定：

age_sec >= hang_timeout_sec で hang

hang 時は Collector を kill して backoff 後に再起動

前進判定：

age_sec < hang_timeout_sec なら「前進」とみなし consecutiveFails を 0 に戻す

6.3 Collector プロセス終了検知

Start-Process -PassThru で保持する $proc

$proc.HasExited なら collector.exited → 失敗回数加算 → backoff → 再起動

max_failures 以上で watchdog 自体が停止（exitReason 設定）

6.4 no_data 連続検知（保険）

status.message が存在する場合のみ

no_data / startup grace の文字列を含む場合にカウント

no_data_fail_limit 以上で watchdog 停止（Collector kill して終了）

6.5 ディスク安全弁（logs のドライブ）

Get-PSDrive で BTC_TS_LOGS_DIR のドライブ空き容量を監視

free_gb_warn 未満で WARN ログ

free_gb_stop 未満で ERROR ログ → Collector kill → watchdog 停止

7. Collector 起動方式
7.1 Python 実体

python コマンド（Get-Command python の Source）を使用

7.2 子プロセスに渡す ENV（明示固定）

Collector 起動時に以下を 明示的に子プロセスへ渡す：

PYTHONPATH

BTC_TS_CONFIG_DIR

BTC_TS_DATA_DIR

BTC_TS_LOGS_DIR

これにより「手動起動との差・事故」を抑止する。

7.3 事前検査（btcts import）

Collector 起動前に必ず btcts が import できるか確認する。

成功：preflight.btcts.ok

失敗：preflight.btcts.ng → preflight failed: btcts import で例外

7.4 ダミー Collector（-UseDummyCollector）

スクリプト：..\tools\test_collector_entry.py

テストモードを強制固定

BTC_TS_TEST_MODE = ok_then_hang

BTC_TS_TEST_MODE_FORCE = ok_then_hang

7.5 本番 Collector

runpy.run_module("btcts.collector.main", run_name="__main__") を python -c で実行

7.6 標準出力/標準エラー採取

BTC_TS_LOGS_DIR\collector_stdout.log

BTC_TS_LOGS_DIR\collector_stderr.log

8. 成果物（生成ファイル）
パス	内容
BTC_TS_LOGS_DIR\supervisor_collector.log	人間向けテキストログ
BTC_TS_LOGS_DIR\supervisor_collector.jsonl	機械向け JSONL（イベント）
BTC_TS_LOGS_DIR\collector_stdout.log	Collector 標準出力
BTC_TS_LOGS_DIR\collector_stderr.log	Collector 標準エラー
BTC_TS_LOGS_DIR\watchdog.lock	多重起動防止ロック（終了時に削除される）
BTC_TS_LOGS_DIR\watchdog.pid	watchdog 自身の pid 情報（終了時に削除される）
9. JSONL イベント一覧（主要）
watchdog

watchdog.start

interval_sec, hang_timeout_sec, data_dir, logs_dir

loop.tick（DEBUG）

watchdog.exit

reason（exitReason）

preflight

preflight.btcts.ok

out

preflight.btcts.ng

exit_code, out

collector lifecycle

collector.start

python, py_path, config_dir, data_dir, logs_dir

collector.start.dummy

script

collector.start.real

module

collector.exited

exit_code, fails

collector.hang

age_sec, hang_sec, last_ok, fails

collector.kill

pid

restart control

backoff.sleep

sec

fails.reset

prev

guards

guard.disk.warn

free_gb, warn_gb

guard.disk.stop

free_gb, stop_gb

no_data

collector.no_data.detected

count, limit

watchdog.stop.no_data_limit

10. 終了理由（exitReason）
reason	意味
loop.ended_or_external_stop	外部停止 / while 抜け（通常系のまとめ）
console.cancel	Ctrl+C による停止
guard.disk.stop	ディスク不足で停止
watchdog.stop.too_many_fails	連続失敗が閾値に到達
watchdog.stop.no_data_limit	no_data 連続が閾値に到達
exception	例外で落ちた
cancel_hook_failed	Ctrl+C フック設定失敗（継続はする）
11. Phase1 テスト手順（最小）
11.1 構文チェック（必須）
$path="C:\BtcTradeSystem\scripts\watchdog_collector.ps1"
$tokens=$null; $errors=$null
[System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors) | Out-Null
$errors | Format-List

11.2 実行（Dummy）
$env:BTC_TS_CONFIG_DIR="C:\BtcTradeSystem\tmp\wd_test\config"
$env:BTC_TS_DATA_DIR  ="C:\BtcTradeSystem\tmp\wd_test\data"
$env:BTC_TS_LOGS_DIR  ="C:\BtcTradeSystem\tmp\wd_test\logs"
Remove-Item "C:\BtcTradeSystem\tmp\wd_test" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $env:BTC_TS_CONFIG_DIR,$env:BTC_TS_DATA_DIR,$env:BTC_TS_LOGS_DIR -Force | Out-Null

& "C:\BtcTradeSystem\scripts\watchdog_collector.ps1" -UseDummyCollector

11.3 成果物確認
Get-ChildItem "$env:BTC_TS_LOGS_DIR" -Force
Get-Content "$env:BTC_TS_LOGS_DIR\supervisor_collector.jsonl" -Tail 50
Get-Content "$env:BTC_TS_LOGS_DIR\collector_stderr.log" -Tail 200

12. 注意点（運用上の地雷）

watchdog.lock は 終了時に必ず消す設計。残っていたら「異常終了/強制終了の痕跡」なので、テストでは削除してよい。

PYTHONPATH がズレると 手動 python 実行が import で落ちるが、watchdog 実行では ENV を固定しているため「watchdogは動くのに単体 python は落ちる」が起こり得る。

単体実行は PYTHONPATH=C:\BtcTradeSystem\btcts_next\src を必ず設定して行うこと。
