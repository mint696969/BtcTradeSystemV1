# path: ./tools/test_prediction_system_ps_q9b_latest_payload_read_only_loader_guard.py
# desc: Focused guard for PS-Q9B minimal guarded read-only latest payload loader.

from __future__ import annotations

import ast
from datetime import datetime, timezone
import os
from pathlib import Path
import tempfile

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_read_only_loader import (
    READ_ONLY_LOADER_VERSION,
    load_prediction_warroom_latest_payload_read_only,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_read_only_loader.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.prediction",
    "btcts.collector_vnext",
    "btcts.autotrade.execution",
    "btcts.autotrade.live_shadow",
    "btcts.processing.l4_consumer_models.shared",
    "streamlit",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
)
FORBIDDEN_TOKENS = (
    "open(",
    "write_text",
    "write_bytes",
    "json.dump",
    "json.dumps",
    "build_prediction_system_result",
    "assess_source_quality",
    "place_order(",
    "send_order(",
    "create_order(",
    "append_decision_jsonl",
    "append_command_ledger_record",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "st.button",
    "st.form",
    "persist=True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
    "authorization_grant_requested: bool = True",
    "autotrade_trigger_enabled: bool = True",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _assert_no_side_effect_flags(packet: dict) -> None:
    false_keys = (
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
        "authorization_grant_requested",
        "autotrade_trigger_enabled",
    )
    for key in false_keys:
        assert packet[key] is False, key
    for item in packet["artifact_results"]:
        for key in false_keys:
            assert item[key] is False, f"{item['artifact_role']}:{key}"


def _make_latest_prediction_file(root: Path, text: str) -> Path:
    path = root / "prediction" / "latest_prediction_system_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_ps_q9b_static_boundaries_and_markers() -> None:
    text = MODULE.read_text(encoding="utf-8")
    imports = _imports_from(MODULE)
    for prefix in FORBIDDEN_IMPORT_PREFIXES:
        assert not any(item == prefix or item.startswith(prefix + ".") for item in imports), prefix
    for token in FORBIDDEN_TOKENS:
        assert token not in text, token
    assert "prediction_warroom_latest_payload_read_only_loader.ps_q9b.v1" in text
    assert "load_prediction_warroom_latest_payload_read_only" in text
    assert "schema_validation_deferred_to_ps_q9c" in text
    assert "DEFAULT_ALLOWED_ARTIFACT_ROLES" in text


def test_ps_q9b_default_does_not_touch_files_without_explicit_allow() -> None:
    packet = load_prediction_warroom_latest_payload_read_only().to_dict()
    assert packet["loader_version"] == READ_ONLY_LOADER_VERSION
    assert packet["loader_state"] == "blocked_actual_read_not_requested"
    assert packet["allow_actual_read_requested"] is False
    assert packet["actual_file_read_attempted"] is False
    assert packet["payload_decode_attempted"] is False
    assert all(item["path_exists"] is False for item in packet["artifact_results"])
    assert packet["loaded_payload_count"] == 0
    assert "allow_actual_read_false" in packet["blocker_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9b_reads_and_decodes_only_allowed_required_json_when_explicitly_enabled() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q9b_loader_") as raw_root:
        root = Path(raw_root)
        _make_latest_prediction_file(root, '{"packet_version":"sample.v1","prediction_run_id":"run-1","value":42}')
        packet = load_prediction_warroom_latest_payload_read_only(
            hot_latest_root_hint=str(root),
            allow_actual_read=True,
            now=datetime.now(timezone.utc),
        ).to_dict()
    assert packet["loader_state"] == "loaded_read_only_payload_decode_succeeded_schema_validation_deferred"
    assert packet["allow_actual_read_requested"] is True
    assert packet["actual_file_read_attempted"] is True
    assert packet["actual_file_read_succeeded"] is True
    assert packet["payload_decode_attempted"] is True
    assert packet["payload_decode_succeeded"] is True
    assert packet["loaded_payload_count"] == 1
    assert "prediction_system_result_snapshot" in packet["loaded_payloads"]
    assert packet["loaded_payloads"]["prediction_system_result_snapshot"]["prediction_run_id"] == "run-1"
    result = packet["artifact_results"][0]
    assert result["artifact_role"] == "prediction_system_result_snapshot"
    assert result["loader_state"] == "loaded_read_only_payload_decode_succeeded"
    assert result["payload_type"] == "dict"
    assert "schema_validation_deferred_to_ps_q9c" in result["warning_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9b_missing_file_blocks_before_read() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q9b_missing_") as raw_root:
        packet = load_prediction_warroom_latest_payload_read_only(
            hot_latest_root_hint=str(Path(raw_root)),
            allow_actual_read=True,
            now=datetime.now(timezone.utc),
        ).to_dict()
    assert packet["loader_state"] == "blocked_before_actual_read"
    assert packet["actual_file_read_attempted"] is False
    assert packet["payload_decode_attempted"] is False
    assert packet["loaded_payload_count"] == 0
    assert "actual_read_candidate_file_missing" in packet["blocker_reasons"]
    _assert_no_side_effect_flags(packet)


def test_ps_q9b_bad_json_reports_decode_failure_without_runtime_write() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q9b_bad_json_") as raw_root:
        root = Path(raw_root)
        _make_latest_prediction_file(root, "{not-json")
        packet = load_prediction_warroom_latest_payload_read_only(
            hot_latest_root_hint=str(root),
            allow_actual_read=True,
            now=datetime.now(timezone.utc),
        ).to_dict()
    assert packet["loader_state"] == "blocked_after_read_or_decode_failure"
    assert packet["actual_file_read_attempted"] is True
    assert packet["actual_file_read_succeeded"] is True
    assert packet["payload_decode_attempted"] is True
    assert packet["payload_decode_succeeded"] is False
    assert packet["loaded_payload_count"] == 0
    result = packet["artifact_results"][0]
    assert "payload_decode_failed" in result["blocker_reasons"]
    assert result["exception_class"] is not None
    _assert_no_side_effect_flags(packet)


def test_ps_q9b_stale_file_blocks_before_read() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q9b_stale_") as raw_root:
        root = Path(raw_root)
        path = _make_latest_prediction_file(root, '{"prediction_run_id":"old"}')
        stale_epoch = 1_700_000_000
        os.utime(path, (stale_epoch, stale_epoch))
        packet = load_prediction_warroom_latest_payload_read_only(
            hot_latest_root_hint=str(root),
            allow_actual_read=True,
            now=datetime(2026, 6, 21, tzinfo=timezone.utc),
        ).to_dict()
    assert packet["loader_state"] == "blocked_before_actual_read"
    assert packet["actual_file_read_attempted"] is False
    assert packet["payload_decode_attempted"] is False
    assert any("freshness_status_stale_before_actual_read" in item for item in packet["blocker_reasons"])
    _assert_no_side_effect_flags(packet)


def main() -> int:
    test_ps_q9b_static_boundaries_and_markers()
    test_ps_q9b_default_does_not_touch_files_without_explicit_allow()
    test_ps_q9b_reads_and_decodes_only_allowed_required_json_when_explicitly_enabled()
    test_ps_q9b_missing_file_blocks_before_read()
    test_ps_q9b_bad_json_reports_decode_failure_without_runtime_write()
    test_ps_q9b_stale_file_blocks_before_read()
    print("[OK] Prediction System PS-Q9B latest payload read-only loader guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
