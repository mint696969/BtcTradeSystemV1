# path: ./tools/check_phase4a_prediction_system_ps_q13e_warroom_realtime_review_uicheck_snapshot.py
# desc: PS-Q13E checker for WarRoom realtime review UI Check JSON snapshots. Read-only file validation only; no runtime writes, parameter apply, ledger, AutoTrade, broker, or mode/order behavior.

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UICHECK_GLOB = "tmp/uicheck/uicheck_*_warroom.json"
EXPECTED_SNAPSHOT_VERSION = "prediction_warroom_realtime_review_uicheck_snapshot.ps_q13d.v1"
EXPECTED_SESSION_STATE_KEY = "warroom_realtime_review_preflight_panel_uicheck_snapshot"

REQUIRED_TOP_LEVEL_MARKERS = (
    "snapshot_version",
    "panel_version",
    "readability_version",
    "preflight_version",
    "panel_state",
    "preflight_state",
    "summary_card_count",
    "gpt_review_checklist_count",
    "parameter_adjustment_candidate_count",
    "surface_row_count",
    "boundary_row_count",
    "parameter_apply_allowed_any",
    "parameter_staging_write_allowed_any",
    "safe_boundary",
)

REQUIRED_SAFE_BOUNDARY_KEYS = (
    "read_only",
    "non_executing",
    "display_only",
    "review_only",
    "warroom_page_mutation_allowed_false",
    "runtime_artifact_write_allowed_false",
    "parameter_mutation_allowed_false",
    "parameter_version_append_allowed_false",
    "approval_or_authorization_allowed_false",
    "ledger_append_allowed_false",
    "autotrade_trigger_allowed_false",
    "broker_private_api_allowed_false",
    "would_write_runtime_artifact_false",
    "would_mutate_live_parameters_false",
    "would_append_parameter_version_false",
    "would_send_to_broker_false",
    "broker_execution_requested_false",
    "mode_apply_requested_false",
    "command_ledger_append_requested_false",
    "decision_ledger_append_requested_false",
    "approval_append_requested_false",
    "authorization_grant_requested_false",
    "autotrade_trigger_enabled_false",
    "parameter_apply_allowed_any_false",
    "parameter_staging_write_allowed_any_false",
)


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
    by_key = _as_mapping(root.get(EXPECTED_SESSION_STATE_KEY))
    if by_key.get("snapshot_version") == EXPECTED_SNAPSHOT_VERSION:
        return by_key
    session_state = _as_mapping(root.get("session_state"))
    by_session = _as_mapping(session_state.get(EXPECTED_SESSION_STATE_KEY))
    if by_session.get("snapshot_version") == EXPECTED_SNAPSHOT_VERSION:
        return by_session
    for candidate in _iter_dicts(payload):
        if candidate.get("snapshot_version") == EXPECTED_SNAPSHOT_VERSION:
            return candidate
    return None


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _candidate_paths(path: str | None) -> list[Path]:
    if path:
        return [Path(path)]
    return sorted(REPO_ROOT.glob(DEFAULT_UICHECK_GLOB), key=lambda item: item.stat().st_mtime if item.exists() else 0, reverse=True)


def validate_snapshot(snapshot: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    for marker in REQUIRED_TOP_LEVEL_MARKERS:
        if marker not in snapshot:
            failures.append(f"missing snapshot marker: {marker}")
    if snapshot.get("snapshot_version") != EXPECTED_SNAPSHOT_VERSION:
        failures.append(f"unexpected snapshot_version: {snapshot.get('snapshot_version')}")
    for key in ("summary_card_count", "gpt_review_checklist_count", "parameter_adjustment_candidate_count", "surface_row_count", "boundary_row_count"):
        try:
            value = int(snapshot.get(key) or 0)
        except (TypeError, ValueError):
            value = 0
        if value <= 0:
            failures.append(f"non_positive count: {key}={snapshot.get(key)}")
    if snapshot.get("parameter_apply_allowed_any") is not False:
        failures.append("parameter_apply_allowed_any must be false")
    if snapshot.get("parameter_staging_write_allowed_any") is not False:
        failures.append("parameter_staging_write_allowed_any must be false")
    safe = _as_mapping(snapshot.get("safe_boundary"))
    for key in REQUIRED_SAFE_BOUNDARY_KEYS:
        if safe.get(key) is not True:
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
    return {
        "ok": not failures,
        "path": str(path),
        "checker": "ps_q13e_warroom_realtime_review_uicheck_snapshot",
        "snapshot_version": snapshot.get("snapshot_version"),
        "panel_state": snapshot.get("panel_state"),
        "preflight_state": snapshot.get("preflight_state"),
        "prediction_run_id": snapshot.get("prediction_run_id"),
        "summary_card_count": snapshot.get("summary_card_count"),
        "gpt_review_checklist_count": snapshot.get("gpt_review_checklist_count"),
        "parameter_adjustment_candidate_count": snapshot.get("parameter_adjustment_candidate_count"),
        "parameter_apply_allowed_any": snapshot.get("parameter_apply_allowed_any"),
        "parameter_staging_write_allowed_any": snapshot.get("parameter_staging_write_allowed_any"),
        "failures": failures,
    }


def check_latest_or_path(path: str | None = None) -> dict[str, Any]:
    paths = _candidate_paths(path)
    if not paths:
        return {
            "ok": False,
            "checker": "ps_q13e_warroom_realtime_review_uicheck_snapshot",
            "path": None,
            "failures": [f"no UI Check JSON matched {DEFAULT_UICHECK_GLOB}"],
        }
    return validate_file(paths[0])


def _sample_snapshot_payload() -> dict[str, Any]:
    safe_boundary = {key: True for key in REQUIRED_SAFE_BOUNDARY_KEYS}
    snapshot = {
        "snapshot_version": EXPECTED_SNAPSHOT_VERSION,
        "panel_version": "prediction_warroom_realtime_review_preflight_panel.ps_q13b.v1",
        "readability_version": "prediction_warroom_realtime_review_readability.ps_q13c.v1",
        "preflight_version": "prediction_warroom_realtime_review_preflight.ps_q13a.v1",
        "panel_state": "realtime_review_preflight_panel_ready",
        "preflight_state": "ready_for_future_warroom_ui_slice",
        "prediction_run_id": "prediction_system.ps_q13e:BTC_JPY:bitFlyer:sample",
        "generated_at": "2026-06-22T14:00:00Z",
        "market_uid": "BTC_JPY:bitFlyer",
        "signal_strength_percent": 57,
        "signal_strength_band": "medium",
        "latest_prediction_source_panel_present": True,
        "latest_prediction_review_ready": True,
        "latest_prediction_blocker_count": 0,
        "latest_prediction_warning_count": 1,
        "scenario_trace_present": True,
        "gpt_review_digest_present": True,
        "ready_for_future_warroom_ui_slice": True,
        "summary_card_count": 4,
        "gpt_review_checklist_count": 3,
        "parameter_adjustment_candidate_count": 3,
        "surface_row_count": 7,
        "boundary_row_count": 12,
        "parameter_apply_allowed_any": False,
        "parameter_staging_write_allowed_any": False,
        "safe_boundary": safe_boundary,
    }
    return {"session_state": {EXPECTED_SESSION_STATE_KEY: snapshot}}


def _write_sample(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_sample_snapshot_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check PS-Q13E WarRoom realtime review UI Check snapshot JSON.")
    parser.add_argument("--path", default=None, help="UI Check JSON path. Defaults to latest tmp/uicheck/uicheck_*_warroom.json.")
    parser.add_argument("--write-sample", default=None, help="Write a sample valid UI Check JSON to this path, then validate it.")
    args = parser.parse_args(argv)

    target_path = args.path
    if args.write_sample:
        sample_path = Path(args.write_sample)
        _write_sample(sample_path)
        target_path = str(sample_path)

    result = check_latest_or_path(target_path)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


def test_ps_q13e_warroom_realtime_review_uicheck_snapshot_checker_sample() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "uicheck_sample_warroom.json"
        _write_sample(path)
        result = validate_file(path)
        assert result["ok"] is True
        assert result["snapshot_version"] == EXPECTED_SNAPSHOT_VERSION
        assert result["summary_card_count"] == 4
        assert result["gpt_review_checklist_count"] == 3
        assert result["parameter_adjustment_candidate_count"] == 3
        assert result["parameter_apply_allowed_any"] is False
        assert result["parameter_staging_write_allowed_any"] is False


if __name__ == "__main__":
    raise SystemExit(main())
