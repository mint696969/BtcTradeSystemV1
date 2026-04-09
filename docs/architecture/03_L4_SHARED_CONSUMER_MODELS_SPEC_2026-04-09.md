# path: ./tmp/03_L4_SHARED_CONSUMER_MODELS_SPEC_2026-04-09.md
# desc: L4 Shared Consumer Models Spec (updated and de-duplicated)

更新日: 2026-04-09
位置づけ: 現行 mainline に合わせた L4 shared / consumer adapter 統合仕様
対象: `btcts_next/src/btcts/processing/l4_consumer_models/`, `btcts_next/src/btcts/apps/operator_ui/`, `btcts_next/src/btcts/market_engine/`

---

## 1. この仕様書の目的
本仕様書は、L4 を **second L3 にしない shared-first 層** として整理し、current implementation と今後の拡張余地を一箇所で読めるようにするための文書である。

ここでは次の 4 点だけを明確にする。

1. L4 は何の owner か
2. `market_summary` の current truth は何か
3. shared / adapter / bridge の責務はどこで切るか
4. 今後どの bundle を shared-first で増やすか

---

## 2. 結論
L4 は **shared-first の shape owner** である。

### L4 がやること
- L3 truth を consumer 利用向けの shared bundle に束ねる
- shared bundle を consumer 固有の thin adapter へ渡す
- 複数 consumer で再利用できる read model を育てる

### L4 がやらないこと
- 新しい market meaning を定義する
- trust / continuity / pressure / wall の owner になる
- UI wording を持つ
- page layout / CSS / refresh 秒数を持つ
- execution orchestration の owner になる

### 現状の一言
L4 は未展開ではない。2026-04-09 時点では、`market_summary` を中核に **最小 shared 実装が成立済み** の段階である。

---

## 3. 現行 L4 配置

### shared
- `btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py`

### operator_ui thin adapter
- `btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py`

### UI 側接続
- `btcts_next/src/btcts/apps/operator_ui/market_state_service.py`
- `btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py`

旧文書群にあった

- 「L4 package 未展開」
- 「market_summary は次フェーズで作る」
- 「operator_ui adapter は skeleton だけ」

という説明は、現行 mainline には合わない。

---

## 4. current L4 flow
現行の shared-first 経路は次である。

```text
market_state row
  ↓
L4 shared builder
  build_market_summary()
  ↓
L4 operator_ui thin adapter
  market_summary_widget_model()
  market_summary_status_payload()
  ↓
UI bridge
  market_state_bridge.py
  ↓
components / page
```

この経路は、

- L3 truth を直接 UI にばらまかず
- L4 shared で一度 bundle 化し
- adapter で consumer 都合の薄変換を行う

という shared-first の原則に沿っている。

---

## 5. `market_summary` shared bundle

## 5.1 current shared contract
`btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py` には、少なくとも次の実体がある。

- `MarketSummary`
- `MarketSummaryBuildInput`
- `build_market_summary()`

### 主な field 群
- identity / provenance
  - `summary_type`
  - `exchange`
  - `symbol_raw`
  - `market_uid`
  - `source_kind`
  - `source_series_id`
- time / freshness
  - `event_ts`
  - `age_sec`
  - `freshness`
  - `is_stale`
- interpretation core
  - `trust_state`
  - `continuity_state`
  - `interpretation_bucket`
  - `interpretation_reason`
- headline / summary
  - `market_state_label`
  - `participation_state`
  - `liquidity_bias`
  - `notable_events`
  - `alert_candidates`
- diagnostics
  - `diagnostics`

## 5.2 この bundle の意味
`market_summary` は、**市場状態の最小 shared summary** として既に成立している。
少なくとも operator UI での再利用に耐え、monitoring / replay / AI metadata へも伸ばしやすい形を持っている。

---

## 6. shared builder の責務
`build_market_summary()` がやるべきことは、shared shape の生成に限定する。

### やってよいこと
- source_kind の正規化
- event_ts / age_sec / freshness / is_stale の決定
- trust / continuity / interpretation 系 field の受け取り
- lightweight な notable / alert tag の付与
- diagnostics の引き継ぎ

### やってはいけないこと
- UI wording 生成
- CSS / layout / card 順の決定
- market meaning の再判定
- execution 用 heavy signal の生成
- widget library 依存 shape の生成

shared builder は、meaning owner ではなく **shared read model builder** として保つ。

---

## 7. thin adapter の責務

## 7.1 current 実体
`btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py` は current thin adapter である。

### current output
- `MarketSummaryWidgetModel`
- `market_summary_widget_model()`
- `market_summary_status_payload()`

## 7.2 adapter がやってよいこと
- field 名の consumer 向け変換
- `*_key` の付与
- placeholder fallback
- widget ごとの subset 切り出し
- status payload の flattening

## 7.3 adapter がやってはいけないこと
- 新しい market meaning の生成
- trust / continuity / interpretation の再判定
- CSS class / layout grid / refresh 秒数の埋め込み
- wording の最終決定

原則として adapter は **meaning-unaware / consumer-aware** に保つ。

---

## 8. bridge / service 側の位置づけ

### `market_state_service.py`
- `market_state` から最新 row を読む
- diagnostics を作る
- `build_market_summary()` へ入力を組む

### `market_state_bridge.py`
- shared bundle を読む
- thin adapter を通して UI 用 payload / widget model を返す
- UI 側 components と shared 経路をつなぐ

### 位置づけ
現時点では妥当である。
ただし bundle 種類が増えたら、bridge / service の責務を bundle ごとに整理する余地がある。

---

## 9. L4 の current limit
L4 は動いているが、全面完成ではない。

### 現在あるもの
- `market_summary` shared bundle
- operator_ui thin adapter
- UI bridge 経路

### まだ formal ではないもの
- `semantic_timeline_bundle`
- `health_digest`
- `liquidity_snapshot_bundle`
- prediction / decision 向け shared bundle
- execution signal 系 bundle

したがって、L4 は「未展開」ではなく、**`market_summary` を起点に拡張中**と表現するのが正しい。

---

## 10. Health と L4 の関係
2026-04-09 時点では、Health の主入力はまだ service 主導であり、L4 shared bundle に全面統一されてはいない。

### できていること
- Health は `market_state` の formal field を読める
- runtime observer として useful な可視化ができる

### まだ未完のこと
- Health 本体の主入力を L4 shared digest に寄せ切っていない
- `health_digest` という shared bundle はまだ formal ではない

### 方針
L4 側に Health digest を作る場合も、observer-only 原則を崩して meaning owner を増やしてはならない。

---

## 11. 次に増やす bundle 候補
current roadmap と Phase 2.5 の stop point を踏まえると、次段の L4 bundle 候補は次の順が自然である。

1. event usage contract を前提にした `semantic_timeline_bundle`
2. observer-only の `health_digest`
3. live wiring contract 固定後の `liquidity_snapshot_bundle`
4. prediction / decision contract を受ける shared bundle

ここで重要なのは、

- event usage contract 前に event-heavy bundle を増やさない
- live wiring contract 前に orderbook semantics bundle を厚くしない

ことである。

---

## 12. additive-first / compatibility
L4 shared は契約として育てる。

### ルール
- field は add を優先する
- rename / remove は deprecate を挟む
- breaking は shared でなく adapter 側で吸収する
- shared bundle は version を持てる設計を優先する

### 推奨 version field
- `bundle_version`
- `schema_version`
- `meaning_version`
- `producer_version`

---

## 13. shared に寄せる判断基準
次のどれかを満たすなら、まず shared を疑う。

- 2 consumer 以上で使う
- wording-free で再利用できる
- market truth を再定義せず shape だけ整えている
- timeline / digest / bundle として共有価値がある

逆に、次は shared に置かない。

- 文言
- 色
- CSS
- widget 固有の final input
- page 固有の並び順
- refresh 秒数

---

## 14. 一言
L4 は未展開ではない。
現在の mainline では `market_summary` を中核に shared-first の最小経路が既に成立している。

今後は、meaning を増やさず shape を育てること、そして contract-first で bundle を増やすことが正しい進み方である。
