# path: ./tmp/02_L3_MARKET_SEMANTICS_AND_EVENT_CONTRACT_SPEC_2026-04-09.md
# desc: L3 Market Semantics and Event Contract Spec (updated after orderbook semantics richer formal spec sync)

更新日: 2026-04-11
位置づけ: 現行 mainline に合わせた L3 正本仕様
対象: `btcts_next/src/btcts/processing/l3_market_semantics/`, `btcts_next/src/btcts/market_engine/`, `btcts_next/src/btcts/replay/`

---

## 1. この仕様書の目的
本仕様書は、L3 を **市場意味の唯一の owner** として固定したまま、2026-04-11 時点の current truth を次の 5 論点で整理するための文書である。

1. continuity / trust / interpretation の owner 境界
2. orderbook semantics の owner 境界
3. event usage の current implementation と contract rows 到達点
4. live runtime outward に出ている partial / additive contract の位置づけ
5. summary / family rows / active event rows の境界

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
- event family / usage guidance の意味分類

### L3 が owner ではないもの
- UI wording
- widget layout
- monitoring phrasing
- page-specific convenience logic
- execution orchestration
- AI wording / proposal phrasing

### 2026-04-11 時点の重要な更新
- event usage は **summary-level runtime outward** を超えて、**event-family contract rows outward** まで到達済み
- live orderbook semantics は **partial live outward** に加え、**active event contracts** が live `market_state` に到達済み
- `orderbook_semantics_summary` は、current row における summary slot の present 情報を `summary_slots_present` / `summary_slots_count` として保持できる段まで進んだ
- shared consumer は raw `market_state` 依存だけでなく、**contract-first bundle** まで前進済み
- immediate open は wiring missing ではなく、**richer formal spec の固定** と **bundle / digest 拡張判断** に移っている

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
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/liquidity_signals.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/signal_events.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/event_enrichment.py`
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/semantic_profile.py`

### event usage helper
- `btcts_next/src/btcts/processing/l3_market_semantics/event_usage_policy.py`

### microstructure / tradeflow / zone
- `btcts_next/src/btcts/processing/l3_market_semantics/microstructure/*`
- `btcts_next/src/btcts/processing/l3_market_semantics/tradeflow/*`
- `btcts_next/src/btcts/processing/l3_market_semantics/zone/*`

---

## 4. continuity / trust / interpretation
current live runtime で outward に最も安定して見えている L3 は、continuity / trust / interpretation 系である。

### live 側の代表接続
- `btcts_next/src/btcts/market_engine/runtime.py`
- `btcts_next/src/btcts/market_engine/market_state/projector.py`
- `btcts_next/src/btcts/market_engine/market_state/schema.py`

### 安定 outward field
- `trust_state`
- `boundary_reason`
- `continuity_state`
- `interpretation_bucket`
- `interpretation_reason`
- `interpretation_policy`

### 原則
これらは L3 owner が決める。
UI や adapter が後から bucket や trust を再判定してはならない。

---

## 5. event usage の current truth

## 5.1 L3 側にある helper
`btcts_next/src/btcts/processing/l3_market_semantics/event_usage_policy.py` には、少なくとも次がある。

- `resolve_event_family()`
- `resolve_usage_grade()`
- `build_event_usage_contract_rows()`
- `resolve_semantic_observer_status()`
- `build_event_usage_summary()`

これは、Health 側の独自 convenience summary ではなく、**L3 owner 側に usage summary と family-row helper がある** ことを意味する。

## 5.2 current reading は 3 層で読む
2026-04-11 時点では、下流が event usage / orderbook semantics の contract を読むとき、少なくとも次の 3 層を明確に分けるべきである。

1. `semantic_usage_summary`
   - aggregate observer summary
2. `semantic_usage_contract_rows`
   - event-family contract rows
3. `orderbook_active_event_contracts`
   - currently active event-level rows

重要なのは、この 3 つを同じ粒度のものとして混ぜないことである。

## 5.3 summary-level runtime outward
live `market_state` outward には、次が additive で追加済みである。

- `semantic_observer_status`
- `semantic_usage_summary`

配置:
- `btcts_next/src/btcts/market_engine/market_state/schema.py`
- `btcts_next/src/btcts/market_engine/market_state/projector.py`

### 位置づけ
これは **aggregate observer summary** であり、family rows や active event rows と同一ではない。

## 5.4 family-row outward
live `market_state` outward には、さらに次が追加済みである。

- `semantic_usage_contract_rows`

projector は L3 owner helper 由来の rows を current mainline で正規に載せる。
各 row の current baseline shape は次である。

- `contract_source`
- `interpretation_bucket`
- `event_family`
- `usage_grade`

### 位置づけ
これは **event-family 単位の contract rows** であり、summary の詳細化ではあるが、event-level row そのものではない。

## 5.5 正しい表現
したがって、2026-04-11 時点では次の表現が正しい。

- `event usage contract is unwired` ではない
- `summary wired only` でももう不十分である
- 正しくは **summary wired -> family-row outward reached -> event-level full formalization still open** である

---

## 6. usage guidance の current baseline
現在の helper 実装から読む限り、usage guidance の baseline は次の粒度で理解できる。

### interpretation_bucket = `allow_structural_use`
- `strong`
- structural use 可

### interpretation_bucket = `observe_only`
- `pressure` -> `watch_weak`
- `wall` / `pull` / `support_resistance` / `depth` / `spread` -> `watch`
- `sweep` / `absorption` -> `tentative`

### interpretation_bucket = `reanchor_required`
- `invalid`
- structural use 不可

### 重要な注意
これは **L3 owner 側にある現行 baseline** であって、まだ future full event contract fields すべてが runtime row に載った完成形ではない。

---

## 7. orderbook semantics の current truth

## 7.1 replay / audit 側
orderbook semantics は replay / audit 側では広く使われている。

### 代表経路
- `btcts_next/src/btcts/replay/replay_pipeline.py`
- `tools/run_l3_official_artifacts.py`

### 意味
- canonical orderbook を rebuild する
- liquidity payload を計算する
- signal events を発行する
- baseline / threshold / profile を replay / audit で検証する

### baseline 第一候補
- `wall_near_rank_threshold = 5`
- `wall_ratio_threshold = 0.30`

これは hard freeze ではなく、baseline 第一候補として維持されている。

## 7.2 live runtime 側の partial contract
`btcts_next/src/btcts/market_engine/market_state/live_orderbook_semantics.py` には、current BookState から partial outward summary を作る thin adapter がある。

### 代表 helper
- `to_orderbook_state()`
- `build_live_orderbook_signal()`
- `build_live_orderbook_transition_summary()`
- `build_live_orderbook_semantics_summary()`

### live outward field
- `orderbook_semantics_contract_status`
- `orderbook_semantics_summary`
- `orderbook_persistence_observable`

### summary 内の current shape
- `near_wall`
- `support`
- `resistance`
- `persistence`
- `summary_slots_present`
- `summary_slots_count`
- `active_event_names`
- `active_event_contracts`

## 7.3 summary slot presence の current formalization
2026-04-11 時点では、`orderbook_semantics_summary` 自体が **current row でどの summary slot が present か** を説明できる。

### current baseline shape
- `summary_slots_present`
  - `near_wall`
  - `support`
  - `resistance`
  - `persistence`
  のうち、current row で present な slot 名 list
- `summary_slots_count`
  - 上記 present slot 数

### 位置づけ
これは active event rows の代替ではない。
**summary slot presence** と **active event rows** は別粒度の contract である。

## 7.4 active event contracts reached
2026-04-11 時点では、`orderbook_semantics_summary.active_event_contracts` が live `market_state` に到達済みである。
current baseline shape は次である。

- `event_name`
- `event_family`
- `usage_grade`
- `side`

### 位置づけ
これは **currently active event-level rows** であり、`semantic_usage_contract_rows` の代替ではない。
family-level rows と active event-level rows は用途も粒度も異なる。

## 7.5 contract status の current reading
current live adapter は、summary slot が 0 件でも **live adapter が動いている限り `missing` ではなく `partial`** として扱う。

### current meaning
- `missing`
  - contract field 自体が live outward で見えていない、または上流から contract status が欠落している読み
- `partial`
  - adapter は live outward まで到達している
  - ただし current row の present summary slot は 0〜3 件でもよい
- `wired`
  - current row で `near_wall / support / resistance / persistence` の 4 slot が present

## 7.6 正しい表現
2026-04-11 時点では、次の表現が正しい。

- live orderbook semantics は **全面未固定** ではない
- `orderbook_semantics_contract_status=missing` は current live mainline の標準状態ではない
- 正しくは **partial live outward fixed / summary slot presence formalized / active event contracts reached / full parity and richer formal spec still open** である

---

## 8. `orderbook_persistence_observable` の意味
この field は current docs でも明文化しておくべき重要点である。

### 意味
- `False` は「persistence が起きていない」と同義ではない
- `False` は **比較可能な前状態がない** 可能性を含む

### 具体例
- series boundary 直後
- `prev_book_state=None`
- 比較不能な初回状態

つまり、`persistence absent` と `persistence not observable` は分けて読む必要がある。

---

## 9. market_state outward の current truth
`btcts_next/src/btcts/market_engine/market_state/schema.py` にある現行 field のうち、Phase 2.5 以降から current richer formal spec sync までの重要追加は次である。

### semantic summary fields
- `semantic_observer_status`
- `semantic_usage_summary`

### semantic family-row fields
- `semantic_usage_contract_rows`

### orderbook runtime fields
- `orderbook_semantics_contract_status`
- `orderbook_semantics_summary`
- `orderbook_persistence_observable`

### orderbook summary subfields
- `summary_slots_present`
- `summary_slots_count`
- `active_event_names`
- `active_event_contracts`

### current reading
これらは **additive field** として扱う。
既存 field を壊す breaking 変更ではなく、runtime contract を育てるための追加とみなす。

---

## 10. Health との関係
Health は L3 owner ではない。
しかし current mainline では、Health が L3 runtime observer としてかなり useful な段に達している。

### できていること
- `market_state` 側の formal field を優先して読む
- `semantic_usage_contract_rows` を優先し、欠ける場合のみ fallback rows を生成する
- `orderbook_semantics_summary.summary_slots_present` を優先し、欠ける場合のみ summary 内容から推論する
- explicit contract / inference を区別表示する
- source / freshness / observable を表示する
- active event contracts を observer-only に表示できる

### やってはいけないこと
- Health 側で event strength を再定義する
- page logic で near wall / support / resistance を再計算する
- L3 wiring gap を UI convenience で埋める

---

## 11. まだ未完のもの
current open は次のように粒度分解して読むのが適切である。

### event usage
- summary-level outward は接続済み
- family-row outward は到達済み
- event-level full formal contract は未完

### live orderbook semantics
- partial stable outward contract は固定済み
- summary slot presence は formalized 済み
- active event contracts は到達済み
- replay/live の完全 parity と richer formal spec の最終固定は未完

### consumer expansion
- shared L4 contract-first bundle には rows / active event contracts が届いている
- broader consumer expansion では、summary / family rows / summary slots / active event rows の境界を崩してはならない

---

## 12. 禁止事項
- UI / adapter で event usage strength を勝手に再定義する
- L4 で second L3 を作る
- live wiring gap を page convenience で埋める
- execution 側で meaning owner を再内包する
- AI proposal を L3 truth に昇格させる

---

## 13. 一言
L3 は市場意味の owner である。
2026-04-11 時点の mainline は、

- event usage summary は owner 側に寄った
- family-row outward は `semantic_usage_contract_rows` まで到達した
- live orderbook semantics は partial outward contract に加え active event contracts まで到達した
- summary slot presence は `summary_slots_present` / `summary_slots_count` として formalized された

という段階にある。

「何もつながっていない」でも「全部完成した」でもなく、**summary / family rows / summary slots / active event rows を分けて扱いながら contract boundary を固定する段階**として読むのが正しい。
