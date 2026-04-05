# path: ./docs/architecture/L4_SHARED_FIRST_MIGRATION_CHECKLIST_2026-04-04.md
# desc: Migration checklist for adopting the L4 shared-first design.
# L4 Shared-First 移行チェックリスト

更新日: 2026-04-04
位置づけ: L4 初期実装着手用 checklist / docs 再配置用ドラフト
前提:
- `tmp/LAYER_RESPONSIBILITY_RUNTIME_SPEC_2026-04-04.md`
- `tmp/L4_SHARED_FIRST_DESIGN_SPEC_2026-04-04.md`

---

## 1. このチェックリストの目的
このチェックリストは、現行コードに散っている consumer 向け整形責務を、L4 shared-first の考え方で安全に移行するための実務用メモである。

目的は次の3つ。

1. 何から移すべきかを明確にする
2. shared に寄せるものと consumer に残すものを分ける
3. L3 / consumer / execution の責務逆流を防ぐ

---

## 2. 移行の基本原則

### 原則1
最初に shared を疑う。

### 原則2
consumer 固有に見える処理でも、他で再利用できる構造部分は shared に切り出す。

### 原則3
wording / UI 表示文言 / 画面都合の並び替えだけを consumer adapter に残す。

### 原則4
L4 で新しい意味を作らない。

### 原則5
L3 の truth owner を薄めない。

---

## 3. 先に作るべき L4 package 骨格

- [ ] `processing/l4_consumer_models/__init__.py`
- [ ] `processing/l4_consumer_models/shared/__init__.py`
- [ ] `processing/l4_consumer_models/operator_ui/__init__.py`
- [ ] `processing/l4_consumer_models/monitoring/__init__.py`
- [ ] `processing/l4_consumer_models/replay/__init__.py`
- [ ] `processing/l4_consumer_models/ai_training/__init__.py`
- [ ] `processing/l4_consumer_models/auto_trading/__init__.py`

### 判定
- ✅ package の器だけを先に作る
- ❌ 中身が固まる前に雑多な helper を詰め込まない

---

## 4. Phase 1: 最初に shared 化する対象

# 4.1 market summary

## 移行元候補
- `apps/operator_ui/market_state_service.py`
- `apps/operator_ui/components/market_monitor_logic.py`
- `apps/operator_ui/components/market_monitor_presenter.py`
- `apps/operator_ui/components/status_panel.py`

## shared へ寄せるもの
- 市場状態の共通 summary struct
- continuity / trust / liquidity / participation の共通 summary field
- UI 固有 wording ではない状態ラベル

## consumer 側に残すもの
- Streamlit 表示順
- metric card 表示名
- caption wording
- 色や tone の UI 都合

## チェック
- [ ] summary の中に UI 文言が混ざっていない
- [ ] summary の中に新しい semantic 判定が混ざっていない
- [ ] summary が monitoring / replay にも流用できる形か確認した

---

# 4.2 semantic timeline

## 移行元候補
- `apps/operator_ui/components/warroom_timeline.py`
- `apps/operator_ui/components/decision_log_panel.py`
- `replay/*timeline*` 相当ロジック

## shared へ寄せるもの
- timeline event row の共通 shape
- event grouping key
- severity / evidence / category field
- wording 前の normalized event bundle

## consumer 側に残すもの
- 表示列の選択
- アイコンや色
- 日本語/英語 wording
- page 固有の絞り込み UI

## チェック
- [ ] timeline row が wording-free になっている
- [ ] timeline row が UI と replay で共有可能か確認した
- [ ] event の意味を adapter 側で再判定していない

---

# 4.3 alert candidates

## 移行元候補
- `apps/operator_ui/components/warroom_alert_logic.py`
- `apps/operator_ui/components/warroom_alert_presenter.py`
- `apps/operator_ui/components/risk_monitor_panel.py`
- monitoring 相当の通知ロジック候補

## shared へ寄せるもの
- candidate_type
- severity
- confidence
- evidence_refs
- escalation_hint

## consumer 側に残すもの
- 通知文言
- operator 向け phrasing
- suppress / mute の UI 操作

## チェック
- [ ] alert candidate が wording を持っていない
- [ ] alert candidate が monitoring と operator UI で共用可能か確認した
- [ ] shared candidate で新しい semantic を作っていない

---

## 5. Phase 2: 次に shared 化する対象

# 5.1 liquidity bundle

## 移行元候補
- `apps/operator_ui/components/liquidity_pressure_panel.py`
- `apps/operator_ui/components/trade_flow_monitor.py`
- `apps/operator_ui/components/market_regime_panel.py`

## shared へ寄せるもの
- wall summary
- pressure summary
- pull/refill summary
- sweep/absorption summary
- zone-aware liquidity snapshot

## consumer 側に残すもの
- panel 配置
- chart / card 分割
- threshold に応じた見せ方の UI 差分

## チェック
- [ ] panel ごとの convenience field が shared を汚していない
- [ ] UI 表示都合の値を shared へ持ち込んでいない

---

# 5.2 health digest

## 移行元候補
- `apps/operator_ui/health_data_service.py`
- `apps/operator_ui/health_truth.py`
- `apps/operator_ui/components/health_*`

## shared へ寄せるもの
- health の共通 digest
- freshness / continuity / degradation の共通要約
- monitoring と operator が共用できる基礎 state

## consumer 側に残すもの
- panel wording
- chart 用色付け
- UX 上の grouping

## チェック
- [ ] digest が monitoring にも流せる形か確認した
- [ ] UI wording が混ざっていない

---

## 6. Phase 3: execution / replay / AI へ広げる対象

# 6.1 execution signal bundle

## 移行元候補
- `market_engine/market_state/projector.py`
- `market_engine/execution/*.py`
- `market_engine/profiles/*.py`

## shared へ寄せるもの
- directional bias
- entry caution flags
- structure trust gate
- liquidity availability hint
- regime compatibility hint

## execution 側に残すもの
- 実行順序
- policy 適用順
- venue 実装差分
- scheduler / runtime lifecycle

## チェック
- [ ] execution 都合で shared truth を曲げていない
- [ ] profile policy と shared signal の境界を説明できる

---

# 6.2 replay bundle

## 移行元候補
- `replay/*report*.py`
- `replay/*fusion*.py`
- `replay/*pipeline*.py`

## shared へ寄せるもの
- semantic timeline bundle
- replay-ready summary bundle
- comparative digest の前段共通 shape

## replay 側に残すもの
- seek / scrub / compare UI
- replay session 固有の制御
- export / report formatting

## チェック
- [ ] replay 専用 convenience と shared summary が混ざっていない
- [ ] replay が L3 owner を再実装していない

---

# 6.3 AI / auto_trading bundle

## 移行元候補
- 今後設計対象

## shared へ寄せるもの
- feature/label bundle の共通 shape
- decision-ready summary
- provenance を持つ共通 signal bundle

## adapter 側に残すもの
- 学習フォーマット
- 戦略パラメータ適用
- routing / execution endpoint 固有事情

## チェック
- [ ] AI / auto_trading の都合で meaning owner を増やしていない

---

## 7. ファイルごとの初回棚卸し対象

### operator_ui
- [ ] `apps/operator_ui/market_state_service.py`
- [ ] `apps/operator_ui/health_data_service.py`
- [ ] `apps/operator_ui/health_truth.py`
- [ ] `apps/operator_ui/components/market_monitor_logic.py`
- [ ] `apps/operator_ui/components/market_monitor_presenter.py`
- [ ] `apps/operator_ui/components/warroom_alert_logic.py`
- [ ] `apps/operator_ui/components/warroom_alert_presenter.py`
- [ ] `apps/operator_ui/components/warroom_timeline.py`
- [ ] `apps/operator_ui/components/liquidity_pressure_panel.py`
- [ ] `apps/operator_ui/components/trade_flow_monitor.py`

### market_engine
- [ ] `market_engine/market_state/projector.py`
- [ ] `market_engine/market_state/schema.py`
- [ ] `market_engine/market_state/writer.py`
- [ ] `market_engine/execution/realtime_engine.py`
- [ ] `market_engine/execution/replay_engine.py`

### replay
- [ ] `replay/replay_fusion.py`
- [ ] `replay/replay_report.py`
- [ ] `replay/strategy_report.py`
- [ ] `replay/regime_report.py`

---

## 8. 移行時のレビュー質問
各ファイルを触る前に、毎回これを問う。

- [ ] これは shared にできるか
- [ ] これは wording か structure か
- [ ] これは L3 の意味 owner を侵食していないか
- [ ] これは consumer 固有都合だけか
- [ ] これは execution 制御であって L4 ではないか

1つでも曖昧なら、いきなり移さずメモを先に作る。

---

## 9. NG パターン
- [ ] UI panel helper をそのまま shared へ移す
- [ ] wording 付き summary を shared model にする
- [ ] L4 で trust / continuity を再判定する
- [ ] execution 用 signal のために semantic 条件を増やす
- [ ] 「とりあえず便利だから」で L4 を雑多 helper 置き場にする

---

## 10. 最初の実装着手順

### Step 1
- [ ] `processing/l4_consumer_models/` package skeleton を作る

### Step 2
- [ ] operator_ui から `market summary` 候補を抽出する
- [ ] wording / presentation を除いた shared field を定義する

### Step 3
- [ ] semantic timeline の shared row 定義を作る

### Step 4
- [ ] alert candidate bundle の shared 定義を作る

### Step 5
- [ ] operator_ui adapter を薄く作り、shared model から描画できる最小経路を作る

### Step 6
- [ ] monitoring / replay でも shared を再利用できるか確認する

---

## 11. 一言でまとめると

```text
L4 移行は、
最初に shared を作り、
consumer 固有要素は最後に薄く残す。
これを崩すと L4 はすぐ便利層になって壊れる。
```
