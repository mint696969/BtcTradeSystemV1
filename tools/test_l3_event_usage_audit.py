# path: ./tools/test_l3_event_usage_audit.py
# desc: Audit L3 event usage grade against continuity interpretation buckets.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json

from btcts.processing.l3_market_semantics.event_usage_policy import resolve_usage_grade


def main() -> int:
    interpretation_buckets = [
        "allow_structural_use",
        "observe_only",
        "reanchor_required",
    ]
    event_families = [
        "pressure",
        "wall",
        "support_resistance",
        "pull",
        "depth",
        "spread",
        "sweep",
        "absorption",
    ]

    rows: list[dict[str, str]] = []
    for bucket in interpretation_buckets:
        for event_family in event_families:
            rows.append(
                {
                    "interpretation_bucket": bucket,
                    "event_family": event_family,
                    "usage_grade": resolve_usage_grade(bucket, event_family),
                }
            )

    report = {
        "policy_version": "phase1_seed_2026-04-08",
        "rows": rows,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())