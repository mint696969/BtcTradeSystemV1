test_rate_control_phase1 仕様書

概要

path: C:\BtcTradeSystem\tools\test_rate_control_phase1.py
目的: Phase1 の API レート制御（RateController）の基本仕様が動いていることを、短時間で再現性高く確認する。

このスクリプトは以下を検証する：

[UNIT] RateController 単体の状態遷移

util 上昇で WARN に遷移する

429 発生で CRIT に遷移し、hold/backoff の状態になる

一定時間（cooldown）経過後に NORMAL に復帰できる

[INTEG] Scheduler と RateController の結線

Scheduler が RateController を使って動作する

rate_state.json / status.json が出力される

429 模擬後に CRIT へ落ち、wait_ms 等の抑制情報が出る

使い方
実行前提

実行場所は C:\BtcTradeSystem を推奨

Python は btcts_next\src を参照できる必要がある（このスクリプトは 自己完結で sys.path を調整している）

実行コマンド
cd C:\BtcTradeSystem
python .\tools\test_rate_control_phase1.py
echo $LASTEXITCODE

出力先（成果物）

本番環境を汚さないため、出力は 強制的に tmp 配下へ寄せる。

BTC_TS_DATA_DIR = C:\BtcTradeSystem\tmp\_rate_test\data

BTC_TS_LOGS_DIR = C:\BtcTradeSystem\tmp\_rate_test\logs

生成物（最低限）：

C:\BtcTradeSystem\tmp\_rate_test\data\collector\rate_state.json

C:\BtcTradeSystem\tmp\_rate_test\data\collector\status.json

成功判定

次の全てを満たせば PASS：

コンソールに DONE が出る

終了コードが 0（$LASTEXITCODE -eq 0）

rate_state_exists= True が出る

tmp\_rate_test\data\collector\rate_state.json が実在する

補助確認：

Get-ChildItem .\tmp\_rate_test -Recurse | Select-Object FullName, Length

期待されるログ例（読み方）
[UNIT] の見方

mode(after util=0.5): WARN が出る → util による警戒モード遷移 OK

mode(after 429): CRIT が出る → 429 を CRIT として扱う仕様 OK

mode(after cool down): NORMAL が出る → 冷却時間後に復帰 OK

[INTEG] の見方

final_mode= CRIT ... wait_ms= ... が出る → Scheduler 側で抑制が効いている

rate_state_exists= True → rate_state.json 出力が実装されている

注意点（重要）

外部 API にはアクセスしない
429 は “模擬” で発生させる設計。ネットワーク状況に依存しない。

環境変数は強制上書きされる
スクリプト実行中は BTC_TS_DATA_DIR / BTC_TS_LOGS_DIR を tmp\_rate_test に寄せる。
→ 本番ディレクトリを汚さない意図。
→ ただし「既存の ENV を尊重したい」用途には向かない。

sys.path の調整はリポ構造に依存
tools から見て ..\btcts_next\src を参照している。
→ リポ構造が変わったら import に失敗する可能性がある。

テストが短時間（約6秒）で終わるのは仕様
長時間の安定稼働テストではなく、状態遷移と出力の存在確認が目的。

既知の課題 / 今後の改善候補

rate_state.json の内容検証が浅い
現状は「存在確認」と「mode/eff_max_rps/wait_ms の表示」まで。
追加で「期待するキーが入っているか」「CRIT→NORMAL 復帰後の値が妥当か」などの assertion を入れる余地がある。

sys.path hack の共通化
tools/test_*.py が増えるなら、共通の import ブートストラップを 1 箇所に集約した方が事故が減る
（例：tools/_bootstrap.py を作り、各テストから import する方式）。