# path: ./tmp/00_ARCHITECTURE_REPLACEMENT_INDEX_2026-04-09.md
# desc: BTC-TS Architecture Replacement Index (updated after Phase 2.5 checkpoint)

更新日: 2026-04-09
位置づけ: `docs/architecture/` 差し替え用の統合インデックス
対象: `btcts_next/src/btcts/` 現行 mainline / Phase 2.5 第一到達点までの repo truth

---

## 1. この文書の目的
この文書は、`docs/architecture/` 配下の現行正本候補を、**2026-04-09 時点の repo 実装**に同期させるための入口である。

旧 2026-04-08 版の architecture 群は、方向性自体は正しいが、次の stale を含んでいた。

- event usage contract が runtime outward にまだ未接続、という表現が強すぎる
- live orderbook semantics wiring が全面未固定、という表現が強すぎる
- Health observer が未来形のまま残っている
- L4 / UI の実装済み部分と、未完部分の粒度が十分に分かれていない

本更新セットでは、実装事実を次の三段階で表現し直す。

1. **既に固定済みのもの**
2. **partial / summary-level で到達済みのもの**
3. **まだ full contract / full parity としては未完のもの**

---

## 2. 現時点の結論
`docs/architecture/` は、次の 6 文書で読むのが最も自然である。

1. `00_ARCHITECTURE_REPLACEMENT_INDEX_2026-04-09.md`
2. `01_L1_L2_CAPTURE_CANONICAL_RUNTIME_SPEC_2026-04-09.md`
3. `02_L3_MARKET_SEMANTICS_AND_EVENT_CONTRACT_SPEC_2026-04-14_MERGED.md`
4. `03_L4_SHARED_CONSUMER_MODELS_SPEC_2026-04-09.md`
5. `04_UI_HUB_OPERATOR_UI_SPEC_2026-04-09.md`
6. `05_SUPPORTING_POLICIES_AND_VERIFICATION_SPEC_2026-04-09.md`

この 6 本で、

- L1 / L2 capture-canonical runtime
- L3 meaning ownership
- L4 shared-first shaping
- UI hub / operator UI
- 補助ポリシー / verification

を、重複を減らしつつひと通り読めるようにした。

---

## 3. 現在の architecture 全体像

```text
L1 capture / lane operation / raw persistence
  owner: collector_vnext
  ↓
L2 canonical / structural truth
  owner: ingestion/l2_canonical
  ↓
L3 market meaning / continuity / trust / interpretation / orderbook semantics
  owner: processing/l3_market_semantics
  ↓
L4 shared read models / consumer adapters
  owner: processing/l4_consumer_models
  ↓
UI / Health / Warroom / Replay / Research
  owner: apps/operator_ui
```

### 固定したい読み方
- L1 は取り続ける層
- L2 は事実を整える層
- L3 は意味の唯一の owner
- L4 は shared-first の shape owner
- UI は表示と orchestration の owner

---

## 4. 2026-04-09 時点の current truth
今回の更新で最も重要なのは、**Phase 2.5 第一到達点までの repo truth を docs に反映すること**である。

### 既に固定済みのもの
- L3 event usage summary helper は `processing/l3_market_semantics/event_usage_policy.py` 側へ寄った
- live `market_state` outward には summary / observer 系 field が additive で追加済み
- live orderbook semantics には partial outward contract が入った
- Health は observer-only のまま、runtime wiring / source / freshness / observable を表示できる
- Phase 2.5 用テストバンドルは追加済みで、handoff 上は PASS 確認済み

### partial / summary-level で到達済みのもの
- `semantic_observer_status`
- `semantic_usage_summary`
- `orderbook_semantics_contract_status`
- `orderbook_semantics_summary`
- `orderbook_persistence_observable`

### まだ未完のもの
- event-level full contract
- live orderbook semantics full parity / full wiring
- Health UI 自動更新
- L4 shared bundle を Health 本体の主入力へ寄せ切る整理
- panel 文言の text layer 移管

---

## 5. current roadmap との整合
この更新セットは、current roadmap を次のように読む前提で書いている。

### 基本原則
- L3 = market meaning owner
- L4 = shared shape owner
- prediction / decision = shared contract
- execution = executor only
- Health = observer-only
- additive-first / adapter absorption / replay-first

### current stop point
- Phase 0 boundary lock は完了済み
- その後の実装は **Health-first roadmap の Phase 2.5 第一到達点** まで進んでいる

### 次の作業優先順
1. architecture docs を repo truth に同期する
2. Health UI 自動更新方針を設計する
3. panel 文言を text layer に寄せる
4. L4 側で Health digest をどう持つかを整理する
5. live orderbook semantics の full parity / full wiring を詰める

---

## 6. 旧 2026-04-08 版からの主な読み替え

### 旧表現
- event usage contract は未接続
- live orderbook semantics wiring は未固定
- Health observer は次フェーズで入れる

### 新表現
- event usage は **event-level full contract は未完だが、summary-level runtime outward は接続済み**
- live orderbook semantics は **full parity は未完だが、partial stable outward contract は固定済み**
- Health は **observer-only として既に導入済み**

この粒度差を明示することが、今回の docs 更新の核心である。

---

## 7. 文書ごとの役割

### `01_L1_L2_CAPTURE_CANONICAL_RUNTIME_SPEC_2026-04-09.md`
- L1 / L2 の責務と runtime 主系を説明する
- collector_vnext と ingestion/l2_canonical の境界を説明する
- L3 以降の意味論は持ち込まない

### `02_L3_MARKET_SEMANTICS_AND_EVENT_CONTRACT_SPEC_2026-04-14_MERGED.md`
- L3 owner 境界を固定する
- continuity / trust / interpretation / orderbook semantics を整理する
- event usage summary / family-row / active-event-row の current truth と runtime outward partial contract の現況を説明する

### `03_L4_SHARED_CONSUMER_MODELS_SPEC_2026-04-09.md`
- L4 shared-first の current implementation を説明する
- `market_summary` を current canonical bundle として扱う
- future bundle を shared-first で整理する

### `04_UI_HUB_OPERATOR_UI_SPEC_2026-04-09.md`
- UI が meaning owner に戻らない境界を固定する
- Health observer 実装の current truth を説明する
- bridge / service / presenter / widget / view の責務を整理する

### `05_SUPPORTING_POLICIES_AND_VERIFICATION_SPEC_2026-04-09.md`
- additive-first / compatibility / AI / path policy / lightweight verification をまとめる
- open issue を partial-complete 前提で粒度分解する

---

## 8. 差し替えの考え方
この更新セットを本採用する場合は、旧 `docs/architecture/` mainline を次の方針で差し替えるのが望ましい。

### 推奨
- stale な 2026-04-08 版は archive / history 扱いへ寄せる
- mainline には current truth を反映した 2026-04-09 版を残す

### 理由
- stale docs を mainline に併置すると、人間と GPT の両方が current truth を見誤るため
- 今回の差分は wording 調整ではなく、Phase 2.5 到達点の反映だから

---

## 9. 一言
今回の docs 更新で最も重要なのは、

- できていないことを過小評価しない
- できていることを過小表現しない
- partial 到達と full completion を混同しない

の 3 点である。

2026-04-09 時点の mainline は、L3 / Health / market_state outward について **明確に前進している**。それを architecture 正本へ正直に反映するのが、この更新セットの目的である。
