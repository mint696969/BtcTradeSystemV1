# path: ./archive/archive/phase25_closeout_artifacts_2026-04-16/phase25_runtime_wiring_closeout_note_2026-04-15.md
# desc: Archived note, specification, report, or reference document.

# Phase 2.5 runtime wiring closeout note

更新日: 2026-04-15
位置づけ: `./tmp/` 作成の closeout note / merged spec 補助メモ
対象: `btcts_next/src/btcts/processing/l3_market_semantics/event_usage_policy.py`, `btcts_next/src/btcts/market_engine/market_state/projector.py`, `btcts_next/src/btcts/apps/operator_ui/health_data_service.py`

---

## 結論
2026-04-15 の current repo truth では、`semantic_usage_contract_rows` の family-row shape は、これまでより一段 **L3 owner 側に寄った** と読んでよい。

今回の変更で固定した読みは次。

- `build_event_usage_contract_rows(...)` 自体が
  - `contract_source`
  - `interpretation_bucket`
  - `event_family`
  - `usage_grade`
  - `meaning_version`
  を返す
- `projector.py` は row shape を新規定義する場所ではなく、L3 helper の row を outward へ橋渡しする場所としてさらに薄くなった
- `health_data_service.py` の fallback family-row も同じ row shape を使うため、observer fallback でも owner truth に寄った

---

## 変更の意味
これは大きな機能追加ではない。

むしろ、Phase 2 closeout bundle の `projector responsibility wording` を **コード側でも一段強化した** 小修正である。

### 変更前の読み
- L3 helper は family-row の core 部分を返す
- `projector` / `health_data_service` が `contract_source` / `interpretation_bucket` を補う

### 変更後の読み
- L3 helper が family-row shape をより正として返す
- `projector` / `health_data_service` は不足時の normalize だけ行う thin bridge/fallback に寄る

このため、current wording として次がさらに言いやすくなった。

- projector は convenience owner ではない
- family-row contract shape は L3 owner 側に寄っている
- UI / Health fallback も second L3 ではなく owner truth reuse line である

---

## 確認したテスト
- `btcts_next/src/btcts/processing/l3_market_semantics/orderbook/tests/test_event_usage_policy_contract.py`
- `btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_semantic_usage.py`
- `btcts_next/src/btcts/market_engine/tests/test_market_state_flow.py`

すべて green。

---

## closeout 読みへの影響
今回の修正で、Phase 2 runtime wiring closeout bundle の B について、次の 2 点はさらに close 寄りに読める。

1. `projector responsibility`
   - summary / contract field を outward へ載せる bridge であり、row shape owner ではない
2. `minimal stable outward line`
   - top-level 3 fields はそのまま維持しつつ、family-row shape owner を L3 側へ寄せた

したがって immediate open は依然として大規模 code churn ではなく、

- wording sync
- docs fixation
- stale open cleanup

に寄る。

---

## 次の推奨
- `docs/architecture/02` merged current-truth draft の wording を今回の row-shape owner 読みに軽く寄せる
- その後、stale risk / open-register cleanup を進める
- `event-level full contract` の broader formalization は、Phase 3 blocker にしない line で carry-forward judgement を続ける
