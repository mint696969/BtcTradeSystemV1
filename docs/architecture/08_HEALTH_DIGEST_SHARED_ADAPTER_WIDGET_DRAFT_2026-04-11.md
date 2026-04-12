# path: ./tmp/08_HEALTH_DIGEST_SHARED_ADAPTER_WIDGET_DRAFT_2026-04-11.md
# desc: Health Digest shared/adapter/widget split draft after responsibility alignment

更新日: 2026-04-11
位置づけ: `docs/architecture/` 続きファイル候補 / health_digest 最小 field draft
対象: `btcts_next/src/btcts/apps/operator_ui/health_data_service.py`, `btcts_next/src/btcts/apps/operator_ui/views/health_page.py`, 将来の `processing/l4_consumer_models/shared/health_digest.py`

---

## 1. この文書の目的
本稿は、`health_digest` を将来的に L4 shared へ正式化する場合に、

- 何を **shared** に置くか
- 何を **consumer adapter** に置くか
- 何を **widget / view** にしか置かないか

を先に固定するための draft である。

ここでの最重要原則は、次の 3 点である。

1. Health は observer-only を保つ
2. L4 shared は consumer-neutral shape に限定する
3. UI convenience を shared へ持ち込まない

---

## 2. current repo truth
`btcts_next/src/btcts/apps/operator_ui/health_data_service.py` の `load_health_snapshot()` は、現在少なくとも次の情報束を返している。

### current snapshot keys
- `collector_state`
- `rate_domains`
- `domain_names`
- `domain_counts`
- `shared_ip`
- `shared_ip_budget`
- `shared_ip_remaining_60s`
- `market_latest`
- `market_diag`
- `selected_range_key`
- `range_presets`
- `api_ws_series`
- `rate_overlay`
- `layer3_series`
- `layer3_semantic_usage_rows`
- `layer3_semantic_usage_summary`
- `layer3_runtime_contract_summary`
- `layer3_orderbook_runtime_summary`
- `api_continuity_rail`
- `ws_continuity_rail`
- `recent_anomalies`
- `paths`

この current snapshot は useful だが、まだ **shared digest** と **UI page convenience bundle** が分離されていない。

---

## 3. 結論
`health_digest` を作るなら、最初から全部を 1 bundle にしない方がよい。

### 正しい最小分解
1. **HealthDigest**
   - current-state / runtime observer の shared snapshot
2. **HealthTimelineBundle**
   - chart / rail 系の時系列
3. **HealthAnomalyFeed**
   - recent anomaly / event list

ただし、最初の formal 化では **1. HealthDigest のみ** を shared に上げるのが安全である。

理由:
- current-state digest は複数 consumer に再利用しやすい
- timeline / anomaly は UI / monitoring / audit で shape が割れやすい
- 最初から全部盛りにすると `health_digest` が太りすぎる

---

## 4. 最小 shared 化の対象
`HealthDigest` の shared 版は、**「今どういう状態か」を consumer-neutral に読むための snapshot** に限定する。

### 4.1 shared に置くべき field 群

#### A. digest metadata
- `digest_type`
- `digest_version`
- `source_kind`
- `exchange`
- `symbol_raw`
- `market_uid`
- `event_ts`
- `freshness`
- `is_stale`

#### B. collector runtime summary
- `collector_mode`
- `collector_ok`
- `runtime_kind`
- `daemon_runtime_kind`
- `status_source`

#### C. API runtime summary
- `api_provider`
- `api_mode`
- `api_utilization`
- `api_target_utilization`
- `api_hard_cap_utilization`
- `api_requests_60s`
- `api_requests_300s`
- `api_last_429_ts`

#### D. WS runtime summary
- `ws_board_state`
- `ws_board_last_error`
- `ws_executions_state`
- `ws_executions_last_error`
- `ws_board_freshness`
- `ws_executions_freshness`

#### E. L3 market runtime summary
- `trust_state`
- `continuity_state`
- `interpretation_bucket`
- `interpretation_reason`
- `source_series_id`
- `market_freshness`

#### F. semantic usage digest
- `semantic_summary_source`
- `semantic_observer_status`
- `semantic_usage_summary`
- `semantic_usage_contract_rows`
- `semantic_runtime_wiring_status`
- `semantic_contract_rows_present`
- `semantic_contract_rows_count`

#### G. orderbook runtime digest
- `orderbook_contract_status_source`
- `orderbook_wiring_status`
- `orderbook_freshness`
- `orderbook_summary_slots_present`
- `orderbook_summary_slots_count`
- `orderbook_persistence_observable`
- `orderbook_active_event_count`
- `orderbook_active_event_names`
- `orderbook_active_event_contracts`

#### H. minimal diagnostics
- `diagnostics`
  - wording-free / debug-safe な補助情報のみ

### 4.2 shared に置かないもの
- `selected_range_key`
- `range_presets`
- `api_ws_series`
- `rate_overlay`
- `layer3_series`
- `api_continuity_rail`
- `ws_continuity_rail`
- `recent_anomalies`
- `paths`

これらは将来 shared 化するなら、`HealthTimelineBundle` や `HealthAnomalyFeed` など別 bundle として切る方がよい。

---

## 5. shared field の具体 draft
最小 shared draft は、次のような shape が自然である。

```text
HealthDigest
  digest_type
  digest_version
  source_kind
  exchange
  symbol_raw
  market_uid
  event_ts
  freshness
  is_stale

  collector_runtime
  api_runtime
  ws_runtime
  market_runtime
  semantic_usage
  orderbook_runtime
  diagnostics
```

### 5.1 nested summary を推奨する理由
flat 1枚 dict よりも、nested summary にした方が

- consumer ごとの subset 切り出しがしやすい
- field 衝突が起きにくい
- 将来の bundle 拡張に耐えやすい

ためである。

### 5.2 nested summary 例
```text
collector_runtime
  mode
  ok
  runtime_kind
  daemon_runtime_kind

api_runtime
  provider
  mode
  utilization
  target_utilization
  hard_cap_utilization
  requests_60s
  requests_300s
  last_429_ts

ws_runtime
  board_state
  board_last_error
  executions_state
  executions_last_error
  board_freshness
  executions_freshness

market_runtime
  trust_state
  continuity_state
  interpretation_bucket
  interpretation_reason
  source_series_id
  freshness

semantic_usage
  summary_source
  observer_status
  summary
  contract_rows
  runtime_wiring_status
  contract_rows_present
  contract_rows_count

orderbook_runtime
  contract_status_source
  wiring_status
  freshness
  summary_slots_present
  summary_slots_count
  persistence_observable
  active_event_count
  active_event_names
  active_event_contracts
```

---

## 6. adapter に置くもの
consumer adapter は、shared digest を **consumer-specific final model** へ薄く変換する。

### operator_ui adapter に置くもの
- metric card 向け flatten
- placeholder fallback
- caption line 向け subset 抽出
- widget 単位の final model 生成
- badge key / tone key / label key の割当
- `*_kind` / `*_count` の UI payload 化

### AI adapter に置くもの
- prompt 用 compact summary
- 長文生成に不要な field の削減
- AI reasoning 用の安全な列挙 shape

### strategy adapter に置くもの
- health gating input
- execution block / caution / allow 判定に使う input model
- ただし strategy policy 自体は strategy owner 側

### monitoring adapter に置くもの
- alert rule が読みやすい flat model
- observer dashboard 向け compact model

### adapter に置いてはいけないもの
- 新しい market meaning 判定
- L3 truth の上書き
- 他 consumer でも使いたい shared shape の定義
- widget 固有の描画処理

---

## 7. widget / view にしか置かないもの
widget / presenter / view に置くのは、表示責務だけである。

### widget / presenter / view に残すもの
- caption 文
- panel title
- 表示順
- columns / layout
- chart library shape
- Streamlit 依存処理
- i18n wording
- expander / fold / tab / section 構成

### shared に持ち込まないもの
- `health_label_*`
- `health_caption_*`
- `health_value_*`
- color / icon / badge 表示都合
- panel ごとの metric grouping

---

## 8. 具体的な分割表

### shared へ上げる
- `layer3_semantic_usage_summary`
- `layer3_semantic_usage_rows`
- `layer3_runtime_contract_summary`
- `layer3_orderbook_runtime_summary`
- collector / rate / ws / market latest から読み取る current runtime summary

### shared へ上げない
- `api_ws_series`
- `rate_overlay`
- `layer3_series`
- `api_continuity_rail`
- `ws_continuity_rail`
- `recent_anomalies`

### 理由
上段は **snapshot digest** であり、複数 consumer がそのまま読みやすい。
下段は **timeline / feed / chart 依存** が強く、shared core とは別 bundle の方が自然である。

---

## 9. 実装方針の推奨順

### Phase A
`processing/l4_consumer_models/shared/health_digest.py` を追加する。

### Phase B
`HealthDigest` / `HealthDigestBuildInput` / `build_health_digest()` を作る。

### Phase C
`processing/l4_consumer_models/operator_ui/health_digest_adapter.py` を追加する。

### Phase D
`health_data_service.py` は
- collector / market_state / audit から raw を読む
- `build_health_digest()` へ入力を渡す
- timeline / anomaly だけは従来のまま残す

### Phase E
Health page は
- current-state panel 群を digest 主入力へ寄せる
- chart / rail / anomaly は段階的に別 bundle 化を検討する

---

## 10. anti-pattern

### 10.1 全部入り `health_snapshot` をそのまま shared 化する
危険。
UI convenience と shared contract が混ざる。

### 10.2 `health_digest` に wording を入れる
危険。
text layer / adapter / widget の責務を侵食する。

### 10.3 `health_digest` で新しい意味判定をする
危険。
L4 が second L3 化する。

### 10.4 timeline / anomaly / chart を core digest に混ぜる
危険。
shape が膨らみ、他 consumer で再利用しにくくなる。

---

## 11. 一言
`health_digest` を formal 化する場合の正しい最小線は、

**「current-state の observer snapshot だけを shared に上げ、timeline / anomaly / widget 表示都合は別責務として残す」**

である。

この線を守れば、
- operator UI
- AI consumer
- monitoring consumer
- strategy gating input

へ拡張しても、L3 / L4 / adapter / widget の責務が崩れにくい。
