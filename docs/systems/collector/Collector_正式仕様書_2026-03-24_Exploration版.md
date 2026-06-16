# Collector 正式仕様書（Exploration Runtime 主役版）

最終更新: 2026-03-24  
対象実装: `btcts_next/src/btcts/collector_vnext/`

## 0. この文書の位置づけ
本書は **Exploration Runtime を主役 runtime として再定義した現行 Collector vNext 実装の正式仕様書** である。  
ここでいう正式仕様とは、実装済みコード・起動導線・出力物・運用前提に乖離しない現在契約を指す。

補助資料の役割分担は以下とする。
- `Collector 正式仕様書.md`
  - Collector vNext の現行実装・起動・出力物・運用契約の正本
- `API_Rate 正式仕様書.md`
  - Exploration Runtime における API レート制御の正式仕様と調整点
- `Health 正式仕様書.md`
  - Health / Operator UI の表示・状態解釈の正式仕様
- `Collector 記録設計 vNext.md`
  - レイヤ責務・将来拡張・設計思想を扱う補助資料

---

## 1. Collector vNext の定義
Collector vNext は、取引所市場データと収集状態を **append-only JSONL** と **state / health / audit** へ記録する記録基盤である。

現在の主責務は以下。
- bitFlyer BTC/JPY の現物データ収集
- raw / canonical への記録
- stream control event の記録
- state / health / checkpoint / daemon health / rate state の更新
- REST support layer の高密度収集（Exploration Runtime）
- WS 主戦場の状態可視化と continuity 観測

Collector は戦略判断や市場判断を行わない。  
責務は **市場事実と収集状態を、順序・出自・品質情報付きで残すこと** に限定する。

---

## 2. 現在の主 runtime
### 2.1 主役 runtime
現行 Collector vNext の主役 runtime は **Exploration Runtime** である。

目的:
- request を節約するより、可能な限り情報を取り切る
- 公式制限に近づきつつも、制御下で取り続ける
- 429 発生時も Collector 全体を止めず、floor まで減速して継続収集する

### 2.2 補助 runtime
従来の smoke / qualification 系 runtime は **補助 runtime** として扱う。

位置づけ:
- 導線確認
- qualification
- smoke
- 基礎健全性確認

主系運用の正本ではない。

---

## 3. 対象取引所・銘柄
- exchange: `bitflyer`
- market: `spot`
- symbol: `BTC_JPY`
- instrument_id: `bitflyer.spot.BTC_JPY`

---

## 4. 現在の収集経路
### 4.1 REST（Exploration 主系）
- `/v1/board`
- `/v1/executions`

Exploration Runtime はこれらを request class として高密度に回す。

### 4.2 WebSocket（主戦場 / 現時点では別主系）
- executions stream
- board stream
- board snapshot stream

WS は system 全体の主戦場だが、2026-03-24 時点では Exploration Runtime の主責務に統合し切っていない。  
Health/UI では stale を含めた状態観測を重視する。

---

## 5. レイヤ責務
現行 Collector vNext は **Raw / Canonical を正本レイヤとして実装**している。

### 5.1 Raw Layer
目的:
- 原本保全
- forensic
- transform 再処理
- provider payload 保持

保存先:
- `<DATA_ROOT>/collector_raw/exchange=<exchange>/symbol=<symbol>/channel=<channel>/date=<YYYY-MM-DD>/part-00001.jsonl`

### 5.2 Canonical Layer
目的:
- downstream 共通入力
- Replay / Research / Market Engine への入力
- stream control / board continuity 記録

保存先:
- `<DATA_ROOT>/market_data/exchange=<exchange>/symbol=<symbol>/type=<record_type>/date=<YYYY-MM-DD>/part-00001.jsonl`

### 5.3 Compact Layer
本日時点の `collector_vnext/` 正本実装は **Compact Layer を主書き込み先として持たない**。  
Compact / UI 向け縮約は後段で扱う。

---

## 6. リアルタイム正本ルート方針
### 6.1 hot 正本
リアルタイム運用の正本は以下とする。
- data: `D:\btc_ts_hot\data`
- logs: `D:\btc_ts_hot\logs`
- state: `D:\btc_ts_hot\state`

### 6.2 cold / secondary
以下は遅延許容の二次用途とする。
- replay
- simulation
- archive
- 重い分析成果物

### 6.3 理由
D と E が混在すると、UI / state / audit / raw / canonical がズレて **残像と戦う** 状態になる。  
リアルタイム運用では D を正本に固定する。

---

## 7. 環境変数
### 7.1 正規運用で使うもの
- `BTC_TS_DATA_DIR`
- `BTC_TS_LOGS_DIR`
- `BTCTS_STATE_ROOT`
- `PYTHONPATH`

### 7.2 互換
collector_vnext/config.py は以下を fallback として許容する。
- `BTCTS_DATA_ROOT`
- `BTCTS_LOGS_ROOT`

ただし運用思想上の正本は `BTC_TS_DATA_DIR` / `BTC_TS_LOGS_DIR` である。

---

## 8. Exploration Runtime の構成
### 8.1 実装ファイル
- `exploration_config.py`
- `exploration_state.py`
- `exploration_scheduler.py`
- `exploration_runtime.py`
- `exploration_daemon.py`

### 8.2 request class
現行の request class は以下。
- `board_snapshot`
- `rest_trades`

### 8.3 request priority
設定は `exploration_runtime_def.yaml` で定義する。

初期値:
- `board_snapshot`
- `rest_trades`

### 8.4 request share 制御
各 request class は以下で制御する。
- `weight`
- `min_share`

scheduler は target share と actual share の差分を用いて dispatch を決定する。

---

## 9. runtime mode
Exploration Runtime の mode は以下。
- `NORMAL`
- `WARN`
- `CRIT`
- `RECOVERY`

### 9.1 NORMAL
- target utilization に沿って通常収集
- `active_target_ratio ~= target_utilization`

### 9.2 WARN
- utilization が warn を超えたときの注意状態
- ただし収集は継続

### 9.3 CRIT
- 短時間 429 反復などの強い制限状態
- `active_target_ratio -> crit_floor_ratio`
- floor まで減速して収集継続

### 9.4 RECOVERY
- cooldown / recovery 条件を満たした後の段階復帰
- target まで step で戻す

---

## 10. 429 時の基本挙動
- 単発 429: hold を反映しつつ継続
- 短時間で 429 反復: `CRIT`
- `active_target_ratio -> crit_floor_ratio`
- cooldown / recovery start after 経過後に `RECOVERY`
- 段階復帰後に `NORMAL`

mode 遷移は audit に `collector_vnext.exploration.mode.changed` として残る。

---

## 11. state / health / checkpoint
保存先:
- `<STATE_ROOT>/collector_vnext/`

Exploration 系で更新される主なファイル:
- `exploration_status.json`
- `exploration_health.json`
- `exploration_rate_state.json`
- `exploration_checkpoint.json`
- `exploration_scheduler_state.json`
- `exploration_daemon_status.json`
- `exploration_daemon_health.json`

### 11.1 `exploration_rate_state.json`
正本用途:
- runtime mode
- utilization
- active target ratio
- hold 情報
- request class ごとの request/success/fail/429

### 11.2 `exploration_scheduler_state.json`
正本用途:
- mode 永続化
- 429 履歴
- request history
- recovery 進行状態

### 11.3 `exploration_daemon_health.json`
用途:
- daemon loop 状態の health
- `cycle_no`
- `consecutive_failures`
- `last_success_ts`
- `last_error`

---

## 12. audit
### 12.1 主なイベント
- `collector_vnext.exploration.board_snapshot.completed`
- `collector_vnext.exploration.board_snapshot.failed`
- `collector_vnext.exploration.rest_trades.completed`
- `collector_vnext.exploration.rest_trades.failed`
- `collector_vnext.exploration.mode.changed`

### 12.2 mode.changed
payload には以下を含む。
- `from_mode`
- `to_mode`
- `exchange`
- `request_class`（可能な場合）
- `status_code`
- `retry_after_sec`

---

## 13. Health / UI との接続
Health は exploration 系 state を優先参照する。

現在の主な表示対象:
- Exploration モード
- Util Ratio
- Last 429
- Hold Until（通常時は `-`）
- Active Target Ratio
- Daemon 状態
- Daemon 最終エラー
- Daemon 連続失敗
- Daemon 最終成功
- WS状態
- WS鮮度
- WS最終更新
- WS経過秒

重要:
- `WS状態 = LIVE` でも `WS鮮度 = BROKEN/停止疑い` なら stale と解釈する

---

## 14. 起動方法
### 14.1 Exploration daemon（推奨）
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\run_collector_vnext_exploration_daemon.ps1
```

### 14.2 直接起動
```powershell
$env:PYTHONPATH = "C:\BtcTradeSystem\btcts_next\src"
$env:BTC_TS_DATA_DIR = "D:\btc_ts_hot\data"
$env:BTC_TS_LOGS_DIR = "D:\btc_ts_hot\logs"
$env:BTCTS_STATE_ROOT = "D:\btc_ts_hot\state"

& "C:\BtcTradeSystem\.venv\Scripts\python.exe" -m btcts.collector_vnext.exploration_daemon
```

---

## 15. 現時点の強み
- Exploration Runtime を主役とする構造が成立
- D hot 正本で raw/canonical/log/state を揃えられる
- 429 反復時の CRIT / RECOVERY / NORMAL が成立
- mode.changed が audit に残る
- Health/UI で現在状態を把握できる
- API rate control が本番思想で稼働可能

---

## 16. 現時点の未完 / 後続タスク
- WS 主戦場の本格統合
- API graph の完全正本時系列化
- tools/tests/docs に残る旧 ENV 名整理
- multi-budget domain（info / order / cancel / shared IP）化

---

## 付録A. 既知の Risk
1. tools/tests/docs に旧 `BTCTS_*` 記述が残る  
   - 本体運用の blocking ではないが、将来の混乱源になり得る。
2. WS は stale を見抜けるが、主戦場としての最終統合は未完  
   - 接続状態と鮮度を分けて見る必要がある。
3. API graph 本体はまだ audit 推定と正本 overlay のハイブリッド  
   - 完全正本時系列化は後続。
