# path: ./tmp/08_HEALTH_DIGEST_SHARED_ADAPTER_WIDGET_SPEC_2026-04-15_MERGED.md
# desc: Health Digest shared/adapter/widget merged current-truth spec after Phase 2.5 closeout progress.

更新日: 2026-04-15
位置づけ: `docs/architecture/08_HEALTH_DIGEST_SHARED_ADAPTER_WIDGET_DRAFT_2026-04-11.md` の current-truth merged spec
対象: `btcts_next/src/btcts/apps/operator_ui/health_data_service.py`, `btcts_next/src/btcts/apps/operator_ui/views/health_page.py`, `btcts_next/src/btcts/processing/l4_consumer_models/shared/health_digest.py`, `btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/health_digest_adapter.py`

---

## 1. この仕様書の目的
本仕様書は、`health_digest` と `health_snapshot` grouped bundle の current truth を、2026-04-15 時点の repo 実装に合わせて固定するための merged spec である。

ここで明確にしたいのは次の 5 点である。

1. `health_digest` の current-state shared path はどこまで reached しているか
2. `current_state_bundle` / `timeline_bundle` / `continuity_bundle` / `anomaly_bundle` / `page_meta_bundle` をどう読むか
3. broader shared contract と page-local convenience の境界はどこか
4. Health v2 observer は何者で、何者ではないか
5. immediate open を code churn ではなく closeout wording としてどう固定するか

---

## 2. 結論
2026-04-15 時点の current repo truth は次のように読むのが正しい。

### reached
- `health_digest` の **current-state shared / adapter / bridge / UI usage path** は reached
- `health_snapshot` は grouped bundle 入口まで mainline に入っている
- Health は **summary-first / observer-only** line で useful な段まで到達している

### not reached
- `timeline_bundle` / `continuity_bundle` / `anomaly_bundle` / `page_meta_bundle` の broader shared-first consumer adoption は reached していない
- Health v2 は prediction observer ではない
- `health_snapshot` grouped contract をそのまま broader shared bundle として読むのは早い

### current reading の一言
Health は **observer-only current-state digest reached / grouped page contract reached / broader consumer formalization still carry-forward** の段にある。

---

## 3. current repo truth
### 3.1 `health_data_service.py` の current grouped contract
`load_health_snapshot()` は flat compatibility を維持したまま、少なくとも次の grouped bundle を返している。

- `current_state_bundle`
- `timeline_bundle`
- `continuity_bundle`
- `anomaly_bundle`
- `page_meta_bundle`

同時に、従来の flat key も残している。

### 3.2 `health_page.py` の current reading
Health page は grouped bundle helper を持ち、主要 section を

- grouped bundle 優先
- flat fallback 維持

で読む current truth に進んでいる。

### 3.3 `health_digest` current-state line
current-state digest line では、少なくとも次が repo mainline に存在する。

- shared builder: `processing/l4_consumer_models/shared/health_digest.py`
- operator_ui thin adapter: `processing/l4_consumer_models/operator_ui/health_digest_adapter.py`
- bridge: `apps/operator_ui/components/health_digest_bridge.py`
- service integration: `apps/operator_ui/health_data_service.py`
- page / panel usage: `apps/operator_ui/views/health_page.py` と panel 群

したがって current open は、`health_digest` をゼロから shared 化することではない。

---

## 4. grouped bundle の current boundary
### 4.1 `current_state_bundle`
**current-state observer owner** として読むのが正しい。

含むもの:
- collector / API / WS の current runtime summary
- market current-state summary
- semantic usage summary / rows
- runtime contract summary
- orderbook runtime summary
- shared `health_digest`

### 4.2 `timeline_bundle`
**series / overlay / layer3 timeline owner** として読むのが正しい。

含むもの:
- `api_ws_series`
- `rate_overlay`
- `layer3_series`

### 4.3 `continuity_bundle`
**rail owner** として読むのが正しい。

含むもの:
- `api_continuity_rail`
- `ws_continuity_rail`

### 4.4 `anomaly_bundle`
**observer feed owner** として読むのが正しい。

含むもの:
- `recent_anomalies`
- anomaly feed metadata

### 4.5 `page_meta_bundle`
**page-local convenience bundle** として読むのが正しい。

含むもの:
- `selected_range_key`
- `range_presets`
- `paths`

### 4.6 重要な読み方
これらはすべて grouped contract に乗っているが、
**broader shared-first adoption reached** と読むのではなく、まずは Health page observer UI stabilization reached と読むのが current truth に近い。

---

## 5. broader shared contract と page-local convenience の線引き
### broader shared contract に寄るもの
- `health_digest` current-state shared path
- current-state の runtime observer summary
- semantic / orderbook runtime observer summary

### page-local convenience に留めるもの
- `page_meta_bundle`
- range 選択 UI 文脈
- paths 表示都合
- page grouping / section orchestration

### carry-forward formalization 候補
- `timeline_bundle`
- `continuity_bundle`
- `anomaly_bundle`

これらは現時点では useful だが、broader consumer need が repo 上で明確ではないため、直ちに shared L4 に押し上げない方が安全である。

---

## 6. Health v2 observer の current truth
### Health v2 が observer であるもの
- semantic runtime contract summary の観測
- orderbook runtime summary の観測
- shared `health_digest` current-state payload / widget key line の観測
- summary presence / freshness / source / observable の観測

### Health v2 が observer ではないもの
- prediction observer
- decision observer
- meaning owner
- event strength 再定義 owner
- orderbook semantics 再計算 owner

### current wording
Health v2 は **runtime semantics observer** であり、prediction observer ではない。

---

## 7. `health_digest` の current stable reading
`health_digest` を current repo truth に即して読むなら、最も安全な表現は次である。

### current-state digest として持ってよいもの
- collector runtime summary
- API runtime summary
- WS runtime summary
- market runtime summary
- semantic usage summary / rows
- runtime contract summary
- orderbook runtime summary
- minimal diagnostics

### current-state digest に混ぜない方がよいもの
- chart series
- continuity rails
- recent anomaly feed
- page-local range / paths / preset convenience

### 理由
- current-state digest は shared-first に再利用しやすい
- timeline / rail / anomaly は consumer / page / monitoring shape が割れやすい
- page meta は page-local context であり、shared contract に押し上げる理由がまだ弱い

---

## 8. adapter / bridge / widget / view の責務
### shared builder がやること
- wording-free current-state digest shape の生成
- summary / rows / runtime status の consumer-neutral bundling

### operator_ui adapter がやること
- widget key / payload shaping
- placeholder fallback
- UI payload flattening
- consumer-aware だが meaning-unaware な薄変換

### bridge / service がやること
- data source 読み出し
- shared builder への入力組み立て
- grouped bundle / digest の page への接続

### widget / view がやること
- caption
- title
- layout
- render library shape
- section grouping
- page orchestration

### 禁止事項
- shared で UI wording を持つ
- adapter で新しい market meaning を作る
- view で orderbook semantics を再計算する
- page convenience を broader shared contract と誤認する

---

## 9. broader consumer demand の current truth
2026-04-15 時点の repo truth では、次は broader consumer adoption reached と読まない。

- `health_snapshot`
- `continuity_bundle`
- `anomaly_bundle`
- `page_meta_bundle`

repo 内 usage は実質 Health page とその focused tests に局在している。

したがって immediate next step は、これらをさらに code 側で shared bundle 化することではなく、
**未需要と current truth を docs / notes / handoff で固定すること**
でよい。

---

## 10. immediate open の正しい読み
current open は次のように読むのが正しい。

### open
- grouped bundle / page_meta / continuity / anomaly の boundary wording fixation
- broader consumer demand 未到達の固定
- Health v2 を runtime semantics observer として固定する docs / handoff / status sync
- carry-forward formalization judgement

### open ではないもの
- `health_digest` のゼロから shared 化
- grouped bundle のゼロから実装
- no-reload foundation のゼロから実装
- prediction observer 実装

---

## 11. 推奨方針
1. current-state shared digest reached を正として固定する
2. grouped bundle は additive contract として保持する
3. page-local convenience は page-local convenience と明言する
4. broader consumer need が出るまで shared 昇格を急がない
5. docs / notes / handoff / status を current truth に同期する

---

## 12. 一言
Health の current truth は、

- `health_digest` current-state shared path reached
- `health_snapshot` grouped page contract reached
- broader consumer adoption not yet reached
- Health v2 = runtime semantics observer only

である。

したがって、ここから先は helper や bundle を増やし続ける段ではなく、**boundary と wording を closeout して Phase 3 entry を邪魔しない形に整える段** として読むのが正しい。
