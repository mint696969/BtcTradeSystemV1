# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_layout_policy.py
# desc: PS-Q26O WarRoom top focus layout policy. Layout-only constants/helpers; no Streamlit rendering, runtime writes, producer/scheduler, AutoTrade, broker, ledger, mode, or parameter behavior.

from __future__ import annotations

from typing import Mapping

WARROOM_FOCUS_LAYOUT_POLICY_VERSION = "prediction_warroom.focus_layout_policy.ps_q26o.v1"

_SECTION_LABELS: Mapping[str, str] = {
    "operator_focus_nav": "最初に見る場所 / WarRoom 入口",
    "prediction_quick_status_detail": "予測最新ステータス / quick status",
    "live_nowcast": "現在状態 nowcast / board・freshness",
    "latest_prediction_read_model": "リアルタイム予測表示 / read model",
}

_SECTION_EXPANDED_DEFAULTS: Mapping[str, bool] = {
    "operator_focus_nav": True,
    "prediction_quick_status_detail": False,
    "live_nowcast": True,
    "latest_prediction_read_model": True,
}


def warroom_focus_section_label(section_id: str) -> str:
    return _SECTION_LABELS.get(str(section_id), str(section_id))


def warroom_focus_section_expanded(section_id: str) -> bool:
    return bool(_SECTION_EXPANDED_DEFAULTS.get(str(section_id), False))


def warroom_focus_layout_rows() -> list[dict[str, object]]:
    return [
        {
            "section_id": "operator_focus_nav",
            "label": warroom_focus_section_label("operator_focus_nav"),
            "expanded_default": True,
            "operator_reason": "最初の読み順を示す入口なので常に開く",
        },
        {
            "section_id": "prediction_quick_status_detail",
            "label": warroom_focus_section_label("prediction_quick_status_detail"),
            "expanded_default": False,
            "operator_reason": "詳細確認用。上部の重複を避けるため通常は畳む",
        },
        {
            "section_id": "live_nowcast",
            "label": warroom_focus_section_label("live_nowcast"),
            "expanded_default": True,
            "operator_reason": "現在状態を最初に読む主要セクション",
        },
        {
            "section_id": "latest_prediction_read_model",
            "label": warroom_focus_section_label("latest_prediction_read_model"),
            "expanded_default": True,
            "operator_reason": "生成時刻と予測鮮度を見る主要セクション",
        },
    ]


def build_warroom_focus_layout_policy_packet() -> dict[str, object]:
    rows = warroom_focus_layout_rows()
    return {
        "ok": True,
        "focus_layout_policy_version": WARROOM_FOCUS_LAYOUT_POLICY_VERSION,
        "externalized_layout_policy_module": True,
        "warroom_page_change_boundary": "import_and_policy_lookup_only",
        "quick_status_detail_folded_default": warroom_focus_section_expanded("prediction_quick_status_detail") is False,
        "operator_focus_nav_expanded_default": warroom_focus_section_expanded("operator_focus_nav") is True,
        "live_nowcast_expanded_default": warroom_focus_section_expanded("live_nowcast") is True,
        "latest_prediction_read_model_expanded_default": warroom_focus_section_expanded("latest_prediction_read_model") is True,
        "section_count": len(rows),
        "rows": rows,
        "keeps_existing_panels_available": True,
        "layout_only_change": True,
        "production_ui_code_changed": True,
        "read_only": True,
        "display_only": True,
        "non_executing": True,
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
