# path: ./tools/test_phase4a_prediction_system_ps_q23j_manifest_first_display_default.py
# desc: Focused guard for PS-Q23J manifest-first default loader in WarRoom latest prediction display panel.

from __future__ import annotations

import json
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels import latest_prediction_warroom_read_model_display_panel as panel  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23J_MANIFEST_FIRST_DISPLAY_DEFAULT_2026-06-28.md"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"


def _model(*, mode: str = "distributed") -> dict:
    return {
        "ok": True,
        "read_model_version": panel.LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "generated_at": "2026-06-28T15:55:36Z",
        "age_sec": 30,
        "freshness_state": "fresh",
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
        "selected_horizon_sec": [15],
        "selected_records_by_horizon": {
            "15": [
                {
                    "family": "directional",
                    "horizon_sec": 15,
                    "horizon_key": "15s",
                    "primary_label": "up",
                    "confidence": "medium",
                    "score": 0.1,
                    "usable": True,
                    "warnings": [],
                    "drivers": [],
                    "read_only": True,
                    "non_executing": True,
                    "would_send_to_broker": False,
                    "would_write_runtime_artifact": False,
                    "would_append_ledger": False,
                }
            ]
        },
        "market_snapshot": {},
        "safety_flags": {"records_all_safe": True},
        "source_artifact_mode": mode,
        "source_artifact_relative_path": "prediction/latest_manifest.json" if mode == "distributed" else "prediction/latest_prediction_system_result.json",
        "distributed_reader_ready": mode == "distributed",
        "distributed_stale_vs_legacy": False,
        "legacy_fallback_ready": True,
    }


def test_spec_declares_manifest_first_display_default_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23j_manifest_first_display_default=true",
        "ui_display_default_loader_manifest_first=true",
        "legacy_loader_retained=true",
        "read_model_injection_compatibility_retained=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_panel_default_uses_manifest_first_loader() -> None:
    calls = {"count": 0}
    def fake_loader(**kwargs):
        calls["count"] += 1
        assert kwargs.get("hot_latest_root_hint") == panel.Q23J_DISPLAY_DEFAULT_HOT_ROOT_HINT
        return _model(mode="distributed")
    with patch.object(panel, "load_latest_prediction_warroom_read_model_manifest_first", side_effect=fake_loader):
        packet = panel.build_latest_prediction_warroom_display_panel_packet(lang="en", fragment_enabled=False)
    assert calls["count"] == 1
    assert packet["ok"] is True
    assert packet["source_artifact_mode"] == "distributed"
    assert packet["source_artifact_relative_path"] == "prediction/latest_manifest.json"
    assert packet["distributed_reader_ready"] is True
    assert packet["distributed_stale_vs_legacy"] is False
    assert packet["legacy_fallback_ready"] is True
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["status_artifact_write_allowed"] is False
    assert packet["prediction_artifact_write_allowed"] is False
    assert packet["view_artifact_write_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_read_model_injection_still_bypasses_default_loader() -> None:
    def forbidden_loader():
        raise AssertionError("default manifest-first loader must not be called when read_model is supplied")
    supplied = _model(mode="legacy_fallback")
    with patch.object(panel, "load_latest_prediction_warroom_read_model_manifest_first", side_effect=forbidden_loader):
        packet = panel.build_latest_prediction_warroom_display_panel_packet(read_model=supplied, lang="en", fragment_enabled=False)
    assert packet["ok"] is True
    assert packet["source_artifact_mode"] == "legacy_fallback"
    assert packet["source_artifact_relative_path"] == "prediction/latest_prediction_system_result.json"


def test_panel_imports_manifest_first_and_not_legacy_default() -> None:
    text = PANEL.read_text(encoding="utf-8")
    assert "load_latest_prediction_warroom_read_model_manifest_first" in text
    assert "else load_latest_prediction_warroom_read_model_manifest_first(hot_latest_root_hint=_prediction_display_hot_root_hint())" in text
    assert "Q23J_DISPLAY_DEFAULT_HOT_ROOT_HINT" in text
    assert panel.Q23J_DISPLAY_DEFAULT_HOT_ROOT_HINT == r"D:\btc_ts_hot"
    assert "else load_latest_prediction_warroom_read_model()" not in text


def test_panel_has_no_scheduler_writer_or_broker_code() -> None:
    text = PANEL.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "write_distributed_sidecars_once",
        "run_one_shot_write",
        "send_order(",
        "place_order(",
        ".write_text(",
        ".write_bytes(",
        "os.replace",
    ):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_spec_declares_manifest_first_display_default_contract()
    test_panel_default_uses_manifest_first_loader()
    test_read_model_injection_still_bypasses_default_loader()
    test_panel_imports_manifest_first_and_not_legacy_default()
    test_panel_has_no_scheduler_writer_or_broker_code()
    print(json.dumps({"ok": True}))
