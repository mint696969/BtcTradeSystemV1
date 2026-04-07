# path: ./docs/architecture/04_UI_HUB_OPERATOR_UI_SPEC_2026-04-08.md
# desc: UI Hub and Operator UI Spec

更新日: 2026-04-08
位置づけ: 現行 mainline に合わせた operator UI / hub / presenter / widget 境界仕様
対象: `btcts_next/src/btcts/apps/operator_ui/`, `btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/`

---

## 1. この仕様書の目的
本仕様書は、旧 `UI_HUB_WIDGET_ARCHITECTURE_SPEC` と `L4_UI_ADAPTER_WIDGET_STRUCTURE_SPEC` の有効部分を統合し、現行 operator UI を責務分離前提で説明し直すための仕様である。

目的は次の4つ。

1. UI が meaning owner に戻らない境界を固定する
2. shared / adapter / bridge / presenter / widget / views の責務を整理する
3. 現在の実装形と将来の正規像を混同しないようにする
4. 次の UI 拡張が L4 原則を壊さないようにする

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
- L4 consumer adapter は用途別薄変換
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
- bridge / service による bundle の読み出し
- operator 向けの見せ方最適化

### 含まないもの
- trust / continuity / pressure / wall の owner 判定
- market summary の shared owner
- alert candidate の shared owner
- canonical / rebuild / semantic 再計算
- execution 意思決定の owner

---

## 4. 現行 mainline の operator UI 構造
現行コードは、完全に理想骨格へ整理済みではないが、方向としては次で読める。

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

現在は、**components/view 中心の運転実装を保ちつつ、一部で shared-first bridge / adapter / presenter への寄せが始まっている段階**である。

---

## 5. UI bridge / service の位置づけ

### 5.1 service
service は storage / file / state source を読む。

例:
- `market_state_service.py`
- `health_data_service.py`

### 5.2 bridge
bridge は shared bundle / status payload / widget model を UI 側へつなぐ。

例:
- `components/market_state_bridge.py`

### 5.3 presenter
presenter は widget が食べやすい最終表示 shape に整える。
文言・短い caption・series shape・card rows は presenter 側で閉じる。

### 5.4 widget / component
render owner。
Streamlit や UI library 依存の最終描画はここで持つ。

---

## 6. current success pattern
現時点でうまく切れている代表は `market_summary` 周辺である。

### 正方向
- `market_state_service.py`
- `processing/l4_consumer_models/shared/market_summary.py`
- `processing/l4_consumer_models/operator_ui/market_summary_adapter.py`
- `components/market_state_bridge.py`
- `components/market_summary_presenter.py`
- 各 panel / page

この pattern は今後の UI 改修基準として再利用できる。

---

## 7. current risks in UI
現時点で architecture 的に注意すべき UI 論点は次である。

### 7.1 event consumer を UI convenience で先に作ること
- event usage contract が未固定のため危険

### 7.2 live orderbook semantics gap を page logic で埋めること
- near wall / support / resistance / persistence を UI 側で暫定再計算すると owner 境界が壊れる

### 7.3 components への logic 蓄積
- `components/` は現行 mainline の現実として受け止めるが、shared 化できるものを閉じ込め続けるべきではない

---

## 8. presenter / widget / text の原則

### presenter がやってよいこと
- line/bar/table/card への最終 shape 化
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

## 9. 将来の正規像
今すぐ全面移行は不要だが、正規像は次として維持する。

```text
apps/operator_ui/
  hub/
    __init__.py
    widget_registry.py
    layout_manager.py
    refresh_manager.py
    layer_manager.py

  presenters/
    __init__.py
    market_summary_presenter.py
    liquidity_presenter.py
    timeline_presenter.py
    alert_presenter.py
    health_presenter.py

  widgets/
    __init__.py
    market_summary_widget.py
    liquidity_widget.py
    timeline_widget.py
    alert_widget.py
    health_widget.py

  views/
  texts/
  services/
  components/
```

### 補足
- `components/` を即全廃する必要はない
- ただし、新規 shared-first 経路は `bridge / presenter / widget` を意識して置く
- `components/` は過渡期実装として増えすぎないようにする

---

## 10. tab / page の考え方
page や tab は meaning owner ではなく grouping 単位である。

### 含意
- health page が独自に market meaning を作らない
- warroom page が独自に timeline truth を作らない
- replay page が shared bundle を bypass して独自 summary を増やさない

shared 入力が必要なら、まず L4 か shared bridge を疑う。

---

## 11. refresh / layout / styling
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

これを混ぜると shared bundle が汚れる。

---

## 12. 新規 UI 作業時の判断ルール

### 12.1 まず shared を疑う場合
- 複数 page / panel で使う
- wording-free で共通化できる
- 状態の束であって描画 shape ではない

### 12.2 UI に残してよい場合
- 表示都合だけ
- page 固有の grouping
- render library 依存 shape
- i18n / wording

### 12.3 絶対に UI へ置かないもの
- semantic owner 判定
- event usage strength の独自決定
- replay/live parity の意味判定

---

## 13. current roadmap との整合
UI 側で今やるべき順序は次である。

1. event usage contract が固まる前に event-heavy consumer を増やさない
2. Health v1 observer を observer-only で入れる
3. live wiring contract が固まる前に near wall consumer を厚くしない
4. prediction / decision shared contract の入力面を shared-first で受ける

つまり、UI は **roadmap 後段の consumer 拡張先**であって、契約未固定論点を先に吸収する場所ではない。

---

## 14. 一言
operator UI は市場意味を作る場所ではない。
shared bundle を受けて、表示・更新・配置・文言化を行う hub として薄く保つのが正しい。
