# path: ./tmp/01_L1_L2_CAPTURE_CANONICAL_RUNTIME_SPEC_2026-04-09.md
# desc: L1 / L2 Capture Canonical Runtime Spec (updated and simplified)

更新日: 2026-04-09
位置づけ: 現行 mainline に合わせた L1/L2 統合仕様
対象: `btcts_next/src/btcts/collector_vnext/`, `btcts_next/src/btcts/ingestion/`, `btcts_next/src/btcts/market_engine/` の関連 runtime

---

## 1. この仕様書の目的
本仕様書は、L1 と L2 の責務境界を current repo truth に合わせて簡潔に固定するための文書である。

ここで固定したいことは 4 つだけでよい。

1. L1 と L2 の owner を明確にする
2. `collector_vnext` と `ingestion/l2_canonical` の役割差を明文化する
3. live runtime 主系と canonical ownership を混同しない
4. L3 以降の意味責務を L1/L2 へ逆流させない

---

## 2. 結論
現在の mainline では、L1 / L2 は次のように読むのが最も正確である。

```text
L1 = capture / lane operation / raw persistence
L2 = canonical / structural truth / rebuild support
```

### 主系の置き場
- L1 live runtime 主系: `btcts_next/src/btcts/collector_vnext/`
- L2 canonical ownership: `btcts_next/src/btcts/ingestion/l2_canonical/`

### 一言で言うと
- `collector_vnext` は **取り続ける運転の owner**
- `ingestion/l2_canonical` は **事実を整える canonical の owner**

---

## 3. L1 Capture

## 3.1 L1 が持つ責務
L1 は、市場からの入力を止めずに取り続ける責務を持つ。

### 含むもの
- REST / WebSocket 接続
- subscribe / recv / retry / reconnect
- lane state / daemon / watchdog の運転
- provider 差異の吸収入口
- raw payload の捕捉と保存
- session / stream continuity の維持
- rate control / health 更新の運転面

### 含まないもの
- pressure / wall / sweep / absorption の意味判断
- support / resistance の決定
- trust / interpretation bucket の owner 判定
- consumer 向け summary 生成
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

## 3.3 L1 の原則
L1 は運転責務であり、意味 owner ではない。
安定化の都合で semantic owner を collector 側へ戻してはならない。

---

## 4. L2 Canonical / Structural Truth

## 4.1 L2 が持つ責務
L2 は raw input を、下流が安全に使える canonical / structural truth に整える責務を持つ。

### 含むもの
- raw -> canonical transform
- event type 正規化
- sequence / source id / timestamp の保持
- snapshot / diff の structural support
- orderbook rebuild 支援
- tradeflow aggregation の structural support
- canonical record contract の維持

### 含まないもの
- pressure / wall / support / resistance の意味判断
- trust / interpretation bucket の決定
- Health / UI 向け observer summary
- consumer wording や page-specific summary

## 4.2 canonical ownership の配置
- `btcts_next/src/btcts/ingestion/event_types.py`
- `btcts_next/src/btcts/ingestion/l2_canonical/orderbook/book_state.py`
- `btcts_next/src/btcts/ingestion/l2_canonical/orderbook/book_apply.py`
- `btcts_next/src/btcts/ingestion/l2_canonical/orderbook/book_rebuilder.py`
- `btcts_next/src/btcts/ingestion/l2_canonical/tradeflow/trade_aggregator.py`

## 4.3 現行 runtime 上の現実
live runtime では `collector_vnext/transforms/` に L2 相当の実導線が残っている。

### 代表配置
- `btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical.py`
- `btcts_next/src/btcts/collector_vnext/transforms/raw_to_canonical_trades.py`
- `btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py`
- `btcts_next/src/btcts/collector_vnext/transforms/ws_trade_to_canonical.py`

これは意味 owner の逆流ではなく、**runtime 実装主系が collector 側にある状態**として読むのが正しい。

---

## 5. L1 / L2 の依存方向

### 正方向
- venue / provider -> `collector_vnext`
- `collector_vnext` -> canonical transform
- canonical output -> downstream consumers

### 禁止方向
- `collector_vnext` -> `processing/l3_market_semantics` 直接依存
- `ingestion` -> `processing` 逆流 import
- UI / consumer が `ingestion` を直読して market meaning を作ること

---

## 6. L2 と L3 の境界で重要なこと
L2 と L3 の境界では、**事実**と**意味**を混ぜないことが最重要である。

### L2 に残すもの
- board / trade の canonical structure
- rebuild 可能性
- sequence continuity 支援
- structural metadata

### L3 に渡すもの
- continuity semantics
- trust semantics
- interpretation semantics
- orderbook semantics
- event family / usage / actionability の意味付け

つまり、L2 は再構成可能な事実を渡し、L3 がその意味を決める。

---

## 7. static に見て白が付く範囲
2026-04-09 時点で、architecture 文書として白が付くのは主に L1 / L2 側である。

### 白が付くもの
- unified daemon / watchdog / lane 導線
- board WS / executions WS の運転導線
- raw 出力継続
- canonical 出力継続
- checkpoint / state 更新継続

### 別論点として切り離すべきもの
- L3 event usage contract formalization
- live orderbook semantics full parity
- Health observer / L4 / prediction / decision の後段契約

L1/L2 仕様に L3 以降の open issue を混ぜ込みすぎないことが読みやすさに直結する。

---

## 8. orderbook state model の層差
L2 と L3 の間には、重要な state model の層差がある。

### L2 canonical 側
- `btcts_next/src/btcts/ingestion/l2_canonical/orderbook/book_state.py`
- `OrderBookState`

### current live runtime / L3 continuity 側
- `btcts_next/src/btcts/processing/l3_market_semantics/continuity/models/book_state.py`
- `BookState`

この差は、live orderbook semantics wiring を考えるときの前提である。
単なる projector field 追加ではなく、state bridge の設計が必要になる。

---

## 9. L1/L2 でやってはいけないこと
- support / resistance をここで決める
- trust / interpretation bucket をここで決める
- Health 用 summary をここで増やす
- consumer 向け wording をここで作る
- 「一時的に便利だから」で L3 owner を巻き戻す

L1/L2 はあくまで capture と canonical の層であり、meaning owner ではない。

---

## 10. 運用 path policy の補足
L1/L2 は運用 path を repo 外へ外出しできる前提で設計する。

### 方針
- ログ・データ・秘密・設定の正本は repo 外 path を優先する
- repo 内は fallback / template の位置づけに留める
- runtime / tool は ENV / resolver / path service で吸収する

この方針は責務分離とも整合する。
path 固定を各モジュールへ散らすと、collector / UI / tool が不要に密結合になるためである。

---

## 11. 一言
L1 は取り続ける。
L2 は事実を整える。
そして意味を作るのは L3 である。

現在の mainline は、その三層のうち L1/L2 については `collector_vnext` と `ingestion/l2_canonical` の二重配置で読むのが最も正確であり、この境界は引き続き維持すべきである。
