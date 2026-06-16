# Collector 正式仕様追補（Unified Collector U1-U2 到達点）

最終更新: 2026-03-24  
対象実装: `btcts_next/src/btcts/collector_vnext/`

## 0. この文書の位置づけ
本書は `Collector_正式仕様書_2026-03-24_Exploration版.md` を補完する **Unified Collector 追補仕様** である。  
既存 Exploration 正式仕様を否定するものではなく、2026-03-24 時点で新たに成立した Unified family の到達点と運用契約を追記する。

本追補の目的:
- Unified family の責務を明示する
- REST + WS board + WS executions の統合到達点を記録する
- state / health / origin / executions status の現行契約を固定する
- D hot / launcher / WS SSL verify 前提を明示する
- bitFlyer board の挙動に対する保守的運用姿勢を明示する

---

## 1. Unified Collector の位置づけ
### 1.1 runtime family
現時点の Collector vNext runtime family は以下のように扱う。

- `smoke`
  - qualification / smoke / 緊急導線確認
- `exploration`
  - REST 主系として成立した現行高密度収集 runtime
- `unified`
  - REST + WS board + WS executions を同一主系視点で扱う次の主役 family

### 1.2 現在の意味
2026-03-24 時点では、Unified Collector は **U1-U2 最小統合が成立** した状態にある。  
すなわち、

- REST lane
- WS board lane
- WS executions lane
- status / health / daemon / UI 接続

が D hot 正本上で一体として動作する。

---

## 2. Unified family の責務
Unified Collector の責務は以下。

- REST support layer の継続収集
- WS board lane の長寿命監視と記録
- WS executions lane の長寿命監視と記録
- D hot 正本への state / health / audit 更新
- Health / UI が単一 family として読める状態契約の提供

Unified Collector は依然として **市場判断をしない**。  
責務は、事実・収集状態・出自・更新時刻を残すことに限定する。

---

## 3. 現在の到達点
### 3.1 成立済み
- `unified_state.py`
- `unified_runtime.py`
- `unified_daemon.py`
- `unified_ws_board_lane.py`
- `unified_ws_executions_lane.py`
- family 別 lock
- launcher
- operator_ui 側の unified priority 読み込み
- status / health / origin / executions status の整合
- Health / audit の unified 寄せ

### 3.2 現実運用で確認済みのこと
- D hot 正本上で daemon 継続稼働
- `unified_status.json` 更新
- `unified_health.json` 更新
- `unified_origin_status.json` 更新
- `unified_executions_status.json` 更新
- `ws_board_lane = live`
- `ws_executions_lane = live`
- REST mode = `NORMAL`
- board / executions の raw / canonical 出力確認

---

## 4. Unified state 契約
保存先:
- `<STATE_ROOT>/collector_vnext/`

### 4.1 Unified 主ファイル
- `unified_status.json`
- `unified_health.json`
- `unified_checkpoint.json`
- `unified_rate_state.json`
- `unified_scheduler_state.json`
- `unified_origin_status.json`
- `unified_executions_status.json`
- `unified_daemon_status.json`
- `unified_daemon_health.json`

### 4.2 `unified_status.json`
主な意味:
- unified family の総合 status
- REST lane 状態
- WS board lane 状態
- WS executions lane 状態

代表項目:
- `runtime_kind`
- `mode`
- `rest_lane`
- `ws_board_lane`
- `ws_executions_lane`
- `rate_control`
- `last_result`

### 4.3 `unified_health.json`
主な意味:
- unified family の総合 health
- REST mode
- board 側 freshness
- executions 側 freshness

代表項目:
- `rest_mode`
- `ws_state`
- `ws_freshness`
- `ws_last_event_ts`
- `ws_last_error`
- `ws_executions_state`
- `ws_executions_freshness`
- `ws_executions_last_event_ts`
- `ws_executions_last_error`
- `ws_executions_trade_count`

### 4.4 `unified_origin_status.json`
主な意味:
- WS board lane の正本状態

代表項目:
- `ws_state`
- `lane_state`
- `last_error`
- `saw_snapshot`
- `saw_delta`
- `gap_detected`
- `resync_active`
- `restart_count`

重要:
- `unified_origin_status.json` は **WS board lane 正本**
- REST runtime から上書きしない

### 4.5 `unified_executions_status.json`
主な意味:
- WS executions lane の正本状態

代表項目:
- `ws_state`
- `lane_state`
- `last_error`
- `restart_count`
- `trade_count`

---

## 5. freshness / stale / broken の現行契約
### 5.1 board
board は以下を使い分ける。

- `ws_state`
  - 接続系状態
- `ws_freshness`
  - 最終イベント時刻に基づく鮮度

現行 freshness:
- `LIVE`
- `QUIET`
- `STALE`
- `BROKEN`
- `CONNECTING`
- `SYNCING`
- `UNKNOWN`

### 5.2 executions
executions も board と同様に、

- `ws_state`
- `ws_freshness`

を分離して扱う。

補足:
- 接続直後で trade 未着の短時間観測では `CONNECTING` / `connected` に見える場合がある
- これは直ちに異常と断定せず、connected_ts / last_event_ts と合わせて解釈する
- 実運用では `LIVE / QUIET / STALE / BROKEN` の推移を優先して見る

### 5.3 原則
- 接続中と stale は別概念
- `LIVE` でも最終更新が古ければ stale/broken を区別する
- 逆に、短時間観測で trade がまだ流れていない場合は即異常と断定しない

---

## 6. bitFlyer board の保守的運用姿勢
bitFlyer board では、snapshot より先に diff が観測されるケースがある。  
現時点ではこれを **直ちに異常とは断定しない**。

運用姿勢:
- bitFlyer 固有挙動・癖として扱う
- 直ちに strategy judgement に結び付けない
- continuity 材料として記録し、後段で review 可能にする
- stale / broken / reconnect / resync は state / audit で明示する

すなわち、
**Collector は bitFlyer の癖を矯正するのではなく、再判断できる材料を残す。**

---

## 7. launcher / 環境前提
使用 launcher:
- `tools/run_collector_vnext_unified_daemon.ps1`

前提:
- `BTC_TS_DATA_DIR = D:\btc_ts_hot\data`
- `BTC_TS_LOGS_DIR = D:\btc_ts_hot\logs`
- `BTCTS_STATE_ROOT = D:\btc_ts_hot\state`
- `PYTHONPATH = C:\BtcTradeSystem\btcts_next\src`

現環境では bitFlyer WS 証明書事情により、
- `BTCTS_WS_SSL_VERIFY = false`

を launcher 側で与える。

重要:
- 単発 `python -m btcts.collector_vnext.unified_runtime` は D hot 正本確認には向かない
- 本運用確認は launcher 経由で行う

---

## 8. lock
family 別 lock を採用する。

現行:
- `smoke_daemon.lock.json`
- `exploration_daemon.lock.json`
- `unified_daemon.lock.json`

目的:
- runtime family ごとの常駐意図を明確化する
- 主系の混線を避ける

---

## 9. Health / UI 接続
Operator UI は unified を優先して state を読む。

優先方針:
- unified
- exploration
- legacy

現在の UI では以下が表示可能:
- runtime kind
- REST mode / utilization
- WS board state / freshness / last update / restart
- WS executions state / freshness / last update / trade count
- daemon status / failures / last success
- recent anomaly / unified audit event

---

## 10. audit
Unified family の主な event:
- `collector_vnext.unified.board_snapshot.completed`
- `collector_vnext.unified.board_snapshot.failed`
- `collector_vnext.unified.rest_trades.completed`
- `collector_vnext.unified.rest_trades.failed`
- `collector_vnext.unified.mode.changed`
- `collector_vnext.unified.ws_board.started`
- `collector_vnext.unified.ws_board.reconnected`
- `collector_vnext.unified.ws_executions.started`
- `collector_vnext.unified.ws_executions.connected`
- `collector_vnext.unified.ws_executions.reconnected`
- `collector_vnext.unified.ws_executions.message.received`
- `collector_vnext.unified.ws_executions.message.skipped`
- `collector_vnext.unified.ws_executions.message.meta`
- `collector_vnext.unified.ws_executions.trade.written`

目的:
- 収集状態を後から再確認できること
- Health / anomaly 表示に流せること
- 原因切り分けを後段で行えること

---

## 11. まだ残るタスク
2026-03-24 時点で未完として残る主なもの:
- board / executions の stale 判定運用磨き
- gap / resync 契約の更なる洗練
- docs / runbook の全面 unified 正式化
- shared primary lock 等の将来設計
- multi-budget 本格化

---

## 12. まとめ
Unified Collector は、2026-03-24 時点で

**REST + WS board + WS executions を、D hot 正本上の単一 family として扱う最小主系**

まで到達した。

今後の拡張でも原則は同じである。

- Collector は判断しない
- 事実・順序・出自・収集状態を残す
- bitFlyer 固有挙動は直ちに異常と断定せず、再判断可能な材料として保持する