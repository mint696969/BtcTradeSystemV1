# path: ./tmp/05_SUPPORTING_POLICIES_AND_VERIFICATION_SPEC_2026-04-09.md
# desc: Supporting Policies and Verification Spec (updated after Phase 2.5 checkpoint)

更新日: 2026-04-09
位置づけ: architecture 補助ポリシー統合仕様
対象: `docs/architecture/` 補助正本

---

## 1. この仕様書の目的
本仕様書は、layered design を支える補助ポリシーを current repo truth に合わせて統合するための文書である。

ここで固定したいのは、個別実装の詳細ではなく次の不変ルールである。

- lightweight verification
- additive-first / compatibility policy
- AI architecture policy
- data / path policy
- current architecture open の正しい粒度

---

## 2. lightweight verification

## 2.1 何を確認するか
L1 / L2 / L3 / L4 / UI の責務分離が mainline で壊れていないことを、次の 4 観点で確認する。

1. ownership
2. import
3. runtime
4. legacy isolation

## 2.2 合格条件の要約
### ownership
- L1 運転主系が `collector_vnext/` にある
- L2 ownership が `ingestion/l2_canonical/` にある
- L3 ownership が `processing/l3_market_semantics/` にある
- L4 shared owner が `processing/l4_consumer_models/` にある
- UI が `apps/operator_ui/` に分かれている

### import
- `collector_vnext/` から L3 への direct import がない
- `ingestion/` から `processing/` への逆流 import がない
- `apps/operator_ui/` が `ingestion` を直接使って meaning を作らない

### runtime
- live restart / daemon rollover / ws recovery / raw-canonical continuity が成立する
- current mainline 上で market_state outward が動いている

### legacy isolation
- active path が legacy mainline に戻っていない
- archive と current mainline が分かれている

## 2.3 現在の読み方
lightweight verification は、L3/L4 が全面完成している証明ではない。
確認するのはあくまで、

- ownership が逆流していないか
- runtime が新構造の上で成立しているか
- current stop point で partial completion を正しく保てているか

である。

---

## 3. additive-first / compatibility policy

## 3.1 原則
L3 と L4 は進化するが、破壊的に揺らしてはならない。

### ルール
- add を優先する
- deprecate を挟んで remove する
- version field を持てる形を優先する
- breaking は shared より adapter 側で吸収する

## 3.2 変更の重さ
### 最も重い
- L3 meaning change

### 中程度
- L4 shared bundle change
- market_state outward contract change

### 軽い
- adapter / presenter / widget change
- UI text / layout / style change

## 3.3 2026-04-09 時点での適用例
今回の Phase 2.5 では、次の追加が **additive-first の正しい例** である。

- `semantic_observer_status`
- `semantic_usage_summary`
- `orderbook_semantics_contract_status`
- `orderbook_semantics_summary`
- `orderbook_persistence_observable`

これは既存 row を壊す rename / remove ではなく、runtime outward contract を育てる追加として扱う。

---

## 4. AI architecture policy

## 4.1 高位方針
AI は operator の相棒であり、提案者・分析者・学習支援者である。

### ただし固定
- AI は proposal / analysis / learning support に置く
- AI は market truth owner ではない
- AI は execution owner ではない
- AI 都合で L3 / L4 / UI 境界を壊さない

## 4.2 current roadmap との整合
prediction / decision を shared contract とする current roadmap と整合させるなら、AI は

- contract consumer
- candidate scorer
- learning consumer
- retrospective analyst

として置くのが自然である。

---

## 5. data / path policy

## 5.1 現実運用の原則
運用データの正本は repo 外 path を優先する。
repo 内は fallback / template として扱う。

### architecture 的な意味
- runtime は path 外出し前提で設計する
- collector / market_engine / UI は repo 内固定 path に依存しすぎない
- ENV / resolver / path service で吸収する

## 5.2 data philosophy
高位方針としては次を維持する。

- Record Everything
- Replay Anything
- Learn Continuously

ただし current mainline は、将来データ基盤全体をまだフル実装しているわけではない。
したがって data architecture は、現況説明より **高位方針** として読むのが正しい。

---

## 6. current architecture open
2026-04-09 時点の open は、「全部未接続」という粗い表現ではなく、次の粒度で読むべきである。

## 6.1 event usage contract
### 到達済み
- L3 owner 側に usage summary helper がある
- runtime outward の summary-level wiring は済んでいる

### 未完
- event-level full contract
- shared bundle 化
- downstream consumer contract の formal completion

### 正しい表現
- `summary wired / event-level full contract unfinished`

## 6.2 live orderbook semantics
### 到達済み
- live adapter がある
- partial stable outward contract は固定済み
- `orderbook_persistence_observable` により observer quality は向上済み

### 未完
- full parity / full wiring
- replay/live final contract の固定

### 正しい表現
- `partial stable outward fixed / full parity unfinished`

## 6.3 UI / Health
### 到達済み
- observer-only の Health 可視化は入っている
- explicit contract / inference を区別できる

### 未完
- UI 自動更新
- L4 shared digest への本体統一
- text layer 移管の完了

---

## 7. verification entry points
2026-04-09 時点で、Phase 2.5 文脈で重要な確認入口は次である。

### repo 側
- `tools/test_phase25_health_bundle.ps1`
- `tools/run_market_engine_runtime_smoke.py`

### gpt_room / runbook 側
- `tmp/gpt_room/reference/runbook/TEST_PHASE25_HEALTH_BUNDLE.ps1`

### 位置づけ
- `test_phase25_health_bundle.ps1` は Phase 2.5 の最小 contract / observer / UI bridge の確認入口
- runtime smoke は live market_state 書き込みの補助確認入口

---

## 8. document maintenance policy
`docs/architecture/` は stale 文書を残すと、人間と GPT の両方が current truth を誤読する。

### maintenance rule
- 現行 repo とズレた architecture 文書は mainline から外す
- 当時のメモは archive / history 相当へ寄せる
- current mainline には current canonical だけを置く

### 含意
- 「未接続」と書き切っているが実装済み、のような stale を放置しない
- partial completion を full completion と混同しない
- full completion を partial completion と過小表現しない

---

## 9. 推奨 review checklist
architecture 更新時は毎回次を確認する。

### 9.1 current repo truth
- 本当に mainline 実装に即しているか
- stale な未来形 / 過去形が混ざっていないか

### 9.2 ownership boundary
- L1/L2/L3/L4/UI の owner 境界が曖昧になっていないか

### 9.3 roadmap sync
- `gpt_room` の current roadmap / handoff / status と矛盾していないか

### 9.4 delete discipline
- 置き換え済みの stale 文書を mainline に残していないか

---

## 10. 一言
verification・compatibility・AI・data は補助論点だが、どれも ownership 境界を支える重要ルールである。
2026-04-09 時点の architecture では、

- summary-level completion と full completion を分けて書くこと
- observer-only 原則を崩さないこと
- additive-first で contract を育てること

が大前提になる。
