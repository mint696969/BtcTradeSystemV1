# BtcTradeSystemV1 Handover (BOOST)
- ts: 2025-10-20T14:56:20Z
## Roots
- data_root: D:\BtcTS_V1\data
- logs_root: D:\BtcTS_V1\logs
## Env
- BTC_TS_MODE: None
- PYTHONPATH_contains_repo: True
## Loaded modules (top 50)
- btc_trade_system
- btc_trade_system.common
- btc_trade_system.common.boost_svc
- btc_trade_system.common.io_safe
- btc_trade_system.common.paths
- btc_trade_system.features
- btc_trade_system.features.audit_dev
- btc_trade_system.features.audit_dev.writer
- btc_trade_system.features.dash
- btc_trade_system.features.dash.audit_svc
- btc_trade_system.features.dash.audit_ui
- btc_trade_system.features.dash.health_svc
- btc_trade_system.features.dash.health_ui
- btc_trade_system.features.dash.leader_annotations
- btc_trade_system.features.dash.providers
- btc_trade_system.features.dash.settings_ui
- btc_trade_system.features.settings
- btc_trade_system.features.settings.modal_ui
- btc_trade_system.features.settings.settings_ui
## Recent dev_audit tail (last 20)
- {"ts":"2025-10-19T14:00:51.344Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":80}}}
- {"ts":"2025-10-19T14:00:51.346Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":81}}}
- {"ts":"2025-10-19T14:00:51.349Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":82}}}
- {"ts":"2025-10-19T14:00:51.351Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":83}}}
- {"ts":"2025-10-19T14:00:51.353Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":84}}}
- {"ts":"2025-10-19T14:00:51.365Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":85}}}
- {"ts":"2025-10-19T14:00:51.373Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":86}}}
- {"ts":"2025-10-19T14:00:51.379Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":87}}}
- {"ts":"2025-10-19T14:00:51.381Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":88}}}
- {"ts":"2025-10-19T14:00:51.383Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":89}}}
- {"ts":"2025-10-19T14:00:51.387Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":90}}}
- {"ts":"2025-10-19T14:00:51.395Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":91}}}
- {"ts":"2025-10-19T14:00:51.397Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":92}}}
- {"ts":"2025-10-19T14:00:51.400Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":93}}}
- {"ts":"2025-10-19T14:00:51.403Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":94}}}
- {"ts":"2025-10-19T14:00:51.407Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":95}}}
- {"ts":"2025-10-19T14:00:51.409Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":96}}}
- {"ts":"2025-10-19T14:00:51.412Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":97}}}
- {"ts":"2025-10-19T14:00:51.414Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":98}}}
- {"ts":"2025-10-19T14:00:51.417Z","mode":"BOOST","event":"dev.ui.mass_test_boost","feature":"audit_dev","level":"INFO","actor":null,"site":null,"session":null,"task":null,"trace_id":null,"payload":{"payload":{"n":99}}}
## How to reproduce (PowerShell)
```powershell
Set-Location $env:USERPROFILE\BtcTradeSystemV1
$env:PYTHONPATH = (Get-Location).Path
if (-not $env:BTC_TS_LOGS_DIR) { $env:BTC_TS_LOGS_DIR = "D:\BtcTS_V1\logs" }
python -m streamlit run .\btc_trade_system\features\dash\dashboard.py --server.port 8501
```
