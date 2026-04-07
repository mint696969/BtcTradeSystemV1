# path: ./docs/architecture/03_L4_SHARED_CONSUMER_MODELS_SPEC_2026-04-08.md
# desc: L4 Shared Consumer Models Spec

更新日: 2026-04-08
位置づけ: 現行 mainline に合わせた L4 shared / consumer adapter 統合仕様
対象: `btcts_next/src/btcts/processing/l4_consumer_models/`, `btcts_next/src/btcts/apps/operator_ui/`, `btcts_next/src/btcts/market_engine/`

---

## 1. この仕様書の目的
本仕様書は、旧 `L4_SHARED_FIRST_DESIGN_SPEC`, `L4_MARKET_SUMMARY_FIELD_SPEC`, `L4_MARKET_SUMMARY_BUILDER_SKELETON_SPEC`, `L4_OPERATOR_UI_ADAPTER_SPEC`, `L4_PACKAGE_SKELETON_IMPLEMENTATION_PLAN`, `L4_SHARED_FIRST_MIGRATION_CHECKLIST` を、現行実装に合わせて統合したものである。

目的は次の5つ。

1. L4 を second L3 にしない境界を固定する
2. shared / adapter の責務を一箇所で読めるようにする
3. `market_summary` の current implementation を正本として説明する
4. 旧文書の stale な「未展開」記述を除去する
5. 次に拡張すべき bundle を明示する

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
- CSS / layout を持つ
- execution orchestration を持つ

現在の mainline では、L4 は「未展開」ではなく、**最小 shared 実装が既に存在する段階**である。

---

## 3. 現行 L4 配置

### shared
- `btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py`

### operator_ui thin adapter
- `btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py`

### UI bridge / service 接続
- `btcts_next/src/btcts/apps/operator_ui/market_state_service.py`
- `btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py`

したがって、旧文書群にあった

- 「L4 package 未展開」
- 「market_summary は次フェーズで作る」
- 「operator_ui adapter は skeleton だけ作る」

という説明は、mainline 現況には合わない。

---

## 4. current L4 flow
現行の最小 shared-first 経路は次である。

```text
market_state row
  ↓
L4 shared builder
  `build_market_summary()`
  ↓
L4 operator_ui thin adapter
  `market_summary_widget_model()`
  `market_summary_status_payload()`
  ↓
UI bridge
  `market_state_bridge.py`
  ↓
UI components / pages
```

この経路は、L4 の「shared -> thin adapter -> UI bridge」という正規方向に沿っている。

---

## 5. MarketSummary shared bundle

## 5.1 current shared contract
`btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py` に、少なくとも次が実体としてある。

- `MarketSummary`
- `MarketSummaryBuildInput`
- `build_market_summary()`

### 主 field
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
- headline
  - `market_state_label`
  - `participation_state`
  - `liquidity_bias`
- summary tags
  - `notable_events`
  - `alert_candidates`
- diagnostics
  - `diagnostics`

## 5.2 現在の意味
この bundle は、**市場状態の最小 shared summary** として十分に成立している。
少なくとも operator UI での利用に耐えるだけでなく、monitoring / replay / AI metadata へも広げやすい形を保っている。

---

## 6. shared builder の責務
`build_market_summary()` がやるべきことは次に限定する。

- source_kind の正規化
- event_ts / age_sec / freshness / is_stale の決定
- trust / continuity / interpretation 系 field の受け取り
- lightweight な notable / alert tag の付与
- diagnostics の引き継ぎ

### やってはいけないこと
- UI 文言生成
- CSS / layout / card 順の決定
- market meaning の再判定
- execution 用 heavy signal の生成
- widget library 依存 shape の生成

---

## 7. operator_ui thin adapter

## 7.1 現行実体
`btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py` は、L4 shared の上に載る current thin adapter である。

### current output
- `MarketSummaryWidgetModel`
- `market_summary_widget_model()`
- `market_summary_status_payload()`

## 7.2 adapter がやってよいこと
- field 名の UI input 向け変換
- `*_key` の付与
- placeholder 用の fallback 適用
- widget ごとの subset 切り出し
- status payload の flattening

## 7.3 adapter がやってはいけないこと
- 新しい market meaning の生成
- trust / continuity / interpretation の再判定
- CSS class / layout grid / refresh 秒数の埋め込み
- wording そのものの生成

原則として、**adapter は meaning unaware / UI aware** に保つ。

---

## 8. current bridge / service 側の位置づけ

### `market_state_service.py`
- data/market_state から最新 row を読む
- diagnostics を作る
- `build_market_summary()` に入力する

### `market_state_bridge.py`
- shared bundle を読む
- thin adapter を通して UI 用 payload / widget model を返す
- bridge として current UI components へ接続する

### 位置づけ
この二つは current mainline では妥当である。
ただし将来的に bundle 種類が増えたら、bridge / service の責務を bundle ごとに整理する余地はある。

---

## 9. L4 shared の current limit
現在の L4 は `market_summary` では実体があるが、全面完成ではない。

### 現在あるもの
- `market_summary` shared bundle
- operator_ui thin adapter
- UI bridge 経路

### まだ formal ではないもの
- `semantic_timeline_bundle`
- `alert_candidate_bundle`
- `liquidity_snapshot_bundle`
- `health_digest`
- `execution_signal_bundle`
- prediction / decision 向け shared bundle

したがって、L4 は「未展開」ではなく、**market_summary を起点に拡張中**と書くのが正しい。

---

## 10. L4 の next bundle 候補
current roadmap と open risk を踏まえると、次段の L4 bundle 候補は次の順が自然である。

1. event usage contract を前提にした `semantic_timeline_bundle`
2. observer-only の `health_digest`
3. live wiring contract 固定後の `liquidity_snapshot_bundle`
4. prediction / decision contract を受ける `execution_signal_bundle` の前段

ここで重要なのは、**event usage contract 前に event consumer bundle を増やさない**こと、そして **runtime wiring contract 前に live orderbook semantics bundle を厚く作らない**ことである。

---

## 11. additive-first / compatibility
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

これは current roadmap の prediction / decision / health-first に進む際にも重要である。

---

## 12. shared へ寄せる判断基準
次のどれかを満たすなら、まず shared を疑う。

- 2 consumer 以上で使う
- wording-free で再利用できる
- market truth を再定義せず shape だけ整えている
- timeline / digest / bundle として共有価値がある

逆に、次は shared に置かない。

- 文言
- 色
- CSS
- graph library 依存 shape
- widget 固有の final input
- page 固有の並び順

---

## 13. 禁止事項
- L4 で second L3 を作る
- UI convenience のために meaning owner を曖昧にする
- event usage 未固定のまま event consumer bundle を増やす
- live wiring 未固定のまま orderbook semantics bundle を outward owner にする
- adapter に heavy logic を溜め込む

---

## 14. 一言
L4 は未展開ではない。
現在の mainline では `market_summary` を中核に shared-first の最小経路が既に成立している。
今後は contract-first で bundle を増やし、meaning を増やさず shape を育てるのが正しい。
