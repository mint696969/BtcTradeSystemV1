# Health 正式仕様書（Exploration / Operator UI 版）

最終更新: 2026-03-24  
対象実装:
- `btcts_next/src/btcts/apps/operator_ui/collector_state_service.py`
- `btcts_next/src/btcts/apps/operator_ui/health_data_service.py`
- `btcts_next/src/btcts/apps/operator_ui/views/health_page.py`
- `btcts_next/src/btcts/apps/operator_ui/texts/health.py`

## 0. 目的
Health は、Collector / Exploration Runtime / WS / Layer3 の状態を **人間が即座に把握できるように可視化する監視・解釈機構** である。

現行の Health は以下を重視する。
- Collector が今正常に回っているか
- API rate control が想定どおり効いているか
- 429 / CRIT / RECOVERY / NORMAL が観測できるか
- WS が本当に生きているか、あるいは stale か
- layer3 / market state が最低限どう見えているか

Health 自身は市場判断・戦略判断・自動制御を行わない。  
役割は **現在状態の可視化と根拠付き表示** に限定する。

---

## 1. 対象範囲
含まれるもの:
- collector / exploration の state 集約
- audit tail からの recent events / continuity 判定
- API rate の current overlay 表示
- WS stale の可視化
- Streamlit UI 表示

含まれないもの:
- 自動復旧・自動停止
- 戦略判断
- 原因推論の自動化
- 通知連携

---

## 2. 参照データ
### 2.1 state 系
Health は以下を優先順で参照する。

#### status
- `exploration_status.json`
- `status.json`

#### health
- `exploration_daemon_health.json`
- `exploration_health.json`
- `daemon_health.json`
- `health.json`

#### rate
- `exploration_rate_state.json`
- `rate_state.json`

#### checkpoint
- `exploration_checkpoint.json`
- `checkpoint.json`

#### 補助
- `exploration_daemon_status.json`
- `exploration_scheduler_state.json`
- `origin_status.json`

### 2.2 audit
- `${BTC_TS_LOGS_DIR}/audit.jsonl`

用途:
- recent anomalies
- API / WS continuity rail
- API event activity 推定

### 2.3 market state
- latest market state
- diagnostics

用途:
- Layer3 Trust / Continuity / Interpretation / Freshness の簡易表示

---

## 3. 現在の表示構成
### 3.1 summary
- Collector
- API Rate
- WS
- Layer3

### 3.2 Current State Snapshot
主に以下を表示する。

#### API / Exploration 側
- Status
- Exploration モード
- Util Ratio
- Last 429
- Hold Until（通常時は `-`）

#### WS / runtime state 側
- WS状態
- WS鮮度
- WS最終更新
- WS経過秒
- Snapshot→LIVE(ms)
- 現在目標比率
- Last Sequence ID

#### daemon / layer3 側
- Daemon 状態
- Daemon 最終エラー
- Daemon 連続失敗
- Daemon 最終成功
- Boundary
- Interpretation

### 3.3 charts
- Collector API Rate (1h)
- API continuity rail (1h)
- WS continuity rail (1h)
- Layer3 Trust (1h)

### 3.4 recent events
- recent anomalies / health events

---

## 4. API Rate の解釈
### 4.1 上段 chart
上段は **audit ベースの活動推定** を表示する。

主系列:
- collector req/min
- collector req / 5m
- private limit / 5m
- 429 marker

### 4.2 下段 overlay
下段は **exploration_rate_state 正本寄りの current overlay** を表示する。

主系列:
- Current Utilization
- Active Target Ratio
- Target Utilization
- Hard Cap Utilization

加えて metric として:
- Budget / 60s
- Budget / 300s
- Target Ratio
- Hard Cap

### 4.3 現時点の注意
API graph 本体はまだ完全正本時系列ではない。  
現時点では **上段 audit 推定 + 下段正本 overlay** のハイブリッド構成である。

---

## 5. API continuity rail
### 5.1 目的
REST / API 側の連続性を 1分セルで見る。

### 5.2 判定材料
- audit 上の REST / exploration activity
- 429
- warn/error
- mode changed

### 5.3 level
- green: steady
- yellow: caution
- orange: unstable
- red: broken
- gray: no data

### 5.4 現在理由
current reason は直近確定バケットの状態を表す。  
Collector が現在動いていなければ `no data / audit 活動なし` は正常な表示である。

---

## 6. WS continuity / freshness
### 6.1 WS状態
`origin_status.json` の `ws_state` を表示する。  
例:
- `LIVE`
- `SYNCING`
- `CONNECTING`

### 6.2 WS鮮度
`origin_status.ts` を「最終 WS 更新時刻」として解釈し、経過秒から freshness を算出する。

現行閾値:
- <= 5秒: `LIVE`
- <= 30秒: `QUIET`
- <= 300秒: `STALE`
- > 300秒: `BROKEN` / `停止疑い`

### 6.3 重要な読み方
`WS状態 = LIVE` でも、`WS鮮度 = BROKEN/停止疑い` なら stale と解釈する。  
接続状態だけではなく freshness を優先して見る。

### 6.4 WS summary
WS summary は `ws_state` だけでなく age も考慮する。
- age > 300秒 なら broken 寄り
- age > 30秒 なら caution 寄り

---

## 7. recent events
### 7.1 収集対象
recent anomalies は audit の末尾から以下を拾う。
- 429
- gap
- resync
- warn/error
- exploration mode changed

### 7.2 event 表示
現時点では event / topic / reason / exchange を表示する。

補助翻訳対象:
- gap/resync
- exploration `crit/recovery/warn/normal`
- exploration request completed/failed

---

## 8. daemon 表示
Health は daemon の状態を runtime 本体と分けて表示する。

表示対象:
- Daemon Status
- Daemon Last Error
- Daemon Failures
- Daemon Last Success

これにより、runtime 本体が正常でも daemon loop が壊れていないかを別に見られる。

---

## 9. D hot 正本前提
Health / audit / collector state / rate state は **D hot 正本前提** で運用する。

リアルタイム正本:
- data: `D:\btc_ts_hot\data`
- logs: `D:\btc_ts_hot\logs`
- state: `D:\btc_ts_hot\state`

理由:
- D/E 混在は UI と実体のズレを生み、残像と戦う状態になるため。

---

## 10. 起動と参照
### 10.1 UI 起動
```powershell
$env:PYTHONPATH = "C:\BtcTradeSystem\btcts_next\src"
$env:BTC_TS_DATA_DIR = "D:\btc_ts_hot\data"
$env:BTC_TS_LOGS_DIR = "D:\btc_ts_hot\logs"
$env:BTCTS_STATE_ROOT = "D:\btc_ts_hot\state"

& "C:\BtcTradeSystem\.venv\Scripts\streamlit.exe" run btcts_next\src\btcts\apps\operator_ui\app.py
```

### 10.2 正常な見え方
#### Exploration 主系が正常
- Exploration モード = 通常
- Util Ratio が高めでも hard cap 未満
- Active Target Ratio ~= target
- API continuity rail は緑寄り
- recent events に異常な failed 連打がない

#### WS stale
- WS状態 = LIVE でも
- WS鮮度 = BROKEN/停止疑い
- WS経過秒が大きい

この場合は「接続状態は見えているが、実質 stale」と解釈する。

---

## 11. 現時点の制約
1. API graph 本体は完全正本時系列ではない  
   - 正本 overlay とのハイブリッド運用中。
2. WS continuity は stale 検出までは良いが、主戦場統合は未完  
   - WS 専用運用系の最終形は後続。
3. recent events の event/topic/reason 文言はさらに polish の余地あり。

---

## 付録A. 既知の Risk
1. `origin_status.ts` に依存する WS freshness は、origin 更新が止まると stale を強く示す  
   - これは意図どおりだが、WS 主戦場の最終仕様では別の正本指標が必要になる可能性がある。
2. audit が動いていないと continuity rail は `no data` になる  
   - Collector 停止時には正常表示であることを運用側が理解しておく必要がある。
3. Layer3 は現時点では補助表示  
   - Exploration 主系ゴールの中心は API / daemon / WS freshness 側である。
