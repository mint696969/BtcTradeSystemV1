# path: ./tools/test_phase4a_prediction_system_ps_q19o_macro_session_context_input_repair_or_decision.py
# desc: Focused guard for PS-Q19O explicit neutral macro/session context default.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_prediction_system_result_builder_runner import (  # noqa: E402
    NEUTRAL_CONTEXT_SOURCE_QUALITY_IDS,
    _build_from_kwargs_contract,
    _source_quality_status_map_from_kwargs_contract,
)
from btcts.prediction.source_quality import _provider_family_for_source_id  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19O_MACRO_SESSION_CONTEXT_INPUT_REPAIR_OR_DECISION_2026-06-25.md"
BUILDER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_system_result_builder_runner.py"
SOURCE_QUALITY = REPO_ROOT / "btcts_next/src/btcts/prediction/source_quality.py"

REQUIRED_MARKERS = (
    "ps_q19o_macro_session_context_input_repair_or_decision=true",
    "macro_session_decision=explicit_neutral_context_only_default",
    "macro_context_neutral_default_supplied=true",
    "session_calendar_context_neutral_default_supplied=true",
    "macro_context_source_quality_status_mapped=true",
    "session_calendar_context_source_quality_status_mapped=true",
    "neutral_context_provider_family_mapped=true",
)

FALSE_BOUNDARIES = (
    "external_macro_api_added=false",
    "external_session_calendar_api_added=false",
    "collector_behavior_changed=false",
    "hot_file_read_scope_changed=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _builder_kwargs() -> dict:
    return {
        "rows": [
            {"event_ts": "2026-06-25T00:00:00Z", "price": 100.0, "size": 0.1, "side": "BUY"},
            {"event_ts": "2026-06-25T00:00:01Z", "price": 101.0, "size": 0.2, "side": "SELL"},
            {"event_ts": "2026-06-25T00:00:02Z", "price": 100.5, "size": 0.3, "side": "BUY"},
        ],
        "venue_snapshots": [
            {"source_id": "bitflyer_fx_ticker", "venue": "bitflyer", "symbol": "FX_BTC_JPY", "market_role": "bitflyer_fx", "price": 100.5, "best_bid": 100.0, "best_ask": 101.0, "collector_ts": "2026-06-25T00:00:02Z"},
        ],
        "feature_depth_context_summary": {
            "source_id": "bitflyer_board_summary",
            "bid_level_count": 20,
            "ask_level_count": 20,
            "event_ts": "2026-06-25T00:00:02Z",
        },
        "requested_horizon_groups": ["nowcast", "long_horizon"],
        "requested_horizons_sec": [15, 14400, 86400],
        "previous_prediction_run_id": None,
        "now": "2026-06-25T00:00:03Z",
    }


def test_spec_declares_neutral_context_decision_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_provider_family_mapping_no_longer_unknown_for_macro_session_defaults() -> None:
    assert _provider_family_for_source_id("macro_context", "prediction_neutral_context_default") == "prediction_neutral_context_default"
    assert _provider_family_for_source_id("session_calendar_context", "prediction_neutral_context_default") == "prediction_neutral_context_default"


def test_source_quality_status_map_includes_neutral_context_statuses() -> None:
    statuses = _source_quality_status_map_from_kwargs_contract(_builder_kwargs())
    assert set(NEUTRAL_CONTEXT_SOURCE_QUALITY_IDS) == {"macro_context", "session_calendar_context"}
    assert set(NEUTRAL_CONTEXT_SOURCE_QUALITY_IDS).issubset(set(statuses))
    for source_id in NEUTRAL_CONTEXT_SOURCE_QUALITY_IDS:
        status = statuses[source_id]
        assert status.usable is True
        assert status.source_family == "prediction_neutral_context_default"
        data = status.to_dict()
        assert data["read_only"] is True
        assert data["non_executing"] is True
        assert data["would_send_to_broker"] is False


def test_build_prediction_system_result_observes_macro_session_context_defaults() -> None:
    payload = _build_from_kwargs_contract(_builder_kwargs())
    supplied = set(payload["source_quality_status_ids_supplied"])
    assert set(NEUTRAL_CONTEXT_SOURCE_QUALITY_IDS).issubset(supplied)
    coverage = payload.get("source_artifact_coverage_summary") or {}
    observed = set(coverage.get("observed_required_source_ids") or [])
    missing_quality = set((coverage.get("tier0_source_quality_gate") or {}).get("missing_quality_status_source_ids") or [])
    assert "macro_context" in observed
    assert "session_calendar_context" in observed
    assert "macro_context" not in missing_quality
    assert "session_calendar_context" not in missing_quality
    assert payload.get("would_send_to_broker") is False


def test_source_quality_and_builder_markers_present() -> None:
    builder = BUILDER.read_text(encoding="utf-8")
    source_quality = SOURCE_QUALITY.read_text(encoding="utf-8")
    assert "NEUTRAL_CONTEXT_SOURCE_QUALITY_IDS" in builder
    assert "_add_neutral_context_source_quality_statuses" in builder
    assert "prediction_neutral_context_default" in builder
    assert '"macro_context": "prediction_neutral_context_default"' in source_quality
    assert '"session_calendar_context": "prediction_neutral_context_default"' in source_quality


if __name__ == "__main__":
    test_spec_declares_neutral_context_decision_and_safety_boundaries()
    test_provider_family_mapping_no_longer_unknown_for_macro_session_defaults()
    test_source_quality_status_map_includes_neutral_context_statuses()
    test_build_prediction_system_result_observes_macro_session_context_defaults()
    test_source_quality_and_builder_markers_present()
    print('{"ok": true}')
