# path: ./tools/test_l3_event_usage_audit.py
# desc: Audit L3 event usage grade policy against current Phase 4-A interpretation buckets.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
from typing import Any, Dict, List

from btcts.processing.l3_market_semantics.event_usage_policy import (
    build_event_contract_row,
    build_event_usage_contract_rows,
    build_event_usage_summary,
    resolve_event_family,
    resolve_semantic_observer_status,
    resolve_usage_grade,
)


POLICY_VERSION = "l3_event_usage_policy.v1alpha1"

INTERPRETATION_BUCKETS = [
    "allow_structural_use",
    "observe_only",
    "reanchor_required",
]

EVENT_FAMILIES = [
    "pressure",
    "wall",
    "support_resistance",
    "pull",
    "depth",
    "spread",
    "sweep",
    "absorption",
]

STABLE_EVENT_NAME_SAMPLES = {
    "pressure_shift": "pressure",
    "imbalance_flip_to_bid": "pressure",
    "imbalance_flip_to_ask": "pressure",
    "wall_created": "wall",
    "wall_removed": "wall",
    "near_wall_created": "wall",
    "near_wall_continued": "wall",
    "support_candidate": "support_resistance",
    "resistance_candidate": "support_resistance",
    "bid_liquidity_pulled": "pull",
    "ask_liquidity_pulled": "pull",
    "bid_liquidity_added": "depth",
    "ask_liquidity_removed": "depth",
    "spread_expansion": "spread",
    "spread_compression": "spread",
    "sweep_candidate": "sweep",
    "absorption_candidate": "absorption",
}

EXPECTED_USAGE_MATRIX = {
    "allow_structural_use": {
        "pressure": "strong",
        "wall": "strong",
        "support_resistance": "strong",
        "pull": "strong",
        "depth": "strong",
        "spread": "strong",
        "sweep": "strong",
        "absorption": "strong",
    },
    "observe_only": {
        "pressure": "watch_weak",
        "wall": "watch",
        "support_resistance": "watch",
        "pull": "watch",
        "depth": "watch",
        "spread": "watch",
        "sweep": "tentative",
        "absorption": "tentative",
    },
    "reanchor_required": {
        "pressure": "invalid",
        "wall": "invalid",
        "support_resistance": "invalid",
        "pull": "invalid",
        "depth": "invalid",
        "spread": "invalid",
        "sweep": "invalid",
        "absorption": "invalid",
    },
}

EXPECTED_OBSERVER_STATUS = {
    "allow_structural_use": "healthy",
    "observe_only": "caution",
    "reanchor_required": "broken",
}


def _assert(cond: bool, message: str, failures: List[str]) -> None:
    if not cond:
        failures.append(message)


def _build_matrix_rows() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for bucket in INTERPRETATION_BUCKETS:
        for event_family in EVENT_FAMILIES:
            rows.append(
                {
                    "interpretation_bucket": bucket,
                    "event_family": event_family,
                    "usage_grade": resolve_usage_grade(bucket, event_family),
                }
            )
    return rows


def _check_usage_matrix(rows: List[Dict[str, str]], failures: List[str]) -> Dict[str, Any]:
    _assert(
        len(rows) == len(INTERPRETATION_BUCKETS) * len(EVENT_FAMILIES),
        "usage matrix row count must cover all buckets x event families",
        failures,
    )

    mismatches: List[Dict[str, str]] = []

    for bucket, family_expectations in EXPECTED_USAGE_MATRIX.items():
        for event_family, expected_grade in family_expectations.items():
            actual = resolve_usage_grade(bucket, event_family)
            if actual != expected_grade:
                mismatches.append(
                    {
                        "interpretation_bucket": bucket,
                        "event_family": event_family,
                        "expected": expected_grade,
                        "actual": actual,
                    }
                )
                failures.append(
                    f"usage matrix mismatch: {bucket}/{event_family}: expected={expected_grade}, actual={actual}"
                )

    return {
        "row_count": len(rows),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }


def _check_event_name_mapping(failures: List[str]) -> Dict[str, Any]:
    mismatches: List[Dict[str, str]] = []

    for event_name, expected_family in STABLE_EVENT_NAME_SAMPLES.items():
        actual = resolve_event_family(event_name)
        if actual != expected_family:
            mismatches.append(
                {
                    "event_name": event_name,
                    "expected": expected_family,
                    "actual": actual,
                }
            )
            failures.append(
                f"event family mapping mismatch: {event_name}: expected={expected_family}, actual={actual}"
            )

    unknown_family = resolve_event_family("unknown_event_name")
    _assert(
        unknown_family == "unknown",
        f"unknown event name must resolve to unknown, got={unknown_family}",
        failures,
    )

    return {
        "sample_count": len(STABLE_EVENT_NAME_SAMPLES),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "unknown_event_name_family": unknown_family,
    }


def _check_contract_rows(failures: List[str]) -> Dict[str, Any]:
    missing_or_bad: List[Dict[str, Any]] = []

    for bucket in INTERPRETATION_BUCKETS:
        rows = build_event_usage_contract_rows(bucket)
        _assert(len(rows) == len(EVENT_FAMILIES), f"contract rows must cover all event families: {bucket}", failures)

        for row in rows:
            checks = {
                "contract_source": row.get("contract_source") == "l3_event_usage_policy",
                "interpretation_bucket": row.get("interpretation_bucket") == bucket,
                "meaning_version": row.get("meaning_version") == POLICY_VERSION,
                "event_family_known": row.get("event_family") in EVENT_FAMILIES,
                "usage_grade_expected": row.get("usage_grade")
                == EXPECTED_USAGE_MATRIX[bucket].get(str(row.get("event_family"))),
            }
            bad = [name for name, ok in checks.items() if not ok]
            if bad:
                missing_or_bad.append({"bucket": bucket, "row": row, "bad": bad})
                failures.append(f"bad event usage contract row: bucket={bucket}, row={row}, bad={bad}")

    support_row = build_event_contract_row(
        "support_candidate",
        "observe_only",
        trust_state="provisional",
        side="bid",
        evidence_refs=["l2:book_depth"],
    )

    expected_support_values = {
        "event_family": "support_resistance",
        "usage_grade": "watch",
        "meaning_version": POLICY_VERSION,
        "confidence": 0.55,
        "trust_bucket": "degraded",
        "actionability": "review",
        "forecast_horizon_hint": "short",
        "half_life_sec": 30,
        "side": "bid",
    }

    for key, expected in expected_support_values.items():
        actual = support_row.get(key)
        if actual != expected:
            missing_or_bad.append(
                {
                    "bucket": "observe_only",
                    "row": support_row,
                    "bad": [f"{key}: expected={expected}, actual={actual}"],
                }
            )
            failures.append(f"bad support_candidate contract field: {key}: expected={expected}, actual={actual}")

    _assert(
        support_row.get("consumer_allowed") == ["ui", "alert", "ai"],
        "observe_only support_candidate consumer_allowed must be UI/alert/AI only",
        failures,
    )
    _assert(
        support_row.get("invalidates_on") == ["series_boundary", "reanchor_required"],
        "event contract invalidates_on must include series boundary and reanchor boundary",
        failures,
    )

    return {
        "bad_count": len(missing_or_bad),
        "bad": missing_or_bad,
        "sample_support_candidate": support_row,
    }


def _check_event_usage_summary(failures: List[str]) -> Dict[str, Any]:
    summaries: Dict[str, Dict[str, Any]] = {}

    for bucket in INTERPRETATION_BUCKETS:
        summary = build_event_usage_summary(
            bucket,
            event_names=list(STABLE_EVENT_NAME_SAMPLES.keys()) + ["unknown_event_name"],
            active_event_contracts=[
                build_event_contract_row(
                    "pressure_shift",
                    bucket,
                    trust_state="trusted" if bucket == "allow_structural_use" else "provisional",
                    side="bid",
                ),
                build_event_contract_row(
                    "unknown_event_name",
                    "reanchor_required",
                    trust_state="broken",
                    side=None,
                ),
            ],
        )
        summaries[bucket] = summary

        _assert(
            summary.get("contract_source") == "l3_event_usage_policy",
            f"summary contract_source mismatch: {bucket}",
            failures,
        )
        _assert(
            summary.get("meaning_version") == POLICY_VERSION,
            f"summary meaning_version mismatch: {bucket}",
            failures,
        )
        _assert(
            summary.get("observer_status") == EXPECTED_OBSERVER_STATUS[bucket],
            f"summary observer_status mismatch: {bucket}",
            failures,
        )
        _assert(
            summary.get("unknown_event_count") == 1,
            f"summary unknown_event_count must remain explicit: {bucket}",
            failures,
        )

    return {
        "summary_count": len(summaries),
        "summaries": summaries,
    }


def main() -> int:
    failures: List[str] = []

    rows = _build_matrix_rows()
    usage_matrix = _check_usage_matrix(rows, failures)
    event_name_mapping = _check_event_name_mapping(failures)
    contract_rows = _check_contract_rows(failures)
    event_usage_summary = _check_event_usage_summary(failures)

    report = {
        "phase": "phase4a_l3_event_usage_policy_audit",
        "policy_version": POLICY_VERSION,
        "checks": {
            "usage_matrix": usage_matrix,
            "event_name_mapping": event_name_mapping,
            "contract_rows": contract_rows,
            "event_usage_summary": event_usage_summary,
        },
        "rows": rows,
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())