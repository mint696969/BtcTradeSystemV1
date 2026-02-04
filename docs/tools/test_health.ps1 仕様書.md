test_health.ps1 仕様書
対象ファイル

C:\BtcTradeSystem\tools\test_health.ps1

目的

Health（監視）機能の表示・判定ロジックを検証するために、テスト用ワークスペースを作成し、Health/UI が参照する設定・入力データを 確実に固定した場所へ生成する。

具体的には以下を行う：

C:\BtcTradeSystem\tmp\health_test\<timestamp>\ 配下にワークスペース作成

ENV を固定して、UI/Health が このワークスペースを読む状態にする

BTC_TS_CONFIG_DIR / BTC_TS_DATA_DIR / BTC_TS_LOGS_DIR / PYTHONPATH

Health が読むことを想定したテスト入力を生成する

config\ui\monitoring.yaml（閾値）

data\collector\status.json（collector 状態）

logs\audit.jsonl（監査ログ最小）

オプションで Streamlit(UI) を起動し、Health タブの表示・判定を目視確認できるようにする

使い方
1) ワークスペース生成のみ（UI 起動しない）
pwsh -NoProfile -File .\tools\test_health.ps1 -Case WARN -NoRun


-NoRun を付けると 生成だけ行い、UI は起動しない

標準出力に Workspace パスが出る（ここが結果確認の起点）

2) ワークスペース生成 + UI 起動
pwsh -NoProfile -File .\tools\test_health.ps1 -Case WARN


最後に C:\BtcTradeSystem\scripts\run.ps1 を呼び、UI を起動する

UI 側は ENV（BTC_TS_*）により、このワークスペースを参照する前提

3) Case と AgeSec の指定

-Case は OK / WARN / CRIT / ERROR のいずれか

-AgeSec を明示すると、Case 自動値よりこちらが優先される

例：

pwsh -NoProfile -File .\tools\test_health.ps1 -Case WARN -AgeSec 25 -NoRun

生成物（ワークスペース構造）

例：C:\BtcTradeSystem\tmp\health_test\20260203_235411\

config\ui\monitoring.yaml

data\collector\status.json

logs\audit.jsonl

結果の見方
1) Workspace を手で指定して中身を見る
$ws = "C:\BtcTradeSystem\tmp\health_test\YYYYMMDD_HHMMSS"
Get-ChildItem $ws -Recurse | Select-Object FullName, Length
Get-Content "$ws\data\collector\status.json" | Select-Object -First 80
Get-Content "$ws\config\ui\monitoring.yaml"
Get-Content "$ws\logs\audit.jsonl"

2) 最新ワークスペースを自動で拾う（推奨）
$ws = Get-ChildItem "C:\BtcTradeSystem\tmp\health_test" -Directory |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1 -ExpandProperty FullName

$ws
Get-Content "$ws\data\collector\status.json" | Select-Object -First 80

テストケースの意味
OK

status.json の age_sec が小さい（既定 0.5）

mode=RUNNING

想定：Health が正常（OK/NORMAL）扱い

WARN

age_sec が warn 閾値を超える（既定 12.0、閾値 warn=10.0）

retries=2（retries warn=1 を超える）

想定：Health が警告（WARN）扱い

CRIT

age_sec が crit 閾値を超える（既定 35.0、閾値 crit=30.0）

想定：Health が重大（CRIT）扱い

ERROR

mode=ERROR

last_error を明示

audit は collector.main.error

想定：Health が異常（ERROR）扱い（表示・通知系がどうなるか確認）

実装上の重要ポイント（このスクリプトの肝）

BTC_TS_CONFIG_DIR / BTC_TS_DATA_DIR / BTC_TS_LOGS_DIR / PYTHONPATH を このスクリプトが必ずセットする
→ これにより「UI がどこを読んでいるか」がブレない

btcts.settings.load_yaml_with_path('monitoring') を Python で呼び、
実際に読まれている monitoring.yaml のパスを表示する
→ ENV 固定が効いていることを機械的に証明できる

注意点

このスクリプトは Collector を本当に起動しない（入力データを“模擬生成”するだけ）

生成する audit.jsonl は最小形（1〜2行）
→ audit を詳細に再現したい用途には不足する

PowerShell の対話セッションで $PSScriptRoot を参照すると空になる
→ 手動検証で $PSScriptRoot を叩かないこと（スクリプト内だけで使う）

既知の課題・改善候補（必要になったら）

ERROR ケースの items[].last_ok を null に寄せるかどうか

現状：ERRORでも last_ok が入る

目的が「UIの表示確認」なら問題なし

目的が「現物に寄せたフォーマット再現」なら null の方が自然

retries / cause / notes のバリエーション増加

現状は最小限

将来、Health 側のロジックが増えたらテストケースを追加する