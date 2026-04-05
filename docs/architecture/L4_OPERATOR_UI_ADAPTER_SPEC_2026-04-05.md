# path: ./docs/architecture/L4_OPERATOR_UI_ADAPTER_SPEC_2026-04-05.md
# desc: Boundary spec for thin operator UI adapters over L4 shared bundles.
# L4 Operator UI Adapter 仕様書

更新日: 2026-04-05
位置づけ: L4 shared bundle と operator UI の境界仕様
対象: `btcts_next/src/btcts/apps/operator_ui/` と将来の `processing/l4_consumer_models/operator_ui/`
関連:
- `tmp/tmp/L4_SHARED_FIRST_DESIGN_SPEC_2026-04-04.md`
- `tmp/tmp/L4_MARKET_SUMMARY_FIELD_SPEC_2026-04-04.md`
- `tmp/tmp/L4_MARKET_SUMMARY_BUILDER_SKELETON_SPEC_2026-04-04.md`
- `tmp/tmp/UI_HUB_WIDGET_ARCHITECTURE_SPEC_2026-04-04.md`

---

## 1. この仕様書の目的
本仕様書は、L4 shared bundle を operator UI が受け取るときの「薄い adapter 層」の責務を固定するための仕様である。

この仕様書が必要な理由は次の通り。

1. shared bundle をそのまま UI に流すと、UI convenience の要求で L4 が汚れやすい
2. 逆に UI 側で独自 summary を作り始めると、L4 shared-first 原則が崩れる
3. その中間に「薄い adapter」を定義すると、shared と UI の責務が安定する

---

## 2. 結論
operator UI adapter は、次の役割だけを持つ。

```text
L4 shared bundle
  ↓
operator_ui adapter
  ↓
widget input model
  ↓
widget render
```

つまり adapter は、

- shared truth を変えない
- widget が食べやすい形に薄く変換する
- UI 文脈を最後に与える

だけを担当する。

---

## 3. adapter の責務

## 3.1 やってよいこと
- 空値の placeholder 方針を適用する
- field 名を widget input contract に合わせる
- badge / chip / card 用の薄い表示カテゴリへ落とす
- icon key / tone key / severity key のような UI key を付与する
- 表示順序に必要な最小 group key を与える
- widget 種別ごとに必要な subset を切り出す

## 3.2 やってはいけないこと
- 新しい市場意味を作る
- trust / continuity / pressure を再判定する
- alert scoring を重く作り直す
- shared bundle の source truth を上書きする
- CSS や layout grid を決める
- refresh interval を埋め込む

---

## 4. L4 shared / UI adapter / widget の境界

## 4.1 L4 shared
- market_summary
- liquidity_bundle
- semantic_timeline_bundle
- alert_candidate_bundle
- health_digest

### 性質
- wording-free
- layout-free
- consumer 横断で再利用可能

## 4.2 operator_ui adapter
- widget input model を作る
- UI key を最小限与える
- placeholder や空値の扱いを揃える

### 性質
- thin
- UI aware
- ただし meaning unaware

## 4.3 widget
- 渡された input model を描画する
- ローカル表示状態だけを持つ

### 性質
- render only
- panel / graph / table の実装責務

---

## 5. market_summary adapter の具体像

## 5.1 入力
- `MarketSummary`

## 5.2 出力
例として、widget 向けの次のような input model を許容する。

```python
@dataclass(frozen=True)
class MarketSummaryWidgetModel:
    widget_kind: str
    freshness_key: str
    trust_key: str | None
    continuity_key: str | None
    interpretation_key: str | None
    headline_key: str | None
    notable_tags: list[str]
    alert_tags: list[str]
    age_sec: float | None
    event_ts: str | None
    source_kind: str
```

### 注意
- これは UI model であり shared bundle ではない
- `*_key` は表示文そのものではない
- i18n 文言解決は presenter / text layer に残す

---

## 6. key と wording の関係

## 6.1 adapter が出すもの
- `freshness_key = "LIVE"`
- `trust_key = "trusted"`
- `headline_key = "normal"`
- `notable_tags = ["stale_source"]`

## 6.2 presenter / text layer がやること
- `"LIVE" -> "ライブ"`
- `"trusted" -> "信頼可能"`
- tag に対応する説明文を引く

### 原則
adapter は key を出す。文言は出さない。

---

## 7. 空値と placeholder

## 7.1 shared bundle
`None` や空 list をそのまま持てる。

## 7.2 adapter
widget 実装が単純になるよう、必要なら placeholder policy を適用してよい。

### 例
- `None -> "unknown" key`
- 空 list -> `[]` のまま

### 注意
placeholder は UI key に留める。
自然文や装飾済み文字列にはしない。

---

## 8. UI key の種類
adapter が作ってよい UI key は次のようなものに限る。

- badge key
- chip key
- severity key
- icon key
- tone key
- group key

### 禁止
- CSS class 名
- 色コード
- grid column index
- refresh 秒数
- drag & drop 座標

これらは UI hub 側の責務。

---

## 9. operator_ui adapter の推奨配置

```text
processing/l4_consumer_models/operator_ui/
  market_summary_adapter.py
  liquidity_adapter.py
  timeline_adapter.py
  alert_adapter.py
  health_adapter.py
```

### 重要
adapter は UI package ではなく、まず L4 配下に置く想定でもよい。
理由は「consumer 固有だが shared truth に近い境界」を明示できるから。

ただし、現行実装への漸進移行中は `apps/operator_ui/` 側に暫定配置してもよい。
最終的には責務で移す。

---

## 10. 初版で対象にする adapter
実装優先順位は次。

1. `market_summary_adapter`
2. `health_adapter`
3. `timeline_adapter`
4. `alert_adapter`
5. `liquidity_adapter`

理由:
- market_summary は最も shared 化しやすい
- UI 全体の薄化に効く
- 他 widget の設計基準になる

---

## 11. review 観点
adapter 実装時は毎回次を問う。

- これは meaning を増やしていないか
- これは wording ではなく key か
- これは widget 固有すぎて adapter ではなく widget 側でよいのではないか
- これは shared に昇格すべきではないか

---

## 12. 一言でまとめると

```text
operator UI adapter は、
L4 shared bundle を壊さずに widget input へ薄く変換するための境界層であり、
新しい意味やレイアウトを持ってはならない。
```
