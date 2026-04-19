# path: ./archive/phase25_event_level_contract_carry_forward_judgement_2026-04-15.md
# desc: Archived note, specification, report, or reference document.

# Phase 2.5 event-level full contract carry-forward judgement

更新日: 2026-04-15
位置づけ: `./tmp/` 成果物 / Phase 3 entry 前 carry-forward judgement note

---

## 結論
2026-04-15 時点の current repo truth では、event usage / orderbook semantics の event-level full contract は
**未配線の immediate blocker** ではなく、
**summary-first / family-row / active-event-row boundary を維持したまま Phase 3 以後へ carry-forward してよい open**
と読むのが正しい。

---

## すでに reached しているもの
### summary level
- `semantic_usage_summary`
- `semantic_observer_status`

### family-row level
- `semantic_usage_contract_rows`
- family-row shape baseline の L3 owner helper 寄せ

### active-event-row level
- `orderbook_semantics_summary.active_event_count`
- `orderbook_semantics_summary.active_event_names`
- `orderbook_semantics_summary.active_event_contracts`

### observer / consumer adoption
- Health observer は summary-first / observer-only line でこれらを観測できる
- shared L4 / operator_ui line でも summary / family rows / active event rows の境界を保った利用が reached している

---

## まだ open のもの
### event-level full contract broader formalization
- event row を cross-consumer contract としてどこまで固定するか
- consumer-facing wording をどこまで共通化するか
- prediction / decision / tactic / execution 側でどの粒度を first-class contract にするか
- active event rows を timeline / bundle / observer にどこまで昇格するか

### 重要な読み方
これらは「いま市場意味が読めない」「runtime wiring が足りない」という意味ではない。
**broader formal completion の open** であって、Phase 2.5 immediate blocker ではない。

---

## Phase 3 blocker ではない理由
1. summary-level は既に mainline にある
2. family-row level も `semantic_usage_contract_rows` として outward にある
3. active-event-row level も `active_event_contracts` まで reached している
4. Health / shared L4 / operator_ui が observer-only / contract-first でこれらを読める
5. 現在の immediate open は wiring 欠落ではなく wording / carry-forward judgement / broader formalization に寄っている

したがって、event-level full contract を今このスレッドで全部 fixed しないと Phase 3 に進めない、とは読まない方が current truth に近い。

---

## 固定したい境界
### 1. `semantic_usage_summary`
aggregate observer summary。

### 2. `semantic_usage_contract_rows`
event-family contract rows。

### 3. `orderbook_active_event_contracts`
currently active event-level rows。

### 4. やってはいけないこと
- 1 / 2 / 3 を同一視する
- family rows を active event rows の代替として扱う
- active event rows を broader future contract の完成形と誤認する
- UI convenience で境界を曖昧にする

---

## current closeout reading
Phase 2.5 closeout bundle A の done reading は、次で十分である。

- `not wired` 読みは retired / superseded
- summary / family-row / active-event-row boundary は固定済み
- event-level full contract は Phase 3 blocker ではなく carry-forward open として明示済み
- 必要なら Phase 3 以後の consumer need に応じて最小 formalization を切る

---

## 次の推奨
1. status / handoff / focus に「Phase 3 blocker ではない carry-forward open」の読みを反映する
2. new helper / new bundle を先食いしない
3. Phase 3 では `shared prediction contract` の first slice を先に切り、event-level full contract の broader completion は consumer need に応じて進める
