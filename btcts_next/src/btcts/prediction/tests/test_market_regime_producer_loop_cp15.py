# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_producer_loop_cp15.py
# desc: CP15 tests for controlled MarketRegime producer loop. Tmp roots only; finite loop; no broker, AutoTrade, order, trade ledger, parameter auto-promotion, or Collector button linkage.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.producer_loop import (  # noqa: E402
    MARKET_REGIME_PRODUCER_LOOP_VERSION,
    market_regime_producer_loop_snapshot,
    run_market_regime_producer_loop,
    write_market_regime_producer_control_request,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _fixture_root(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-08/150000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-08T15:00:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-08/150000/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "horizon_sec": 300, "primary_label": "range_candidate", "score": 0.80, "values_snapshot": {"estimated_signal_strength_percent": 70, "estimated_reference_hit_rate_percent": 65, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 900, "primary_label": "trend_candidate", "score": 0.88, "values_snapshot": {"estimated_signal_strength_percent": 82, "estimated_reference_hit_rate_percent": 74, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {"last_symbol_raw": "FX_BTC_JPY", "last_best_bid": 9729064.0, "last_best_ask": 9730264.0, "last_spread": 1200.0, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "status": "healthy", "ws_state": "LIVE", "ws_freshness": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def test_cp15_control_request_writes_safe_stop(tmp_path: Path) -> None:
    result = write_market_regime_producer_control_request(tmp_path, action="safe_stop", reason="test_stop")
    assert result["ok"] is True
    path = Path(result["control_path"])
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["action"] == "safe_stop"
    assert payload["safety"]["broker_private_api_allowed"] is False
    assert payload["safety"]["autotrade_trigger_allowed"] is False


def test_cp15_finite_loop_writes_latest_artifacts_and_stops(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    result = run_market_regime_producer_loop(hot_root=tmp_path, interval_sec=0, max_iterations=2, sleep_fn=lambda _sec: None)
    assert result["ok"] is True
    assert result["version"] == MARKET_REGIME_PRODUCER_LOOP_VERSION
    assert result["mode"] == "STOPPED"
    assert result["active"] is False
    assert result["iteration"] == 2
    assert result["writes"] == 2
    assert result["stop_reason"] == "max_iterations_reached"
    assert result["safety"]["collector_button_linked"] is False
    assert result["safety"]["broker_private_api_allowed"] is False
    assert (tmp_path / "prediction/market_regime/latest_cards.json").exists()
    snapshot = market_regime_producer_loop_snapshot(tmp_path)
    assert snapshot["mode"] == "STOPPED"
    assert snapshot["iteration"] == 2


def test_cp15_loop_blocks_when_preflight_fails(tmp_path: Path) -> None:
    _write_json(tmp_path / "state/collector_vnext/unified_market_state_status.json", {"read_only": True, "would_send_to_broker": False})
    result = run_market_regime_producer_loop(hot_root=tmp_path, interval_sec=0, max_iterations=1, sleep_fn=lambda _sec: None)
    assert result["ok"] is True
    assert result["writes"] == 0
    assert result["blocked"] == 1
    assert not (tmp_path / "prediction/market_regime/latest_cards.json").exists()
    status = json.loads((tmp_path / "state/market_regime_inference/producer_loop_status.json").read_text(encoding="utf-8"))
    assert status["safety"]["write_when_preflight_blocks"] is False


def test_cp15_loop_obeys_safe_stop_before_writing(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    write_market_regime_producer_control_request(tmp_path, action="safe_stop", reason="test_stop_before_start")
    result = run_market_regime_producer_loop(hot_root=tmp_path, interval_sec=0, max_iterations=3, sleep_fn=lambda _sec: None)
    assert result["stop_reason"] == "safe_stop_requested"
    assert result["iteration"] == 0
    assert result["writes"] == 0
    assert not (tmp_path / "prediction/market_regime/latest_cards.json").exists()


def test_cp15_source_has_no_execution_or_external_scheduler_side_effects() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/producer_loop.py"
    text = path.read_text(encoding="utf-8")
    forbidden = [
        "import streamlit",
        "subprocess.Popen",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "trade_ledger_append_allowed: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
        "\"collector_button_linked\": True",
    ]
    hits = []
    for token in forbidden:
        if isinstance(token, tuple):
            continue
        if token in text:
            hits.append(token)
    assert hits == []
    assert "controlled_loop_only" in text
    assert "preflight_market_regime_latest_artifacts_once" in text
