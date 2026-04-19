# path: ./archive/archive/phase25_closeout_artifacts_2026-04-16/phase1_phase15_contract_bundle_README.md
# desc: Archived note, specification, report, or reference document.

# Phase 1 / 1.5 Contract Bundle README

## 目的
この bundle は、今回スレで進めた

- Phase 1 `event usage contract`
- Phase 1.5 `Health v1 semantic observer`

の成果が、期待通りの contract 境界で出ているかを、層ごとに切り分けて確認するためのもの。

## 実行ファイル
- `C:\BtcTradeSystem\tmp\phase1_phase15_contract_bundle.ps1`

## 何を確認するか
### 1. l3_event_usage_policy
- event usage summary / contract rows の owner helper が壊れていないか

### 2. market_state_runtime_contracts
- `live_orderbook_semantics.py`
- `projector.py`

の outward 契約が壊れていないか

### 3. l4_shared_and_adapter
- `market_summary`
- `health_digest`
- operator_ui adapter

の shared-first 形が壊れていないか

### 4. operator_ui_health_and_bridge
- `health_data_service`
- `health_chart_panels`
- `health_digest_bridge`
- `market_state_bridge`

の observer / bridge 境界が壊れていないか

## 使い方
```powershell
powershell -ExecutionPolicy Bypass -File C:\BtcTradeSystem\tmp\phase1_phase15_contract_bundle.ps1
```

## 失敗時の読み方
- `compile::...` で落ちた場合
  - まず構文や import を疑う
- `test::l3_event_usage_policy::...` で落ちた場合
  - L3 owner helper / summary contract を疑う
- `test::market_state_runtime_contracts::...` で落ちた場合
  - projector / live orderbook semantics outward を疑う
- `test::l4_shared_and_adapter::...` で落ちた場合
  - shared bundle / thin adapter の shape drift を疑う
- `test::operator_ui_health_and_bridge::...` で落ちた場合
  - Health observer / bridge / service の summary-first 読み取りを疑う

## 補足
今回のスレ成果を明確に見るには、
この bundle をまず回してから、必要なら個別テストへ降りるのが一番切り分けしやすい。
