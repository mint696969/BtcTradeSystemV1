# path: ./tools/test_phase4a_prediction_system_ps_q20g_warroom_read_model_optional_preferred_row_observation_section.py
# desc: Focused guard for PS-Q20G optional preferred-row observation section.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from btcts.apps.operator_ui.components.prediction_warroom_preferred_row_adapter import (  # noqa: E402
    build_prediction_warroom_preferred_row_adapter,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.preferred_row_observation_section import (  # noqa: E402
    PREFERRED_ROW_OBSERVATION_SECTION_KEY,
    PREFERRED_ROW_OBSERVATION_SECTION_VERSION,
    attach_preferred_row_observation_section,
    build_preferred_row_observation_section,
)
from btcts.market_engine.market_state.consumer_integration_design import LANE_WARROOM_READ  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20G_WARROOM_READ_MODEL_OPTIONAL_PREFERRED_ROW_OBSERVATION_SECTION_2026-06-26.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/preferred_row_observation_section.py"

REQUIRED_MARKERS = (
    "ps_q20g_warroom_read_model_optional_preferred_row_observation_section=true",
    "optional_section=true",
    "read_only_section=true",
    "explicit_attach_required=true",
    "latest_prediction_warroom_read_model_loader_changed=false",
    "existing_market_snapshot_replaced=false",
    "existing_warroom_runtime_rewired=false",
)

FALSE_BOUNDARIES = (
    "component_runtime_binding_allowed=false",
    "ui_code_changed=false",
    "warroom_ui_trigger_enabled=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "runtime_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "would_write_warroom_view_artifact=false",
    "ps_q19r_scoring_policy_changed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _row(*, ok: bool = True) -> dict:
    if ok:
        return {
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "symbol_raw": "FX_BTC_JPY",
            "collector_ts": "2026-06-25T12:04:14Z",
            "trust_state": "trusted",
            "interpretation_bucket": "allow_structural_use",
            "semantic_observer_status": "healthy",
            "best_bid": 9905261,
            "best_ask": 9907274,
            "spread": 2013,
            "mid_price": 9906267.5,
            "source_series_id": "series:1",
            "source_stream_session_id": "stream:1",
        }
    return {
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "symbol_raw": "FX_BTC_JPY",
        "collector_ts": "2026-06-25T12:04:14Z",
        "trust_state": "quarantined",
        "interpretation_bucket": "reanchor_required",
        "semantic_observer_status": "broken",
        "best_bid": 9906282,
        "best_ask": 9906280,
        "spread": -2,
        "mid_price": 9906281,
        "source_series_id": "series:1",
        "source_stream_session_id": "stream:1",
    }


def _read_model() -> dict:
    return {
        "ok": True,
        "read_model_version": "prediction_warroom.latest_prediction_warroom_read_model.ps_q19c.v1",
        "market_snapshot": {"source_kind": "market_state_preferred", "market_uid": "bitflyer.fx.FX_BTC_JPY", "spread": 2013},
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
    }


def test_spec_declares_optional_section_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_section_ready_when_adapter_has_preferred_row() -> None:
    adapter = build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=True)], lane=LANE_WARROOM_READ).to_dict()
    section = build_preferred_row_observation_section(read_model=_read_model(), preferred_row_adapter_packet=adapter).to_dict()
    assert section["section_version"] == PREFERRED_ROW_OBSERVATION_SECTION_VERSION
    assert section["section_key"] == PREFERRED_ROW_OBSERVATION_SECTION_KEY
    assert section["section_state"] == "preferred_row_observation_section_ready"
    assert section["adapter_packet_present"] is True
    assert section["adapter_allowed_for_warroom"] is True
    assert section["selected_row_available"] is True
    assert section["selected_row_summary"]["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert section["selected_row_summary"]["trust_state"] == "trusted"
    assert section["selected_row_summary"]["spread"] == 2013
    assert section["diagnostic_rows_retained"] is True
    assert section["would_send_to_broker"] is False


def test_attach_adds_optional_section_without_replacing_market_snapshot_or_mutating_original() -> None:
    model = _read_model()
    original_snapshot = dict(model["market_snapshot"])
    adapter = build_prediction_warroom_preferred_row_adapter([_row(ok=True)], lane=LANE_WARROOM_READ).to_dict()
    attached = attach_preferred_row_observation_section(model, preferred_row_adapter_packet=adapter)
    assert PREFERRED_ROW_OBSERVATION_SECTION_KEY in attached
    assert attached["market_snapshot"] == original_snapshot
    assert model.get(PREFERRED_ROW_OBSERVATION_SECTION_KEY) is None
    assert attached["preferred_row_observation_section_attached"] is True
    assert attached["preferred_row_observation_section_runtime_wired"] is False
    assert attached["market_snapshot_replaced_by_preferred_row_observation"] is False
    assert attached["would_send_to_broker"] is False


def test_section_observe_only_when_adapter_missing() -> None:
    section = build_preferred_row_observation_section(read_model=_read_model(), preferred_row_adapter_packet=None).to_dict()
    assert section["section_state"] == "preferred_row_observation_section_not_attached"
    assert section["adapter_packet_present"] is False
    assert section["selected_row_available"] is False
    assert "preferred_row_adapter_packet_not_supplied_for_design_context" in section["warning_reasons"]


def test_section_blocks_when_adapter_fail_closed() -> None:
    adapter = build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=False)], lane=LANE_WARROOM_READ).to_dict()
    section = build_preferred_row_observation_section(read_model=_read_model(), preferred_row_adapter_packet=adapter).to_dict()
    assert section["section_state"] == "preferred_row_observation_section_blocked"
    assert section["adapter_packet_present"] is True
    assert section["adapter_allowed_for_warroom"] is False
    assert section["selected_row_available"] is False
    assert "consumer_preferred_market_overview_row_missing" in section["blocked_reasons"]


def test_module_has_no_runtime_io_or_control_behavior() -> None:
    text = MODULE.read_text(encoding="utf-8")
    forbidden = (
        "read_text(",
        "write_text(",
        "open(",
        "Path(",
        "load_latest_market_state(",
        "load_latest_prediction_warroom_read_model(",
        "append_jsonl(",
        "send_order(",
        "place_order(",
        "requests.",
        "urllib.",
        "latest_prediction_warroom_read_model_loader_changed: bool = True",
        "component_runtime_binding_allowed: bool = True",
        "ui_code_changed: bool = True",
        "producer_enabled: bool = True",
        "scheduler_enabled: bool = True",
        "warroom_ui_trigger_enabled: bool = True",
        "view_artifact_write_allowed: bool = True",
        "would_write_warroom_view_artifact: bool = True",
        "ps_q19r_scoring_policy_changed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "broker_private_api_allowed: bool = True",
        "would_send_to_broker: bool = True",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_optional_section_and_safety_boundaries()
    test_section_ready_when_adapter_has_preferred_row()
    test_attach_adds_optional_section_without_replacing_market_snapshot_or_mutating_original()
    test_section_observe_only_when_adapter_missing()
    test_section_blocks_when_adapter_fail_closed()
    test_module_has_no_runtime_io_or_control_behavior()
    print('{"ok": true}')
