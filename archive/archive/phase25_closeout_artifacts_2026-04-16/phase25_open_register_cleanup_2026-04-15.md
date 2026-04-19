# path: ./archive/archive/phase25_closeout_artifacts_2026-04-16/phase25_open_register_cleanup_2026-04-15.md
# desc: Archived note, specification, report, or reference document.

# Phase 2.5 open register cleanup

更新日: 2026-04-15
位置づけ: `./tmp/` 成果物 / Phase 3 entry 前 open-register cleanup note

---

## 結論
2026-04-15 時点の current truth では、Phase 2 / 2.5 周辺の immediate open は、
実装欠落の大穴ではなく **closeout wording / docs fixation / stale risk retirement / carry-forward judgement** に寄っている。

したがって、open set は次のように絞って読むのが正しい。

### current actual open
1. runtime wiring wording / projector responsibility fixation
2. Health grouped bundle / observer boundary wording fixation
3. event-level full contract の carry-forward judgement
4. stale risk / resolved bucket / open-register cleanup

### current non-open / superseded
- `L3_EVENT_USAGE_POLICY_NOT_WIRED_2026-04-06.md`
- `L3_RUNTIME_ORDERBOOK_SEMANTICS_WIRING_GAP_2026-04-06.md`
- hardcoded path 3本
- UI patch insertion / recursion risk

---

## 今回までで close 寄りに読めるもの
### runtime wiring
- `orderbook_semantics_contract_status`
- `orderbook_semantics_summary`
- `orderbook_persistence_observable`

の 3 top-level fields は mainline にある。

### event usage
- `semantic_usage_summary`
- `semantic_usage_contract_rows`
- family-row shape baseline の L3 owner 寄せ

まで到達済み。

### Health
- fragment-slot foundation reached
- current-state shared digest path reached
- observer-only current line reached

---

## current blocker ではないもの
### stale title risk
- `NOT WIRED`
- `WIRING GAP`

はいずれも current repo truth では immediate blocker title としては stale。

### resolved bucket
- logs / replay / research hardcoded path risks
- UI patch insertion / recursion risk

は current actual open から除外してよい。

---

## Phase 3 entry 前に維持したい判断
- Phase 2.5 を延命しながら field や helper を増やさない
- L3 / L4 / UI の owner boundary を壊さない
- broader formalization は carry-forward しつつ、immediate blocker と混ぜない
- merged spec は `./tmp/` 側で作り、`gpt_room` には current truth と handoff を残す

---

## 次の推奨
1. `docs/architecture/02` 差し替え後の current truth を前提に stale open をさらに絞る
2. Health observer closeout wording を最小で固める
3. Phase 3 entry 用の first open を `shared prediction contract` に限定する
