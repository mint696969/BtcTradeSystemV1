# path: ./tmp/07_CONSUMER_ADAPTER_AND_WIDGET_BOUNDARY_SPEC_2026-04-11.md
# desc: Consumer Adapter and Widget Boundary Spec (merged current-truth sync after L4/UI responsibility alignment)

更新日: 2026-04-14
位置づけ: `docs/architecture/` 続きファイル候補 / L4 shared・consumer adapter・widget 境界固定
対象: `btcts_next/src/btcts/processing/l4_consumer_models/`, `btcts_next/src/btcts/apps/operator_ui/`, 将来の AI / strategy / execution / monitoring consumer

---

## 1. この仕様書の目的
本仕様書は、L3 / L4 / UI の責務分離を今後ぶらさないために、特に誤解されやすい次の境界を固定するための文書である。

1. L4 shared と consumer adapter の境界
2. consumer adapter と widget の境界
3. UI 専用 shape と、他 consumer で再利用できる shape の境界
4. `health_digest` のような次 bundle をどこまで L4 に置くべきかの判断基準

---

## 2. 結論
責務分離は次で読むのが正しい。

```text
L1 capture / raw persistence
  ↓
L2 canonical / structural truth
  ↓
L3 market meaning owner
  ↓
L4 shared consumer-neutral bundle
  ↓
consumer-specific adapter
  ↓
consumer-specific final model
  ↓
widget / page / execution entry / AI prompt input
```

### 一言
- L3 は意味を決める
- L4 shared は consumer が再利用しやすい shape に束ねる
- adapter は consumer 専用の薄変換を行う
- widget は表示するだけ

したがって、**他 consumer で使い回したいものは L4 shared に置く** のが正しい。
**UI adapter は UI 専用 thin layer** であり、再利用の中心ではない。

---

## 3. 用語の固定

## 3.1 L4 shared
consumer-neutral な shared bundle。
複数 consumer が読める形に整えた read model。

### 例
- `MarketSummary`
- `HealthDigest`
- 将来の `LiquiditySnapshotBundle`
- 将来の `SemanticTimelineBundle`

## 3.2 consumer adapter
shared bundle を特定 consumer が使いやすい shape に変換する薄い adapter。

### 例
- `operator_ui` adapter
- AI input adapter
- strategy input adapter
- monitoring adapter

## 3.3 widget
UI の描画単位。
widget model を受けて表示する責務を持つ。

### 例
- metric panel
- chart panel
- table panel
- caption panel

## 3.4 presenter / view
- presenter: 表示直前の line / card / table / badge 形へ整える
- view: page orchestration、並び順、slot 割当、layout 管理

---

## 4. 各レイヤーの責務

## 4.1 L3 の責務
L3 は **市場意味の唯一の owner** である。

### 含むもの
- trust
- continuity
- interpretation
- event family
- usage grade
- orderbook semantics
- microstructure semantics

### 含まないもの
- UI grouping
- widget model
- consumer-specific payload
- page wording
- CSS / layout
- AI prompt wording
- strategy-specific execution shape

### 原則
L3 は market meaning を決めるが、consumer shape を決めない。

---

## 4.2 L4 shared の責務
L4 shared は **consumer-neutral shape owner** である。

### 含むもの
- L3 truth の shared bundle 化
- additive-first な contract field の正規化
- 複数 consumer が共通で読みたい rows / slot presence / digest shape
- diagnostics のうち wording-free に共有できるもの

### 含まないもの
- 新しい market meaning の定義
- trust / continuity / interpretation の再判定
- UI wording
- widget layout
- CSS / tone / icon
- page-specific grouping
- strategy 固有の trigger 決定
- execution action 決定

### 原則
**他 consumer で使い回したいところまでを L4 に置く。**
それ以上 consumer 固有になった時点で adapter 以下へ落とす。

---

## 4.3 consumer adapter の責務
adapter は **consumer-specific thin transform** である。

### 含むもの
- field 名の変換
- consumer 向け subset 切り出し
- placeholder fallback
- flattening
- null-safe 補完
- consumer 用 final model 生成

### 含まないもの
- market meaning の再定義
- L3 / L4 truth の上書き
- 複数 consumer 共通で使いたい shape の定義
- widget 固有の render 処理

### 原則
adapter は thin に保つ。
shared へ上げられる logic を永続的に抱え込まない。

---

## 4.4 widget の責務
widget は **render owner** である。

### 含むもの
- metric / chart / table の描画
- layout 依存の表示
- Streamlit 依存処理
- ローカル表示状態
- UI caption / panel 表示

### 含まないもの
- shared bundle の構築
- market meaning の再判定
- consumer-neutral なデータ整形
- 他 consumer が再利用したい model 定義

### 原則
widget は受け取った model を表示するだけに寄せる。

---

## 5. 再利用の中心をどこに置くか
結論として、再利用の中心は **L4 shared** に置くのが正しい。

### 正しい再利用
```text
L4 shared
  ├─ operator_ui adapter
  ├─ ai adapter
  ├─ strategy adapter
  ├─ monitoring adapter
  └─ future consumer adapter
```

### 避けるべき再利用
```text
operator_ui adapter を他 consumer が直接使う
widget model を AI / strategy が直接使う
page payload を shared truth のように扱う
```

理由は、adapter / widget model には UI 都合が入りやすく、他 consumer の最適 shape とズレるためである。

---

## 6. `MarketSummary` を基準にした current success pattern
現時点で最も成功している例は `MarketSummary` 系である。

```text
market_state row
  ↓
L4 shared `MarketSummary`
  ↓
operator_ui adapter
  ↓
status payload / widget model
  ↓
bridge / presenter / widget / view
```

### current reading
- `semantic_usage_contract_rows`
- `orderbook_summary_slots_present`
- `orderbook_summary_slots_count`
- `orderbook_active_event_names`
- `orderbook_active_event_contracts`
- `orderbook_persistence_observable`

のような **他 consumer にも価値のある contract / shape** は shared にあるべきである。

また current repo truth では、shared mainline の reuse line は少なくとも次でかなり強まっている。

- `processing/l4_consumer_models/operator_ui/market_summary_adapter.py`
- `apps/operator_ui/components/market_state_bridge.py`
- `apps/operator_ui/components/market_summary_presenter.py`
- `apps/operator_ui/components/market_monitor_presenter.py`

一方で、caption 文や metric card の最終表示 shape は adapter / presenter / widget に残すのが正しい。
monitor / presenter / widget は shared line の **再整形** であって、meaning owner ではない。

---

## 7. 将来 consumer の基本形
今後増える consumer は、原則として次のように増やす。

## 7.1 operator UI
- shared bundle を読む
- thin adapter で widget model / payload へ変換する
- widget は描画のみ

## 7.2 AI consumer
- shared bundle を読む
- AI adapter で prompt-safe / reasoning-safe input model に変換する
- AI wording は AI adapter より下流で持つ

## 7.3 strategy / decision consumer
- shared bundle を読む
- strategy adapter で decision input model へ変換する
- signal threshold / decision policy は strategy owner 側で持つ

## 7.4 execution consumer
- shared bundle を読むことはあっても、execution 自体が meaning owner になってはならない
- execution は executor であり、meaning owner ではない

## 7.5 monitoring / audit consumer
- shared bundle を読む
- observer-only adapter で digest / alert input に変換する

---

## 8. `health_digest` をどこまで L4 に置くべきか
`health_digest` は、2026-04-13 時点では **current-state observer-only shared digest path reached** と読める。
そのうえで、broader split を formal 化する場合も次の線を守る。

### L4 shared に置いてよいもの
- freshness
- source_kind
- wiring_status
- semantic summary
- semantic usage contract rows
- semantic observer presence / contract row presence
- orderbook summary slot presence
- orderbook summary slot count
- orderbook active event names
- orderbook active event contracts
- persistence observable
- wording-free な runtime health digest

### adapter 以下に置くもの
- caption 文
- metric label
- badge 文言
- panel grouping
- page ごとの見せ方
- widget key / payload shaping

### L4 shared に置いてはいけないもの
- 新しい health meaning 判定
- 「売買してよい / 悪い」の判断
- widget 固有の card shape
- Streamlit 固有表現

### 一言
`health_digest` は future-only の想定ではなく、**current-state observer-only shared digest path reached** を前提に、timeline / anomaly / broader split を carry-forward formalization するのが正しい。

---

## 9. 判断ルール
新しい field / logic / bundle をどこへ置くか迷ったら、次の順で判定する。

## 9.1 L4 shared に置く条件
- 2 consumer 以上で使う
- wording-free に共有できる
- market truth を再定義していない
- contract / slot / digest として bundle 価値がある
- UI を離れても意味が通る

## 9.2 adapter に置く条件
- 1 consumer 専用である
- thin transform で済む
- shared truth を壊さない
- field rename / flatten / subset 程度である

## 9.3 widget / presenter に置く条件
- 表示ライブラリ依存である
- caption / bar / table / metric の shape である
- page 都合の並び順である
- i18n / human wording が必要である

## 9.4 置いてはいけない条件
- UI convenience のために meaning を作る
- shared の代わりに adapter を再利用基盤にする
- widget model を shared contract のように扱う
- adapter が second L3 になる

---

## 10. anti-pattern

### 10.1 UI adapter の shared 化
operator_ui adapter をそのまま AI / strategy が読む。

### なぜ危険か
- UI都合が混ざる
- flatten しすぎる
- wording / placeholder / panel都合が混じる

## 10.2 widget model の流用
widget model を contract と誤認する。

### なぜ危険か
- render 都合の shape は shared truth ではない
- UI変更で他 consumer が壊れる

## 10.3 L4 で meaning を再判定
L4 で trust / interpretation / event strength を作り直す。

### なぜ危険か
- second L3 化する
- owner 境界が崩れる

## 10.4 UI で暫定再計算
contract が足りないからといって page logic で near wall / support / resistance を再推定する。

### なぜ危険か
- UI convenience が意味 owner を侵食する

---

## 11. 今後の作業原則
今後の mainline 作業では、次を常に守る。

1. L3 は意味 owner のまま固定
2. 他 consumer で使い回したいものはまず L4 shared を疑う
3. consumer-specific な shape は adapter へ閉じる
4. widget は表示だけに寄せる
5. UI page は orchestration と layout に集中する
6. adapter / widget / page に meaning を置かない

---

## 12. 現在の推奨アクション
この仕様に沿うなら、次の順で進めるのが自然である。

1. `health_digest` current-state line を docs 上で current truth に合わせて固定する
2. そのうえで broader split を
   - shared に置く field
   - adapter に置く field
   - widget にしか置かない field
   に三分割する
3. 実装は additive-first で shared bundle を増やす
4. UI 側はその bundle を読むように薄く寄せる

---

## 13. 一言
今後の責務分離をぶらさないための最重要原則は、

**「再利用したいものは L4 shared に置き、consumer-specific な最終 shape は adapter に置き、widget は表示だけにする」**

である。

この原則を守れば、UI / AI / strategy / monitoring などの consumer が増えても、L3 owner 境界を崩さずに拡張しやすい。
