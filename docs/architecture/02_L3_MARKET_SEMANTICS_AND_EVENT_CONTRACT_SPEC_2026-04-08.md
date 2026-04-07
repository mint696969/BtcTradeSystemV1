# path: ./docs/architecture/02_L3_MARKET_SEMANTICS_AND_EVENT_CONTRACT_SPEC_2026-04-08.md
# desc: L3 Market Semantics and Event Contract Spec

更新日: 2026-04-08
位置づけ: 現行 mainline に合わせた L3 正本仕様
対象: `btcts_next/src/btcts/processing/l3_market_semantics/`, `btcts_next/src/btcts/replay/`, `btcts_next/src/btcts/market_engine/`

---

## 1. この仕様書の目的
本仕様書は、L3 を「市場意味の唯一の owner」として固定しつつ、current roadmap の先頭論点である **event usage contract** を含めて現況を整理するための仕様である。

目的は次の5つ。

1. L3 の owner 境界を明文化する
2. continuity / trust / interpretation と orderbook semantics の関係を整理する
3. replay 側と live 側の接続差を説明する
4. event usage contract の formalization 入口を作る
5. 下流が勝手に event 強度を再解釈しない前提を固定する

---

## 2. 結論
L3 は、**市場意味の唯一の正本層**である。

### L3 が owner であるもの
- continuity semantics
- trust semantics
- interpretation semantics
- orderbook semantics
- microstructure semantics
- zone shaping
- event の意味分類

### L3 が owner ではないもの
- UI wording
- widget layout
- monitoring phrasing
- execution orchestration
- AI proposal wording

さらに current phase では、次を明示する。

- replay / audit scope では L3 closeout 到達とみなしてよい
- ただし event usage contract は formal spec / outward wiring が未固定
- live orderbook semantics full wiring は未固定

---

## 3. 現行 L3 配置
L3 の正規 ownership は `processing/l3_market_semantics/` にある。

### continuity
- `btcts_next/src/btcts/processing/l3_market_semantics/continuity/interpretation_engine.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/continuity/orderbook_engine.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/continuity/series_engine.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/continuity/trust_engine.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/continuity/models/*`

### orderbook semantics
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/liquidity_pipeline.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/liquidity_signals.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/signal_events.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/event_enrichment.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/semantic_profile.py`

### microstructure / tradeflow / zone
- `btcts_next/src/btcts/processing/l3_market_semantics/microstructure/*`
- `btcts_next/src/btcts/processing/l3_market_semantics/tradeflow/*`
- `btcts_next/src/btcts/processing/l3_market_semantics/zone/*`

---

## 4. continuity / trust / interpretation
current live runtime で outward に安定して見えている L3 は、主に continuity / trust / interpretation である。

### live 側の代表接続
- `btcts_next/src/btcts/market_engine/runtime.py`
- `btcts_next/src/btcts/market_engine/market_state/projector.py`
- `btcts_next/src/btcts/market_engine/market_state/schema.py`

### 現行 outward field
- `trust_state`
- `boundary_reason`
- `continuity_state`
- `interpretation_bucket`
- `interpretation_reason`
- `interpretation_policy`

### 原則
continuity / trust / interpretation は L3 owner が決める。
UI や adapter が後から勝手に bucket を上書きしない。

---

## 5. orderbook semantics
orderbook semantics は replay / audit 側で広く使われている。

### replay 側代表接続
- `btcts_next/src/btcts/replay/replay_pipeline.py`

### current replay path の意味
- canonical orderbook を rebuild する
- liquidity payload を計算する
- signal events を発行する
- baseline / threshold / profile を replay / audit で検証する

### 代表 event
- `pressure_shift`
- `wall_created`
- `wall_removed`
- `near_wall_created`
- `near_wall_continued`
- `support_candidate`
- `resistance_candidate`
- `absorption_candidate`
- `sweep_candidate`

### baseline 現況
- `wall_near_rank_threshold = 5`
- `wall_ratio_threshold = 0.30`

これは hard freeze ではなく、**baseline 第一候補**である。

---

## 6. profileization
threshold / sensitivity は meaning owner と切り分けて扱う。

### 固定するもの
- meaning owner
- semantic category
- continuity / interpretation の責務境界

### 可変にするもの
- threshold
- venue baseline
- regime overlay
- adaptive overlay
- experiment overlay

### 現行入口
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/semantic_profile.py`
- `btcts_next/src/btcts/market_engine/profiles/base.py`
- `btcts_next/src/btcts/market_engine/profiles/bitflyer.py`

原則として、**意味は L3 に固定し、可変にするのは threshold / policy 側に限定する。**

---

## 7. replay と live の接続差

## 7.1 replay でできていること
- L2 canonical から rebuild できる
- liquidity payload を計算できる
- signal event を組める
- audit / official artifact を生成できる

## 7.2 live で outward に見えているもの
- trust / continuity / interpretation 中心
- top book / near zone / imbalance summary

## 7.3 live で未固定のもの
- near wall / support / resistance / persistence の outward stable contract
- event bundle の stable outward schema
- replay/live parity をどこまで求めるかの固定

したがって、**replay で意味 owner が成立していること**と、**live でそのまま outward に出ていること**は同義ではない。

---

## 8. event usage contract

## 8.1 現状
event usage の考え方は整理済みだが、formal spec / runtime outward contract にはまだ乗っていない。

### 現行の確認できる根拠
- continuity interpretation bucket は runtime 実装済み
- `tools/test_l3_event_usage_audit.py` に draft policy がある
- `signal_events.py` / `event_enrichment.py` の event 自体には usage field がまだない
- `market_state/schema.py` に usage field はまだない

## 8.2 問題
このまま consumer を先に作ると、下流が

- `observe_only` を strong に扱う
- 逆に watch-only の価値まで捨てる
- UI 側で event の強度を独自評価する

という drift を起こしやすい。

## 8.3 formalization で固定したい最小 field
current roadmap に沿う最小案として、event contract では次の概念を持てる形を推奨する。

- `event_name`
- `event_family`
- `meaning_version`
- `confidence`
- `trust_bucket`
- `consumer_allowed`
- `actionability`
- `forecast_horizon_hint`
- `half_life`
- `invalidates_on`
- `evidence_refs`

## 8.4 現段階の推奨
実装に先行して、少なくとも **文書レベルで usage contract を固定**する。
その後に additive-first で runtime / replay / shared bundle へ接続する。

---

## 9. event family の考え方
minimum family としては、次のように整理するのが自然である。

- `pressure`
- `wall`
- `pull`
- `sweep`
- `absorption`
- `support_resistance`
- `continuity`
- `trust`
- `interpretation`

重要なのは、**event_name の羅列より family と usage guidance を先に固定する**ことである。

---

## 10. usage guidance の初期案
現時点で方向性が妥当とみなせる draft は次である。

### interpretation_bucket = `allow_structural_use`
- strong
- structural use 可
- downstream shared bundles の根拠に使ってよい

### interpretation_bucket = `observe_only`
- pressure: watch_weak
- wall / pull: watch
- sweep / absorption: tentative
- structure change や execution 決定の owner 根拠にはしない

### interpretation_bucket = `reanchor_required`
- invalid
- structural use 不可
- replay/live consumer は再アンカーを要求する

この draft は、現時点では **正式実装値**ではなく、**formalization 対象の初期基準**として扱う。

---

## 11. official artifact policy
L3 の official artifact は live outward 常時出力ではなく、現時点では replay / audit 再計算成果物を正本とする。

### 正式入口
- `tools/run_l3_official_artifacts.py`

### 意味
- collector canonical data を正本入力にする
- L3 meaning は replay / audit で再計算する
- closeout / baseline / policy の議論はこの artifact を根拠に進める

これは live wiring gap を UI convenience で埋めないための重要方針でもある。

---

## 12. 禁止事項
- UI / adapter で event usage 強度を勝手に再定義する
- L4 shared bundle で second L3 を作る
- live wiring gap を page convenience で埋める
- execution 側で meaning owner を再内包する
- AI proposal をそのまま L3 truth に昇格させる

---

## 13. 次段の推奨順序
1. event usage contract 文書固定
2. Health v1 semantic observer 導入
3. live orderbook semantics runtime wiring contract 固定
4. Health v2 runtime observer
5. prediction / decision contract へ進む

この順序を守ることで、consumer を急いで増やして責務が逆流する事故を防げる。

---

## 14. 一言
L3 は市場意味の owner である。
現在の mainline では replay / audit でその owner 性はかなり固まっているが、event usage contract と live orderbook semantics wiring は次に正式化すべき論点である。
