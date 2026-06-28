# path: ./tools/test_phase4a_prediction_system_ps_q23c_distributed_reader_validator.py
# desc: Focused guard for PS-Q23C distributed reader validator.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q23a_read_only_artifact_layout_builder import LATEST_RELATIVE_PATH, STATUS_RELATIVE_PATH  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q23c_distributed_reader_validator import (  # noqa: E402
    LATEST_MANIFEST_RELATIVE_PATH,
    VALIDATOR_VERSION,
    run_reader_validator,
)
from tools.run_phase4a_prediction_system_ps_q23b_gated_dual_write_sidecars_once import (  # noqa: E402
    REQUIRED_CONFIRMATION,
    write_distributed_sidecars_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23C_DISTRIBUTED_READER_VALIDATOR_2026-06-28.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q23c_distributed_reader_validator.py"


def _payload(generated_at: str = "2026-06-28T08:35:27Z") -> dict:
    return {
        "generated_at": generated_at,
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "forecast_batch": {
            "generated_at": generated_at,
            "family_count": 2,
            "horizon_count": 2,
            "record_count": 2,
            "records": [
                {"family": "market_regime", "horizon_key": "15s", "score": 0.5, "warnings": []},
                {"family": "breakout", "horizon_key": "60s", "score": 0.7, "warnings": ["sample_warning"]},
            ],
        },
    }


def _seed_latest(root: Path, generated_at: str = "2026-06-28T08:35:27Z") -> None:
    latest = root / LATEST_RELATIVE_PATH
    status = root / STATUS_RELATIVE_PATH
    latest.parent.mkdir(parents=True, exist_ok=True)
    status.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps(_payload(generated_at), ensure_ascii=False, sort_keys=True), encoding="utf-8")
    status.write_text(json.dumps({"ok": True}, ensure_ascii=False), encoding="utf-8")


def test_spec_declares_reader_validator_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23c_distributed_reader_validator=true",
        "prefers_latest_manifest=true",
        "reads_distributed_sidecars=true",
        "fallback_to_legacy_latest=true",
        "writes_d_hot_runtime_artifacts=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_reader_prefers_distributed_sidecars_when_present(tmp_path: Path) -> None:
    _seed_latest(tmp_path)
    write_result = write_distributed_sidecars_once(
        hot_root=tmp_path,
        operator_acknowledged=True,
        execute_sidecar_write_once=True,
        confirmation=REQUIRED_CONFIRMATION,
        require_clean_tree=False,
        allow_test_root=True,
    )
    assert write_result["success"] is True
    result = run_reader_validator(hot_root=tmp_path)
    assert result["validator_version"] == VALIDATOR_VERSION
    assert result["source_artifact_mode"] == "distributed"
    assert result["distributed_reader_ready"] is True
    assert result["legacy_fallback_ready"] is True
    assert result["selected_record_count"] == 2
    assert result["distributed"]["record_count"] == 2
    assert result["distributed"]["summary"]["records_embedded"] is False
    assert ":" not in result["distributed"]["run_dir"]
    assert (tmp_path / LATEST_MANIFEST_RELATIVE_PATH).exists()
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert result["would_send_to_broker"] is False


def test_reader_falls_back_to_legacy_latest_when_manifest_missing(tmp_path: Path) -> None:
    _seed_latest(tmp_path)
    result = run_reader_validator(hot_root=tmp_path)
    assert result["source_artifact_mode"] == "legacy_fallback"
    assert result["distributed_reader_ready"] is False
    assert result["legacy_fallback_ready"] is True
    assert result["selected_record_count"] == 2
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False


def test_reader_detects_record_count_mismatch_and_uses_legacy_fallback(tmp_path: Path) -> None:
    _seed_latest(tmp_path)
    write_distributed_sidecars_once(
        hot_root=tmp_path,
        operator_acknowledged=True,
        execute_sidecar_write_once=True,
        confirmation=REQUIRED_CONFIRMATION,
        require_clean_tree=False,
        allow_test_root=True,
    )
    manifest = json.loads((tmp_path / LATEST_MANIFEST_RELATIVE_PATH).read_text(encoding="utf-8"))
    records_path = tmp_path / manifest["sidecars"]["forecast_records"]
    lines = records_path.read_text(encoding="utf-8").splitlines()
    records_path.write_text(lines[0] + "\n", encoding="utf-8")
    result = run_reader_validator(hot_root=tmp_path)
    assert result["source_artifact_mode"] == "legacy_fallback"
    assert result["distributed_reader_ready"] is False
    assert result["legacy_fallback_ready"] is True
    assert any(item.startswith("record_count_mismatch") for item in result["distributed"]["distributed_blockers"])


def test_reader_uses_legacy_fallback_when_legacy_latest_is_newer_than_distributed(tmp_path: Path) -> None:
    _seed_latest(tmp_path, generated_at="2026-06-28T08:35:27Z")
    write_distributed_sidecars_once(
        hot_root=tmp_path,
        operator_acknowledged=True,
        execute_sidecar_write_once=True,
        confirmation=REQUIRED_CONFIRMATION,
        require_clean_tree=False,
        allow_test_root=True,
    )
    _seed_latest(tmp_path, generated_at="2026-06-28T09:05:30Z")
    result = run_reader_validator(hot_root=tmp_path)
    assert result["distributed_reader_ready"] is True
    assert result["legacy_fallback_ready"] is True
    assert result["distributed_stale_vs_legacy"] is True
    assert result["source_artifact_mode"] == "legacy_fallback"
    assert result["selected_generated_at"] == "2026-06-28T09:05:30Z"
    assert "distributed_artifact_older_than_legacy_latest" in result["distributed"]["distributed_warnings"]


def test_validator_tool_contains_no_runtime_write_calls() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        ".write_text(",
        ".write_bytes(",
        ".mkdir(",
        ".unlink(",
        "os.replace",
        "shutil.",
    )
    for item in forbidden:
        assert item not in text, item
    assert "source_artifact_mode" in text
    assert "legacy_fallback" in text


if __name__ == "__main__":
    test_spec_declares_reader_validator_contract()
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        test_reader_prefers_distributed_sidecars_when_present(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_reader_falls_back_to_legacy_latest_when_manifest_missing(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_reader_detects_record_count_mismatch_and_uses_legacy_fallback(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_reader_uses_legacy_fallback_when_legacy_latest_is_newer_than_distributed(Path(tmp))
    test_validator_tool_contains_no_runtime_write_calls()
    print(json.dumps({"ok": True}))
