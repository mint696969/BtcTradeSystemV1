# path: ./tools/diagnose_phase4a_prediction_system_ps_q26i_warroom_technical_term_allowlist_ui_review.py
# desc: Read-only diagnostic for PS-Q26I WarRoom technical term allowlist and UI review audit.

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26i_warroom_technical_term_allowlist_ui_review.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26I_WARROOM_TECHNICAL_TERM_ALLOWLIST_UI_REVIEW_2026-07-01.md"
AUDIT_TARGETS = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/texts/latest_prediction_display_texts.py",
)

ALLOWLIST_TERMS = (
    "heartbeat",
    "fallback",
    "runtime binding",
    "AutoTrade",
    "broker",
    "scheduler",
    "producer",
    "artifact",
    "fragment",
    "Streamlit",
    "latest prediction",
)
LEGACY_COMPAT_PATTERNS = (
    "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT",
    "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS",
    "latest_prediction_summary_widget_q18aj_searchable_plain_text",
    "latest_prediction_summary_widget_q18ak_searchable_plain_text",
)
REVIEW_CANDIDATE_PATTERNS = (
    "real_render=false",
    "real_widget_render=false",
    "autotrade=false",
    "broker=false",
    "writes=false",
    "view_write=false",
    "broad_page_reload",
    "display-only",
    "current-state",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _line_hits(text: str, patterns: Iterable[str]) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for pattern in patterns:
            if pattern in line:
                hits.append({"line": line_no, "pattern": pattern, "text": line.strip()[:220]})
    return hits


def _is_comment_or_docline(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("#") or stripped.startswith(chr(34) * 3) or stripped.startswith(chr(39) * 3)


def _classify_review_hit(path: Path, hit: dict[str, object]) -> str:
    line_text = str(hit.get("text") or "")
    pattern = str(hit.get("pattern") or "")
    if any(token in line_text for token in LEGACY_COMPAT_PATTERNS):
        return "legacy_compat"
    if pattern in {"display-only", "current-state"} and _is_comment_or_docline(line_text):
        return "allowlisted_comment_or_doc"
    if path.name in {"latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel.py", "latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py"} and (
        "searchable_plain_text" in line_text or "PS_Q18AP_SEARCHABLE" in line_text
    ):
        return "legacy_compat"
    if pattern in {"autotrade=false", "broker=false", "real_render=false", "real_widget_render=false", "writes=false", "view_write=false", "broad_page_reload"}:
        return "review_candidate"
    if pattern in {"display-only", "current-state"}:
        has_japanese_context = any(ch in line_text for ch in "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん現在表示確認予測")
        return "allowlisted_with_japanese_context" if has_japanese_context else "review_candidate"
    return "review_candidate"


def run_warroom_technical_term_allowlist_ui_review_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    for marker in (
        "ps_q26i_warroom_technical_term_allowlist_ui_review=true",
        "audit_only=true",
        "technical_term_allowlist_recorded=true",
        "ui_review_classification_recorded=true",
        "production_ui_code_changed=false",
        "legacy_searchable_compatibility_preserved=true",
        "allowlist_hit_count_recorded=true",
        "review_candidate_count_recorded=true",
        "legacy_compat_count_recorded=true",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")

    allowlist_hits: list[dict[str, object]] = []
    legacy_hits: list[dict[str, object]] = []
    review_hits: list[dict[str, object]] = []
    allowed_review_hits: list[dict[str, object]] = []
    files_scanned: list[str] = []

    for path in AUDIT_TARGETS:
        text = _read(path)
        if not text:
            blockers.append(f"audit_target_missing:{path.relative_to(REPO_ROOT)}")
            continue
        files_scanned.append(str(path.relative_to(REPO_ROOT)))
        for hit in _line_hits(text, ALLOWLIST_TERMS):
            allowlist_hits.append({"path": str(path.relative_to(REPO_ROOT)), **hit})
        for hit in _line_hits(text, LEGACY_COMPAT_PATTERNS):
            legacy_hits.append({"path": str(path.relative_to(REPO_ROOT)), **hit})
        for hit in _line_hits(text, REVIEW_CANDIDATE_PATTERNS):
            classification = _classify_review_hit(path, hit)
            item = {"path": str(path.relative_to(REPO_ROOT)), "classification": classification, **hit}
            if classification == "review_candidate":
                review_hits.append(item)
            else:
                allowed_review_hits.append(item)

    if not allowlist_hits:
        blockers.append("allowlist_hits_missing")
    if not legacy_hits:
        blockers.append("legacy_compat_hits_missing")
    if not review_hits:
        blockers.append("review_candidate_hits_missing")

    next_priorities = [
        {
            "priority": "P1",
            "slice": "PS_Q26J_WARROOM_UI_REVIEW_REMAINING_REVIEW_CANDIDATE_POLISH_DISPLAY_ONLY",
            "reason": "Review-candidate false fragments and broad_page_reload labels should be polished only where operator-visible, while preserving legacy searchable tokens.",
        },
        {
            "priority": "P2",
            "slice": "PS_Q26K_WARROOM_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_DISPLAY_ONLY",
            "reason": "Allowed technical terms should get consistent Japanese helper wording rather than being removed.",
        },
    ]

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "audit_only": True,
        "technical_term_allowlist_recorded": True,
        "ui_review_classification_recorded": True,
        "production_ui_code_changed": False,
        "legacy_searchable_compatibility_preserved": True,
        "files_scanned": files_scanned,
        "allowlist_terms": list(ALLOWLIST_TERMS),
        "legacy_compat_patterns": list(LEGACY_COMPAT_PATTERNS),
        "review_candidate_patterns": list(REVIEW_CANDIDATE_PATTERNS),
        "allowlist_hit_count": len(allowlist_hits),
        "legacy_compat_count": len(legacy_hits),
        "review_candidate_count": len(review_hits),
        "allowed_review_hit_count": len(allowed_review_hits),
        "allowlist_hits_sample": allowlist_hits[:30],
        "legacy_compat_hits_sample": legacy_hits[:30],
        "review_candidates_sample": review_hits[:40],
        "allowed_review_hits_sample": allowed_review_hits[:30],
        "next_priorities": next_priorities,
        "recommended_next_slice": "PS_Q26J_WARROOM_UI_REVIEW_REMAINING_REVIEW_CANDIDATE_POLISH_DISPLAY_ONLY",
        "safety": {
            "read_only": True,
            "audit_only": True,
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
    result = run_warroom_technical_term_allowlist_ui_review_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
