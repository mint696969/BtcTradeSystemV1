# path: ./docs/architecture/L4_PACKAGE_SKELETON_IMPLEMENTATION_PLAN_2026-04-05.md
# desc: Implementation plan for the initial L4 and UI package skeleton.
# L4 Package Skeleton Implementation Plan

更新日: 2026-04-05
位置づけ: 次フェーズで実際に package skeleton を作るための具体実装計画
対象: `btcts_next/src/btcts/processing/` と `btcts_next/src/btcts/apps/operator_ui/`
関連:
- `tmp/L4_UI_ADAPTER_WIDGET_STRUCTURE_SPEC_2026-04-05.md`
- `tmp/L3_L4_EVOLUTION_AND_COMPATIBILITY_POLICY_2026-04-05.md`
- `docs/architecture/L4_SHARED_FIRST_DESIGN_SPEC_2026-04-04.md`
- `docs/architecture/L4_OPERATOR_UI_ADAPTER_SPEC_2026-04-05.md`

---

## 1. この計画の目的
本計画は、L4 以降の責務分離を概念ではなく repository 構造として固定するために、次フェーズで最初に作る package skeleton を具体化するものである。

目的は次の4つ。

1. 後続 GPT が置き場所を誤らないようにする
2. L4 shared / adapter / widget の責務境界を器として固定する
3. 実装前に「どこまで空で作るか」を決めて過剰実装を防ぐ
4. 次の最小実装対象を `market_summary` に絞る

---

## 2. 結論
最初に作るのは、**全部入りの完成形ではなく、最小骨格**である。

### 先に作るもの
- `processing/l4_consumer_models/` package
- `shared/` package
- `operator_ui/` adapter package
- `apps/operator_ui/hub/` package
- `apps/operator_ui/presenters/` package
- `apps/operator_ui/widgets/` package

### まだ作らないもの
- monitoring / replay / ai_training / auto_trading の中身
- widget 実装本体
- heavy adapter 群
- graph library 依存コード

---

## 3. 最初に作る正規構造

```text
btcts_next/src/btcts/processing/
  l4_consumer_models/
    __init__.py
    shared/
      __init__.py
      market_summary.py
    operator_ui/
      __init__.py
      market_summary_adapter.py

btcts_next/src/btcts/apps/operator_ui/
  hub/
    __init__.py
  presenters/
    __init__.py
  widgets/
    __init__.py
```

### 重要点
- 最初は `market_summary` だけ通す
- 他 bundle 名はまだ空にしてよい
- 器を固定することが第一目的

---

## 4. 各ファイルの役割

## 4.1 `processing/l4_consumer_models/__init__.py`
### 役割
L4 consumer models package の入口。

### 初版内容
- package comment
- 「shared bundle と consumer adapter を置く」ことの明記

---

## 4.2 `processing/l4_consumer_models/shared/__init__.py`
### 役割
shared bundle package の入口。

### 初版内容
- shared-first の原則コメント
- `market_summary` が最初の bundle であることの明記

---

## 4.3 `processing/l4_consumer_models/shared/market_summary.py`
### 役割
L4 shared の最初の実コード対象。

### 初版内容
- `MarketSummary` dataclass
- `MarketSummaryBuildInput` dataclass
- `build_market_summary()`
- normalization helper

### 注意
- widget shape を入れない
- wording を入れない
- chart shape を入れない

---

## 4.4 `processing/l4_consumer_models/operator_ui/__init__.py`
### 役割
operator UI 向け thin adapter package の入口。

### 初版内容
- thin adapter の責務コメント
- shared truth を変えないことの明記

---

## 4.5 `processing/l4_consumer_models/operator_ui/market_summary_adapter.py`
### 役割
`MarketSummary` を UI widget 前段 input へ薄く変換する。

### 初版内容
- `MarketSummaryWidgetModel` dataclass
- `adapt_market_summary_for_widget()`
- key 化 helper

### 注意
- 文言は入れない
- CSS / layout は入れない
- widget library 依存 shape にしない

---

## 4.6 `apps/operator_ui/hub/__init__.py`
### 役割
UI hub package の器。

### 初版内容
- widget orchestration package であることの明記
- 将来 `registry / layout / refresh` が入ることの明記

### まだ作らないもの
- `widget_registry.py`
- `layout_manager.py`
- `refresh_manager.py`

今は器だけでよい。

---

## 4.7 `apps/operator_ui/presenters/__init__.py`
### 役割
widget が食う最終 shape を作る package の器。

### 初版内容
- presenter は render 前の shape 整形層であることの明記

---

## 4.8 `apps/operator_ui/widgets/__init__.py`
### 役割
widget 実装 package の器。

### 初版内容
- widget は render owner であることの明記

---

## 5. 初版で意図的に残す空白

### 残す空白1
monitoring / replay / ai_training / auto_trading adapter package は、今は作らない。

### 理由
- 今の主戦場は operator UI が一番分かりやすい
- 先に shared + UI の最小経路を作る方が安全

### 残す空白2
presenter / widget の本体も、今は作らない。

### 理由
- L4 shared と adapter の境界を先に固定したい
- UI 実装へ広げると手が広がる

---

## 6. 実装順序

### Step 1
package / directory skeleton を作る

### Step 2
`shared/market_summary.py` を作る

### Step 3
`operator_ui/market_summary_adapter.py` を作る

### Step 4
既存 `apps/operator_ui/market_state_service.py` と `market_monitor_*` を読み、adapter 接続点を決める

### Step 5
必要になったら `presenters/market_summary_presenter.py` を追加する

---

## 7. 最初の接続方針
最初の経路は次の形で十分。

```text
market_state_service.py
  ↓
L4 shared build_market_summary()
  ↓
operator_ui market_summary_adapter
  ↓
既存 component / panel へ最小接続
```

### ポイント
- 既存 UI を一気に壊さない
- まず 1 経路だけ shared-first へ差し替える
- 成功パターンを作ってから横展開する

---

## 8. 後続 GPT への明示ルール

### ルール1
最初の実装対象は `market_summary` に限定する。

### ルール2
`l4_consumer_models/shared/` に widget 最終入力 shape を置かない。

### ルール3
`operator_ui/market_summary_adapter.py` は thin に保つ。

### ルール4
UI の render / layout / wording は `apps/operator_ui/` 側に残す。

### ルール5
構造を整えるために、まだ使わない package を少数だけ空で作ってよい。

---

## 9. 実装時のレビュー観点

### 観点1
shared bundle に UI convenience が混ざっていないか

### 観点2
adapter が meaning owner 化していないか

### 観点3
widget / presenter を先走って作りすぎていないか

### 観点4
最初の変更が market_summary に閉じているか

---

## 10. 一言でまとめると

```text
最初に作るのは、
L4 shared / UI adapter / UI hub の完成形ではなく、
market_summary を通すための最小骨格である。
```
