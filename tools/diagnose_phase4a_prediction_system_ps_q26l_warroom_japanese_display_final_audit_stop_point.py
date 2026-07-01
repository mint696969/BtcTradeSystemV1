# path: ./tools/diagnose_phase4a_prediction_system_ps_q26l_warroom_japanese_display_final_audit_stop_point.py
# desc: Final audit-only diagnostic for PS-Q26L WarRoom Japanese display cycle stop point.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q26i_warroom_technical_term_allowlist_ui_review import run_warroom_technical_term_allowlist_ui_review_diagnostic  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q26j_warroom_review_candidate_polish import run_warroom_review_candidate_polish_diagnostic  # noqa: E402
from tools.diagnose_phase4a_prediction_system_ps_q26k_allowed_tech_term_label_help_text import run_allowed_tech_term_label_help_text_diagnostic  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26l_warroom_japanese_display_final_audit_stop_point.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26L_WARROOM_JAPANESE_DISPLAY_FINAL_AUDIT_AND_STOP_POINT_2026-07-01.md"
SELF = Path(__file__)
TEST = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q26l_warroom_japanese_display_final_audit_stop_point.py"
CLOSE = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q26l_warroom_japanese_display_final_audit_stop_point_close_guard.py"

NEXT_LANE_CHOICES = [
    {"lane": "A", "label": "UI actual screenshot review / visual confirmation", "requires_human_choice": True},
    {"lane": "B", "label": "WarRoom data freshness / live D-hot observation audit", "requires_human_choice": True},
    {"lane": "C", "label": "Prediction producer 60s disabled dry-run gate planning", "requires_human_choice": True},
    {"lane": "D", "label": "Documentation/handoff consolidation", "requires_human_choice": True},
    {"lane": "E", "label": "Pause implementation and run CC review", "requires_human_choice": True},
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _all_false(packet: dict, keys: tuple[str, ...]) -> list[str]:
    return [key for key in keys if packet.get(key) is not False]


def _all_true(packet: dict, keys: tuple[str, ...]) -> list[str]:
    return [key for key in keys if packet.get(key) is not True]


def run_warroom_japanese_display_final_audit_stop_point_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    for marker in (
        "ps_q26l_warroom_japanese_display_final_audit_and_stop_point=true",
        "final_audit_only=true",
        "production_ui_code_changed=false",
        "q26i_audit_ready=true",
        "q26j_polish_ready=true",
        "q26k_help_text_ready=true",
        "warroom_japanese_display_cycle_complete=true",
        "stop_point_reached=true",
        "human_next_lane_choice_required=true",
        "automatic_next_implementation_disallowed=true",
        "recommended_next_slice=HUMAN_CHOICE_REQUIRED",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for path, markers in (
        (SELF, ("NEXT_LANE_CHOICES", "HUMAN_CHOICE_REQUIRED", "stop_point_reached")),
        (TEST, ("test_q26l_final_audit_ready_and_stop_point", "human_next_lane_choice_required")),
        (CLOSE, ("production_ui_code_changed", "human_next_lane_choice_required")),
    ):
        text = _read(path)
        for marker in markers:
            if marker not in text:
                blockers.append(f"marker_required:{path.relative_to(REPO_ROOT)}:{marker}")

    q26i = run_warroom_technical_term_allowlist_ui_review_diagnostic()
    q26j = run_warroom_review_candidate_polish_diagnostic()
    q26k = run_allowed_tech_term_label_help_text_diagnostic()
    for name, packet in (("q26i", q26i), ("q26j", q26j), ("q26k", q26k)):
        if packet.get("ready") is not True:
            blockers.append(f"{name}_not_ready:{packet.get('blockers')}")
    if q26i.get("legacy_compat_count") != 4:
        blockers.append(f"q26i_legacy_compat_count_changed:{q26i.get('legacy_compat_count')}")
    if not isinstance(q26j.get("post_q26j_review_candidate_count"), int) or q26j.get("post_q26j_review_candidate_count") >= q26j.get("baseline_review_candidate_count", 45):
        blockers.append("q26j_review_candidate_count_not_reduced")
    if q26j.get("post_q26j_legacy_compat_count") != 4:
        blockers.append(f"q26j_legacy_compat_count_changed:{q26j.get('post_q26j_legacy_compat_count')}")
    if q26k.get("term_count") != 7:
        blockers.append(f"q26k_term_count_changed:{q26k.get('term_count')}")
    if q26k.get("q26i_legacy_compat_count") != 4:
        blockers.append(f"q26k_legacy_compat_count_changed:{q26k.get('q26i_legacy_compat_count')}")

    false_keys = (
        "trade_guidance_added",
        "trade_signal_added",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    )
    true_keys = ("read_only", "display_only", "non_executing")
    for name, diag in (("q26i", q26i), ("q26j", q26j), ("q26k", q26k)):
        safety = diag.get("safety") if isinstance(diag.get("safety"), dict) else {}
        for key in _all_true(safety, true_keys):
            blockers.append(f"{name}_safety_true_required:{key}")
        for key in _all_false(safety, false_keys):
            blockers.append(f"{name}_safety_false_required:{key}")

    final_packet = {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "final_audit_only": True,
        "production_ui_code_changed": False,
        "q26i_audit_ready": q26i.get("ready") is True,
        "q26j_polish_ready": q26j.get("ready") is True,
        "q26k_help_text_ready": q26k.get("ready") is True,
        "warroom_japanese_display_cycle_complete": True,
        "stop_point_reached": True,
        "human_next_lane_choice_required": True,
        "automatic_next_implementation_disallowed": True,
        "recommended_next_slice": "HUMAN_CHOICE_REQUIRED",
        "next_lane_choices": NEXT_LANE_CHOICES,
        "q26i_review_candidate_count": q26i.get("review_candidate_count"),
        "q26i_legacy_compat_count": q26i.get("legacy_compat_count"),
        "q26j_baseline_review_candidate_count": q26j.get("baseline_review_candidate_count"),
        "q26j_post_review_candidate_count": q26j.get("post_q26j_review_candidate_count"),
        "q26j_legacy_compat_count": q26j.get("post_q26j_legacy_compat_count"),
        "q26k_term_count": q26k.get("term_count"),
        "q26k_review_candidate_count": q26k.get("q26i_review_candidate_count"),
        "q26k_legacy_compat_count": q26k.get("q26i_legacy_compat_count"),
        "allowed_technical_terms_preserved": q26k.get("allowed_technical_terms_preserved") is True,
        "japanese_helper_wording_added": q26k.get("japanese_helper_wording_added") is True,
        "legacy_searchable_compatibility_preserved": q26k.get("legacy_searchable_compatibility_preserved") is True,
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "trade_guidance_added": False,
        "trade_signal_added": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "final_packet": final_packet,
        "q26i_summary": {
            "ready": q26i.get("ready"),
            "allowlist_hit_count": q26i.get("allowlist_hit_count"),
            "review_candidate_count": q26i.get("review_candidate_count"),
            "legacy_compat_count": q26i.get("legacy_compat_count"),
        },
        "q26j_summary": {
            "ready": q26j.get("ready"),
            "baseline_review_candidate_count": q26j.get("baseline_review_candidate_count"),
            "post_q26j_review_candidate_count": q26j.get("post_q26j_review_candidate_count"),
            "post_q26j_legacy_compat_count": q26j.get("post_q26j_legacy_compat_count"),
            "post_q26j_allowlist_hit_count": q26j.get("post_q26j_allowlist_hit_count"),
        },
        "q26k_summary": {
            "ready": q26k.get("ready"),
            "term_count": q26k.get("term_count"),
            "q26i_review_candidate_count": q26k.get("q26i_review_candidate_count"),
            "q26i_legacy_compat_count": q26k.get("q26i_legacy_compat_count"),
            "recommended_next_slice": q26k.get("recommended_next_slice"),
        },
        "stop_point_reached": True,
        "human_next_lane_choice_required": True,
        "recommended_next_slice": "HUMAN_CHOICE_REQUIRED",
        "next_lane_choices": NEXT_LANE_CHOICES,
        "safety": {
            "read_only": True,
            "display_only": True,
            "non_executing": True,
            "trade_guidance_added": False,
            "trade_signal_added": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_warroom_japanese_display_final_audit_stop_point_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
