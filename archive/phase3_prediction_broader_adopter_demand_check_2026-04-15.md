# path: ./archive/phase3_prediction_broader_adopter_demand_check_2026-04-15.md
# desc: Archived note, specification, report, or reference document.

# Phase 3 prediction broader adopter demand check

更新日: 2026-04-15
位置づけ: `./tmp/` 成果物 / PredictionSummary broader adopter demand check

---

## 結論
2026-04-15 時点の repo truth では、`PredictionSummary` の broader adopter rollout を急ぐ需要はまだ弱い。

current reading として最も安全なのは次。
- first adopter は `ai_reasoning_panel` snapshot で十分
- `risk_monitor_panel` / `warroom_header` はまだ `PredictionSummary` 必須ではない
- immediate next step は panel 横展開ではなく、first slice minimality の維持

---

## 現物確認した候補
### 1. `risk_monitor_panel.py`
現行の関心は次に集中している。
- spread
- imbalance / delta conflict
- wall_ratio
- audit latency
- current `market_summary` caption

### 読み
ここは operational risk monitor であり、prediction first slice がないと成立しない構造ではない。
むしろ `PredictionSummary` を入れると、risk score と prediction hint の owner 境界が曖昧になりやすい。

### 判断
- immediate adopter need: 弱い
- 追加するなら将来の caution-only caption 程度だが、今は不要

---

### 2. `warroom_header.py`
現行の関心は次に集中している。
- regime
- spread state
- pressure
- trade flow
- ai decision (lightweight)
- risk label
- current `market_summary` caption

### 読み
ここは war room の冒頭 summary であり、既存の lightweight signal + summary caption で十分に機能している。
`PredictionSummary` をここへ即投入すると、header が first slice を代表する場所に見えやすく、narrow rollout の方針とズレる。

### 判断
- immediate adopter need: 弱い
- 追加するなら将来の optional one-line hint 程度だが、今は不要

---

## current safe line
### keep
- `ai_reasoning_panel` snapshot 補助表示
- `PredictionSummary` shared / adapter / state / bridge の thin line

### hold
- `risk_monitor_panel`
- `warroom_header`
- other panels

### reason
- actual missing need が repo 現物からまだ見えない
- rollout を急ぐと helper / adapter / presenter が先回りで増えやすい
- first slice の minimality と boundary hold を優先した方が安全

---

## 次の推奨
1. broader adopter はいったん増やさない
2. `PredictionSummary` evidence / diagnostics を最小のまま維持する
3. actual demand が見えたら、その consumer 専用 thin state / adapter を 1 本だけ切る

---

## 一言
今は `PredictionSummary` を広く見せる段ではない。
**repo truth 上で need が見えている narrow first adopter だけに留める** のが正しい。
