Collector 正式仕様書（確定版 / Phase 1）

（BtcTradeSystem / btcts_next）

1. 目的（What & Why）

Collector は 取引所 API からの時系列データ収集を、24/7 安全かつ再現可能に実行する常駐プロセスである。

主目的は以下の 3 点に集約される。

市場データの永続取得

orderbook / trades 等の raw に近いが「扱いやすく正規化された」データを継続収集

運用事故を起こさない

レート制限・設定ミス・未対応 endpoint を確実に検知し、
「動いているように見える事故」 を起こさない

他機能（Health / Dashboard / AI）への信頼できる入力源

status / audit / data の 3 系統を分離し、監視・可視化・分析に耐える構造を提供

Collector は 分析・判断を行わない。
「正しく・安全に・記録する」ことのみに責任を持つ。

2. 全体構成（責務分離）
collector/
├─ main.py        … エントリポイント / 設定読込 / 状態管理
├─ scheduler.py  … 実行スケジューラ / no_data 判定
├─ rate.py       … レート制御（RatePolicy）
├─ providers/
│   └─ bitflyer.py … APIアクセス + compact 処理
├─ status.py     … status.json の構造定義

設計原則

設定駆動（YAML）

失敗は即 ERROR

成功と skip を明確に区別

ファイルは append-only（jsonl）

3. 設定ファイルと役割
3.1 exchanges.yaml

取引所単位の 有効/無効

公式レート上限と安全係数

RatePolicy の入力元

例（概念）：

exchanges:
  bitflyer:
    enabled: true
    rate:
      max_rps: 10
      soft_ratio: 0.9
      hard_ratio: 0.8

3.2 endpoints.yaml

Collector が 何を・どの頻度で取りに行くかを定義。

対応形式：

items: [...] 形式

{exchange: {topic: {...}}} マップ形式（現行）

重要ルール：

endpoint が 0 件の場合は即起動失敗

未対応 topic は skip + no_data 判定対象

3.3 collector.yaml

Collector 自身の挙動制御。

主要項目：

tick_sec

status_every_sec

startup_grace_sec

no_data_check_every_sec

3.4 monitoring.yaml

レート安全係数（safety_factor）

将来 Health と統合予定

4. 実行モデル（How it works）
4.1 起動フロー

main.py 起動

YAML 読込

Scheduler 構築

Endpoint 登録

status = RUNNING

run_forever 開始

4.2 Endpoint 実行

各 endpoint は以下の流れで実行される。

RatePolicy による実行制御

provider.fetch_xxx()

compact 処理（構造縮約）

jsonl へ append

audit: collector.endpoint.ok

4.3 未対応 endpoint

_make_runner で fallback

必ず audit に理由と hint を残す

EndpointSkipped を投げる

Scheduler 側で 成功扱いにしない

これにより：

「APIは呼ばれているがデータが無い」状態を no_data として検出可能

5. 成果物（Artifacts）
5.1 データ（市場データ）

保存先：

<DATA_DIR>/collector/<exchange>/<topic>/<YYYYMMDD>.jsonl


例：

data/collector/bitflyer/orderbook/20260119.jsonl


形式：

jsonl（1行1レコード）

append-only

file_lock により多重起動耐性あり

5.2 status.json（状態）

保存先：

<DATA_DIR>/collector/status.json


内容：

mode: RUNNING / ERROR / STOPPED

items: 各 endpoint の状態

last_error: 直近致命エラー

用途：

Health / Dashboard が直接参照

「今 Collector が信用できるか」の一次判断材料

5.3 audit.jsonl（監査ログ）

保存先：

<LOGS_DIR>/audit.jsonl


記録内容：

起動 / 停止

endpoint 成功

skip 理由

no_data 判定

設定ミス

人間と GPT が後追いで原因解析するための唯一の正史

6. エラー・異常系設計
6.1 endpoints 未定義

起動失敗

status = ERROR

audit: collector.endpoints.empty

6.2 未対応 topic

audit: collector.endpoint.skip

startup_grace 超過で collector.no_data

status = ERROR

6.3 API 429

RatePolicy に即反映

CRIT audit

last_ok を更新しない

7. 他機能との連携
Health

status.json を監視

audit.jsonl を根拠として WARN / CRIT 判定

Dashboard

status.json → 表示

data/collector → 可視化・分析

AI / Analysis

data/collector 以下のみ参照

Collector 自体には一切依存しない

8. 開発・拡張時の注意点（重要）

❌ Collector に判断ロジックを入れない

❌ ダミー endpoint を登録しない

❌ skip を success 扱いにしない

✅ 未対応は 必ず理由付きで skip

✅ データは必ず jsonl append-only

9. 現状の完成度評価

設計：完成

異常系：網羅

運用安全性：高

拡張余地：十分
