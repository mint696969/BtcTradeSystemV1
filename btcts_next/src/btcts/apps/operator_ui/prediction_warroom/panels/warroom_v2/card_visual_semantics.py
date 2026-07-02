# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/card_visual_semantics.py
# desc: WarRoom v2 card visual semantics. Display-only; separates tone, freshness, and evidence meaning.

from __future__ import annotations

from typing import Any

WARROOM_V2_CARD_VISUAL_SEMANTICS_VERSION = "prediction_warroom.v2.card_visual_semantics.ps_q29i.v1"

_TONE_CLASS = {
    "good": "wv2-tone-good",
    "caution": "wv2-tone-caution",
    "danger": "wv2-tone-danger",
    "unknown": "wv2-tone-unknown",
}

_EVIDENCE_CLASS = {
    "STRONG": "wv2-evidence-strong",
    "PARTIAL": "wv2-evidence-partial",
    "WEAK": "wv2-evidence-weak",
    "CONFLICTED": "wv2-evidence-conflicted",
    "MISSING": "wv2-evidence-missing",
}

_FRESHNESS_CLASS = {
    "LIVE": "wv2-freshness-live",
    "WARM": "wv2-freshness-warm",
    "STALE": "wv2-freshness-stale",
    "MISSING": "wv2-freshness-missing",
    "NO_DATA": "wv2-freshness-missing",
}


def build_warroom_v2_card_visual_semantics_packet(payload: dict[str, Any]) -> dict[str, Any]:
    tone = str(payload.get("background_tone") or "unknown").lower()
    evidence = str(payload.get("evidence_quality") or "MISSING").upper()
    freshness = str(payload.get("freshness_badge") or "NO_DATA").upper()
    return {
        "ok": True,
        "visual_semantics_version": WARROOM_V2_CARD_VISUAL_SEMANTICS_VERSION,
        "background_tone": tone if tone in _TONE_CLASS else "unknown",
        "background_class": _TONE_CLASS.get(tone, _TONE_CLASS["unknown"]),
        "freshness_badge": freshness,
        "freshness_class": _FRESHNESS_CLASS.get(freshness, _FRESHNESS_CLASS["NO_DATA"]),
        "evidence_quality": evidence if evidence in _EVIDENCE_CLASS else "MISSING",
        "evidence_class": _EVIDENCE_CLASS.get(evidence, _EVIDENCE_CLASS["MISSING"]),
        "background_color_never_encodes_freshness": True,
        "freshness_encoded_by_badge_only": True,
        "freshness_not_encoded_by_border": True,
        "border_meaning": "evidence_quality",
        "display_only": True,
        "runtime_connected": False,
        "push_connected": False,
        "would_send_to_broker": False,
    }


def warroom_v2_card_visual_semantics_css() -> str:
    return """
.wv2-tone-good { background: #DCFAE6; }
.wv2-tone-caution { background: #FEF7C3; }
.wv2-tone-danger { background: #FEE4E2; }
.wv2-tone-unknown { background: #F2F4F7; }
.wv2-evidence-strong { border: 2px solid rgba(21,112,239,.95); }
.wv2-evidence-partial { border: 2px solid rgba(105,65,198,.82); }
.wv2-evidence-weak { border: 2px solid rgba(102,112,133,.72); }
.wv2-evidence-conflicted { border: 2px dashed rgba(105,65,198,.95); }
.wv2-evidence-missing { border: 2px dotted rgba(102,112,133,.9); }
.wv2-freshness-live { color: #027A48; }
.wv2-freshness-warm { color: #B54708; }
.wv2-freshness-stale, .wv2-freshness-missing { color: #667085; }
""".strip()
