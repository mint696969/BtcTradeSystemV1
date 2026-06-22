# path: ./tools/check_phase4a_prediction_system_ps_q15a_source_readiness_root_cause.py
# desc: PS-Q15A read-only diagnostic for WarRoom latest prediction source readiness root cause. Metadata/adapter inspection only; no freshness bypass, force-ready, runtime write, ledger, broker, mode/order, AutoTrade, parameter apply, or staging behavior.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_payload_loader_permission_contract import (  # noqa: E402
    DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC,
)
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_adapter import (  # noqa: E402
    build_prediction_warroom_latest_prediction_source_adapter,
)
from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import (  # noqa: E402
    DEFAULT_HOT_LATEST_ROOT_HINT,
)

CHECKER = "ps_q15a_source_readiness_root_cause"
EXPECTED_RELATIVE_PATH = "prediction/latest_prediction_system_result.json"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_generated_at(payload: Mapping[str, Any]) -> str:
    value = payload.get("generated_at")
    if isinstance(value, str) and value:
        return value
    forecast = _as_mapping(payload.get("forecast_batch"))
    value = forecast.get("generated_at")
    return value if isinstance(value, str) else ""


def _read_top_level_json(path: Path) -> Mapping[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    return data if isinstance(data, Mapping) else {}


def _file_metadata(path: Path, *, now: datetime) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path),
            "path_exists": False,
            "file_size_bytes": None,
            "mtime_utc": "",
            "age_sec": None,
            "freshness_max_age_sec": DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC,
            "freshness_status": "missing",
            "generated_at": "",
        }
    stat = path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    age_sec = max(0, int((now - mtime).total_seconds()))
    payload = _read_top_level_json(path)
    return {
        "path": str(path),
        "path_exists": True,
        "file_size_bytes": int(stat.st_size),
        "mtime_utc": mtime.isoformat().replace("+00:00", "Z"),
        "age_sec": age_sec,
        "freshness_max_age_sec": DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC,
        "freshness_status": "fresh" if age_sec <= DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC else "stale",
        "generated_at": _parse_generated_at(payload),
        "top_level_key_count": len(payload),
        "top_level_preview_keys": list(payload.keys())[:16],
    }


def _adapter_snapshot(hot_root: str) -> dict[str, Any]:
    packet = build_prediction_warroom_latest_prediction_source_adapter(
        hot_latest_root_hint=hot_root,
        allow_actual_read=True,
        session_state={},
        store_in_session_state=True,
    ).to_dict()
    loader = _as_mapping(packet.get("loader_result"))
    composition = _as_mapping(packet.get("composition_harness"))
    handoff = _as_mapping(packet.get("session_state_handoff"))
    return {
        "adapter_state": packet.get("adapter_state"),
        "actual_file_read_attempted": packet.get("actual_file_read_attempted"),
        "actual_file_read_succeeded": packet.get("actual_file_read_succeeded"),
        "payload_decode_attempted": packet.get("payload_decode_attempted"),
        "payload_decode_succeeded": packet.get("payload_decode_succeeded"),
        "loaded_payload_count": packet.get("loaded_payload_count"),
        "review_packet_ready": packet.get("review_packet_ready"),
        "session_state_updated": packet.get("session_state_updated"),
        "blocker_count": packet.get("blocker_count"),
        "warning_count": packet.get("warning_count"),
        "blocked_reasons": _list(packet.get("blocked_reasons")),
        "warning_reasons": _list(packet.get("warning_reasons")),
        "loader_state": loader.get("loader_state"),
        "loader_blocker_reasons": _list(loader.get("blocker_reasons")),
        "loader_warning_reasons": _list(loader.get("warning_reasons")),
        "composition_state": composition.get("harness_state"),
        "composition_blocked_reasons": _list(composition.get("blocked_reasons")),
        "composition_warning_reasons": _list(composition.get("warning_reasons")),
        "handoff_state": handoff.get("harness_state"),
        "handoff_blocked_reasons": _list(handoff.get("blocked_reasons")),
        "handoff_warning_reasons": _list(handoff.get("warning_reasons")),
    }


def _classify_root_causes(file_meta: Mapping[str, Any], adapter: Mapping[str, Any]) -> list[dict[str, Any]]:
    causes: list[dict[str, Any]] = []
    if file_meta.get("path_exists") is False:
        causes.append(
            {
                "rank": 1,
                "category": "latest_prediction_file_missing",
                "evidence": "expected D-hot prediction/latest_prediction_system_result.json is missing",
                "impact": "Q9B cannot read/decode; downstream review packet and handoff remain blocked",
                "safe_next_check": "confirm prediction producer writes the latest prediction artifact to D-hot prediction/latest_prediction_system_result.json",
            }
        )
    elif file_meta.get("freshness_status") == "stale":
        causes.append(
            {
                "rank": 1,
                "category": "latest_prediction_artifact_stale",
                "evidence": f"age_sec={file_meta.get('age_sec')} exceeds freshness_max_age_sec={file_meta.get('freshness_max_age_sec')}",
                "impact": "PS-Q9A blocks before actual read; Q9B does not read/decode the payload",
                "safe_next_check": "inspect why prediction/latest_prediction_system_result.json is not being refreshed; do not bypass freshness",
            }
        )
    if adapter.get("loaded_payload_count") == 0:
        causes.append(
            {
                "rank": 2,
                "category": "q9b_no_loaded_payload",
                "evidence": f"actual_file_read_succeeded={adapter.get('actual_file_read_succeeded')}; payload_decode_succeeded={adapter.get('payload_decode_succeeded')}; loaded_payload_count={adapter.get('loaded_payload_count')}",
                "impact": "Q9O receives no effective prediction_result_payload mapping",
                "safe_next_check": "check Q9A/Q9B preflight blockers first; do not force a payload into review state",
            }
        )
    if "prediction_result_payload_mapping_missing" in _list(adapter.get("blocked_reasons")):
        causes.append(
            {
                "rank": 3,
                "category": "downstream_mapping_missing_after_loader_block",
                "evidence": "prediction_result_payload_mapping_missing is present after Q9B fail-closed loader result",
                "impact": "Q9C/Q9E/Q9F composition cannot build a ready review packet",
                "safe_next_check": "resolve upstream freshness/read/decode before changing mapping logic",
            }
        )
    if "q10k_session_state_handoff_not_updated" in _list(adapter.get("blocked_reasons")):
        causes.append(
            {
                "rank": 4,
                "category": "handoff_blocked_because_review_packet_not_ready",
                "evidence": f"review_packet_ready={adapter.get('review_packet_ready')}; session_state_updated={adapter.get('session_state_updated')}",
                "impact": "WarRoom source handoff remains blocked/fallback",
                "safe_next_check": "do not mutate session_state manually; make upstream review packet legitimately ready first",
            }
        )
    return causes


def build_report(*, hot_root: str = DEFAULT_HOT_LATEST_ROOT_HINT, now: datetime | None = None) -> dict[str, Any]:
    observed_now = now or _utc_now()
    hot_root_path = Path(hot_root)
    expected_path = hot_root_path / EXPECTED_RELATIVE_PATH
    file_meta = _file_metadata(expected_path, now=observed_now)
    adapter = _adapter_snapshot(str(hot_root_path))
    causes = _classify_root_causes(file_meta, adapter)
    return {
        "ok": True,
        "checker": CHECKER,
        "hot_root": str(hot_root_path),
        "observed_at_utc": observed_now.isoformat().replace("+00:00", "Z"),
        "expected_latest_prediction_path": str(expected_path),
        "file_metadata": file_meta,
        "adapter_snapshot": adapter,
        "root_cause_summary": causes,
        "primary_root_cause": causes[0]["category"] if causes else "no_blocking_root_cause_detected_by_ps_q15a",
        "safety": {
            "read_only_diagnostic": True,
            "freshness_bypass_added": False,
            "force_ready_added": False,
            "loader_behavior_changed": False,
            "readiness_behavior_changed": False,
            "runtime_artifact_write_allowed": False,
            "ledger_append_allowed": False,
            "broker_private_api_allowed": False,
            "mode_apply_requested": False,
            "order_placement_requested": False,
            "autotrade_trigger_allowed": False,
            "parameter_apply_allowed": False,
            "parameter_staging_write_allowed": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only root-cause diagnostic for WarRoom latest prediction source readiness.")
    parser.add_argument("--hot-root", default=DEFAULT_HOT_LATEST_ROOT_HINT, help="Hot data root. Defaults to D:\\btc_ts_hot.")
    args = parser.parse_args(argv)
    report = build_report(hot_root=args.hot_root)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def test_ps_q15a_source_readiness_root_cause_stale_classification() -> None:
    now = datetime(2026, 6, 22, 8, 13, 23, tzinfo=timezone.utc)
    file_meta = {
        "path_exists": True,
        "age_sec": 37_416,
        "freshness_max_age_sec": DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC,
        "freshness_status": "stale",
    }
    adapter = {
        "actual_file_read_succeeded": False,
        "payload_decode_succeeded": False,
        "loaded_payload_count": 0,
        "review_packet_ready": False,
        "session_state_updated": False,
        "blocked_reasons": [
            "freshness_status_stale_before_actual_read",
            "prediction_result_payload_mapping_missing",
            "q10k_session_state_handoff_not_updated",
        ],
    }
    causes = _classify_root_causes(file_meta, adapter)
    assert causes[0]["category"] == "latest_prediction_artifact_stale"
    assert any(item["category"] == "q9b_no_loaded_payload" for item in causes)
    assert any(item["category"] == "downstream_mapping_missing_after_loader_block" for item in causes)
    assert any(item["category"] == "handoff_blocked_because_review_packet_not_ready" for item in causes)
    assert now.isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
