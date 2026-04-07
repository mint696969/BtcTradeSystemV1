# path: ./docs/architecture/05_SUPPORTING_POLICIES_AND_VERIFICATION_SPEC_2026-04-08.md
# desc: Supporting Policies and Verification Spec

更新日: 2026-04-08
位置づけ: architecture 補助ポリシー統合仕様
対象: `docs/architecture/` 補助正本

---

## 1. この仕様書の目的
本仕様書は、旧 architecture 文書群に分散していた補助ポリシーを、mainline 用に読みやすく統合するための仕様である。

統合対象の代表は次。

- L2/L3 lightweight verification
- L3/L4 evolution and compatibility policy
- AI architecture の高位方針
- data architecture の高位方針
- path / output / operational data の architecture 観点

これらは個別の詳細仕様ではなく、**レイヤ設計を支える不変ルール**として読む。

---

## 2. lightweight verification

## 2.1 何を確認するか
L2/L3 分離が mainline で壊れていないことを、次の4観点で確認する。

1. ownership
2. import
3. runtime
4. legacy isolation

## 2.2 合格条件の要約
### ownership
- L2 ownership が `ingestion/l2_canonical/` にある
- L3 ownership が `processing/l3_market_semantics/` にある

### import
- `collector_vnext/` から L3 への direct import がない
- `ingestion/` から `processing/` への逆流 import がない
- `apps/operator_ui/` が `ingestion` を直接使って meaning を作らない

### runtime
- live restart / daemon rollover / ws recovery / raw-canonical continuity が成立する

### legacy isolation
- active path が legacy mainline に戻っていない
- archive と current mainline が分かれている

## 2.3 現在の読み方
lightweight verification は、**L3/L4 が全部完成している証明**ではない。

確認するのはあくまで、
- ownership が逆流していないか
- mainline runtime が新構造の上で成立しているか

である。

---

## 3. compatibility / additive-first policy

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

### 軽い
- adapter / presenter / widget change

## 3.3 AI の位置づけ
AI は提案者になれても、L3 meaning の owner にはならない。

### AI がやること
- 観測
- 仮説生成
- 提案
- 誤差発見

### AI がやらないこと
- 正本 meaning の無審査上書き
- 仕様なき semantic 変更

---

## 4. data / path policy

## 4.1 現実運用の原則
運用データの正本は repo 外 path を優先する。
repo 内は fallback / template として扱う。

### architecture 的な意味
- runtime は path 外出し前提で設計する
- collector / market_engine / UI は repo 内固定 path へ依存しすぎない
- ENV / resolver / path service で吸収する

## 4.2 data philosophy
高位方針としては次を維持する。

- Record Everything
- Replay Anything
- Learn Continuously

ただし現行 mainline は、旧 `DATA_ARCHITECTURE.md` のような将来データ基盤全体をまだフル実装しているわけではない。
したがって data architecture は **現況説明より将来方針として読む** のが正しい。

---

## 5. AI architecture policy

## 5.1 高位方針
AI は operator の相棒であり、戦略的協働者である。

### ただし architecture 上の固定
- AI は proposal / analysis / learning support に置く
- AI は market truth owner ではない
- AI は execution owner ではない
- AI 都合で L3/L4 境界を壊さない

## 5.2 current roadmap との整合
prediction / decision を shared contract とする current roadmap と整合させるなら、AI は

- contract consumer
- candidate scorer
- learning consumer
- retrospective analyst

として置くのが自然である。

---

## 6. current architecture open
architecture 観点で current open として扱うべき論点は、主に次の2件である。

### 6.1 event usage contract not wired
- policy の考え方はある
- formal spec / runtime outward / shared bundle 接続が未固定

### 6.2 live orderbook semantics wiring gap
- replay 側 owner は成立
- live outward stable contract が未固定
- UI convenience で埋めてはならない

この2件を current blocker として管理し、これ以外の stale path drift や naming residue は副次扱いに留める。

---

## 7. document maintenance policy
`docs/architecture/` は stale 文書を残すと GPT / 人間の両方を混乱させる。

### maintenance rule
- 現行 repo とズレた architecture 文書は mainline から外す
- 「当時の設計メモ」は archive か history 相当へ寄せる
- current mainline には current canonical だけを置く

### 含意
- `tmp/tmp/...` 参照の残りは削除または更新する
- 「未展開」と書いてあるが既に実装済み、のような stale は放置しない

---

## 8. 推奨 review checklist
architecture 更新時は毎回次を確認する。

### 8.1 current repo truth
- 本当に mainline 実装に即しているか
- stale な未来形 / 過去形が混ざっていないか

### 8.2 ownership boundary
- L1/L2/L3/L4/UI の owner 境界が曖昧になっていないか

### 8.3 roadmap sync
- `gpt_room` の current roadmap / handoff / status と矛盾していないか

### 8.4 delete discipline
- 置き換え済みの stale 文書を mainline に残していないか

---

## 9. 一言
verification・compatibility・AI・data は補助論点だが、どれも ownership 境界を支える重要ルールである。
mainline の architecture では、個別設計より前にこの補助ポリシーを壊さないことが大前提になる。
