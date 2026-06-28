# path: ./tools/test_phase4a_prediction_system_ps_q23a_read_only_artifact_layout_builder.py
# desc: Focused guard for PS-Q23A read-only distributed artifact layout builder.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q23a_read_only_artifact_layout_builder import (  # noqa: E402
    DIAGNOSTIC_VERSION,
    LATEST_RELATIVE_PATH,
    STATUS_RELATIVE_PATH,
    build_candidate_layout,
    run_layout_diagnostic,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23A_READ_ONLY_LAYOUT_BUILDER_2026-06-28.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q23a_read_only_artifact_layout_builder.py"


def _payload() -> dict:
    return {
        "generated_at": "2026-06-28T06:15:25Z",
        "prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-28T06:15:25Z",
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "forecast_batch": {
            "generated_at": "2026-06-28T06:15:25Z",
            "family_count": 2,
            "horizon_count": 2,
            "record_count": 2,
            "records": [
                {"family": "market_regime", "horizon_key": "15s", "score": 0.5, "warnings": []},
                {"family": "breakout", "horizon_key": "60s", "score": 0.7, "warnings": ["sample_warning"]},
            ],
        },
    }


def _meta(size: int = 5_250_000) -> dict:
    return {"exists": True, "size_bytes": size, "mtime_utc": "2026-06-28T06:15:25Z", "sha256_prefix": "abcdef0123456789"}


def test_spec_declares_read_only_builder_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23a_read_only_layout_builder=true",
        "reads_legacy_latest=true",
        "builds_candidate_manifest=true",
        "builds_candidate_sidecar_plan=true",
        "writes_d_hot_runtime_artifacts=false",
        "backward_compat_latest_retained=true",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_candidate_layout_uses_manifest_and_run_sidecars_without_embedding_records() -> None:
    layout = build_candidate_layout(hot_root=Path("D:/btc_ts_hot"), payload=_payload(), latest_meta=_meta())
    assert layout["candidate_feasible"] is True
    manifest = layout["latest_manifest_candidate"]
    assert manifest["layout_version"] == DIAGNOSTIC_VERSION
    assert manifest["legacy_latest_path"] == "prediction/latest_prediction_system_result.json"
    assert manifest["record_count"] == 2
    assert "prediction/runs/2026-06-28/061525_" in manifest["run_dir"]
    assert layout["candidate_sidecars"]["forecast_records"].endswith("forecast_records.jsonl")
    assert layout["summary_candidate_not_written"]["records_embedded"] is False
    assert layout["candidate_sizes"]["forecast_records_jsonl_estimated_bytes"] > 0


def test_layout_warns_when_legacy_latest_exceeds_long_term_target() -> None:
    layout = build_candidate_layout(hot_root=Path("D:/btc_ts_hot"), payload=_payload(), latest_meta=_meta(size=5_250_000))
    assert "legacy_latest_exceeds_long_term_target_bytes" in layout["candidate_warnings"]


def test_run_diagnostic_reads_legacy_latest_but_writes_nothing(tmp_path: Path) -> None:
    latest = tmp_path / LATEST_RELATIVE_PATH
    status = tmp_path / STATUS_RELATIVE_PATH
    latest.parent.mkdir(parents=True, exist_ok=True)
    status.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps(_payload()), encoding="utf-8")
    status.write_text(json.dumps({"ok": True}), encoding="utf-8")
    before_latest_mtime = latest.stat().st_mtime_ns
    result = run_layout_diagnostic(hot_root=tmp_path)
    after_latest_mtime = latest.stat().st_mtime_ns
    assert before_latest_mtime == after_latest_mtime
    assert result["layout_ready_for_future_dual_write"] is True
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert result["would_send_to_broker"] is False
    assert not (tmp_path / "prediction/latest_manifest.json").exists()
    assert not (tmp_path / "prediction/runs").exists()


def test_tool_contains_no_runtime_write_calls_for_d_hot_sidecars() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden_write_apis = (
        ".write_text(",
        ".write_bytes(",
        ".open(\"w",
        ".open('w",
        ".mkdir(",
        ".unlink(",
        "shutil.move",
        "shutil.copy",
        "os.replace",
        "Path.replace",
    )
    for api in forbidden_write_apis:
        assert api not in text, api
    assert "latest_manifest_written" in text


if __name__ == "__main__":
    test_spec_declares_read_only_builder_contract()
    test_candidate_layout_uses_manifest_and_run_sidecars_without_embedding_records()
    test_layout_warns_when_legacy_latest_exceeds_long_term_target()
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        test_run_diagnostic_reads_legacy_latest_but_writes_nothing(Path(tmp))
    test_tool_contains_no_runtime_write_calls_for_d_hot_sidecars()
    print(json.dumps({"ok": True}))
