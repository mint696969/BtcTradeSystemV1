# path: ./tools/check_phase4a_prediction_system_ps_q14b_source_readiness_uicheck_snapshot.py
# desc: PS-Q14B checker for WarRoom latest prediction source-readiness explanation UI Check JSON snapshots. Read-only validation only; no runtime write, freshness bypass, force-ready, ledger, AutoTrade, broker, mode/order, parameter apply, or staging write behavior.

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UICHECK_GLOB = "tmp/uicheck/uicheck_*_warroom.json"
EXPECTED_SESSION_STATE_KEY = "warroom_latest_prediction_source_review_panel_uicheck_snapshot"
EXPECTED_SNAPSHOT_VERSION = "prediction_warroom_latest_prediction_source_uicheck_snapshot.ps_q12h.v1"
EXPECTED_READINESS_EXPLANATION_VERSION = "prediction_warroom_latest_prediction_source_readiness_explanation.ps_q14a.v1"

REQUIRED_TOP_LEVEL_MARKERS = (
    "snapshot_version",
    "panel_version",
    "readability_polish_version",
    "readiness_explanation_version",
    "readiness_explanation_row_count",
    "panel_state",
    "adapter_state",
    "loaded_payload_count",
    "actual_file_read_succeeded",
    "payload_decode_succeeded",
    "review_packet_ready",
    "session_state_updated",
    "q9g_session_state_seed_ready",
    "blocker_count",
    "warning_count",
    "readability_row_count",
    "issue_row_count",
    "safe_boundary",
)

REQUIRED_SAFE_BOUNDARY_KEYS = (
    "read_only",
    "non_executing",
    "display_only",
    "warroom_page_mutation_allowed_false",
    "warroom_panel_mutation_allowed_false",
    "runtime_artifact_write_allowed_false",
    "approval_or_authorization_allowed_false",
    "ledger_append_allowed_false",
    "autotrade_trigger_allowed_false",
    "broker_private_api_allowed_false",
    "would_write_runtime_artifact_false",
    "would_send_to_broker_false",
)

REDACTED_SAFE_BOUNDARY_KEYS = frozenset({"approval_or_authorization_allowed_false", "broker_private_api_allowed_false"})
REDACTED_VALUE = "<redacted>"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _iter_dicts(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_dicts(child)


def _find_snapshot(payload: Any) -> Mapping[str, Any] | None:
    root = _as_mapping(payload)
    direct = _as_mapping(root.get(EXPECTED_SESSION_STATE_KEY))
    if direct.get("snapshot_version") == EXPECTED_SNAPSHOT_VERSION:
        return direct
    session_state = _as_mapping(root.get("session_state"))
    nested = _as_mapping(session_state.get(EXPECTED_SESSION_STATE_KEY))
    if nested.get("snapshot_version") == EXPECTED_SNAPSHOT_VERSION:
        return nested
    for candidate in _iter_dicts(payload):
        if candidate.get("snapshot_version") == EXPECTED_SNAPSHOT_VERSION and "readiness_explanation_row_count" in candidate:
            return candidate
    return None


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _candidate_paths(path: str | None) -> list[Path]:
    if path:
        return [Path(path)]
    return sorted(REPO_ROOT.glob(DEFAULT_UICHECK_GLOB), key=lambda item: item.stat().st_mtime if item.exists() else 0, reverse=True)


def _positive_int(snapshot: Mapping[str, Any], key: str, failures: list[str]) -> int:
    try:
        value = int(snapshot.get(key) or 0)
    except (TypeError, ValueError):
        value = 0
    if value <= 0:
        failures.append(f"non_positive count: {key}={snapshot.get(key)}")
    return value


def validate_snapshot(snapshot: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    for marker in REQUIRED_TOP_LEVEL_MARKERS:
        if marker not in snapshot:
            failures.append(f"missing snapshot marker: {marker}")
    if snapshot.get("snapshot_version") != EXPECTED_SNAPSHOT_VERSION:
        failures.append(f"unexpected snapshot_version: {snapshot.get('snapshot_version')}")
    if snapshot.get("readiness_explanation_version") != EXPECTED_READINESS_EXPLANATION_VERSION:
        failures.append(f"unexpected readiness_explanation_version: {snapshot.get('readiness_explanation_version')}")
    _positive_int(snapshot, "readability_row_count", failures)
    _positive_int(snapshot, "issue_row_count", failures)
    _positive_int(snapshot, "readiness_explanation_row_count", failures)
    safe = _as_mapping(snapshot.get("safe_boundary"))
    for key in REQUIRED_SAFE_BOUNDARY_KEYS:
        value = safe.get(key)
        if value is True:
            continue
        if key in REDACTED_SAFE_BOUNDARY_KEYS and value == REDACTED_VALUE:
            continue
        failures.append(f"safe boundary not true: {key}")
    return failures


def validate_file(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    snapshot = _find_snapshot(payload)
    failures: list[str] = []
    if snapshot is None:
        failures.append(f"missing {EXPECTED_SESSION_STATE_KEY} snapshot with version {EXPECTED_SNAPSHOT_VERSION}")
        snapshot = {}
    else:
        failures.extend(validate_snapshot(snapshot))
    safe = _as_mapping(snapshot.get("safe_boundary"))
    redacted_safe_boundary_keys = sorted(key for key in REDACTED_SAFE_BOUNDARY_KEYS if safe.get(key) == REDACTED_VALUE)
    return {
        "ok": not failures,
        "checker": "ps_q14b_source_readiness_uicheck_snapshot",
        "path": str(path),
        "snapshot_version": snapshot.get("snapshot_version"),
        "readiness_explanation_version": snapshot.get("readiness_explanation_version"),
        "panel_state": snapshot.get("panel_state"),
        "adapter_state": snapshot.get("adapter_state"),
        "blocker_count": snapshot.get("blocker_count"),
        "warning_count": snapshot.get("warning_count"),
        "readability_row_count": snapshot.get("readability_row_count"),
        "issue_row_count": snapshot.get("issue_row_count"),
        "readiness_explanation_row_count": snapshot.get("readiness_explanation_row_count"),
        "actual_file_read_succeeded": snapshot.get("actual_file_read_succeeded"),
        "payload_decode_succeeded": snapshot.get("payload_decode_succeeded"),
        "review_packet_ready": snapshot.get("review_packet_ready"),
        "session_state_updated": snapshot.get("session_state_updated"),
        "q9g_session_state_seed_ready": snapshot.get("q9g_session_state_seed_ready"),
        "redacted_safe_boundary_keys": redacted_safe_boundary_keys,
        "redaction_tolerance": {"enabled": True, "allowed_keys": sorted(REDACTED_SAFE_BOUNDARY_KEYS)},
        "failures": failures,
    }


def check_latest_or_path(path: str | None = None) -> dict[str, Any]:
    paths = _candidate_paths(path)
    if not paths:
        return {
            "ok": False,
            "checker": "ps_q14b_source_readiness_uicheck_snapshot",
            "path": None,
            "failures": [f"no UI Check JSON matched {DEFAULT_UICHECK_GLOB}"],
        }
    return validate_file(paths[0])


def _sample_snapshot_payload(*, redacted: bool = False) -> dict[str, Any]:
    safe_boundary = {key: True for key in REQUIRED_SAFE_BOUNDARY_KEYS}
    if redacted:
        for key in REDACTED_SAFE_BOUNDARY_KEYS:
            safe_boundary[key] = REDACTED_VALUE
    snapshot = {
        "snapshot_version": EXPECTED_SNAPSHOT_VERSION,
        "panel_version": "prediction_warroom_latest_prediction_source_review_panel.ps_q12b.v1",
        "readability_polish_version": "prediction_warroom_latest_prediction_source_readability_polish.ps_q12g.v1",
        "readiness_explanation_version": EXPECTED_READINESS_EXPLANATION_VERSION,
        "panel_state": "latest_prediction_source_review_panel_blocked",
        "adapter_state": "latest_prediction_source_blocked",
        "prediction_run_id": "",
        "generated_at": "",
        "market_uid": "",
        "signal_strength_percent": None,
        "signal_strength_band": "unknown",
        "loaded_payload_count": 0,
        "actual_file_read_succeeded": False,
        "payload_decode_succeeded": False,
        "review_packet_ready": False,
        "session_state_updated": False,
        "q9g_session_state_seed_ready": False,
        "blocker_count": 10,
        "warning_count": 3,
        "readability_row_count": 6,
        "issue_row_count": 13,
        "readiness_explanation_row_count": 13,
        "safe_boundary": safe_boundary,
    }
    return {"session_state": {EXPECTED_SESSION_STATE_KEY: snapshot}}


def _write_sample(path: Path, *, redacted: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_sample_snapshot_payload(redacted=redacted), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check PS-Q14B source-readiness explanation UI Check snapshot JSON.")
    parser.add_argument("--path", default=None, help="UI Check JSON path. Defaults to latest tmp/uicheck/uicheck_*_warroom.json.")
    parser.add_argument("--write-sample", default=None, help="Write a sample valid UI Check JSON to this path, then validate it.")
    parser.add_argument("--redacted-sample", action="store_true", help="When writing sample, redact known safe-boundary keys.")
    args = parser.parse_args(argv)
    target_path = args.path
    if args.write_sample:
        sample_path = Path(args.write_sample)
        _write_sample(sample_path, redacted=bool(args.redacted_sample))
        target_path = str(sample_path)
    result = check_latest_or_path(target_path)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


def test_ps_q14b_source_readiness_uicheck_snapshot_checker_sample() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "uicheck_ps_q14b_sample_warroom.json"
        _write_sample(path)
        result = validate_file(path)
        assert result["ok"] is True
        assert result["readiness_explanation_version"] == EXPECTED_READINESS_EXPLANATION_VERSION
        assert result["readiness_explanation_row_count"] == 13
        assert result["blocker_count"] == 10
        assert result["warning_count"] == 3


def test_ps_q14b_source_readiness_uicheck_snapshot_checker_redacted_sample() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "uicheck_ps_q14b_redacted_sample_warroom.json"
        _write_sample(path, redacted=True)
        result = validate_file(path)
        assert result["ok"] is True
        assert set(result["redacted_safe_boundary_keys"]) == REDACTED_SAFE_BOUNDARY_KEYS
        assert result["readiness_explanation_row_count"] == 13


if __name__ == "__main__":
    raise SystemExit(main())
