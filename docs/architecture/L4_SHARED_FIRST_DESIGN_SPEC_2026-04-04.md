# path: ./docs/architecture/L4_SHARED_FIRST_DESIGN_SPEC_2026-04-04.md
# desc: Shared-first design spec for L4 consumer models.
# L4 Shared-First 設計仕様書

更新日: 2026-04-04
位置づけ: next phase 設計初版 / docs 再配置用ドラフト
対象: `btcts_next/src/btcts/processing/l4_consumer_models/` の将来設計

---

## 1. この仕様書の目的
本仕様書は、BTC Trade System vNext における L4 の役割を明確化し、今後 `processing/l4_consumer_models/` を設計・実装するための初版仕様を定義する。

L4 の目的は、L3 が定義した共有市場意味を、consumer ごとに使いやすい形へ整えることである。
ただし、L4 は新しい意味を定義してはならない。

本仕様書の主目的は次の4つ。

1. L4 を second L3 にしないための境界を固定する
2. shared-first 原則を具体化する
3. 既存 consumer / market_state / UI 側に散っている整形責務の受け皿を定義する
4. 将来の UI / replay / monitoring / AI / execution で共通利用できるモデル層の方向を固める

---

## 2. L4 とは何か
L4 は、L3 の shared truth を consumer 利用向けに再構成する層である。

一言で言うと、

```text
L3 が「市場はどういう意味か」を決め、
L4 が「その意味をどう使いやすい形で束ねるか」を決める。
```

L4 は次の役割を持つ。

- shared な digest を作る
- timeline-ready な event bundle を作る
- panel / page / monitoring / replay が利用しやすい read model を作る
- consumer 専用差分を最小化する

L4 は次の役割を持たない。

- 新しい market meaning の定義
- trust / continuity / pressure の owner 化
- raw/canonical reconstruction
- daemon / runtime / scheduler 制御

---

## 3. shared-first 原則

### 3.1 基本原則
L4 は、最初から consumer 専用に分岐しない。
先に「複数 consumer で共有できる形」を作り、最後に薄い adapter を噛ませる。

つまり順番は次である。

```text
L3 truth
  ↓
L4 shared models
  ↓
L4 thin consumer adapters
  ↓
Consumers
```

### 3.2 この原則が必要な理由
shared-first にしないと、次の問題が起きる。

- UI 用 summary と replay 用 summary がズレる
- monitoring 用 alert candidate と operator 用 warning が別物になる
- execution 用 signal bundle と AI 用 feature bundle が重複する
- consumer ごとに意味境界が再び崩れる

### 3.3 shared-first の判断基準
その整形が次のどれかに当てはまるなら、まず shared を疑う。

- 2つ以上の consumer が使う
- 市場状態の共通要約である
- timeline / digest / bundle として再利用できる
- wording ではなく structure である
- domain meaning を変えずに shape だけ整えている

---

## 4. L4 の責務

## 4.1 L4 が担当するもの
- shared market summary model
- shared liquidity snapshot bundle
- shared event timeline bundle
- shared alert candidate bundle
- shared health digest
- shared execution-ready signal bundle
- shared replay-ready semantic stream bundle
- shared AI-ready feature bundle
- consumer adapter 用の薄い data shape

## 4.2 L4 が担当しないもの
- pressure/wall/sweep/trust/continuity の判定本体
- consumer wording
- Streamlit widget 直接描画データの最終加工
- alert 文言生成
- scheduling / lifecycle / watchdog logic
- venue-specific raw reconstruction

## 4.3 L4 の本質
L4 は、

- truth の owner ではない
- storage owner でもないことが多い
- shape owner である

ここを崩すと L3 と consumer の間に新しい責務混在が生まれる。

---

## 5. 入出力の考え方

## 5.1 入力
L4 の主要入力は次を想定する。

- L3 semantic state
- L3 semantic event
- feature summary
- L2 canonical summary
- market_engine / market_state 側の projection context
- consumer contract

### 補足
L4 は必要に応じて L2 や features を参照してよいが、真実の主役は L3 に置く。
L2 や features の直接利用は、意味を作るためではなく補助 shape を作るために限る。

## 5.2 出力
L4 の出力は次のような shared read model を想定する。

- market_summary
- liquidity_snapshot_bundle
- semantic_timeline_bundle
- alert_candidate_bundle
- replay_view_bundle
- ai_feature_bundle
- execution_signal_bundle
- monitoring_digest

## 5.3 永続化方針
2026-04-04 時点では、L4 の永続出力先は未固定である。

ただし方針は次の通り。

- L4 はまず in-memory / handoff shape から設計する
- 永続化は consumer bridge と market_state 接続を見ながら決める
- 共有価値が高いものだけを shared output として保存対象にする

---

## 6. 推奨フォルダ構造

```text
btcts_next/src/btcts/processing/l4_consumer_models/
  __init__.py
  shared/
    market_summary.py
    liquidity_bundle.py
    semantic_timeline.py
    alert_candidates.py
    health_digest.py
    execution_signal_bundle.py
    replay_bundle.py
    ai_feature_bundle.py

  operator_ui/
    presenter_models.py
    panel_models.py

  monitoring/
    digest_models.py
    notification_models.py

  replay/
    replay_models.py
    timeline_models.py

  ai_training/
    dataset_models.py
    label_bundle.py

  auto_trading/
    decision_models.py
    routing_models.py
```

### 重要点
- shared を最上位に置く
- per-consumer は最後の薄い adapter のみ
- 新しい意味 owner を per-consumer に作らない

---

## 7. shared で持つべき代表モデル

## 7.1 market_summary
### 目的
市場全体の状態を複数 consumer で共有できるようにする。

### 入力
- L3 の regime / continuity / trust / pressure / zone summary

### 出力例
- market_state_label
- trust_state
- continuity_state
- liquidity_bias
- participation_state
- notable_events

### 利用先
- operator UI
- monitoring
- replay summary
- AI training metadata

---

## 7.2 liquidity_snapshot_bundle
### 目的
orderbook / tradeflow / microstructure の重要断面を1束にする。

### 入力
- L3 orderbook semantics
- L3 tradeflow semantics
- features summary

### 出力例
- wall summary
- pressure summary
- pull / refill summary
- recent sweep / absorption summary
- zone-aware liquidity view

### 利用先
- operator UI panels
- replay
- execution support

---

## 7.3 semantic_timeline_bundle
### 目的
L3 semantic events を時系列利用しやすい shape に整える。

### 入力
- L3 semantic event stream
- trust / continuity event

### 出力例
- normalized timeline rows
- event severity
- event grouping key
- display-ready but wording-free tags

### 利用先
- operator timeline
- replay timeline
- monitoring review

---

## 7.4 alert_candidate_bundle
### 目的
consumer ごとの通知文言を作る前段として、共有 alert candidate を作る。

### 入力
- L3 semantic state
- health / continuity / trust state

### 出力例
- candidate_type
- severity
- confidence
- evidence_refs
- escalation_hint

### 利用先
- monitoring
- operator UI warning panels
- decision support

---

## 7.5 execution_signal_bundle
### 目的
execution layer が直接 consumer presentation に依存せずに利用できる共有 signal bundle を作る。

### 入力
- L3 semantics
- profile policy input
- market_state context

### 出力例
- directional bias
- entry caution flags
- structure trust gate
- liquidity availability hint
- regime compatibility hint

### 利用先
- market_engine/execution
- auto_trading
- AI training label assist

---

## 8. consumer adapter の役割
shared model の上に載る consumer adapter は薄く保つ。

## 8.1 operator_ui adapter
- panel ごとの field 名へ整形
- 並び順・表示グループの付与
- wording 直前の shape 調整

## 8.2 monitoring adapter
- 通知 payload 形への変換
- severity routing 用 shape
- suppression / grouping の補助 key 付与

## 8.3 replay adapter
- replay timeline shape
- scrub / seek / time bucket 対応 shape

## 8.4 AI adapter
- dataset row bundle
- label / feature alignment shape

## 8.5 execution adapter
- runtime が参照しやすい signal struct
- policy engine が扱いやすい compact bundle

### 原則
adapter は薄く、shared を壊さない。
「adapter の中で意味を生やす」のは NG。

---

## 9. 既存実装からの移行対象
2026-04-04 時点では、L4 専用 package は未展開であり、consumer 向け整形責務は一部既存コードに散っている。

主な移行候補は次。

### operator UI 側
- `apps/operator_ui/market_state_service.py`
- `apps/operator_ui/health_data_service.py`
- `apps/operator_ui/health_truth.py`
- `apps/operator_ui/components/*presenter*.py`
- `apps/operator_ui/components/*logic*.py`

### market_engine 側
- `market_engine/market_state/projector.py`
- `market_engine/market_state/schema.py`
- `market_engine/market_state/writer.py`

### replay 側
- `replay/*report*.py`
- `replay/*fusion*.py`
- timeline / summary 相当の整形責務

### 注意
これらは一気に移すのではなく、

1. shared 化できる責務を抽出
2. consumer 専用残しを薄くする
3. L3 ownership と競合しないことを確認

の順で進める。

---

## 10. 禁止事項

### 禁止1
L4 で新しい market meaning を定義する

### 禁止2
L4 で trust / continuity の owner を再定義する

### 禁止3
consumer convenience のために L2/L3 の境界を壊す

### 禁止4
UI wording を shared model に混ぜる

### 禁止5
execution 専用都合で shared truth を曲げる

### 禁止6
L4 を「何でも置ける便利層」にする

---

## 11. 実装順序の推奨
L4 は次の順で実装する。

### Phase 1
- `shared/market_summary.py`
- `shared/semantic_timeline.py`
- `shared/alert_candidates.py`

### Phase 2
- `shared/liquidity_bundle.py`
- `shared/health_digest.py`
- operator_ui adapter 初版

### Phase 3
- `shared/execution_signal_bundle.py`
- monitoring adapter
- replay adapter

### Phase 4
- AI / auto_trading adapter
- shared output 永続化方針の固定

---

## 12. L4 完了の定義
L4 が「着手済み」ではなく「成立した」と言うための条件は次。

- shared package が実体として存在する
- operator_ui / monitoring / replay の少なくとも2つが shared model を使う
- consumer 側で新しい market meaning を作っていない
- execution / UI / replay の summary が共通 shared truth に基づく
- L3 と L4 の責務境界が review 可能な形で保たれている

---

## 13. 今の一言まとめ

```text
L4 は、L3 の共有意味を shared-first で利用向けモデルへ変換する層であり、
新しい意味を作る層ではない。
```
