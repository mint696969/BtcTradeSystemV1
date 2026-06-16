# path: ./tmp/04_UI_HUB_OPERATOR_UI_SPEC_2026-04-09.md
# desc: UI Hub and Operator UI Spec (merged current-truth sync after Phase 2 / 2.5 closeout)

更新日: 2026-04-14
位置づけ: 現行 mainline に合わせた operator UI / hub / presenter / widget 境界仕様
対象: `btcts_next/src/btcts/apps/operator_ui/`, `btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/`

---

## 1. この仕様書の目的
本仕様書は、operator UI を **meaning owner に戻さない** ための境界仕様である。

ここで整理する論点は次の 4 つで十分である。

1. UI の責務と非責務
2. bridge / service / presenter / widget / view の役割
3. Health observer 実装の current truth
4. 今後 UI で手を入れるときの判断基準

---

## 2. 結論
operator UI は、最終的に次の責務分離で読むのが正しい。

```text
L3 truth
  ↓
L4 shared bundle
  ↓
L4 consumer adapter
  ↓
UI bridge / service
  ↓
presenter / widget / view
```

### 一言で言うと
- L3 は意味
- L4 shared は共有束
- adapter は consumer 向け薄変換
- bridge / service は接続
- presenter / widget / view は表示

UI は **表示と orchestration の owner** であって、意味 owner ではない。

---

## 3. UI が持つ責務

### 含むもの
- page / tab grouping
- widget / panel 表示
- presenter による最終 shape 整形
- text / i18n
- refresh / layout / grouping の UI 都合
- bridge / service による bundle 読み出し
- operator 向けの見せ方最適化

### 含まないもの
- trust / continuity / pressure / wall の owner 判定
- market summary の shared owner
- canonical / rebuild / semantic 再計算
- event usage strength の独自決定
- execution 意思決定の owner

---

## 4. 現行 mainline の UI 構造
現行コードは、完全に理想骨格へ移し切ってはいないが、方向としては十分読める。

### current packages
- `btcts_next/src/btcts/apps/operator_ui/views/`
- `btcts_next/src/btcts/apps/operator_ui/components/`
- `btcts_next/src/btcts/apps/operator_ui/texts/`
- `btcts_next/src/btcts/apps/operator_ui/tests/`
- `btcts_next/src/btcts/apps/operator_ui/market_state_service.py`
- `btcts_next/src/btcts/apps/operator_ui/health_data_service.py`
- `btcts_next/src/btcts/apps/operator_ui/health_truth.py`

### partial skeleton
- `btcts_next/src/btcts/apps/operator_ui/widgets/`
- `btcts_next/src/btcts/apps/operator_ui/presenters/`
- `btcts_next/src/btcts/apps/operator_ui/hub/`

### 現状の読み方
- `views/` = page orchestration
- `components/` = render helper / 過渡期 UI ロジック
- `texts/` = 文言
- service / bridge = データ接続

`components/` は過渡期の現実として受け止めつつも、新規ロジックを無秩序に積み上げる場所にはしない。

---

## 5. bridge / service / presenter / widget / view の責務

## 5.1 service
service は storage / file / state source を読む。

### 例
- `market_state_service.py`
- `health_data_service.py`

## 5.2 bridge
bridge は shared bundle / status payload / widget model を UI 側へつなぐ。

### 例
- `components/market_state_bridge.py`
- `components/health_digest_bridge.py`

## 5.3 presenter
presenter は widget が食べやすい最終表示 shape に整える。
文言 key、badge key、caption、table row の最終 shape はここで閉じるのが理想である。

## 5.4 widget / component
render owner。
Streamlit 依存の描画はここで持つ。

## 5.5 view
page の orchestration owner。
widget の並び、slot 割当、page-level grouping を担当する。

---

## 6. current success pattern
現時点で最も素直に shared-first を実現しているのは `market_summary` 周辺と `health_digest` current-state line である。

### 正方向
- `market_state_service.py`
- `processing/l4_consumer_models/shared/market_summary.py`
- `processing/l4_consumer_models/operator_ui/market_summary_adapter.py`
- `components/market_state_bridge.py`
- presenter / component / page

### Health current-state line
- `health_data_service.py`
- `processing/l4_consumer_models/shared/health_digest.py`
- `processing/l4_consumer_models/operator_ui/health_digest_adapter.py`
- `components/health_digest_bridge.py`
- current-state panel / caption / page

この経路は今後の UI 拡張の基準になる。

---

## 7. Health observer の current truth
2026-04-13 時点では、Health は未来形ではなく、**summary-first / observer-only** の current line が repo mainline にかなり固定されている。

### 主な service 側実装
- `build_layer3_semantic_usage_summary()`
- `build_layer3_runtime_contract_summary()`
- `build_layer3_orderbook_runtime_summary()`

配置:
- `btcts_next/src/btcts/apps/operator_ui/health_data_service.py`

### 表示側実装
- `btcts_next/src/btcts/apps/operator_ui/components/health_chart_panels.py`
- `btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py`
- `btcts_next/src/btcts/apps/operator_ui/components/health_detail_panels.py`
- `btcts_next/src/btcts/apps/operator_ui/components/health_digest_bridge.py`
- `btcts_next/src/btcts/apps/operator_ui/views/health_page.py`

### current truth
Health observer は、少なくとも次を current line として読める。

#### semantic observer line
- `observer_present`
- `usage_summary_present`
- `contract_rows_present`
- `contract_rows_count`
- `source_series_present`
- `summary_source`
- `summary_contract`
- `summary_version`
- `active_events`
- `mapped_events`
- `unknown_events`
- distribution fields

#### orderbook runtime line
- `wiring_status`
- `contract_status_source`
- `freshness`
- `summary_slots_present`
- `summary_slots_count`
- `near_wall_present`
- `support_present`
- `resistance_present`
- `persistence_present`
- `persistence_observable`
- `active_event_names`
- `active_event_contracts`

### 重要な読み方
- Health は wiring / summary presence / active event delivery を観測するのであって、meaning owner ではない
- `persistence_present` と `persistence_observable` は混同しない
- Health が `unhealthy` や `STALE` を出していても、それは formal market_state を正直に表示しているだけの可能性がある
- UI convenience で contract gap を埋めない

---

## 8. Health 側でまだ未完のもの
### current reached
- `health_page.py` は `render_fragment_slot()` を広く使い、Health page を fragment-first refresh path へかなり寄せている
- `test_live_shell_refresh_plan.py` は health の fragment path を検証している
- shared `health_digest` / adapter / bridge / current-state panel usage は repo mainline に到達済み

### remaining open
- fragment-first foundation reached 後の stability / wording / remaining scope judgment
- L4 shared input の broader formalization
- timeline / anomaly split の formalization
- panel 文言の一部 text layer 整理

### 現時点の立場
したがって stale な読みは、
- `UI 自動更新は未実装`
- `page 全リロードなしの no-reload refresh は未実装`

ではなく、

- **fragment-slot foundation reached**
- **Health page is on fragment-first refresh path**
- **remaining open = stability / wording / broader formalization**

と書くのが current repo truth に近い。

---

## 9. current risks in UI
現時点で architecture 的に注意すべき UI 論点は次である。

### 9.1 event consumer を UI convenience で先に作ること
event usage contract が event-level full contract としてはまだ未完なので危険。

### 9.2 live orderbook semantics gap を page logic で埋めること
near wall / support / resistance / persistence を UI 側で暫定再計算すると owner 境界が壊れる。

### 9.3 `components/` への logic 蓄積
現状は許容するが、shared 化できる logic を永続的に閉じ込め続けるべきではない。

---

## 10. presenter / text / widget の原則

### presenter がやってよいこと
- line / bar / table / card への最終 shape 化
- badge key / tone key / icon key の割当
- caption の組み立て
- UI 表示順の決定

### presenter がやってはいけないこと
- market meaning の再定義
- trust / continuity / interpretation の再判定
- raw / canonical の再構築

### text layer がやること
- i18n
- wording
- human-readable label
- descriptive sentences

### widget / component がやること
- render
- local visual state
- chart / metric / table 描画

---

## 11. refresh / layout / styling の責務
これらは UI の責務である。

### UI に置くもの
- refresh interval
- manual / automatic refresh policy
- graph layer visibility
- widget size / layout hint
- style override
- theme / language

### L4 に置かないもの
- CSS class
- color code
- grid coordinates
- drag & drop state
- page-specific ordering

shared bundle に UI 都合を持ち込まないこと。

---

## 12. 今後の UI 作業時の判断ルール

### まず shared を疑う場合
- 複数 page / panel で使う
- wording-free で共通化できる
- 状態の束であって描画 shape ではない

### UI に残してよい場合
- 表示都合だけ
- page 固有の grouping
- render library 依存 shape
- i18n / wording

### 絶対に UI へ置かないもの
- semantic owner 判定
- event usage strength の独自決定
- replay/live parity の意味判定
- orderbook semantics の暫定再計算

---

## 13. current roadmap と UI の整合
2026-04-14 時点では、UI 側で次の順序を守るのが安全である。

1. architecture docs を repo truth に同期する
2. Health current truth を stale wording なく保持する
3. panel 文言を text layer へ寄せる
4. L4 側で Health digest の broader formalization を進める
5. full wiring / full parity の consumer 拡張は contract 固定後に進める

つまり UI は、契約未固定論点を先に吸収する場所ではない。

---

## 14. 一言
operator UI は市場意味を作る場所ではない。
2026-04-14 時点では、Health observer 実装は既に useful な段まで進んでおり、fragment-first refresh path と current-state digest path も mainline に到達しているが、なお owner 境界は守られている。

今後も、

- service / bridge / presenter / widget / view を混ぜないこと
- UI convenience で meaning owner を汚さないこと
- auto refresh 追加時も page logic を厚くしすぎないこと

を守るのが正しい。
