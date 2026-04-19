# path: ./archive/phase3_entry_first_open_framing_2026-04-15.md
# desc: Archived note, specification, report, or reference document.

# Phase 3 entry first-open framing

更新日: 2026-04-15
位置づけ: `./tmp/` 成果物 / Phase 2.5 closeout 後の Phase 3 entry framing

---

## 結論
Phase 2.5 closeout 後の次 mainline は、
**Phase 3 shared prediction contract entry**
として切るのが正しい。

ここで重要なのは、Phase 3 を

- event usage full completion phase
- Health v2 拡張 phase
- decision / tactic / execution phase

として始めないことである。

最初の 1 本目はあくまで、
**shared-first / evidence-first / horizon-separated な prediction contract の first slice**
に限定する。

---

## Phase 2.5 で close 寄りになったもの
### A. event usage
- `semantic_usage_summary`
- `semantic_usage_contract_rows`
- `orderbook_active_event_contracts`
- summary / family-row / active-event-row boundary
- event-level full contract は Phase 3 blocker ではなく carry-forward open

### B. runtime wiring
- `orderbook_semantics_contract_status`
- `orderbook_semantics_summary`
- `orderbook_persistence_observable`
  の minimal stable outward line
- projector responsibility wording の current truth
- `wiring gap` stale title の retirement

### C. Health observer
- `health_digest` current-state shared path reached
- grouped bundle reached
- Health v2 = runtime semantics observer only
- broader shared-first consumer adoption は未到達

### D. regression / cleanup
- stale risk cleanup
- open-register cleanup
- current focus / handoff / status / roadmap sync

---

## Phase 3 に持ち込むもの
### first-open として持ち込むもの
- shared prediction contract の first slice
- shared-first / wording-free / evidence-first な prediction shape
- L3 / L4 truth を入力として受ける contract-first bundle

### first slice 候補
- short horizon bias
- regime transition risk
- liquidity deterioration risk
- continuation likelihood
- mean-reversion likelihood
- caution level
- execution feasibility hint

### 設計条件
- L3 meaning owner を再定義しない
- L4 shared-first shape owner を崩さない
- prediction observer はまだ混ぜない
- decision / tactic / execution owner はまだ混ぜない
- Health に future prediction shape を逆流させない

---

## Phase 3 に持ち込まないもの
### immediate first-open に混ぜないもの
- prediction observer
- decision contract
- tactic contract
- label / target contract
- execution bundle
- event-level full contract broader completion
- Health grouped bundle の broader shared expansion

### 理由
これらを最初の 1 本目に混ぜると、
Phase 2.5 closeout の「何を閉じて、何を carry-forward にしたか」が再び濁るため。

---

## first-open の正しい framing
### 1. input
- `market_summary` を broader consumer anchor として使う
- 必要に応じて `health_digest` は observer / caution 補助入力として参照する
- direct raw L3 / UI convenience 読みを増やさない

### 2. contract shape
- shared-first
- wording-free
- additive-first
- horizon-separated
- evidence / provenance / confidence を持つ

### 3. non-goals
- prediction wording の UI 固定
- tactic recommendation の固定
- auto execution 連携
- prediction observer UI の本格導入

---

## next done definition
Phase 3 first-open の near-term done は次。

1. shared prediction contract の first slice が 1 本の shared bundle として切れている
2. input は `market_summary` anchor を優先している
3. Health / UI / decision / execution と責務混線していない
4. prediction observer / tactic / execution を混ぜていない
5. focused regression が green のまま進められる

---

## 一言
Phase 3 の最初の一手は、
**「いまある closeout 済みの truth を土台に、shared prediction contract の first slice だけを静かに切る」**
である。

ここで欲張って observer / decision / tactic / execution を混ぜないことが、最短で次の mainline を安定させる。
