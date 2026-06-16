# path: ./tools/test_collector_vnext_board_ws_rebuild_diagnose.py
# desc: Diagnose whether WS board rebuild mismatch is likely fixable on our side or should be treated as an exchange-side usable-range limitation.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
from typing import Any

from test_collector_vnext_board_ws_rebuild_long import observe_rebuild_accuracy_long


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


def _avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def _classify(result: dict[str, Any]) -> dict[str, Any]:
    summary = result.get("summary") if isinstance(result, dict) else {}
    worst_cases = result.get("worst_cases") if isinstance(result, dict) else []
    compare_results = result.get("compare_results") if isinstance(result, dict) else []

    best_bid_match_rate = float(summary.get("best_bid_match_rate") or 0.0)
    best_ask_match_rate = float(summary.get("best_ask_match_rate") or 0.0)
    top10_bid_avg_ratio = float(summary.get("top10_bid_avg_ratio") or 0.0)
    top10_ask_avg_ratio = float(summary.get("top10_ask_avg_ratio") or 0.0)
    top20_bid_avg_ratio = float(summary.get("top20_bid_avg_ratio") or 0.0)
    top20_ask_avg_ratio = float(summary.get("top20_ask_avg_ratio") or 0.0)
    top50_bid_avg_ratio = float(summary.get("top50_bid_avg_ratio") or 0.0)
    top50_ask_avg_ratio = float(summary.get("top50_ask_avg_ratio") or 0.0)
    top100_bid_avg_ratio = float(summary.get("top100_bid_avg_ratio") or 0.0)
    top100_ask_avg_ratio = float(summary.get("top100_ask_avg_ratio") or 0.0)

    ask_side_weaker_than_bid_top50_count = int(summary.get("ask_side_weaker_than_bid_top50_count") or 0)
    ask_side_weaker_than_bid_top100_count = int(summary.get("ask_side_weaker_than_bid_top100_count") or 0)
    compare_count = int(summary.get("compare_count") or 0)

    worst_top10_bid = min((float(x.get("top10_bid_ratio") or 0.0) for x in worst_cases), default=0.0)
    worst_top10_ask = min((float(x.get("top10_ask_ratio") or 0.0) for x in worst_cases), default=0.0)
    worst_top50_bid = min((float(x.get("top50_bid_ratio") or 0.0) for x in worst_cases), default=0.0)
    worst_top50_ask = min((float(x.get("top50_ask_ratio") or 0.0) for x in worst_cases), default=0.0)

    diffs_applied_values = [int(x.get("diffs_applied") or 0) for x in compare_results]
    worst_case_diffs = [int(x.get("diffs_applied") or 0) for x in worst_cases]
    avg_diffs_applied = _avg([float(x) for x in diffs_applied_values])
    avg_worst_diffs_applied = _avg([float(x) for x in worst_case_diffs])

    signals = {
        "best_is_strong": best_bid_match_rate >= 0.90 and best_ask_match_rate >= 0.90,
        "top10_is_strong": top10_bid_avg_ratio >= 0.80 and top10_ask_avg_ratio >= 0.80,
        "top20_is_strong": top20_bid_avg_ratio >= 0.75 and top20_ask_avg_ratio >= 0.75,
        "deep_levels_weaken": top50_bid_avg_ratio < top20_bid_avg_ratio or top50_ask_avg_ratio < top20_ask_avg_ratio,
        "very_deep_levels_weaken": top100_bid_avg_ratio < top50_bid_avg_ratio or top100_ask_avg_ratio < top50_ask_ratio if False else (top100_bid_avg_ratio < top50_bid_avg_ratio or top100_ask_avg_ratio < top50_ask_avg_ratio),
        "ask_side_bias_exists": compare_count > 0 and (
            ask_side_weaker_than_bid_top50_count >= max(3, compare_count // 5)
            or ask_side_weaker_than_bid_top100_count >= max(3, compare_count // 5)
        ),
        "worst_cases_are_extreme": (
            worst_top10_bid <= 0.20
            or worst_top10_ask <= 0.20
            or worst_top50_bid <= 0.30
            or worst_top50_ask <= 0.30
        ),
        "worst_cases_follow_long_diff_chain": avg_worst_diffs_applied > max(10.0, avg_diffs_applied * 1.15),
        "near_levels_are_also_weak": top10_bid_avg_ratio < 0.70 or top10_ask_avg_ratio < 0.70,
    }

    notes: list[str] = []

    if signals["best_is_strong"] and signals["top10_is_strong"] and signals["deep_levels_weaken"]:
        notes.append("best/top10 are strong while deeper levels weaken")
    if signals["ask_side_bias_exists"]:
        notes.append("ask side appears systematically weaker than bid side in deeper levels")
    if signals["worst_cases_follow_long_diff_chain"]:
        notes.append("worst cases correlate with longer diff chains; periodic rebasing may help")
    if signals["worst_cases_are_extreme"]:
        notes.append("some worst cases are extreme enough that full-depth continuous truth remains unsafe")
    if signals["near_levels_are_also_weak"]:
        notes.append("near levels are also weak; rebuild/comparison logic likely needs stronger investigation")

    if signals["best_is_strong"] and signals["top10_is_strong"] and signals["deep_levels_weaken"]:
        if signals["ask_side_bias_exists"] or signals["worst_cases_follow_long_diff_chain"]:
            diagnosis = "exchange_side_limited_but_usable"
            recommendation = {
                "top10": "operationally_usable",
                "top20": "likely_usable_with_care",
                "top50": "conditional_only",
                "top100": "reference_only",
                "strategy": "use_near_book_signals_and_consider_periodic_rebase",
            }
        else:
            diagnosis = "comparison_method_needs_care"
            recommendation = {
                "top10": "usable",
                "top20": "usable_with_care",
                "top50": "needs_more_evidence",
                "top100": "not_for_truth_use",
                "strategy": "inspect snapshot-diff timing alignment before changing rebuild semantics",
            }
    elif signals["near_levels_are_also_weak"] or not signals["best_is_strong"]:
        diagnosis = "collector_side_fixable"
        recommendation = {
            "top10": "not_yet_trusted",
            "top20": "not_yet_trusted",
            "top50": "not_yet_trusted",
            "top100": "not_yet_trusted",
            "strategy": "investigate rebuild semantics, deletion handling, and comparison logic before operational use",
        }
    else:
        diagnosis = "comparison_method_needs_care"
        recommendation = {
            "top10": "usable_with_observation",
            "top20": "usable_with_care",
            "top50": "conditional_only",
            "top100": "reference_only",
            "strategy": "increase diagnostic detail and verify whether mismatch is timing or semantics",
        }

    return {
        "diagnosis": diagnosis,
        "signals": signals,
        "notes": notes,
        "recommendation": recommendation,
    }


def main() -> int:
    max_seconds = _env_float("BTCTS_WS_REBUILD_DIAG_SECONDS", 300.0)
    max_compare_count = _env_int("BTCTS_WS_REBUILD_DIAG_COMPARE_COUNT", 50)

    result = observe_rebuild_accuracy_long(
        max_seconds=max_seconds,
        max_compare_count=max_compare_count,
    )
    diagnosis = _classify(result)

    report = {
        "ok": True,
        "gate_type": "ws_board_rebuild_diagnose",
        "observe_result": result,
        "diagnosis": diagnosis,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())