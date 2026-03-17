# path: ./tools/test_collector_vnext_live_diff_gate.py
# desc: Evaluate live WS board rebuild credibility against gate thresholds before weekly soak.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os

from test_collector_vnext_board_ws_rebuild import observe_rebuild_accuracy


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except Exception:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def main() -> int:
    max_compare_count = _env_int("BTCTS_LIVE_DIFF_GATE_COMPARE_COUNT", 6)
    max_seconds = _env_float("BTCTS_LIVE_DIFF_GATE_SECONDS", 120.0)

    min_best_bid_match_rate = _env_float("BTCTS_LIVE_DIFF_MIN_BEST_BID_MATCH", 0.80)
    min_best_ask_match_rate = _env_float("BTCTS_LIVE_DIFF_MIN_BEST_ASK_MATCH", 0.80)
    min_top10_bid_ratio = _env_float("BTCTS_LIVE_DIFF_MIN_TOP10_BID_RATIO", 0.60)
    min_top10_ask_ratio = _env_float("BTCTS_LIVE_DIFF_MIN_TOP10_ASK_RATIO", 0.60)

    result = observe_rebuild_accuracy(
        max_compare_count=max_compare_count,
        max_seconds=max_seconds,
    )

    summary = result.get("summary") if isinstance(result, dict) else {}
    best_bid_match_rate = float(summary.get("best_bid_match_rate") or 0.0)
    best_ask_match_rate = float(summary.get("best_ask_match_rate") or 0.0)
    top10_bid_avg_ratio = float(summary.get("top10_bid_avg_ratio") or 0.0)
    top10_ask_avg_ratio = float(summary.get("top10_ask_avg_ratio") or 0.0)

    checks = {
        "has_compare_results": int(result.get("compare_count") or 0) > 0,
        "best_bid_match_rate_ok": best_bid_match_rate >= min_best_bid_match_rate,
        "best_ask_match_rate_ok": best_ask_match_rate >= min_best_ask_match_rate,
        "top10_bid_ratio_ok": top10_bid_avg_ratio >= min_top10_bid_ratio,
        "top10_ask_ratio_ok": top10_ask_avg_ratio >= min_top10_ask_ratio,
    }

    ok = all(checks.values())

    report = {
        "ok": ok,
        "gate_type": "live_diff_rebuild_credibility",
        "thresholds": {
            "min_best_bid_match_rate": min_best_bid_match_rate,
            "min_best_ask_match_rate": min_best_ask_match_rate,
            "min_top10_bid_ratio": min_top10_bid_ratio,
            "min_top10_ask_ratio": min_top10_ask_ratio,
        },
        "checks": checks,
        "observe_result": result,
        "operator_note": (
            "acceptable_for_next_stage" if ok else "needs_more_rebuild_investigation"
        ),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())