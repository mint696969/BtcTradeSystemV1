# path: ./tools/diagnose_phase4a_prediction_system_ps_q26f_warroom_japanese_display_review_remaining_token_audit.py
# desc: Read-only diagnostic for PS-Q26F WarRoom Japanese display review and remaining token audit.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26f_warroom_japanese_display_review_remaining_token_audit.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26F_WARROOM_JAPANESE_DISPLAY_REVIEW_REMAINING_TOKEN_AUDIT_2026-07-01.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
Q18AJ = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel.py"
Q18AK = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py"
PRED_PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
NOWCAST_PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
TEXTS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/texts/latest_prediction_display_texts.py"

AUDIT_TARGETS = (
    ("warroom_page", WARROOM_PAGE),
    ("q18aj_bounded_auto_refresh_panel", Q18AJ),
    ("q18ak_freshness_error_fallback_panel", Q18AK),
    ("latest_prediction_display_panel", PRED_PANEL),
    ("live_nowcast_panel", NOWCAST_PANEL),
    ("prediction_display_texts", TEXTS),
)

VISIBLE_TOKEN_PATTERNS = (
    "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT",
    "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS",
    "autotrade=false",
    "broker=false",
    "writes=false",
    "real_render=false",
    "broad_page_reload",
    "display-only",
    "current-state",
    "runtime binding=false",
    "fallback=",
    "heartbeat=",
)

SAFE_TECHNICAL_TERMS = (
    "AutoTrade",
    "broker",
    "heartbeat",
    "fallback",
    "runtime",
    "fragment",
    "scheduler",
    "producer",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _line_hits(text: str, pattern: str) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if pattern in line:
            hits.append({"line": line_no, "pattern": pattern, "text": line.strip()[:220]})
    return hits


def _priority_for(name: str, pattern: str) -> str:
    if name in {"q18aj_bounded_auto_refresh_panel", "q18ak_freshness_error_fallback_panel"}:
        return "P1"
    if pattern.startswith("PS_Q18AP") or pattern in {"autotrade=false", "broker=false", "writes=false"}:
        return "P1"
    if name == "warroom_page":
        return "P2"
    return "P3"


def _recommendation_for(name: str, pattern: str) -> str:
    if name == "q18aj_bounded_auto_refresh_panel":
        return "Q26Gで Q18AJ caption/searchable text/display row note を日本語化する"
    if name == "q18ak_freshness_error_fallback_panel":
        return "Q26Gで Q18AK freshness/fallback caption/searchable text/display row note を日本語化する"
    if name == "warroom_page":
        return "Q26H以降で WarRoom top reading captions の英語説明を日本語化する"
    return "Q26G以降の小sliceで visible token を文脈に応じて日本語化する"


def run_warroom_japanese_display_review_remaining_token_audit() -> dict:
    blockers: list[str] = []
    doc_text = _read(DOC)
    for marker in (
        "ps_q26f_warroom_japanese_display_review_remaining_token_audit=true",
        "audit_only=true",
        "source_rendered_rows_audited=true",
        "production_ui_code_changed=false",
        "remaining_token_findings_recorded=true",
        "next_polish_priorities_recorded=true",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")

    findings: list[dict[str, object]] = []
    files_scanned: list[str] = []
    for name, path in AUDIT_TARGETS:
        text = _read(path)
        if not text:
            blockers.append(f"audit_target_missing:{path}")
            continue
        files_scanned.append(str(path.relative_to(REPO_ROOT)))
        for pattern in VISIBLE_TOKEN_PATTERNS:
            for hit in _line_hits(text, pattern):
                findings.append({
                    "surface": name,
                    "path": str(path.relative_to(REPO_ROOT)),
                    "line": hit["line"],
                    "pattern": pattern,
                    "priority": _priority_for(name, pattern),
                    "recommendation": _recommendation_for(name, pattern),
                    "evidence": hit["text"],
                })

    p1 = [item for item in findings if item.get("priority") == "P1"]
    q18aj_hits = [item for item in findings if item.get("surface") == "q18aj_bounded_auto_refresh_panel"]
    q18ak_hits = [item for item in findings if item.get("surface") == "q18ak_freshness_error_fallback_panel"]
    if not findings:
        blockers.append("audit_findings_missing_expected_remaining_tokens")
    if not q18aj_hits:
        blockers.append("q18aj_remaining_token_findings_missing")
    if not q18ak_hits:
        blockers.append("q18ak_remaining_token_findings_missing")
    if not p1:
        blockers.append("p1_findings_missing")

    next_priorities = [
        {
            "priority": "P1",
            "slice": "PS_Q26G_Q18AJ_Q18AK_LEGACY_PANEL_JAPANESE_LOCALIZATION_DISPLAY_ONLY",
            "reason": "Q18AJ/Q18AK legacy panels still contain visible searchable PS_Q18AP text, autotrade=false/broker=false fragments, and English row notes.",
        },
        {
            "priority": "P2",
            "slice": "PS_Q26H_WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_DISPLAY_ONLY",
            "reason": "WarRoom top reading block captions still use English explanatory text.",
        },
        {
            "priority": "P3",
            "slice": "PS_Q26I_WARROOM_TECHNICAL_TERM_ALLOWLIST_AND_UI_REVIEW_DISPLAY_ONLY",
            "reason": "Some technical terms should remain visible but need an allowlist so Japanese UI review does not treat them as defects.",
        },
    ]
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "audit_only": True,
        "source_rendered_rows_audited": True,
        "production_ui_code_changed": False,
        "files_scanned": files_scanned,
        "visible_token_patterns": list(VISIBLE_TOKEN_PATTERNS),
        "safe_technical_terms": list(SAFE_TECHNICAL_TERMS),
        "finding_count": len(findings),
        "p1_finding_count": len(p1),
        "q18aj_finding_count": len(q18aj_hits),
        "q18ak_finding_count": len(q18ak_hits),
        "findings": findings[:80],
        "next_priorities": next_priorities,
        "recommended_next_slice": "PS_Q26G_Q18AJ_Q18AK_LEGACY_PANEL_JAPANESE_LOCALIZATION_DISPLAY_ONLY",
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
    result = run_warroom_japanese_display_review_remaining_token_audit()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
