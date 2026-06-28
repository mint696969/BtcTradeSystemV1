# path: ./tools/test_phase4a_prediction_system_ps_q23e_manifest_first_live_read_model_diagnostic.py
# desc: Focused guard for PS-Q23E manifest-first live read-model diagnostic.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q23e_manifest_first_live_read_model import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    run_manifest_first_live_read_model_diagnostic,
)
from tools.run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once import (  # noqa: E402
    REQUIRED_CONFIRMATION,
    write_distributed_sidecars_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23E_MANIFEST_FIRST_LIVE_READ_MODEL_DIAGNOSTIC_2026-06-28.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q23e_manifest_first_live_read_model.py"


def _payload(generated_at: str = "2026-06-28T10:05:27Z") -> dict:
    return {
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "forecast_batch": {
            "generated_at": generated_at,
            "read_only": True,
            "non_executing": True,
            "family_count": 1,
            "horizon_count": 2,
            "record_count": 2,
            "records": [
                {
                    "family": "market_regime",
                    "horizon_sec": 15,
                    "horizon_key": "15s",
                    "primary_label": "trend_candidate",
                    "confidence": "medium",
                    "score": 0.62,
                    "usable": True,
                    "warnings": [],
                    "drivers": ["moving_average_directional_structure"],
                    "values_snapshot": {"estimated_signal_strength_percent": 61},
                    "read_only": True,
                    "non_executing": True,
                    "would_send_to_broker": False,
                    "would_write_runtime_artifact": False,
                    "would_append_ledger": False,
                },
                {
                    "family": "market_regime",
                    "horizon_sec": 60,
                    "horizon_key": "60s",
                    "primary_label": "trend_candidate",
                    "confidence": "medium",
                    "score": 0.61,
                    "usable": True,
                    "warnings": [],
                    "drivers": ["moving_average_directional_structure"],
                    "values_snapshot": {"estimated_signal_strength_percent": 60},
                    "read_only": True,
                    "non_executing": True,
                    "would_send_to_broker": False,
                    "would_write_runtime_artifact": False,
                    "would_append_ledger": False,
                },
            ],
        },
    }


def _seed_latest(root: Path, generated_at: str = "2026-06-28T10:05:27Z") -> None:
    latest = root / LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps(_payload(generated_at), ensure_ascii=False, sort_keys=True), encoding="utf-8")
    status = root / "prediction/status/non_ui_scheduled_producer_status.json"
    status.parent.mkdir(parents=True, exist_ok=True)
    status.write_text(json.dumps({"ok": True}, ensure_ascii=False), encoding="utf-8")


def _write_sidecars(root: Path) -> None:
    result = write_distributed_sidecars_once(
        hot_root=root,
        operator_acknowledged=True,
        execute_sidecar_write_once=True,
        confirmation=REQUIRED_CONFIRMATION,
        require_clean_tree=False,
        allow_test_root=True,
    )
    assert result["success"] is True


def test_spec_declares_q23e_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23e_manifest_first_live_read_model_diagnostic=true",
        "uses_q23d_manifest_first_adapter=true",
        "ui_default_call_path_changed=false",
        "compact_live_output=true",
        "writes_d_hot_runtime_artifacts=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_diagnostic_selects_distributed_when_current(tmp_path: Path) -> None:
    _seed_latest(tmp_path, generated_at="2026-06-28T10:05:27Z")
    _write_sidecars(tmp_path)
    result = run_manifest_first_live_read_model_diagnostic(hot_root=tmp_path, now_utc="2026-06-28T10:06:00Z")
    assert result["ok"] is True
    assert result["diagnostic_version"] == DIAGNOSTIC_VERSION
    assert result["source_artifact_mode"] == "distributed"
    assert result["distributed_reader_ready"] is True
    assert result["legacy_fallback_ready"] is True
    assert result["distributed_stale_vs_legacy"] is False
    assert result["selected_record_count"] == 2
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert result["would_send_to_broker"] is False


def test_diagnostic_selects_legacy_when_distributed_is_stale(tmp_path: Path) -> None:
    _seed_latest(tmp_path, generated_at="2026-06-28T10:05:27Z")
    _write_sidecars(tmp_path)
    _seed_latest(tmp_path, generated_at="2026-06-28T10:10:27Z")
    result = run_manifest_first_live_read_model_diagnostic(hot_root=tmp_path, now_utc="2026-06-28T10:11:00Z")
    assert result["ok"] is True
    assert result["source_artifact_mode"] == "legacy_fallback"
    assert result["distributed_reader_ready"] is True
    assert result["legacy_fallback_ready"] is True
    assert result["distributed_stale_vs_legacy"] is True
    assert result["selected_generated_at"] == "2026-06-28T10:10:27Z"
    assert "distributed_artifact_older_than_legacy_latest" in result["payload_status"]["warning_reason_codes"]


def test_legacy_only_option_disables_distributed_preference(tmp_path: Path) -> None:
    _seed_latest(tmp_path, generated_at="2026-06-28T10:05:27Z")
    _write_sidecars(tmp_path)
    result = run_manifest_first_live_read_model_diagnostic(hot_root=tmp_path, prefer_distributed=False, now_utc="2026-06-28T10:06:00Z")
    assert result["ok"] is True
    assert result["source_artifact_mode"] == "legacy_fallback"
    assert result["distributed_reader_ready"] is False
    assert result["legacy_fallback_ready"] is True


def test_tool_contains_no_runtime_write_calls() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for forbidden in (".write_text(", ".write_bytes(", ".mkdir(", ".unlink(", "os.replace", "shutil."):
        assert forbidden not in text, forbidden
    assert "compact" in text
    assert "read_only_diagnostic" in text


if __name__ == "__main__":
    test_spec_declares_q23e_contract()
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        test_diagnostic_selects_distributed_when_current(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_diagnostic_selects_legacy_when_distributed_is_stale(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_legacy_only_option_disables_distributed_preference(Path(tmp))
    test_tool_contains_no_runtime_write_calls()
    print(json.dumps({"ok": True}))
