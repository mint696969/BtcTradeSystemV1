# path: ./btcts_next/src/btcts/apps/sr_fx_final_readiness_checkpoint_once.py
# desc: Final SR-FX data/UI readiness checkpoint for human review. Read-only; no broker calls/no mode changes.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from btcts.collector_vnext.config import load_config

STAGE = "sr_fx_final_readiness_checkpoint_once"
CHECKPOINT_VERSION = "sr_fx_final_readiness_checkpoint.v1"
EXPECTED_PRODUCT_CODE = "FX_BTC_JPY"
EXPECTED_MARKET_UID = "bitflyer.fx.FX_BTC_JPY"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _state_root() -> Path:
    return load_config().roots()["state"]


def _audit_path() -> Path:
    return _state_root() / "operator_ui" / "sr_fx_data_lineage_parity_audit.json"


def _checkpoint_path() -> Path:
    return _state_root() / "operator_ui" / "sr_fx_final_readiness_checkpoint.json"


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return data


def _write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return path


def _stage_map(audit: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = audit.get("stages") or []
    out: dict[str, Mapping[str, Any]] = {}
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, Mapping) and row.get("stage_id"):
                out[str(row.get("stage_id"))] = row
    return out


def build_sr_fx_final_readiness_checkpoint_payload(
    *,
    audit_payload: Mapping[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    audit_path = _audit_path()
    checkpoint_path = _checkpoint_path()
    audit = dict(audit_payload or _read_json(audit_path))
    summary = dict(audit.get("summary") or {})
    context = dict(audit.get("context") or {})
    stages = _stage_map(audit)

    checks = {
        "audit_ok": bool(audit.get("ok")),
        "parity_complete": bool(audit.get("parity_complete")),
        "no_audit_blockers": not bool(audit.get("blocked_by")),
        "execution_product_code_ok": str(context.get("product_code") or context.get("symbol_raw") or "") == EXPECTED_PRODUCT_CODE,
        "execution_market_uid_ok": str(context.get("market_uid") or "") == EXPECTED_MARKET_UID,
        "primary_lineage_continuous_ws": str(summary.get("primary_lineage") or "") == "continuous_ws",
        "continuous_ws_l3_lineage_present": bool(summary.get("continuous_ws_l3_lineage_present")),
        "service_not_stale": not bool(summary.get("service_stale")),
        "l4_not_blocked": not bool(summary.get("l4_service_input_blocked")),
        "orderbook_context_available": bool(summary.get("orderbook_context_available")),
        "semantic_context_available": bool(summary.get("semantic_context_available")),
        "trusted_structural_market_state": bool(summary.get("trusted_structural_market_state")),
        "audit_read_only": bool(audit.get("read_only")),
        "audit_would_not_send_to_broker": not bool(audit.get("would_send_to_broker")),
        "decision_is_final_review_eligible": str(audit.get("decision") or "") == "eligible_for_final_human_review_before_autotrade_resume",
        "ws_board_stage_ok": str((stages.get("l1_public_ws_board") or {}).get("status") or "") == "ok",
        "ws_executions_stage_ok": str((stages.get("l1_public_ws_executions") or {}).get("status") or "") == "ok",
        "l3_stage_ok": str((stages.get("l3_market_state_overview") or {}).get("status") or "") == "ok",
        "l4_stage_ok": str((stages.get("l4_execution_market_service_input") or {}).get("status") or "") == "ok",
    }
    blocked_by = [name for name, ok in checks.items() if not ok]

    return {
        "stage": STAGE,
        "checkpoint_version": CHECKPOINT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "ok": not blocked_by,
        "data_ui_integrity_ready_for_final_human_review": not blocked_by,
        "autotrade_resume_authorized": False,
        "final_human_review_required": True,
        "mode_changed": False,
        "read_only": True,
        "would_send_to_broker": False,
        "decision": (
            "ready_for_final_human_review_only"
            if not blocked_by
            else "hold_final_review_until_checkpoint_blockers_clear"
        ),
        "blocked_by": blocked_by,
        "warnings": [
            "checkpoint_does_not_authorize_autotrade_resume",
            "private_rest_and_live_execution_safety_gates_remain_separate",
            "human_final_review_required_before_any_mode_change",
        ],
        "checks": checks,
        "context": context,
        "summary": summary,
        "audit_decision": audit.get("decision"),
        "audit_blocked_by": audit.get("blocked_by") or [],
        "stage_status": {
            stage_id: row.get("status")
            for stage_id, row in stages.items()
        },
        "paths": {
            "audit_path": str(audit_path),
            "checkpoint_path": str(checkpoint_path),
        },
    }


def write_sr_fx_final_readiness_checkpoint(payload: Mapping[str, Any]) -> Path:
    return _write_json(_checkpoint_path(), payload)


def main() -> int:
    try:
        payload = build_sr_fx_final_readiness_checkpoint_payload()
        write_sr_fx_final_readiness_checkpoint(payload)
    except Exception as exc:
        try:
            path = _checkpoint_path()
        except Exception:
            path = Path("sr_fx_final_readiness_checkpoint.json")
        payload = {
            "stage": STAGE,
            "checkpoint_version": CHECKPOINT_VERSION,
            "generated_at": _utc_now_iso(),
            "ok": False,
            "data_ui_integrity_ready_for_final_human_review": False,
            "autotrade_resume_authorized": False,
            "final_human_review_required": True,
            "mode_changed": False,
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["sr_fx_final_readiness_checkpoint_failed"],
            "paths": {"checkpoint_path": str(path)},
            "read_only": True,
            "would_send_to_broker": False,
        }
        try:
            _write_json(path, payload)
        except Exception:
            pass
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
