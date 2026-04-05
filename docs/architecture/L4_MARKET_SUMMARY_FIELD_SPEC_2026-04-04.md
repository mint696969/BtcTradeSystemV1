# path: ./docs/architecture/L4_MARKET_SUMMARY_FIELD_SPEC_2026-04-04.md
# desc: Field contract spec for the L4 market summary shared bundle.
# L4 Market Summary 具体フィールド定義仕様書

更新日: 2026-04-04
位置づけ: L4 shared-first 実装着手用の具体 field spec
対象: `btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py` 想定
関連:
- `docs/architecture/VNL_LAYER_RESPONSIBILITY_RUNTIME_SPEC_2026-04-04.md`
- `docs/architecture/VNL_L4_SHARED_FIRST_DESIGN_SPEC_2026-04-04.md`
- `tmp/tmp/UI_HUB_WIDGET_ARCHITECTURE_SPEC_2026-04-04.md`

---

## 1. この仕様書の目的
本仕様書は、L4 shared における `market_summary` の最小 field contract を固定するための具体仕様である。

目的は次の4つ。

1. market summary を UI 専用 convenience object にしない
2. monitoring / replay / AI / trading / logic でも再利用できる shared bundle にする
3. operator UI から shared 化しやすい最小単位を決める
4. L4 と UI adapter の境界を具体 field レベルで固定する

---

## 2. market summary の位置づけ
`market_summary` は、L3 の shared truth を「市場全体の現在状態をざっくり掴むための共通 summary」として束ねた L4 shared bundle である。

これは UI の card 専用データではない。
また、monitoring 専用 digest でもない。

一言で言うと、

```text
market_summary は、
現在の市場状態を consumer 横断で共有するための最小 summary bundle である。
```

---

## 3. 原則

### 原則1
L3 が意味 owner。
`market_summary` は意味を再定義しない。

### 原則2
`market_summary` は wording-free。
表示文や日本語 caption を含めない。

### 原則3
`market_summary` は layout-free。
列順、card 順、色、CSS、widget 配置情報を含めない。

### 原則4
`market_summary` は shared-first。
operator UI 以外でも利用できる field に限る。

### 原則5
UI 専用の差分は UI adapter 側へ残す。

---

## 4. 想定入力源
`market_summary` は次の情報源から構成される想定とする。

### 主入力
- L3 continuity / trust / interpretation 系 state
- market_state の overview record

### 補助入力
- source freshness 判定
- source 系 diagnostics
- 必要に応じて L2/L3 から来る notable flags

### 現行 operator_ui で近い材料
- `apps/operator_ui/market_state_service.py`
- `apps/operator_ui/components/market_monitor_logic.py`
- 将来的には L4 shared builder 経由へ寄せる

---

## 5. market_summary の最小 field 定義

以下を **初版の必須 field** とする。

# 5.1 identity / provenance

## `summary_type: str`
固定値候補: `market_summary`

### 目的
bundle 種別を明示する。

---

## `exchange: str | None`
例: `bitflyer`

### 目的
市場識別の一部。

---

## `symbol_raw: str | None`
例: `BTC_JPY`

### 目的
銘柄識別。

---

## `market_uid: str | None`
例: `bitflyer.spot.BTC_JPY`

### 目的
consumer 横断の一意識別補助。

---

## `source_kind: str`
候補例:
- `market_state_live`
- `market_state_preferred`
- `live_canonical`
- `replay_fallback`
- `unknown`

### 目的
summary がどの経路由来かを shared に示す。

### 注意
これは source label の raw contract であり、UI 向け表示文ではない。

---

## `source_series_id: str | None`

### 目的
series / continuity 系の provenance をたどる補助。

---

# 5.2 time / freshness

## `event_ts: str | None`
優先候補:
- `collector_ts`
- `exchange_ts`
- summary 生成時に採用した基準 ts

### 目的
summary の基準時刻。

---

## `age_sec: float | None`

### 目的
freshness 判定の元値。

### 注意
UI はこの値を元に表示を変えてよいが、色や wording はここに持ち込まない。

---

## `freshness: str`
候補例:
- `LIVE`
- `QUIET`
- `STALE`
- `UNKNOWN`

### 目的
consumer が summary の鮮度を共通的に扱えるようにする。

---

## `is_stale: bool | None`

### 目的
条件分岐を軽くする補助 field。

---

# 5.3 market interpretation core

## `trust_state: str | None`
候補例:
- `trusted`
- `provisional`
- `broken`

### 目的
L3 trust の shared summary.

---

## `continuity_state: str | None`
候補例:
- `continuous`
- `resynced`
- `broken`
- `unknown`

### 目的
L3 continuity の shared summary.

---

## `interpretation_bucket: str | None`
候補例:
- `allow_structural_use`
- `review_required`
- `unsafe`

### 目的
L3 interpretation の使用可能性 summary.

---

## `interpretation_reason: str | None`

### 目的
bucket の簡潔な機械可読理由。

### 注意
ここは UI 向け自然文ではなく、reason code / short reason の粒度を維持する。

---

# 5.4 market condition headline

## `market_state_label: str | None`
例:
- `normal`
- `imbalanced`
- `fragile`
- `transition`

### 目的
市場状態の headline を shared に渡す。

### 注意
初版で未使用なら `None` でよい。
将来的な L3/L4 接続拡張余地として確保する。

---

## `participation_state: str | None`
例:
- `active`
- `thin`
- `quiet`

### 目的
市場参加度の headline.

### 注意
これも初版で未使用なら `None` 可。

---

## `liquidity_bias: str | None`
例:
- `bid_support`
- `ask_pressure`
- `balanced`

### 目的
板・流動性バイアスの headline.

### 注意
これを UI 独自ロジックで決めない。
shared に昇格する時だけ L4 へ入れる。

---

# 5.5 notable summary

## `notable_events: list[str]`
例:
- `fresh_snapshot`
- `resync_recent`
- `trust_degraded`
- `stale_source`

### 目的
複数 consumer が使える notable flags を共通で持つ。

### 注意
文言ではなく tag として扱う。

---

## `alert_candidates: list[str]`
例:
- `review_required`
- `stale_market_state`
- `trust_not_trusted`

### 目的
alert candidate bundle ほど重くない最小フラグ群。

### 注意
本格 alert 情報は別 bundle に切り出す余地あり。
初版では軽量 flag に留める。

---

# 5.6 diagnostics

## `diagnostics: dict[str, object]`
初版の想定 subfield 例:
- `preferred_row_freshness`
- `preferred_row_age_sec`
- `latest_part_age_sec`
- `latest_part_exists`

### 目的
運用・デバッグ・比較確認のための補助情報。

### 注意
肥大化させない。
consumer が常用する主 contract は top-level field で表現する。

---

## 6. 初版 dataclass イメージ

```python
@dataclass
class MarketSummary:
    summary_type: str
    exchange: str | None
    symbol_raw: str | None
    market_uid: str | None
    source_kind: str
    source_series_id: str | None
    event_ts: str | None
    age_sec: float | None
    freshness: str
    is_stale: bool | None
    trust_state: str | None
    continuity_state: str | None
    interpretation_bucket: str | None
    interpretation_reason: str | None
    market_state_label: str | None
    participation_state: str | None
    liquidity_bias: str | None
    notable_events: list[str]
    alert_candidates: list[str]
    diagnostics: dict[str, object]
```

---

## 7. UI adapter に残すもの
以下は `market_summary` に入れず、UI adapter または widget 側へ残す。

- 表示タイトル
- caption 文言
- 色
- badge の日本語文字列
- card の並び順
- widget の grid 配置
- CSS class / style override
- 何秒ごとに更新するか

つまり、

```text
market_summary は意味の束。
UI はそれをどう見せるかを決める。
```

---

## 8. 初版 builder の責務
想定ファイル:
- `processing/l4_consumer_models/shared/market_summary.py`

想定責務:
- 入力 row / state から MarketSummary を構築する
- freshness を共通ルールで計算する
- source_kind を正規化する
- notable_events / alert_candidates を軽量タグで付与する
- wording や layout 情報は持ち込まない

---

## 9. 初版でやらないこと
- UI 文言の生成
- card 専用 field の生成
- CSS hint の付与
- graph layer の定義
- 実行判断用の重い signal 生成
- 複雑な alert scoring

---

## 10. 実装順序
### Step 1
`MarketSummary` dataclass を作る

### Step 2
`market_state_service.py` 相当の入力から builder で初版を組む

### Step 3
operator_ui 側では presenter を薄い adapter に寄せる

### Step 4
monitoring / replay で同 bundle を再利用できるか確認する

---

## 11. 一言でまとめると

```text
L4 market_summary は、
trust / continuity / interpretation / freshness を中心に、
市場の現在状態を consumer 横断で共有するための最小 summary bundle である。
```
