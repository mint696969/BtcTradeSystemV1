test_collector.ps1 仕様書

(Phase1 Collector E2E テストランナー)

1. 概要（このスクリプトは何をするか）

test_collector.ps1 は、BtcTradeSystem NEXT（btcts_next）における Collector の Phase1 結合テスト（E2E）を自動実行する PowerShell スクリプトです。

Collector 単体ではなく、以下を含む 実運用に近い結合状態を短時間で検証することを目的としています。

settings_svc（effective config 解決）

scheduler（endpoint 登録）

rate 制御

audit 出力

status.json 出力

data ファイル生成

本スクリプトは bitFlyer の公開 API のみを対象とし、
秘密情報（APIキー等）は一切使用しません。

2. 位置づけ（Phase1 における役割）

Phase1 の 「Collector が正しく起動・失敗・成功するか」 を確認するための基準テスト

CI というより 開発者が手動で回す信頼性チェック用

Phase2 以降（データ品質ガード等）の テスト注入母体

3. 配置場所と命名規約
スクリプト本体
C:\BtcTradeSystem\tools\test_collector.ps1

テスト成果物（毎回自動生成）
C:\BtcTradeSystem\tmp\collector_test\<runId>\
├─ config\ui\        # テスト用 YAML（毎回生成）
├─ data\             # collector 出力データ
├─ logs\             # audit.jsonl / effective_*.json 等
└─ _last_workspace.txt


<runId> は UTC 時刻ベースで毎回一意

既存成果物は 一切上書きしない

_last_workspace.txt に直近 workspace パスを記録（親シェルから参照可能）

4. 実行方法（どう使うか）
前提条件

PowerShell 7.x

Python 3.12 以上

リポジトリルート：C:\BtcTradeSystem

btcts_next/src/btcts/__init__.py が存在すること

実行コマンド
pwsh -NoProfile -File .\tools\test_collector.ps1

5. 実行時に行われること（処理フロー）
共通初期化

作業用 tmp workspace を作成

以下の環境変数を この PowerShell プロセス内だけに設定

PYTHONPATH

BTC_TS_CONFIG_DIR

BTC_TS_DATA_DIR

BTC_TS_LOGS_DIR

BTC_TS_MODE=DEBUG

stray な collector プロセスがあれば可能な限り停止

6. 各テスト内容
TEST 1: endpoints empty（異常系）

目的

endpoint が 0 件のときに

collector.endpoints.empty

status.mode=ERROR
が確実に出るか

方法

collector.enabled_exchanges=[]

endpoints.yaml = items: []

期待結果

audit に collector.endpoints.empty

status.json が ERROR

→ PASS

TEST 2: unsupported topic（異常系）

目的

未対応 topic が設定された場合に

collector.endpoint.skip

collector.no_data

status.mode=ERROR
になるか

方法

feeds に unknown_topic を有効化

正常 topic はすべて無効化

期待結果

skip + no_data（または endpoints.empty）

status が ERROR

→ PASS

TEST 3: orderbook normal（正常系）

目的

正常な endpoint で

audit の collector.endpoint.ok
または

data ファイル生成
が確認できるか

方法

orderbook のみ有効化

最大 20 秒待機

成功が観測できた時点で即停止（最小負荷）

成功判定（重要）

data file が出た OR audit に endpoint.ok が出た


I/O タイミングや rate 制限による揺れを吸収するため、
二重判定になっています。

TEST 4: データ品質注入（0byte）

目的

Phase2 用のテスト注入

0byte ファイルを人工的に生成

内容

_dq_zero_byte.jsonl を作成

現時点では 作成できたかだけを確認

TEST 5: データ品質注入（JSON破損）

目的

JSON decode failure の疑似再現

内容

壊れた JSON 行を 1 行書き込み

Python で JSON パースし、破損行番号を検出

7. 結果の見方（どう判断するか）
コンソール出力

各 TEST ごとに [OK] / [FAIL] が明示される

最後に ExitCode が表示される

ExitCode 仕様
値	意味
0	全テスト PASS
非0	最初に失敗した TEST のコード
重要ファイル

logs/audit.jsonl
→ Collector の事実ログ（最重要）

data/collector/status.json
→ Collector の状態最終値

logs/*.effective_*.json
→ settings_svc が実際に読んだ設定の現物

8. 注意点・設計上の割り切り

TEST3 は 短時間で終わることを優先

10秒/20秒待つ設計だが、成功が見えたら即終了する

audit 判定は 文字列検索

JSON 全体パースは壊れた1行で失敗するため

Stop-Process は テスト都合の停止

失敗扱いではない

9. 既知の課題 / 今後の拡張

TEST4/5 は Phase2 実装待ち（現時点では注入のみ）

将来的に

data quality guard

retry / quarantine
をこのスクリプトから検証予定

CI 組み込みは 未想定（手動確認用）

10. まとめ

このスクリプトは、

「Collector が、正しく起動し、正しく失敗し、正しく成功する」

ことを 最小時間・最大再現性で確認するための
Phase1 の基準点です。

ここが安定していれば、
以降の Health / Watchdog / Phase2 実装は 迷わず進められます。