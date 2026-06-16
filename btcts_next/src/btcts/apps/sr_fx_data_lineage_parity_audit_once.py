# path: ./btcts_next/src/btcts/apps/sr_fx_data_lineage_parity_audit_once.py
# desc: Read-only SR-FX L1-L4 data lineage parity audit before AutoTrade resume. No broker calls.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from btcts.collector_vnext.config import load_config
from btcts.apps.operator_ui.components.market_state_bridge import (
    execution_market_context,
    load_execution_market_overview,
    load_execution_market_summary_bundle,
    load_execution_market_summary_status_payload,
)
from btcts.processing.l4_consumer_models.shared import build_execution_market_service_input

AUDIT_VERSION = "sr_fx_data_lineage_parity_audit.v1"
STAGE = "sr_fx_data_lineage_parity_audit_once"


def _as_bool(value: Any) -> bool:
    return bool(value)


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    return [str(value)]


def _identity_ok(ctx: Mapping[str, Any], overview: Mapping[str, Any], summary: Mapping[str, Any]) -> bool:
    return (
        str(ctx.get("product_code") or ctx.get("symbol_raw") or "") == "FX_BTC_JPY"
        and str(ctx.get("market_uid") or "") == "bitflyer.fx.FX_BTC_JPY"
        and str(overview.get("symbol_raw") or summary.get("symbol_raw") or "") == "FX_BTC_JPY"
        and str(overview.get("market_uid") or summary.get("market_uid") or "") == "bitflyer.fx.FX_BTC_JPY"
    )


def _status(ok: bool, *, partial: bool = False) -> str:
    if ok and not partial:
        return "ok"
    if ok and partial:
        return "partial"
    return "missing_or_blocked"


def _stage_row(
    *,
    stage_id: str,
    layer: str,
    name: str,
    status: str,
    evidence: Mapping[str, Any] | None = None,
    blockers: list[str] | tuple[str, ...] | None = None,
    warnings: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "layer": layer,
        "name": name,
        "status": status,
        "evidence": dict(evidence or {}),
        "blockers": list(blockers or []),
        "warnings": list(warnings or []),
    }


def build_sr_fx_data_lineage_parity_audit_payload(
    *,
    context: Mapping[str, Any] | None = None,
    overview: Mapping[str, Any] | None = None,
    summary_payload: Mapping[str, Any] | None = None,
    service_input_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a read-only parity audit for SR-FX data lineage.

    This deliberately distinguishes usable REST-baseline lineage from spot-equivalent
    continuous WS lineage.  It is an audit/report contract, not an order contract.
    """

    ctx = dict(context or execution_market_context())
    ov = dict(overview or load_execution_market_overview() or {})
    summary = dict(summary_payload or load_execution_market_summary_status_payload() or {})
    if service_input_payload is None:
        service_input = build_execution_market_service_input(
            load_execution_market_summary_bundle(),
            diagnostics={"entrypoint": STAGE},
        ).to_dict()
    else:
        service_input = dict(service_input_payload or {})

    blocked: list[str] = []
    warnings: list[str] = []

    identity_ok = _identity_ok(ctx, ov, summary)
    if not identity_ok:
        blocked.append("sr_fx_execution_market_identity_not_consistent")

    market_state_present = bool(ov)
    if not market_state_present:
        blocked.append("sr_fx_market_state_missing")

    continuity_state = str(ov.get("continuity_state") or summary.get("continuity_state") or service_input.get("continuity_state") or "")
    trust_state = str(ov.get("trust_state") or summary.get("trust_state") or service_input.get("trust_state") or "")
    interpretation_bucket = str(
        ov.get("interpretation_bucket")
        or summary.get("interpretation_bucket")
        or service_input.get("interpretation_bucket")
        or ""
    )
    service_warnings = _as_list(service_input.get("warnings"))
    service_blockers = _as_list(service_input.get("blocked_by"))
    service_stale = bool(service_input.get("is_stale")) or "market_summary_stale" in service_blockers
    if service_blockers:
        blocked.append("sr_fx_l4_service_input_blocked")
    if "execution_market_rest_baseline_not_continuous_ws_series" in service_warnings:
        blocked.append("sr_fx_continuous_ws_l3_lineage_missing")
    if "orderbook_context_missing" in service_warnings:
        blocked.append("sr_fx_orderbook_context_missing")
    if "semantic_context_missing" in service_warnings:
        warnings.append("sr_fx_semantic_context_missing")

    trade_delta_present = ov.get("trade_delta") is not None or summary.get("trade_delta") is not None
    rest_baseline = continuity_state == "rest_baseline_snapshot"
    continuous_ws = (
        continuity_state == "continuous"
        and "execution_market_rest_baseline_not_continuous_ws_series" not in service_warnings
        and not service_stale
    )
    orderbook_context_available = str(service_input.get("orderbook_wiring_status") or summary.get("orderbook_wiring_status") or "") in {
        "partial",
        "wired",
    }
    semantic_context_available = str(service_input.get("semantic_runtime_wiring_status") or summary.get("semantic_runtime_wiring_status") or "") in {
        "partial",
        "wired",
    }
    trusted_structural = trust_state == "trusted" and interpretation_bucket == "allow_structural_use"
    continuous_state_observed = continuity_state == "continuous"
    primary_lineage = (
        "continuous_ws"
        if continuous_ws
        else "continuous_ws_stale"
        if continuous_state_observed and service_stale
        else "rest_baseline"
        if rest_baseline
        else "unknown"
    )
    rest_board_status = (
        "partial"
        if identity_ok and market_state_present and rest_baseline
        else "not_current_primary"
        if continuous_state_observed
        else "missing_or_blocked"
    )
    rest_board_warnings = (
        ["rest_baseline_snapshot_not_continuous_ws_series"]
        if rest_baseline
        else ["rest_board_not_current_primary_lineage"]
        if continuous_state_observed
        else []
    )

    stages = [
        _stage_row(
            stage_id="l1_public_rest_board",
            layer="L1 raw acquisition",
            name="FX public REST board baseline / fallback",
            status=rest_board_status,
            evidence={
                "product_code": ctx.get("product_code") or ctx.get("symbol_raw"),
                "market_uid": ctx.get("market_uid"),
                "continuity_state": continuity_state,
                "primary_lineage": primary_lineage,
                "source_series_id": ov.get("source_series_id") or summary.get("source_series_id"),
            },
            warnings=rest_board_warnings,
        ),
        _stage_row(
            stage_id="l1_public_rest_executions",
            layer="L1 raw acquisition",
            name="FX public REST executions/backfill or trade delta",
            status=_status(identity_ok and trade_delta_present, partial=True),
            evidence={
                "trade_delta": ov.get("trade_delta"),
                "source_series_id": ov.get("source_series_id"),
                "primary_lineage": primary_lineage,
            },
            warnings=["rest_executions_backfill_or_reconcile_not_realtime_primary"] if not continuous_ws else ["rest_executions_not_current_primary_lineage"],
        ),
        _stage_row(
            stage_id="l1_public_ws_board",
            layer="L1 raw acquisition",
            name="FX public WS board stream",
            status="ok" if continuous_ws else "partial",
            evidence={
                "expected_role": "continuous_ws_series",
                "current_continuity_state": continuity_state,
                "service_stale": service_stale,
            },
            blockers=[] if continuous_ws else [
                "continuous_ws_board_stale" if service_stale else "continuous_ws_board_not_bound_to_l3_market_state"
            ],
        ),
        _stage_row(
            stage_id="l1_public_ws_executions",
            layer="L1 raw acquisition",
            name="FX public WS executions stream",
            status="ok" if continuous_ws else "partial",
            evidence={
                "expected_role": "realtime_primary_trade_stream",
                "current_continuity_state": continuity_state,
                "service_stale": service_stale,
            },
            blockers=[] if continuous_ws else [
                "continuous_ws_executions_stale" if service_stale else "continuous_ws_executions_not_bound_to_l3_market_state"
            ],
        ),
        _stage_row(
            stage_id="l2_canonical_identity",
            layer="L2 normalized/canonical",
            name="FX canonical identity separation",
            status=_status(identity_ok),
            evidence={
                "symbol_raw": ov.get("symbol_raw") or summary.get("symbol_raw"),
                "market_uid": ov.get("market_uid") or summary.get("market_uid"),
                "service_input_role": summary.get("service_input_role") or service_input.get("service_input_role"),
            },
        ),
        _stage_row(
            stage_id="l3_market_state_overview",
            layer="L3 market_state / bundle",
            name="FX market.overview preferred row",
            status=_status(identity_ok and market_state_present and trusted_structural, partial=not continuous_ws),
            evidence={
                "trust_state": trust_state,
                "interpretation_bucket": interpretation_bucket,
                "continuity_state": continuity_state,
                "best_bid": ov.get("best_bid"),
                "best_ask": ov.get("best_ask"),
                "spread": ov.get("spread"),
                "imbalance": ov.get("imbalance"),
                "trade_delta": ov.get("trade_delta"),
            },
            warnings=["market_state_is_rest_baseline_snapshot"] if rest_baseline else [],
        ),
        _stage_row(
            stage_id="l3_orderbook_semantics",
            layer="L3 market_state / bundle",
            name="FX orderbook semantic/context wiring",
            status=_status(orderbook_context_available, partial=orderbook_context_available and not continuous_ws),
            evidence={
                "orderbook_wiring_status": service_input.get("orderbook_wiring_status") or summary.get("orderbook_wiring_status"),
                "orderbook_active_event_count": summary.get("orderbook_active_event_count"),
                "orderbook_summary_slots_count": summary.get("orderbook_summary_slots_count"),
            },
            blockers=[] if orderbook_context_available else ["orderbook_context_missing"],
        ),
        _stage_row(
            stage_id="l4_execution_market_service_input",
            layer="L4 consumer/service input",
            name="FX execution market service input",
            status=_status(not service_blockers and identity_ok, partial=bool(service_warnings)),
            evidence={
                "contract_type": service_input.get("contract_type"),
                "service_input_role": service_input.get("service_input_role"),
                "consumer_allowed": service_input.get("consumer_allowed"),
                "capabilities": service_input.get("capabilities"),
                "blocked_by": service_blockers,
                "warnings": service_warnings,
            },
            blockers=service_blockers,
            warnings=service_warnings,
        ),
        _stage_row(
            stage_id="private_rest_readiness",
            layer="Private REST state",
            name="FX private/account/order/fill state readiness",
            status="not_evaluated_by_l1_l4_audit",
            evidence={
                "note": "Private REST readiness is checked by private_state/live-readiness gates; included here as related pre-live material, not public L1-L4 lineage.",
                "execution_product_code": ctx.get("product_code") or ctx.get("symbol_raw"),
                "execution_market_uid": ctx.get("market_uid"),
            },
        ),
    ]

    blocked = list(dict.fromkeys(blocked))
    warnings = list(dict.fromkeys(warnings))
    parity_complete = not blocked

    return {
        "stage": STAGE,
        "audit_version": AUDIT_VERSION,
        "ok": parity_complete,
        "parity_complete": parity_complete,
        "summary": {
            "execution_market_identity_ok": identity_ok,
            "market_state_present": market_state_present,
            "trusted_structural_market_state": trusted_structural,
            "continuous_ws_l3_lineage_present": continuous_ws,
            "rest_baseline_usable": rest_baseline and trusted_structural,
            "semantic_context_available": semantic_context_available,
            "orderbook_context_available": orderbook_context_available,
            "l4_service_input_blocked": bool(service_blockers),
            "service_stale": service_stale,
            "primary_lineage": primary_lineage,
        },
        "context": ctx,
        "stages": stages,
        "blocked_by": blocked,
        "warnings": warnings,
        "decision": (
            "hold_autotrade_resume_until_gaps_resolved_or_explicitly_accepted"
            if blocked
            else "eligible_for_final_human_review_before_autotrade_resume"
        ),
        "read_only": True,
        "would_send_to_broker": False,
    }


def _output_path() -> Path:
    cfg = load_config()
    out = cfg.roots()["state"] / "operator_ui" / "sr_fx_data_lineage_parity_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def write_sr_fx_data_lineage_parity_audit(payload: Mapping[str, Any]) -> Path:
    out = _output_path()
    out.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return out


def main() -> int:
    try:
        payload = build_sr_fx_data_lineage_parity_audit_payload()
        out = write_sr_fx_data_lineage_parity_audit(payload)
        print(json.dumps({**payload, "paths": {"audit_path": str(out)}}, ensure_ascii=False, indent=2, sort_keys=True, default=str))
        return 0
    except Exception as exc:
        payload = {
            "stage": STAGE,
            "audit_version": AUDIT_VERSION,
            "ok": False,
            "parity_complete": False,
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["sr_fx_data_lineage_parity_audit_failed"],
            "read_only": True,
            "would_send_to_broker": False,
        }
        try:
            out = write_sr_fx_data_lineage_parity_audit(payload)
            payload["paths"] = {"audit_path": str(out)}
        except Exception:
            pass
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
