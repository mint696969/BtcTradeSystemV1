# path: ./tools/test_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars.py
# desc: Focused guard for PS-Q23B gated distributed sidecar writer.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once import (  # noqa: E402
    LATEST_MANIFEST_RELATIVE_PATH,
    LATEST_RELATIVE_PATH,
    REQUIRED_CONFIRMATION,
    STATUS_RELATIVE_PATH,
    WRITER_VERSION,
    write_distributed_sidecars_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23B_GATED_DUAL_WRITE_SIDECARS_2026-06-28.md"
TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once.py"


def _payload() -> dict:
    return {
        "generated_at": "2026-06-28T07:20:25Z",
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "forecast_batch": {
            "generated_at": "2026-06-28T07:20:25Z",
            "family_count": 2,
            "horizon_count": 2,
            "record_count": 2,
            "records": [
                {"family": "market_regime", "horizon_key": "15s", "score": 0.5, "warnings": []},
                {"family": "breakout", "horizon_key": "60s", "score": 0.7, "warnings": ["sample_warning"]},
            ],
        },
    }


def _seed_latest(root: Path) -> tuple[Path, Path]:
    latest = root / LATEST_RELATIVE_PATH
    status = root / STATUS_RELATIVE_PATH
    latest.parent.mkdir(parents=True, exist_ok=True)
    status.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps(_payload(), ensure_ascii=False, sort_keys=True), encoding="utf-8")
    status.write_text(json.dumps({"ok": True}, ensure_ascii=False), encoding="utf-8")
    return latest, status


def test_spec_declares_gated_dual_write_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23b_gated_dual_write_sidecars=true",
        "explicit_sidecar_write_gate_required=true",
        "default_execution_is_dry_run_no_write=true",
        "legacy_latest_retained=true",
        "latest_manifest_atomic_replace=true",
        "run_manifest_written_last=true",
        "status_artifact_written=false",
        "broker_autotrade=false",
        REQUIRED_CONFIRMATION,
    ):
        assert marker in text, marker


def test_default_blocks_without_writing(tmp_path: Path) -> None:
    _seed_latest(tmp_path)
    result = write_distributed_sidecars_once(
        hot_root=tmp_path,
        operator_acknowledged=False,
        execute_sidecar_write_once=False,
        confirmation="",
        require_clean_tree=False,
        allow_test_root=True,
    )
    assert result["success"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert "operator_acknowledgement_required" in result["blocked_reasons"]
    assert not (tmp_path / LATEST_MANIFEST_RELATIVE_PATH).exists()
    assert not (tmp_path / "prediction/runs").exists()


def test_gated_test_root_write_materializes_sidecars_without_touching_legacy_latest_or_status(tmp_path: Path) -> None:
    latest, status = _seed_latest(tmp_path)
    before_latest = latest.read_bytes()
    before_status = status.read_bytes()
    result = write_distributed_sidecars_once(
        hot_root=tmp_path,
        operator_acknowledged=True,
        execute_sidecar_write_once=True,
        confirmation=REQUIRED_CONFIRMATION,
        require_clean_tree=False,
        allow_test_root=True,
    )
    assert result["success"] is True
    assert result["writer_version"] == WRITER_VERSION
    assert result["latest_manifest_written"] is True
    assert result["run_sidecars_written"] is True
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert latest.read_bytes() == before_latest
    assert status.read_bytes() == before_status
    latest_manifest = tmp_path / LATEST_MANIFEST_RELATIVE_PATH
    assert latest_manifest.exists()
    manifest = json.loads(latest_manifest.read_text(encoding="utf-8"))
    assert manifest["layout_version"] == WRITER_VERSION
    assert manifest["legacy_latest_retained"] is True
    assert manifest["status_artifact_written"] is False
    assert ":" not in manifest["run_dir"]
    run_dir = tmp_path / manifest["run_dir"]
    assert run_dir.exists()
    for name in ("manifest.json", "summary.json", "forecast_batch_summary.json", "forecast_records.jsonl", "warnings.json", "lineage.json", "timings.json", "safety.json", "checksums.json"):
        assert (run_dir / name).exists(), name
    records_lines = (run_dir / "forecast_records.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(records_lines) == 2
    assert json.loads(records_lines[0])["family"] == "market_regime"
    run_manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert run_manifest["legacy_latest_modified"] is False
    assert run_manifest["status_artifact_written"] is False


def test_live_d_hot_write_requires_exact_gate_even_when_layout_exists(tmp_path: Path) -> None:
    _seed_latest(tmp_path)
    result = write_distributed_sidecars_once(
        hot_root=tmp_path,
        operator_acknowledged=True,
        execute_sidecar_write_once=True,
        confirmation="WRONG",
        require_clean_tree=False,
        allow_test_root=True,
    )
    assert result["success"] is False
    assert "exact_distributed_sidecar_write_confirmation_required" in result["blocked_reasons"]
    assert not (tmp_path / LATEST_MANIFEST_RELATIVE_PATH).exists()


def test_tool_markers_present() -> None:
    text = TOOL.read_text(encoding="utf-8")
    assert "REQUIRED_CONFIRMATION" in text
    assert "os.replace" in text
    assert "latest_prediction_artifact_written" in text
    assert "status_artifact_written" in text
    assert "broker_private_api_allowed" in text
    assert "autotrade_trigger_allowed" in text


if __name__ == "__main__":
    test_spec_declares_gated_dual_write_contract()
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        test_default_blocks_without_writing(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_gated_test_root_write_materializes_sidecars_without_touching_legacy_latest_or_status(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_live_d_hot_write_requires_exact_gate_even_when_layout_exists(Path(tmp))
    test_tool_markers_present()
    print(json.dumps({"ok": True}))
