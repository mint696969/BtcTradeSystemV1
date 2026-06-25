# path: ./tools/test_phase4a_prediction_system_ps_q19q_warroom_read_model_artifact_size_cap_alignment.py
# desc: Focused guard for PS-Q19Q WarRoom read-model artifact size cap alignment.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    DEFAULT_MAX_ARTIFACT_BYTES,
    build_latest_prediction_warroom_read_model,
    load_latest_prediction_payload,
    load_latest_prediction_payload_status,
)
from tools.check_phase4a_prediction_system_ps_q19f_warroom_live_smoke import build_ps_q19f_warroom_live_smoke_packet  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19Q_WARROOM_READ_MODEL_ARTIFACT_SIZE_CAP_ALIGNMENT_2026-06-25.md"
READ_MODEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/latest_prediction_warroom_read_model.py"
SMOKE = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q19f_warroom_live_smoke.py"

REQUIRED_MARKERS = (
    "ps_q19q_warroom_read_model_artifact_size_cap_alignment=true",
    "root_cause=latest_prediction_artifact_exceeded_ps_q19c_read_model_max_bytes",
    "old_read_model_max_bytes=5000000",
    "new_read_model_max_bytes=12000000",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _payload() -> dict:
    return {
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "forecast_batch": {
            "generated_at": "2026-06-25T00:00:00Z",
            "read_only": True,
            "non_executing": True,
            "family_count": 1,
            "horizon_count": 1,
            "record_count": 1,
            "records": [
                {
                    "family": "market_regime",
                    "horizon_sec": 15,
                    "horizon_key": "15s",
                    "primary_label": "range_candidate",
                    "confidence": "medium",
                    "score": 0.5,
                    "usable": True,
                    "warnings": [],
                    "drivers": ["range_boundary_visible"],
                    "values_snapshot": {"estimated_signal_strength_percent": 51},
                    "read_only": True,
                    "non_executing": True,
                    "would_send_to_broker": False,
                    "would_write_runtime_artifact": False,
                    "would_append_ledger": False,
                }
            ],
        },
    }


def test_spec_declares_artifact_size_cap_alignment_and_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_default_max_artifact_bytes_allows_current_growth_band() -> None:
    assert DEFAULT_MAX_ARTIFACT_BYTES == 12_000_000
    assert DEFAULT_MAX_ARTIFACT_BYTES > 5_250_000


def test_payload_status_reports_oversize_blocker_instead_of_silent_empty(tmp_path: Path) -> None:
    target = tmp_path / "latest_prediction_system_result.json"
    target.write_text(json.dumps(_payload()) + "\n" + (" " * 256), encoding="utf-8")
    status = load_latest_prediction_payload_status(path=target, max_bytes=32)
    assert status["ok"] is False
    assert status["artifact_size_bytes"] > 32
    assert status["blocked_reason"] == "latest_prediction_artifact_exceeds_read_model_max_bytes"
    assert load_latest_prediction_payload(path=target, max_bytes=32) == {}


def test_read_model_builds_rows_when_payload_available() -> None:
    model = build_latest_prediction_warroom_read_model(payload=_payload(), now_utc="2026-06-25T00:00:01Z")
    assert model["ok"] is True
    assert model["record_count"] == 1
    assert model["freshness_state"] == "fresh"
    assert model["selected_records_by_horizon"]["15"]
    assert model["would_send_to_broker"] is False


def test_smoke_fails_when_supplied_read_model_is_not_ready() -> None:
    model = build_latest_prediction_warroom_read_model(payload={}, now_utc="2026-06-25T00:00:01Z")
    packet = build_ps_q19f_warroom_live_smoke_packet(
        supplied_read_model=model,
        manual_visual_confirmation=True,
        observed_panel_visible=True,
        observed_prediction_rows=True,
        observed_market_snapshot=True,
        observed_safety_flags=True,
    )
    assert packet["ok"] is False
    assert "ps_q19c_read_model_not_ready" in packet["failures"]
    assert "ps_q19d_prediction_rows_missing" in packet["failures"]


def test_file_markers_present() -> None:
    read_model = READ_MODEL.read_text(encoding="utf-8")
    smoke = SMOKE.read_text(encoding="utf-8")
    assert "DEFAULT_MAX_ARTIFACT_BYTES = 12_000_000" in read_model
    assert "load_latest_prediction_payload_status" in read_model
    assert "payload_load_blocked_reason" in read_model
    assert "ps_q19c_read_model_not_ready" in smoke
    assert "ps_q19d_prediction_rows_missing" in smoke


if __name__ == "__main__":
    test_spec_declares_artifact_size_cap_alignment_and_boundaries()
    test_default_max_artifact_bytes_allows_current_growth_band()
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as tmp:
        test_payload_status_reports_oversize_blocker_instead_of_silent_empty(Path(tmp))
    test_read_model_builds_rows_when_payload_available()
    test_smoke_fails_when_supplied_read_model_is_not_ready()
    test_file_markers_present()
    print('{"ok": true}')
