# path: ./docs/architecture/L4_MARKET_SUMMARY_BUILDER_SKELETON_SPEC_2026-04-04.md
# desc: Skeleton spec for the L4 market summary builder and dataclass.
# L4 Market Summary Builder / Dataclass 骨子仕様書

更新日: 2026-04-04
位置づけ: `market_summary.py` 実装着手用 skeleton spec
対象: `btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py` 想定
関連:
- `tmp/tmp/L4_MARKET_SUMMARY_FIELD_SPEC_2026-04-04.md`
- `tmp/tmp/UI_HUB_WIDGET_ARCHITECTURE_SPEC_2026-04-04.md`

---

## 1. この仕様書の目的
本仕様書は、L4 shared の `market_summary` を実装する際の最初の骨子を固定するための仕様である。

ここで固定したいのは次の3つ。

1. dataclass の形
2. builder の責務
3. UI / monitoring / replay が再利用しやすい最小 API

この段階では、まだ UI adapter までは実装しない。
まず shared の核を安定させる。

---

## 2. 実装方針
`market_summary.py` は、少なくとも次の3層で構成する。

```text
raw/state row
  ↓
normalize helpers
  ↓
MarketSummaryBuilder
  ↓
MarketSummary dataclass
```

重要なのは、

- dataclass は contract
- builder は assembly
- helper は normalization

として役割を分けること。

---

## 3. 推奨ファイル構成
初版は 1 ファイル内で十分。

```text
processing/l4_consumer_models/shared/market_summary.py
  - MarketSummary dataclass
  - MarketSummaryBuildInput dataclass
  - build_market_summary(...)
  - helper functions
```

将来肥大化したら分割する。
初手から過分割しない。

---

## 4. dataclass 設計

## 4.1 `MarketSummary`
shared consumer bundle の正本 contract。

### 推奨形
```python
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
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
    notable_events: list[str] = field(default_factory=list)
    alert_candidates: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
```

### 補足
- `frozen=True` を推奨
- shared bundle は build 後に書き換えない前提を明示できる
- list / dict は default_factory を使う

---

## 4.2 `MarketSummaryBuildInput`
builder に渡す入力束。

### 目的
builder 関数に生の dict を大量に並べない。
入力責務を見える化する。

### 推奨形
```python
@dataclass(frozen=True)
class MarketSummaryBuildInput:
    market_state_row: dict[str, Any] | None = None
    diagnostics: dict[str, Any] | None = None
    source_kind: str | None = None
```

### 初版の考え方
最初はこれくらい薄くてよい。
必要になったら、
- board row
- continuity state
- trust state
- feature summary

などを追加する。

---

## 5. builder の責務

## 5.1 `build_market_summary(...)`
shared bundle を構築する主関数。

### 推奨シグネチャ
```python
def build_market_summary(inp: MarketSummaryBuildInput) -> MarketSummary:
    ...
```

### 責務
- source_kind を正規化する
- event_ts / age_sec / freshness / is_stale を決める
- trust / continuity / interpretation 系 field を拾う
- notable_events / alert_candidates を軽量に組む
- diagnostics を肥大化させず引き継ぐ

### 非責務
- 文言生成
- 色の決定
- widget 用 layout hint
- CSS
- refresh interval

---

## 5.2 builder は薄く保つ
builder は「何でも詰める場所」になりやすい。
初版では、次の原則を守る。

- heavy business logic を増やさない
- UI convenience field を入れない
- L3 を再判定しない
- field が増えたら shared 価値を先に問う

---

## 6. helper 関数
初版で必要な helper は次程度。

### `_safe_str(value) -> str | None`
空文字や不正値を吸収する。

### `_safe_float(value) -> float | None`
年齢や数値補助用。

### `_pick_event_ts(row) -> str | None`
- `collector_ts`
- `exchange_ts`
の優先順で選ぶ。

### `_resolve_freshness(age_sec) -> str`
- `LIVE`
- `QUIET`
- `STALE`
- `UNKNOWN`

### `_resolve_is_stale(freshness) -> bool | None`
簡易分岐用。

### `_normalize_source_kind(value) -> str`
未指定時は `unknown`。

### `_collect_notable_events(...) -> list[str]`
軽量タグを作る。

### `_collect_alert_candidates(...) -> list[str]`
軽量フラグを作る。

---

## 7. 初版ルール

## 7.1 freshness ルール
初版は `market_state_service.py` に寄せた閾値でよい。

- `LIVE`: age <= 30 sec
- `QUIET`: age <= 120 sec
- `STALE`: それ以上
- `UNKNOWN`: age 不明

### 注意
後で設定化する余地はあるが、最初から設定依存にしすぎない。

---

## 7.2 notable_events ルール
初版は軽量で十分。

### 例
- `fresh_snapshot`
- `trust_degraded`
- `resync_recent`
- `stale_source`
- `review_required`

### ルール
文言ではなく tag にする。

---

## 7.3 alert_candidates ルール
初版は重い alert scoring にしない。

### 例
- `stale_market_state`
- `trust_not_trusted`
- `interpretation_review_required`

---

## 8. 初版の builder 擬似コード

```python
def build_market_summary(inp: MarketSummaryBuildInput) -> MarketSummary:
    row = inp.market_state_row or {}
    diagnostics = dict(inp.diagnostics or {})

    event_ts = _pick_event_ts(row)
    age_sec = _safe_float(diagnostics.get("preferred_row_age_sec"))
    if age_sec is None:
        age_sec = _safe_float(diagnostics.get("age_sec"))

    freshness = _resolve_freshness(age_sec)
    is_stale = _resolve_is_stale(freshness)

    trust_state = _safe_str(row.get("trust_state"))
    continuity_state = _safe_str(row.get("continuity_state"))
    interpretation_bucket = _safe_str(row.get("interpretation_bucket"))
    interpretation_reason = _safe_str(row.get("interpretation_reason"))

    source_kind = _normalize_source_kind(inp.source_kind or diagnostics.get("source_kind"))
    source_series_id = _safe_str(row.get("source_series_id"))

    notable_events = _collect_notable_events(
        freshness=freshness,
        trust_state=trust_state,
        continuity_state=continuity_state,
        interpretation_bucket=interpretation_bucket,
    )
    alert_candidates = _collect_alert_candidates(
        freshness=freshness,
        trust_state=trust_state,
        interpretation_bucket=interpretation_bucket,
    )

    return MarketSummary(
        summary_type="market_summary",
        exchange=_safe_str(row.get("exchange")),
        symbol_raw=_safe_str(row.get("symbol_raw") or row.get("symbol")),
        market_uid=_safe_str(row.get("market_uid")),
        source_kind=source_kind,
        source_series_id=source_series_id,
        event_ts=event_ts,
        age_sec=age_sec,
        freshness=freshness,
        is_stale=is_stale,
        trust_state=trust_state,
        continuity_state=continuity_state,
        interpretation_bucket=interpretation_bucket,
        interpretation_reason=interpretation_reason,
        market_state_label=_safe_str(row.get("market_state_label")),
        participation_state=_safe_str(row.get("participation_state")),
        liquidity_bias=_safe_str(row.get("liquidity_bias")),
        notable_events=notable_events,
        alert_candidates=alert_candidates,
        diagnostics=diagnostics,
    )
```

---

## 9. UI adapter との関係
UI 側では、`MarketSummary` をそのまま widget に渡すのではなく、必要なら薄い adapter を噛ませる。

### UI adapter がやること
- badge text へ変換
- 表示順を決める
- 空値時の placeholder を決める
- 色や icon を決める

### shared builder がやらないこと
- 日本語文言
- card 順序
- CSS class
- widget title

---

## 10. 初版の完了条件
最初の実装完了を言うための条件は次。

- `MarketSummary` dataclass ができている
- `build_market_summary()` ができている
- operator_ui の既存 market state 入力から 1 件 build できる
- UI wording なしで bundle 単体確認ができる
- monitoring / replay でも再利用できそうな field 粒度を保っている

---

## 11. 次段階
この skeleton 実装の次にやるべきこと。

1. operator_ui の market monitor 側に薄い adapter を作る
2. `notable_events` / `alert_candidates` の粒度調整
3. monitoring への再利用可否確認
4. timeline / liquidity bundle へ展開

---

## 12. 一言でまとめると

```text
market_summary.py は、
shared contract と shared builder を持つ薄い L4 実装核であり、
UI convenience を持ち込まないことが最重要である。
```
