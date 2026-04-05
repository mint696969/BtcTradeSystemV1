# path: ./docs/architecture/L4_UI_ADAPTER_WIDGET_STRUCTURE_SPEC_2026-04-05.md
# desc: Structure spec for separating L4 shared bundles, UI adapters, presenters, and widgets.
# L4 / UI Adapter / Widget Structure 仕様書

更新日: 2026-04-05
位置づけ: L4 以降の責務分離を将来実装でも崩さないための構造仕様
対象: `btcts_next/src/btcts/processing/` と `btcts_next/src/btcts/apps/operator_ui/`

---

## 1. この仕様書の目的
本仕様書は、L4 shared / consumer adapter / UI widget の境界を「説明」だけでなく「配置先」まで固定するためのものである。

この仕様書が必要な理由は次の通り。

1. 責務分離は概念だけだと後続 GPT が崩しやすい
2. UI 向け加工は工程が多く、L4 shared 本体へ混ざりやすい
3. 実フォルダ skeleton を先に作ると、将来の drift を抑えやすい
4. L4 以降の再設計コストを下げたい

---

## 2. 結論
L4 以降は次の4段で切る。

```text
L3
  shared market meaning
    ↓
L4 shared
  shared bundle / summary / digest
    ↓
L4 consumer adapter
  consumer-specific thin conversion
    ↓
UI widget / presenter / hub
  render / layout / orchestration
```

### 一言で言うと
- L3 は意味
- L4 shared は共有束
- L4 consumer adapter は用途別の薄い変換
- UI は表示と orchestration

---

## 3. 現在の問題意識
現状の repository では責務分離自体は進んでいるが、`btcts_next/src/btcts/` の見た目だけでは次の境界がまだ薄い。

- `processing/l4_consumer_models/` はまだ未展開
- `apps/operator_ui/` に logic / presenter / component が混在している
- 後続 GPT が「widget 入力化」を L4 shared 本体へ混ぜる危険がある

そのため、「どこで切るか」を package skeleton として先に固定する。

---

## 4. 固定したい正規構造

## 4.1 processing 側
次を正規構造とする。

```text
btcts_next/src/btcts/processing/
  l4_consumer_models/
    __init__.py
    shared/
      __init__.py
      market_summary.py
      liquidity_bundle.py
      semantic_timeline.py
      alert_candidates.py
      health_digest.py

    operator_ui/
      __init__.py
      market_summary_adapter.py
      liquidity_adapter.py
      timeline_adapter.py
      alert_adapter.py
      health_adapter.py

    monitoring/
      __init__.py

    replay/
      __init__.py

    ai_training/
      __init__.py

    auto_trading/
      __init__.py
```

### 意味
- `shared/` は複数 consumer で共有する束
- `operator_ui/` は UI 専用の thin adapter
- 他 consumer も同じ考え方で揃える

---

## 4.2 apps/operator_ui 側
次を将来の正規像とする。

```text
btcts_next/src/btcts/apps/operator_ui/
  hub/
    __init__.py
    widget_registry.py
    layout_manager.py
    refresh_manager.py
    layer_manager.py

  widgets/
    __init__.py
    market_summary_widget.py
    liquidity_widget.py
    timeline_widget.py
    alert_widget.py
    health_widget.py

  presenters/
    __init__.py
    market_summary_presenter.py
    liquidity_presenter.py
    timeline_presenter.py
    alert_presenter.py
    health_presenter.py

  texts/
    ...
  views/
    ...
```

### 意味
- `hub/` は widget orchestration
- `widgets/` は描画部品
- `presenters/` は widget が食べる最終 shape の整形
- `texts/` は wording / i18n
- `views/` は page grouping

---

## 5. 何をどこに置くか

## 5.1 L4 shared に置くもの
### 例
- market summary
- liquidity bundle
- timeline bundle
- alert candidate bundle
- health digest

### 条件
- 複数 consumer で使える
- wording-free
- layout-free
- widget library 非依存
- UI の card / chart 固有 shape ではない

---

## 5.2 L4 consumer adapter に置くもの
### 例
- MarketSummary -> MarketSummaryWidgetModel への変換
- LiquidityBundle -> GraphWidgetInput への前段 shape 変換
- alert candidate -> UI key 変換

### 条件
- その consumer 専用
- ただし thin
- meaning を増やさない
- layout や CSS は持たない

---

## 5.3 UI presenter / widget に置くもの
### presenter の例
- line series / bar series / marker series 生成
- card rows 生成
- gauge 用 current / min / max 整形
- table row 生成

### widget の例
- Streamlit 描画
- chart 描画
- badge / chip / card の render

### 条件
- 表示ライブラリ依存 shape はここ
- 表示順 / icon /色 / placeholder wording はここ
- shared truth を書き換えない

---

## 6. 典型フロー

### 6.1 market summary
```text
L3 continuity / trust / interpretation
  ↓
L4 shared: MarketSummary
  ↓
L4 operator_ui adapter: MarketSummaryWidgetModel
  ↓
UI presenter: cards / badges / compact rows
  ↓
widget render
```

### 6.2 liquidity graph
```text
L3 liquidity semantics
  ↓
L4 shared: LiquidityBundle
  ↓
L4 operator_ui adapter: LiquidityWidgetModel
  ↓
UI presenter: line/bar/marker/layer arrays
  ↓
widget render
```

### 6.3 alerts
```text
L3 trust / continuity / interpretation
  ↓
L4 shared: AlertCandidateBundle
  ↓
L4 operator_ui adapter: AlertWidgetModel
  ↓
UI text/presenter: short label / icon / tone
  ↓
widget render
```

---

## 7. 後続 GPT に対する固定ルール

### ルール1
widget が食べる最終 shape を L4 shared 本体に入れない。

### ルール2
chart library 依存 shape を L4 shared に入れない。

### ルール3
表示文・色・レイアウトを L4 consumer adapter に入れすぎない。

### ルール4
UI 側で trust / continuity / pressure などの meaning owner を再定義しない。

### ルール5
shared にできるものは adapter や widget に閉じる前に L4 shared を疑う。

---

## 8. 実装順序

### Phase 1
- `processing/l4_consumer_models/` package skeleton
- `shared/market_summary.py`
- `operator_ui/market_summary_adapter.py`

### Phase 2
- `apps/operator_ui/hub/` skeleton
- `apps/operator_ui/presenters/` skeleton
- market summary widget の最小経路

### Phase 3
- liquidity / timeline / alert / health へ横展開

---

## 9. 最低限の package 作成方針
今すぐ全実装を作る必要はない。
しかし将来 drift を防ぐため、最低限次は早めに作る価値が高い。

- `processing/l4_consumer_models/__init__.py`
- `processing/l4_consumer_models/shared/__init__.py`
- `processing/l4_consumer_models/operator_ui/__init__.py`
- `apps/operator_ui/hub/__init__.py`
- `apps/operator_ui/widgets/__init__.py`
- `apps/operator_ui/presenters/__init__.py`

空でもよい。
器を先に固定することが目的である。

---

## 10. 一言でまとめると

```text
L4 shared は「何を見せる価値があるか」までを作る。
UI adapter と presenter は「それを widget がどう食べるか」を作る。
描画は widget が持つ。
```
