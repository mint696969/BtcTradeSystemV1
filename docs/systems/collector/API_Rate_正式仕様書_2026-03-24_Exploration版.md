# API_Rate 正式仕様書（Exploration Runtime 制御版）

最終更新: 2026-03-24  
対象実装:
- `btcts_next/src/btcts/collector_vnext/exploration_scheduler.py`
- `btcts_next/src/btcts/collector_vnext/exploration_runtime.py`
- `btcts_next/src/btcts/collector_vnext/exploration_config.py`
- `btcts_next/config/schema/exploration_runtime_def.yaml`

## 0. 目的と位置づけ
本仕様書は、BtcTradeSystem NEXT における **Exploration Runtime の API レート制御** を正式に定義する。

本仕様の目的は以下の通りである。
- 各取引所・各 API 提供元が定めるレート上限を **制御下で使い切る方向で運用**する
- 429（Too Many Requests）を可能な限り避けつつ、発生時も Collector 全体を停止させない
- 情報取得量を可能な限り維持しつつ、自動で減速・復帰する
- Health / UI / audit / soak で診断可能な正準 state を持つ

本仕様は、従来の smoke 的最小制御から、**Exploration-first / production-first** の制御へ切り替えた現行仕様である。

---

## 1. 基本思想
### 1.1 安全運転を主役にしない
本仕様は「最初から request を節約する」思想ではない。  
目的は **可能な限り情報を取得すること** である。

### 1.2 429 は停止理由ではなく減速理由
429 が出ても Collector 全体を止めない。  
必要に応じて floor まで減速しつつ、情報取得は継続する。

### 1.3 95% は探索開始値
bitFlyer 初期値では target utilization を 95% とする。  
ただしこれは最終値ではなく、探索開始値である。

### 1.4 取引所別調整を前提とする
MAX 血（target / hard cap / recovery など）は取引所別に調整できる構造とする。

---

## 2. 現行対象
### 2.1 取引所
- `bitflyer`

### 2.2 監視窓
現行の正本制御窓は以下。
- `window_300s = 500`
- `window_60s_ip = 500`

### 2.3 request class
- `board_snapshot`
- `rest_trades`

### 2.4 request class priority
初期 priority は以下。
1. `board_snapshot`
2. `rest_trades`

---

## 3. mode 定義
Exploration Runtime の制御 mode は以下。
- `NORMAL`
- `WARN`
- `CRIT`
- `RECOVERY`

### 3.1 NORMAL
- 通常収集
- `active_target_ratio ~= target_utilization`
- 収集を主役として継続

### 3.2 WARN
- utilization が warn 閾値を超えた注意状態
- 強い抑制ではなく注意・予防的評価

### 3.3 CRIT
- 短時間 429 反復などの強い制限状態
- `active_target_ratio -> crit_floor_ratio`
- floor で収集継続

### 3.4 RECOVERY
- cooldown / recovery 条件を満たした後の段階復帰
- `crit_floor_ratio -> target_utilization` を段階的に戻す

---

## 4. 利用率の定義
### 4.1 utilization
利用率は 60秒窓 / 300秒窓のうち厳しい方を採る。

現行実装概念:
- `utilization_60s = requests_60s / window_60s_ip`
- `utilization_300s = requests_300s / window_300s`
- `utilization = max(utilization_60s, utilization_300s)`

### 4.2 budget
現在許容される budget は `active_target_ratio` を元に算出する。

例:
- `budget_60s = window_60s_ip * active_target_ratio`
- `budget_300s = window_300s * active_target_ratio`

---

## 5. 制御フロー
### 5.1 通常時
1. scheduler が `current_budget()` を算出
2. `allowed_now` が true なら dispatch 候補を選ぶ
3. request class の target share / min_share / weight を見て dispatch を決定
4. request 送信後、result を反映
5. snapshot / state / audit を更新

### 5.2 429 発生時
1. `note_request_result()` で `status_code == 429` を検出
2. `last_429_ts` を更新
3. `recent_429_ts` に追加
4. `retry_after_sec` があれば `hold_until_ts` を更新
5. `_refresh_mode()` で 429 反復数を評価
6. 短時間 429 反復なら `CRIT` に遷移
7. `active_target_ratio = crit_floor_ratio`

### 5.3 CRIT 中
- hold/cooldown 中でも Collector は止めない
- `allowed_now` が残る限り floor で継続収集
- `active_target_ratio = crit_floor_ratio`

### 5.4 CRIT -> RECOVERY
条件:
- `ts >= hold_until_ts`
- `last_429_ts` から `recovery_start_after_sec` 経過

遷移時:
- `mode = RECOVERY`
- `recovery_started_ts = now`
- `active_target_ratio = crit_floor_ratio`
- `recent_429_ts.clear()`

### 5.5 RECOVERY -> NORMAL
1. `_recovery_target_ratio()` が step に応じて ratio を返す
2. `active_target_ratio` を段階的に上げる
3. `active_target_ratio >= target_utilization` かつ `utilization <= warn_utilization` なら `NORMAL`

### 5.6 RECOVERY 中の逆戻り
- 新しい 429 が短時間に来た場合は再度 `CRIT`
- これにより無理な即時復帰を避ける

---

## 6. 調整パラメータ（正本）
正本設定ファイル:
- `btcts_next/config/schema/exploration_runtime_def.yaml`

現行 bitFlyer 初期値:
```yaml
limits:
  window_300s: 500
  window_60s_ip: 500

control:
  target_utilization: 0.95
  warn_utilization: 0.95
  hard_cap_utilization: 0.98

  crit_floor_ratio: 0.50
  crit_trigger_429_count: 2
  crit_trigger_window_sec: 30
  crit_cooldown_sec: 60

  recovery_start_after_sec: 180
  recovery_step_count: 5
  recovery_step_interval_sec: 180
  recovery_policy: time_based
  recovery_curve: linear
  recovery_steps: []

request_priority:
  - board_snapshot
  - rest_trades

request_classes:
  board_snapshot:
    enabled: true
    weight: 1.0
    min_share: 0.50

  rest_trades:
    enabled: true
    weight: 0.8
    min_share: 0.30
```

---

## 7. 調整項目の意味
### 7.1 `target_utilization`
通常時の目標利用率。  
高くすると取得量は増えるが、429 リスクも増える。

### 7.2 `warn_utilization`
WARN 判定閾値。  
通常は target と同値から始めてよい。

### 7.3 `hard_cap_utilization`
論理的な上限。  
`active_target_ratio` がこれを超えないよう clamp する。

### 7.4 `crit_floor_ratio`
CRIT 時の floor。  
Collector を止めずにどこまで落とすかの下限。

### 7.5 `crit_trigger_429_count`
CRIT 入りに必要な 429 回数。  
現行初期値は 2。

### 7.6 `crit_trigger_window_sec`
429 反復を評価する時間窓。  
短くすると敏感、長くすると鈍感になる。

### 7.7 `crit_cooldown_sec`
CRIT で最低限維持する cooldown 時間。  
短くすると復帰が速いが再429しやすい。

### 7.8 `recovery_start_after_sec`
最後の 429 から RECOVERY を始めるまでの待機時間。

### 7.9 `recovery_step_count`
復帰段数。  
増やすと滑らか、減らすと速い。

### 7.10 `recovery_step_interval_sec`
各段の間隔。  
10分・15分・30分設計はこの値で調整する。

### 7.11 `recovery_curve`
現行は `linear`。  
将来 `custom_steps` を許容する future-proof slot。

### 7.12 `recovery_steps`
`custom_steps` 用の ratio 列。  
現時点は空配列が標準。

### 7.13 `request_priority`
request class の優先順。  
初期候補選択や enabled class の並びに使う。

### 7.14 `weight`
request class の配分重み。  
大きいほど share を取りやすい。

### 7.15 `min_share`
最低限守りたい share。  
片方に偏りすぎるのを防ぐ。

---

## 8. どの数値を触るべきか
### 8.1 取得量を増やしたい
主に触る:
- `target_utilization`
- `hard_cap_utilization`
- `weight`
- `min_share`

### 8.2 429 が多い
主に触る:
- `target_utilization` を下げる
- `crit_floor_ratio` を下げる
- `crit_cooldown_sec` を伸ばす
- `recovery_start_after_sec` を伸ばす
- `recovery_step_interval_sec` を伸ばす

### 8.3 復帰が遅すぎる
主に触る:
- `crit_cooldown_sec`
- `recovery_start_after_sec`
- `recovery_step_interval_sec`
- `recovery_step_count`

### 8.4 board_snapshot を優先したい
主に触る:
- `request_priority`
- `board_snapshot.weight`
- `board_snapshot.min_share`
- `rest_trades.weight`

### 8.5 rest_trades を厚くしたい
主に触る:
- `rest_trades.weight`
- `rest_trades.min_share`
- `board_snapshot.weight`

---

## 9. 観測と診断
### 9.1 正本 state
- `exploration_rate_state.json`
- `exploration_scheduler_state.json`

### 9.2 Health/UI で見る値
- `mode`
- `utilization`
- `active_target_ratio`
- `last_429_ts`
- `hold_until_ts`
- class別 request/success/fail/429

### 9.3 audit
- `collector_vnext.exploration.*.completed`
- `collector_vnext.exploration.*.failed`
- `collector_vnext.exploration.mode.changed`

### 9.4 正常状態の目安
- `mode = NORMAL`
- `active_target_ratio ~= 0.95`
- `utilization` は 0.80〜0.95 近辺
- `requests_300s` は budget を使い切り気味でも hard cap 未満
- `consecutive_failures = 0`

---

## 10. 起動と確認
### 10.1 推奨起動
```powershell
powershell -ExecutionPolicy Bypass -File .\tools\run_collector_vnext_exploration_daemon.ps1
```

### 10.2 直接起動
```powershell
$env:PYTHONPATH = "C:\BtcTradeSystem\btcts_next\src"
$env:BTC_TS_DATA_DIR = "D:\btc_ts_hot\data"
$env:BTC_TS_LOGS_DIR = "D:\btc_ts_hot\logs"
$env:BTCTS_STATE_ROOT = "D:\btc_ts_hot\state"

& "C:\BtcTradeSystem\.venv\Scripts\python.exe" -m btcts.collector_vnext.exploration_daemon
```

### 10.3 目視確認
- Health UI の `Exploration モード`
- `Util Ratio`
- `Last 429`
- `Hold Until`
- `Active Target Ratio`
- API continuity rail
- audit の completed/failed と mode.changed

---

## 11. 既知の Risk
1. 429 は取引所由来以外でも出る可能性がある  
   - proxy / network / 多重起動由来の偽陽性に注意。
2. 現状は info系 budget 中心  
   - order/cancel/shared IP を含む multi-budget domain は未実装。
3. request class は 2種のみ  
   - 将来の REST 拡張時に share 設計を再調整する必要がある。
4. API graph 本体はまだ完全正本時系列ではない  
   - 正本 overlay と audit 推定のハイブリッドで運用中。

---

## 付録A. 実運用 tuning の初手
bitFlyer 初期運用では以下を推奨する。
- `target_utilization = 0.95`
- `hard_cap_utilization = 0.98`
- `crit_floor_ratio = 0.50`
- `crit_trigger_429_count = 2`
- `crit_trigger_window_sec = 30`
- `crit_cooldown_sec = 60`
- `recovery_start_after_sec = 180`
- `recovery_step_count = 5`
- `recovery_step_interval_sec = 180`

この値は「本番でまず回し、観測しながら詰める」ための探索開始値である。
