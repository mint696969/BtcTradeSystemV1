# path: ./tools/check_phase4a_prediction_system_ps_q12h_warroom_uicheck_snapshot.py
# desc: PS-Q12H non-UI checker for GPT UI Check snapshots containing the WarRoom latest prediction source safe snapshot. Reads tmp/uicheck only; no runtime write, AutoTrade, broker, approval, or ledger behavior.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "prediction_system_ps_q12h_warroom_uicheck_snapshot_check.v1"
UICHK_GLOB = "tmp/uicheck/uicheck_*_warroom.json"
SNAPSHOT_KEY = "warroom_latest_prediction_source_review_panel_uicheck_snapshot"
EXPECTED_SNAPSHOT_VERSION = "prediction_warroom_latest_prediction_source_uicheck_snapshot.ps_q12h.v1"
EXPECTED_PANEL_STATE = "latest_prediction_source_review_panel_ready"
EXPECTED_ADAPTER_STATE = "latest_prediction_source_ready"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list_latest_uicheck_paths(*, glob_pattern: str = UICHK_GLOB) -> list[Path]:
    return sorted(REPO_ROOT.glob(glob_pattern), key=lambda path: path.stat().st_mtime, reverse=True)


def load_latest_warroom_uicheck_payload(*, glob_pattern: str = UICHK_GLOB) -> tuple[Path | None, Mapping[str, Any]]:
    paths = _list_latest_uicheck_paths(glob_pattern=glob_pattern)
    if not paths:
        return None, {}
    latest = paths[0]
    try:
        return latest, json.loads(latest.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - fail closed in checker output
        return latest, {"_load_error": repr(exc)}


def _snapshot_from_uicheck(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    session_state = _as_mapping(payload.get("session_state_safe"))
    selected = _as_mapping(session_state.get("selected_safe_values"))
    return _as_mapping(selected.get(SNAPSHOT_KEY))


def validate_warroom_inference_uicheck_snapshot_payload(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    page = _as_mapping(data.get("page"))
    snapshot = _snapshot_from_uicheck(data)
    safe_boundary = _as_mapping(snapshot.get("safe_boundary"))
    failures: list[str] = []
    warnings: list[str] = []
    if data.get("_load_error"):
        failures.append("uicheck_payload_load_error")
    if page.get("selected_page_key") and page.get("selected_page_key") != "warroom":
        failures.append("selected_page_key_not_warroom")
    if not snapshot:
        failures.append("warroom_latest_prediction_source_uicheck_snapshot_missing")
    if snapshot and snapshot.get("snapshot_version") != EXPECTED_SNAPSHOT_VERSION:
        failures.append("snapshot_version_mismatch")
    if snapshot and snapshot.get("panel_state") != EXPECTED_PANEL_STATE:
        failures.append("panel_state_not_ready")
    if snapshot and snapshot.get("adapter_state") != EXPECTED_ADAPTER_STATE:
        failures.append("adapter_state_not_ready")
    if snapshot and int(snapshot.get("loaded_payload_count") or 0) < 1:
        failures.append("loaded_payload_count_less_than_one")
    if snapshot and snapshot.get("actual_file_read_succeeded") is not True:
        failures.append("actual_file_read_not_succeeded")
    if snapshot and snapshot.get("payload_decode_succeeded") is not True:
        failures.append("payload_decode_not_succeeded")
    if snapshot and snapshot.get("review_packet_ready") is not True:
        failures.append("review_packet_not_ready")
    if snapshot and snapshot.get("session_state_updated") is not True:
        failures.append("session_state_not_updated")
    if snapshot and snapshot.get("q9g_session_state_seed_ready") is not True:
        failures.append("q9g_session_state_seed_not_ready")
    if snapshot and int(snapshot.get("blocker_count") or 0) != 0:
        failures.append("blocker_count_not_zero")
    if snapshot and int(snapshot.get("readability_row_count") or 0) < 6:
        failures.append("readability_rows_missing")
    if snapshot and int(snapshot.get("issue_row_count") or 0) < 1:
        warnings.append("issue_rows_not_present_or_empty")
    if snapshot and (not safe_boundary or not all(bool(value) for value in safe_boundary.values())):
        failures.append("safe_boundary_not_all_true")
    return {
        "ok": not failures,
        "schema_version": SCHEMA_VERSION,
        "snapshot_key": SNAPSHOT_KEY,
        "selected_page_key": page.get("selected_page_key"),
        "snapshot_present": bool(snapshot),
        "snapshot": dict(snapshot),
        "safe_boundary": dict(safe_boundary),
        "failures": failures,
        "warnings": warnings,
        "operator_note": "PS-Q12H checker reads GPT UI Check JSON only; no runtime write, approval, ledger, AutoTrade, broker/private API.",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q12H WarRoom inference UI Check snapshot validator")
    parser.add_argument("--path", default="", help="Specific uicheck JSON path; default is latest tmp/uicheck/uicheck_*_warroom.json")
    parser.add_argument("--allow-missing", action="store_true", help="Exit 0 when no uicheck file exists; useful before UI observation")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.path:
        path = Path(args.path)
        if not path.is_absolute():
            path = REPO_ROOT / path
        payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    else:
        path, payload = load_latest_warroom_uicheck_payload()
    if not payload:
        result = {
            "ok": bool(args.allow_missing),
            "schema_version": SCHEMA_VERSION,
            "uicheck_path": str(path) if path else None,
            "failures": [] if args.allow_missing else ["warroom_uicheck_file_missing"],
            "operator_note": "Enable GPT UI Auto Save, open WarRoom, then rerun this checker.",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["ok"] else 1
    result = validate_warroom_inference_uicheck_snapshot_payload(payload)
    result["uicheck_path"] = str(path) if path else None
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
