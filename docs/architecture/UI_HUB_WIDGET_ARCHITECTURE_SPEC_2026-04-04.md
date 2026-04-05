# path: ./docs/architecture/UI_HUB_WIDGET_ARCHITECTURE_SPEC_2026-04-04.md
# desc: Architecture spec for the thin UI hub and widget-oriented design.
# UI Hub / Widget Architecture 仕様書

更新日: 2026-04-04
位置づけ: operator UI 次フェーズ設計仕様 / layered design 補助仕様
対象: `btcts_next/src/btcts/apps/operator_ui/`

---

## 1. この仕様書の目的
本仕様書は、BTC Trade System vNext における operator UI を、重いロジック層ではなく、L4 shared bundle を受けて表示する薄い hub として再設計するための仕様を定義する。

目的は次の5つ。

1. UI が market meaning owner に戻らないようにする
2. UI を widget/gadget 単位で拡張できる構造にする
3. widget ごとの更新頻度・配置・CSS 調整に耐える形にする
4. 将来の drag & drop / resize / 自由配置に進める前提を作る
5. L4 と UI の責務境界を固定する

---

## 2. 結論
operator UI は、最終的に次のような薄い hub として扱う。

```text
L3: shared truth
  ↓
L4: shared bundles / thin ui adapter input
  ↓
UI Hub: widget registry / layout / refresh / layer composition / style override
  ↓
Widget: rendering only
```

つまり、UI は原則として

- 意味を作らない
- shared digest を作り直さない
- 表示・更新・配置・重ね表示を担当する

という位置づけにする。

---

## 3. UI の責務

## 3.1 UI が持つ責務
- widget/gadget 単位の表示
- widget の登録と呼び出し
- widget ごとの更新頻度管理
- graph layer の重ね表示管理
- widget ごとの CSS 微調整
- tab / section / dashboard の配置管理
- drag & drop / resize / 自由配置への将来拡張
- shared bundle を widget input に渡す最終接続

## 3.2 UI が持たない責務
- pressure / wall / trust / continuity などの意味判定
- market summary の shared owner
- alert candidate の shared owner
- replay / monitoring / execution と共有すべき digest の生成
- canonical / structural rebuild
- L3 相当の semantic 再定義

---

## 4. L4 と UI の境界

## 4.1 L4 がやること
L4 は、L3 の truth を shared に使いやすい単位へ束ねる。

例:
- market_summary_bundle
- liquidity_bundle
- semantic_timeline_bundle
- alert_candidate_bundle
- health_digest
- execution_signal_bundle

## 4.2 UI がやること
UI は、その bundle を widget に流し込んで表示する。

例:
- market_summary_bundle を cards に分解する
- liquidity_bundle を graph + badges に割り当てる
- semantic_timeline_bundle を timeline widget に渡す
- alert_candidate_bundle を alert widget に渡す

## 4.3 最重要ルール
L4 は「意味の束」を作る。
UI は「表示の束」を作る。

この境界を崩してはならない。

---

## 5. widget first 設計

## 5.1 基本思想
UI は page first ではなく widget first で組み立てる。

タブや画面は固定の巨大ページではなく、複数 widget の配置結果として表現する。

### 理由
- widget 単位追加に強くなる
- 更新頻度を個別化しやすい
- drag & drop / resize へ移行しやすい
- tab 間で widget を使い回しやすい

## 5.2 widget の最小責務
各 widget は原則として次だけを持つ。

- input contract を受ける
- 表示する
- ローカルな表示状態だけを持つ

widget 自身は shared meaning を作らない。

---

## 6. widget contract

## 6.1 widget input の基本形
各 widget は最低限次の契約で入力を受けることを想定する。

```text
widget_id
widget_kind
data_bundle
refresh_policy
layout_hint
style_override
layer_config
ui_context
```

## 6.2 各 field の意味
### widget_id
widget の一意識別子。

### widget_kind
widget 種別。
例:
- market_summary
- liquidity
- timeline
- alerts
- health
- executions

### data_bundle
L4 または thin adapter から渡される表示用入力。
ここに market meaning の最終 owner を持ち込まない。

### refresh_policy
更新頻度・更新契機。
例:
- manual
- fixed interval
- event driven
- hybrid

### layout_hint
初期配置やサイズの hint。
これは layout manager が使うが、意味 owner ではない。

### style_override
CSS や見た目の微調整。
shared meaning と混ぜない。

### layer_config
graph layer の重ね表示設定。
例:
- visible layers
- z-order
- opacity
- shared axis policy

### ui_context
言語、テーマ、表示モードなど UI 文脈。

---

## 7. widget registry

## 7.1 役割
widget registry は、widget の種類と実装を紐づける。

### 例
- widget kind → renderer
- widget kind → default refresh policy
- widget kind → supported data bundle types
- widget kind → default size / min size / resize policy

## 7.2 UI hub との関係
UI hub は registry を参照して widget を配置・描画する。
個別タブが勝手に独自 widget 解決を始めないほうがよい。

---

## 8. refresh policy

## 8.1 基本方針
widget ごとに更新頻度を個別設定できるようにする。

### 例
- high frequency: orderbook / executions
- medium frequency: market summary / liquidity digest
- low frequency: health / alerts / reports

## 8.2 UI の責務
UI は refresh timing を管理するが、意味そのものは作らない。

## 8.3 L4 の責務
L4 は data bundle を作るが、UI の polling / scheduling owner にはならない。

---

## 9. graph layer overlay

## 9.1 目的
単一 widget の中で複数の情報層を重ね表示できるようにする。

例:
- price layer
- liquidity layer
- signal layer
- alert marker layer
- event annotation layer

## 9.2 責務分離
### L4
重ね表示に使う元データの bundle を出す

### UI
どの layer を表示し、どう重ねるかを決める

### widget
与えられた layer config に従って描画する

---

## 10. CSS 微調整

## 10.1 基本方針
widget ごとの CSS 微調整は UI 側の責務とする。

## 10.2 禁止
- CSS 用都合を shared bundle に入れない
- L4 へ色・余白・カード順などの UI 都合を持ち込まない

---

## 11. drag & drop / resize / 自由配置

## 11.1 将来前提
将来的に `streamlit-elements` などによる drag & drop / resize / 自由配置に進める前提で設計する。

## 11.2 今の段階で必要なこと
現時点で固定すべきなのは、表示ライブラリではなく layout contract である。

つまり今は、
- widget id
- widget type
- size hint
- position hint
- resize capability
- group / tab affiliation

を持てるようにしておけばよい。

---

## 12. tab の考え方

## 12.1 tab はハブの grouping 単位
各 tab は「特別な意味 owner」ではなく、widget の grouping 単位として扱う。

### 例
- collector tab
- warroom tab
- health tab
- replay tab

## 12.2 禁止
タブごとに shared summary を別々に組み直すこと。

shared な入力は L4 から来る前提にする。

---

## 13. 推奨構造

```text
apps/operator_ui/
  hub/
    widget_registry.py
    layout_manager.py
    refresh_manager.py
    layer_manager.py
    style_manager.py
    widget_contracts.py

  widgets/
    market_summary_widget.py
    liquidity_widget.py
    timeline_widget.py
    alerts_widget.py
    health_widget.py
    executions_widget.py

  adapters/
    l4_ui_bundle_adapter.py

  views/
    ...
```

### 補足
現時点でこの構造へ即全面移行する必要はない。
ただし将来の正規像として保持する。

---

## 14. 実装時の判断ルール

### ルール1
その処理は意味を作っているか。
作っているなら UI に置かない。

### ルール2
その処理は複数 widget や複数 consumer で再利用できるか。
できるなら UI に閉じず L4 を疑う。

### ルール3
その処理は表示都合だけか。
表示都合だけなら UI 側でよい。

### ルール4
その処理は widget 個別差分か、それとも shared bundle か。
widget 個別差分なら UI adapter / widget に残す。

---

## 15. 一言でまとめると

```text
UI は意味を作る場所ではない。
L4 の束を受けて、widget を並べ、更新し、重ね、見せるための hub である。
```
