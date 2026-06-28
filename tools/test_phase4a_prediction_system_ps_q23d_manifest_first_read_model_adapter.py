# path: ./tools/test_phase4a_prediction_system_ps_q23d_manifest_first_read_model_adapter.py
# desc: Focused guard for PS-Q23D manifest-first WarRoom read-model adapter.

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

from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    LATEST_MANIFEST_RELATIVE_PATH,
    LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
    load_latest_prediction_payload,
    load_latest_prediction_payload_status_manifest_first,
    load_latest_prediction_warroom_read_model_manifest_first,
)
from tools.run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once import (  # noqa: E402
    REQUIRED_CONFIRMATION,
    write_distributed_sidecars_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23D_MANIFEST_FIRST_READ_MODEL_ADAPTER_2026-06-28.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/latest_prediction_warroom_read_model.py"


def _payload(generated_at: str = "2026-06-28T08:35:27Z") -> dict:
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
            "family_count": 2,
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
                    "family": "trend_bias",
                    "horizon_sec": 60,
                    "horizon_key": "60s",
                    "primary_label": "short_bias",
                    "confidence": "medium",
                    "score": 0.66,
                    "usable": True,
                    "warnings": [],
                    "drivers": ["ma_falling_short_below_long"],
                    "values_snapshot": {"estimated_reference_hit_rate_percent": 65},
                    "read_only": True,
                    "non_executing": True,
                    "would_send_to_broker": False,
                    "would_write_runtime_artifact": False,
                    "would_append_ledger": False,
                },
            ],
        },
    }


def _seed_latest(root: Path, generated_at: str = "2026-06-28T08:35:27Z") -> Path:
    latest = root / LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps(_payload(generated_at), ensure_ascii=False, sort_keys=True), encoding="utf-8")
    status = root / "prediction/status/non_ui_scheduled_producer_status.json"
    status.parent.mkdir(parents=True, exist_ok=True)
    status.write_text(json.dumps({"ok": True}, ensure_ascii=False), encoding="utf-8")
    return latest


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


def test_spec_declares_adapter_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23d_manifest_first_read_model_adapter=true",
        "manifest_first_adapter_added=true",
        "existing_legacy_loader_retained=true",
        "ui_default_call_path_changed=false",
        "freshness_arbitration_against_legacy_latest=true",
        "writes_d_hot_runtime_artifacts=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_existing_legacy_loader_remains_unchanged(tmp_path: Path) -> None:
    latest = _seed_latest(tmp_path)
    payload = load_latest_prediction_payload(path=latest, max_bytes=100_000)
    assert payload["forecast_batch"]["record_count"] == 2
    assert payload["forecast_batch"]["generated_at"] == "2026-06-28T08:35:27Z"


def test_manifest_first_adapter_selects_distributed_when_current(tmp_path: Path) -> None:
    _seed_latest(tmp_path, generated_at="2026-06-28T08:35:27Z")
    _write_sidecars(tmp_path)
    status = load_latest_prediction_payload_status_manifest_first(hot_latest_root_hint=tmp_path)
    assert status["ok"] is True
    assert status["source_artifact_mode"] == "distributed"
    assert status["distributed_reader_ready"] is True
    assert status["legacy_fallback_ready"] is True
    assert status["distributed_stale_vs_legacy"] is False
    assert status["payload"]["forecast_batch"]["record_count"] == 2
    assert status["source_artifact_relative_path"] == LATEST_MANIFEST_RELATIVE_PATH
    assert (tmp_path / LATEST_MANIFEST_RELATIVE_PATH).exists()


def test_manifest_first_adapter_falls_back_when_legacy_is_newer(tmp_path: Path) -> None:
    _seed_latest(tmp_path, generated_at="2026-06-28T08:35:27Z")
    _write_sidecars(tmp_path)
    _seed_latest(tmp_path, generated_at="2026-06-28T09:05:30Z")
    status = load_latest_prediction_payload_status_manifest_first(hot_latest_root_hint=tmp_path)
    assert status["ok"] is True
    assert status["source_artifact_mode"] == "legacy_fallback"
    assert status["distributed_reader_ready"] is True
    assert status["legacy_fallback_ready"] is True
    assert status["distributed_stale_vs_legacy"] is True
    assert status["payload"]["forecast_batch"]["generated_at"] == "2026-06-28T09:05:30Z"
    assert "distributed_artifact_older_than_legacy_latest" in status["warning_reason_codes"]


def test_manifest_first_read_model_preserves_display_only_safety(tmp_path: Path) -> None:
    _seed_latest(tmp_path, generated_at="2026-06-28T08:35:27Z")
    _write_sidecars(tmp_path)
    model = load_latest_prediction_warroom_read_model_manifest_first(
        hot_latest_root_hint=tmp_path,
        now_utc="2026-06-28T08:36:00Z",
    )
    assert model["ok"] is True
    assert model["source_artifact_mode"] == "distributed"
    assert model["record_count"] == 2
    assert model["source_artifact_relative_path"] == LATEST_MANIFEST_RELATIVE_PATH
    assert model["read_only"] is True
    assert model["non_executing"] is True
    assert model["display_only"] is True
    for key in (
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_send_to_broker",
    ):
        assert model[key] is False, key


def test_adapter_module_adds_no_write_calls() -> None:
    text = MODULE.read_text(encoding="utf-8")
    added_section = text.split("# PS-Q23D manifest-first distributed read adapter", 1)[1]
    for marker in (".write_text(", ".write_bytes(", ".mkdir(", ".unlink(", "os.replace", "shutil."):
        assert marker not in added_section, marker
    assert "load_latest_prediction_payload_status_manifest_first" in text
    assert "load_latest_prediction_warroom_read_model_manifest_first" in text


if __name__ == "__main__":
    test_spec_declares_adapter_contract()
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        test_existing_legacy_loader_remains_unchanged(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_manifest_first_adapter_selects_distributed_when_current(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_manifest_first_adapter_falls_back_when_legacy_is_newer(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_manifest_first_read_model_preserves_display_only_safety(Path(tmp))
    test_adapter_module_adds_no_write_calls()
    print(json.dumps({"ok": True}))
