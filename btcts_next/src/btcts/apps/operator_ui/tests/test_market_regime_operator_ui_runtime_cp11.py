# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_operator_ui_runtime_cp11.py
# desc: Tests Operator UI managed market-regime preflight/run-once controls. Tmp roots only; no scheduler, broker, or AutoTrade.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
COLLECTOR_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py"

from btcts.prediction.market_regime.operator_ui_runtime import (  # noqa: E402
    market_regime_operator_ui_snapshot,
    request_market_regime_preflight,
    request_market_regime_run_once,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _fixture_root(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-08/122000/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-08T12:20:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-08/122000/forecast_records.jsonl"},
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


def test_cp11_operator_ui_preflight_writes_status_only(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    ok, msg, status = request_market_regime_preflight(tmp_path)
    assert ok is True
    assert "can_write_live_once=True" in msg
    assert status["mode"] == "PREFLIGHT_OK"
    assert status["would_write"] is False
    assert status["broker_private_api_allowed"] is False
    assert status["autotrade_trigger_allowed"] is False
    assert (tmp_path / "state/market_regime_inference/status.json").exists()
    assert not (tmp_path / "prediction/market_regime/latest_cards.json").exists()


def test_cp11_operator_ui_run_once_writes_latest_and_status(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    ok, msg, status = request_market_regime_run_once(tmp_path)
    assert ok is True
    assert "run_once ok" in msg
    assert status["mode"] == "RUN_ONCE_OK"
    assert status["would_write"] is True
    assert status["scheduler_enabled"] is False
    assert status["producer_loop_enabled"] is False
    assert (tmp_path / "prediction/market_regime/latest_cards.json").exists()
    snapshot = market_regime_operator_ui_snapshot(tmp_path)
    assert snapshot["latest_cards_available"] is True
    assert snapshot["card_count"] == 8
    assert snapshot["active"] is False


def test_cp11_operator_ui_run_once_blocks_when_sources_missing(tmp_path: Path) -> None:
    _write_json(tmp_path / "state/collector_vnext/unified_market_state_status.json", {"read_only": True, "would_send_to_broker": False})
    ok, msg, status = request_market_regime_run_once(tmp_path)
    assert ok is False
    assert "blocked" in msg
    assert status["mode"] == "RUN_ONCE_BLOCKED"
    assert status["would_write"] is False
    assert "latest_manifest" in status["missing_sources"]
    assert not (tmp_path / "prediction/market_regime/latest_cards.json").exists()


def test_cp11_collector_page_contains_market_regime_runtime_controls() -> None:
    text = COLLECTOR_PAGE.read_text(encoding="utf-8")
    required = [
        "MarketRegime Inference Runtime",
        "request_market_regime_preflight",
        "request_market_regime_run_once",
        "Preflight",
        "Run Once",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "market_regime scheduler enabled",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
