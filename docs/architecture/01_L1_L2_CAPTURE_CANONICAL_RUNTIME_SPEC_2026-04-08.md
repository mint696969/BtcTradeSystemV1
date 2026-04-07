# path: ./docs/architecture/01_L1_L2_CAPTURE_CANONICAL_RUNTIME_SPEC_2026-04-08.md
# desc: L1 / L2 Capture Canonical Runtime Spec

更新日: 2026-04-08
位置づけ: 現行 mainline に合わせた L1/L2 統合仕様
対象: `btcts_next/src/btcts/collector_vnext/`, `btcts_next/src/btcts/ingestion/`, `btcts_next/src/btcts/market_engine/` の関連 runtime

---

## 1. この仕様書の目的
本仕様書は、旧 `LAYER_RESPONSIBILITY_RUNTIME_SPEC` と `L2_L3 separation verification` 群のうち、**L1 と L2 の現況説明に関わる部分**を現行 repository に合わせて統合したものである。

目的は次の4つ。

1. L1 と L2 の責務を現在の実装位置に即して説明する
2. `collector_vnext/` と `ingestion/l2_canonical/` の役割差を明確にする
3. live runtime で確認済みの範囲と、未確認論点を分けて書く
4. 下流の L3/L4 に不要な責務逆流を起こさないための境界を固定する

---

## 2. 結論
現在の mainline は、L1/L2 について次のように読むのが最も正確である。

```text
L1 = capture / connection / lane operation / raw persistence
L2 = canonical / structural truth / rebuild support / canonical persistence
```

ただし物理配置は二層に分かれる。

### 2.1 live runtime 主系
- `btcts_next/src/btcts/collector_vnext/`

### 2.2 canonical ownership
- `btcts_next/src/btcts/ingestion/`
- 特に `ingestion/l2_canonical/`

つまり、

- **運転主系**は `collector_vnext/`
- **canonical ownership** は `ingestion/l2_canonical/`

である。

---

## 3. L1 Capture

## 3.1 責務
L1 は市場から壊さず受け取り続ける。

### 含むもの
- REST / WebSocket 接続
- subscribe / recv / retry / reconnect
- lane 運転と health 更新
- provider 差分の吸収入口
- raw payload の捕捉
- session / stream continuity の運転維持
- stop / restart / watchdog 協調

### 含まないもの
- pressure / wall / sweep / absorption の意味付け
- trust / continuity interpretation の owner
- consumer 向け summary
- UI wording
- execution decision

## 3.2 代表配置
- `btcts_next/src/btcts/collector_vnext/providers/bitflyer_rest.py`
- `btcts_next/src/btcts/collector_vnext/providers/bitflyer_ws.py`
- `btcts_next/src/btcts/collector_vnext/providers/bitflyer_ws_board.py`
- `btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py`
- `btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py`
- `btcts_next/src/btcts/collector_vnext/unified_daemon.py`
- `btcts_next/src/btcts/collector_vnext/unified_watchdog.py`
- `btcts_next/src/btcts/collector_vnext/rate_runtime.py`

## 3.3 代表出力
- raw JSONL
- lane status
- daemon / watchdog status
- checkpoint / health 更新の一部

## 3.4 原則
L1 は運転責務であり、意味 owner ではない。
collector の都合で semantic owner を戻してはならない。

---

## 4. L2 Canonical / Structural Truth

## 4.1 責務
L2 は raw を下流が安全に使える canonical / structural truth に変換する。

### 含むもの
- raw -> canonical transform
- event type 正規化
- source event id / sequence の保持
- snapshot / diff の構造支援
- orderbook rebuild の structural support
- tradeflow aggregation の structural support
- canonical record contract の維持

### 含まないもの
- pressure / wall 強度の意味判断
- support / resistance の意味判断
- trust / interpretation bucket の決定
- UI / monitoring 向け文言生成

## 4.2 canonical ownership
L2 の正規 ownership は `ingestion/l2_canonical/` である。

### 代表配置
- `btcts_next/src/btcts/ingestion/event_types.py`
- `btcts_next/src/btcts/ingestion/l2_canonical/orderbook/book_state.py`
- `btcts_next/src/btcts/ingestion/l2_canonical/orderbook/book_apply.py`
- `btcts_next/src/btcts/ingestion/l2_canonical/orderbook/book_rebuilder.py`
- `btcts_next/src/btcts/ingestion/l2_canonical/tradeflow/trade_aggregator.py`

## 4.3 runtime 側の現実
現行 live runtime では、`collector_vnext/transforms/` に L2 相当の実導線が残る。

### 代表配置
- `btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical.py`
- `btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical_trades.py`
- `btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py`
- `btcts_next/src/btcts/collector_vnext/transforms/ws_trade_to_canonical.py`

この状態は責務逆流ではなく、**runtime 実装主系が collector 側に残っている段階**として扱う。

---

## 5. L1/L2 の依存方向

### 正方向
- venue/provider -> collector_vnext
- collector_vnext -> ingestion event contract / canonical transform
- canonical output -> downstream consumers

### 禁止方向
- collector_vnext -> L3 meaning owner 直接依存
- ingestion -> processing 逆流 import
- consumer -> ingestion 直読みで意味再計算

---

## 6. 現行 static 状態の要約
現行 repository では、少なくとも次の分離方向は維持されている。

- `collector_vnext/` から `processing/l3_market_semantics` 直接 import は mainline 上で確認されていない
- `ingestion/` から `processing/` 逆流 import は mainline 上で確認されていない
- `apps/operator_ui/` から `ingestion` 直参照は mainline 上で確認されていない

したがって、L1/L2/L3 の ownership 逆流は静的には抑えられている。

---

## 7. live runtime で白が付いている範囲
architecture 文書として現時点で白を付けてよいのは、主に L1/L2 寄りである。

### 白が付くもの
- unified supervisor / watchdog / daemon 導線
- board WS / executions WS の live recovery
- raw 出力継続
- canonical 出力継続
- checkpoint 更新継続

### まだ別論点のもの
- L3 orderbook semantics full live wiring
- event usage contract outward formalization
- L4 beyond market_summary の shared bundle 拡張

ここを混ぜて説明しないことが重要である。

---

## 8. orderbook runtime state の層差
L2 と L3 の間には、重要な state model 差がある。

### L2 canonical 側
- `btcts_next/src/btcts/ingestion/l2_canonical/orderbook/book_state.py`
- `OrderBookState`

### current live runtime 側
- `btcts_next/src/btcts/processing/l3_market_semantics/continuity/models/book_state.py`
- `BookState`

この差は、将来 live orderbook semantics wiring をやる際の重要前提である。
単に projector に field を足せば済む話ではない。

---

## 9. L1/L2 の done / not done

### done とみなしてよいもの
- live runtime 主系として `collector_vnext` が mainline で動いている
- canonical ownership が `ingestion/l2_canonical` に分離されている
- raw / canonical の運転導線が mainline 上にある
- legacy 主系は archive に退避済みである

### done とみなしてはいけないもの
- L3 full live semantics の完成
- L4 全面 shared-first 化の完了
- prediction / decision / execution bundle 契約の完成

---

## 10. 運用判断ルール

### 10.1 その処理が L1 か
- 接続・受信・維持・再接続か
- lane / daemon / watchdog 都合か
- raw を壊さず捕捉する処理か

yes が多ければ L1。

### 10.2 その処理が L2 か
- canonical / structural truth 化だけか
- event type / sequence / rebuild support か
- まだ意味ラベルを作っていないか

yes が多ければ L2。

### 10.3 L1/L2 から外すべき兆候
- market meaning を作っている
- support / resistance / sweep / absorption を定義している
- trust bucket / interpretation bucket を決めている
- consumer 用 wording や summary を作っている

これらは L1/L2 に置かない。

---

## 11. Path / data policy の補足
運用上の正本 path は repo 内ではなく外部運用 path を優先する。

### 方針
- ログ・データ・秘密・設定の正本は repo 外の運用 path を優先
- repo 内は fallback / template の位置づけ
- tool / runtime は ENV 優先で解決する

architecture 観点では、これは **L1/L2 の責務分離を保ったまま運用 path を外出しするための原則**である。

---

## 12. 一言
L1 は取り続ける。
L2 は事実を整える。
現在の mainline は、その二層については `collector_vnext` と `ingestion/l2_canonical` の二重配置で説明するのが最も正確である。
