# path: ./tools/test_phase4a_prediction_system_ps_q20i_explicit_read_only_loader_binding_helper_disabled_by_default.py
# desc: Focused guard for PS-Q20I explicit read-only loader binding helper disabled by default.

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
from btcts.apps.operator_ui.prediction_warroom.read_models.explicit_read_only_loader_binding_helper import (  # noqa: E402
    EXPLICIT_READ_ONLY_LOADER_BINDING_HELPER_VERSION,
    build_explicit_read_only_loader_binding_helper,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.preferred_row_observation_section import (  # noqa: E402
    PREFERRED_ROW_OBSERVATION_SECTION_KEY,
)
from btcts.market_engine.market_state.consumer_integration_design import LANE_WARROOM_READ  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20I_EXPLICIT_READ_ONLY_LOADER_BINDING_HELPER_DISABLED_BY_DEFAULT_2026-06-26.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/explicit_read_only_loader_binding_helper.py"

REQUIRED_MARKERS = (
    "ps_q20i_explicit_read_only_loader_binding_helper_disabled_by_default=true",
    "explicit_helper_only=true",
    "disabled_by_default=true",
    "enable_explicit_read_only_loader_binding_default=false",
    "target_loader_invoked=false",
    "latest_prediction_artifact_read=false",
    "latest_prediction_warroom_read_model_loader_changed=false",
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


def _adapter_ready() -> dict:
    return build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=True)], lane=LANE_WARROOM_READ).to_dict()


def test_spec_declares_disabled_helper_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_helper_is_disabled_by_default_and_does_not_attach_optional_section() -> None:
    model = _read_model()
    packet = build_explicit_read_only_loader_binding_helper(read_model=model, preferred_row_adapter_packet=_adapter_ready()).to_dict()
    output = packet["output_read_model"]
    assert packet["helper_version"] == EXPLICIT_READ_ONLY_LOADER_BINDING_HELPER_VERSION
    assert packet["helper_state"] == "explicit_read_only_loader_binding_helper_disabled"
    assert packet["enable_explicit_read_only_loader_binding"] is False
    assert packet["dry_run_ready"] is True
    assert packet["optional_section_attached"] is False
    assert PREFERRED_ROW_OBSERVATION_SECTION_KEY not in output
    assert output["market_snapshot"] == model["market_snapshot"]
    assert "explicit_read_only_loader_binding_disabled_by_default" in packet["warning_reasons"]
    assert packet["target_loader_invoked"] is False
    assert packet["would_send_to_broker"] is False


def test_helper_attaches_only_when_explicitly_enabled_and_dry_run_ready() -> None:
    model = _read_model()
    packet = build_explicit_read_only_loader_binding_helper(
        read_model=model,
        preferred_row_adapter_packet=_adapter_ready(),
        enable_explicit_read_only_loader_binding=True,
    ).to_dict()
    output = packet["output_read_model"]
    assert packet["helper_state"] == "explicit_read_only_loader_binding_helper_attached"
    assert packet["enable_explicit_read_only_loader_binding"] is True
    assert packet["dry_run_ready"] is True
    assert packet["optional_section_attached"] is True
    assert PREFERRED_ROW_OBSERVATION_SECTION_KEY in output
    assert output["market_snapshot"] == model["market_snapshot"]
    assert model.get(PREFERRED_ROW_OBSERVATION_SECTION_KEY) is None
    assert output["explicit_read_only_loader_binding_runtime_wired"] is False
    assert output["explicit_read_only_loader_binding_target_loader_invoked"] is False
    assert output["explicit_read_only_loader_binding_would_write_artifact"] is False
    assert output["would_send_to_broker"] is False


def test_helper_blocks_enabled_attach_when_dry_run_not_ready() -> None:
    adapter = build_prediction_warroom_preferred_row_adapter([_row(ok=False), _row(ok=False)], lane=LANE_WARROOM_READ).to_dict()
    packet = build_explicit_read_only_loader_binding_helper(
        read_model=_read_model(),
        preferred_row_adapter_packet=adapter,
        enable_explicit_read_only_loader_binding=True,
    ).to_dict()
    assert packet["helper_state"] == "explicit_read_only_loader_binding_helper_blocked"
    assert packet["dry_run_ready"] is False
    assert packet["optional_section_attached"] is False
    assert "read_only_loader_binding_dry_run_not_ready" in packet["blocked_reasons"]
    assert "consumer_preferred_market_overview_row_missing" in packet["blocked_reasons"]


def test_module_has_no_loader_invocation_io_runtime_binding_or_execution_behavior() -> None:
    text = MODULE.read_text(encoding="utf-8")
    forbidden = (
        "read_text(",
        "write_text(",
        "open(",
        "Path(",
        "load_latest_market_state(",
        "load_latest_prediction_warroom_read_model(",
        "latest_prediction_artifact_path(",
        "load_latest_prediction_payload(",
        "append_jsonl(",
        "send_order(",
        "place_order(",
        "requests.",
        "urllib.",
        "DEFAULT_ENABLE_EXPLICIT_READ_ONLY_LOADER_BINDING = True",
        "target_loader_invoked: bool = True",
        "latest_prediction_artifact_read: bool = True",
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
    test_spec_declares_disabled_helper_and_safety_boundaries()
    test_helper_is_disabled_by_default_and_does_not_attach_optional_section()
    test_helper_attaches_only_when_explicitly_enabled_and_dry_run_ready()
    test_helper_blocks_enabled_attach_when_dry_run_not_ready()
    test_module_has_no_loader_invocation_io_runtime_binding_or_execution_behavior()
    print('{"ok": true}')
