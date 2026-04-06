# path: ./tools/test_l3_event_usage_audit.py
# desc: Audit L3 event usage grade against continuity interpretation buckets.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json


def _usage_grade(interpretation_bucket: str, event_kind: str) -> str:
    if interpretation_bucket == "allow_structural_use":
        return "strong"

    if interpretation_bucket == "observe_only":
        if event_kind == "pressure":
            return "watch_weak"
        if event_kind in {"wall", "pull"}:
            return "watch"
        if event_kind in {"sweep", "absorption"}:
            return "tentative"
        return "watch"

    if interpretation_bucket == "reanchor_required":
        return "invalid"

    return "unknown"


def main() -> int:
    interpretation_buckets = [
        "allow_structural_use",
        "observe_only",
        "reanchor_required",
    ]
    event_kinds = [
        "pressure",
        "wall",
        "pull",
        "sweep",
        "absorption",
    ]

    rows: list[dict[str, str]] = []
    for bucket in interpretation_buckets:
        for event_kind in event_kinds:
            rows.append(
                {
                    "interpretation_bucket": bucket,
                    "event_kind": event_kind,
                    "usage_grade": _usage_grade(bucket, event_kind),
                }
            )

    report = {
        "policy_version": "draft_2026-04-05",
        "rows": rows,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())