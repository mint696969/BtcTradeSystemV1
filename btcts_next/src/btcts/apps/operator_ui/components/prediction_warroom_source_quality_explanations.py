# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_source_quality_explanations.py
# desc: Source-quality and signal-cap explanation panel for Prediction WarRoom display packets. Display-only transform; no runtime reads, rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

PANEL_VERSION = "prediction_warroom_source_quality_explanations.ps_q5a.v1"

_REASON_LABELS_JA: Mapping[str, str] = {
    "tier0_source_quality_blocked": "Tier 0情報源品質ゲートでブロック",
    "tier0_source_quality_warning_context_only": "Tier 0情報源品質が警告状態",
    "tier0_source_quality_signal_strength_capped": "情報源品質により参考度を制限",
    "context_profile_family_minimum_sources_missing": "文脈別の必須情報源が不足",
    "source_artifact_input_coverage_incomplete": "入力情報源カバレッジが不足",
    "prediction_unavailable": "予測不能または根拠不足",
}

_REASON_SEVERITY: Mapping[str, str] = {
    "tier0_source_quality_blocked": "blocker",
    "tier0_source_quality_warning_context_only": "warning",
    "tier0_source_quality_signal_strength_capped": "warning",
    "context_profile_family_minimum_sources_missing": "warning",
    "source_artifact_input_coverage_incomplete": "warning",
    "prediction_unavailable": "blocker",
}


@dataclass(frozen=True)
class PredictionWarRoomSourceQualityExplanationPanel:
    panel_version: str
    prediction_run_id: str | None = None
    signal_cap_explanations: Tuple[Mapping[str, Any], ...] = ()
    source_quality_gate_cards: Tuple[Mapping[str, Any], ...] = ()
    missing_source_cards: Tuple[Mapping[str, Any], ...] = ()
    family_cap_cards: Tuple[Mapping[str, Any], ...] = ()
    watch_points: Tuple[Mapping[str, Any], ...] = ()
    operator_summary_ja: str = ""
    read_only: bool = True
    non_executing: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "panel_version": self.panel_version,
            "prediction_run_id": self.prediction_run_id,
            "signal_cap_explanations": [dict(item) for item in self.signal_cap_explanations],
            "source_quality_gate_cards": [dict(item) for item in self.source_quality_gate_cards],
            "missing_source_cards": [dict(item) for item in self.missing_source_cards],
            "family_cap_cards": [dict(item) for item in self.family_cap_cards],
            "watch_points": [dict(item) for item in self.watch_points],
            "operator_summary_ja": self.operator_summary_ja,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _unique_strings(values: Any) -> list[str]:
    out: list[str] = []
    for item in _list(values):
        text = str(item)
        if text and text not in out:
            out.append(text)
    return out


def _reason_label(reason: str) -> str:
    if reason in _REASON_LABELS_JA:
        return _REASON_LABELS_JA[reason]
    if reason.startswith("context_profile_missing:"):
        return "文脈別エビデンスプロファイル不足"
    return "参考度制限理由"


def _reason_severity(reason: str) -> str:
    if reason in _REASON_SEVERITY:
        return _REASON_SEVERITY[reason]
    if reason.startswith("context_profile_missing:"):
        return "warning"
    return "info"


def _signal_cap_explanations(primary_signal: Mapping[str, Any], warning_panel: Mapping[str, Any]) -> Tuple[Mapping[str, Any], ...]:
    reasons = _unique_strings(primary_signal.get("signal_strength_cap_reasons"))
    reasons.extend(reason for reason in _unique_strings(warning_panel.get("signal_strength_cap_reasons")) if reason not in reasons)
    unavailable = _unique_strings(primary_signal.get("prediction_unavailable_reasons"))
    unavailable.extend(reason for reason in _unique_strings(warning_panel.get("prediction_unavailable_reasons")) if reason not in unavailable)
    cards: list[Mapping[str, Any]] = []
    for reason in reasons:
        cards.append(
            {
                "card_version": "prediction_warroom_signal_cap_explanation.ps_q5a.v1",
                "reason_code": reason,
                "label_ja": _reason_label(reason),
                "severity": _reason_severity(reason),
                "estimated_signal_strength_percent": primary_signal.get("estimated_signal_strength_percent"),
                "estimated_reference_hit_rate_percent": primary_signal.get("estimated_reference_hit_rate_percent"),
                "signal_strength_band_label_ja": primary_signal.get("signal_strength_band_label_ja"),
                "explanation_ja": "この理由により、表示上の参考度は控えめに扱います。",
                "operator_action_kind": "observe_only",
                "read_only": True,
                "non_executing": True,
            }
        )
    for reason in unavailable:
        cards.append(
            {
                "card_version": "prediction_warroom_signal_cap_explanation.ps_q5a.v1",
                "reason_code": reason,
                "label_ja": _reason_label(reason),
                "severity": _reason_severity(reason),
                "estimated_signal_strength_percent": 0,
                "estimated_reference_hit_rate_percent": 0,
                "signal_strength_band_label_ja": "予測不能",
                "explanation_ja": "予測不能または根拠不足として扱います。",
                "operator_action_kind": "observe_only",
                "read_only": True,
                "non_executing": True,
            }
        )
    return tuple(cards)


def _source_quality_gate_cards(source_quality_panel: Mapping[str, Any]) -> Tuple[Mapping[str, Any], ...]:
    gate = _as_mapping(source_quality_panel.get("tier0_source_quality_gate"))
    if not gate:
        return ()
    state = str(gate.get("gate_state") or gate.get("state") or "unknown")
    severity = "ok" if state == "passed" else "blocker" if state == "blocked" else "warning"
    return (
        {
            "card_version": "prediction_warroom_source_quality_gate_card.ps_q5a.v1",
            "gate_id": "tier0_source_quality_gate",
            "gate_state": state,
            "gate_version": gate.get("gate_version") or gate.get("version"),
            "severity": severity,
            "label_ja": "Tier 0情報源品質ゲート",
            "explanation_ja": "予測表示に使う最低限の情報源品質・鮮度・信頼性を確認するゲートです。",
            "gate_summary": dict(gate),
            "operator_action_kind": "observe_only",
            "read_only": True,
            "non_executing": True,
        },
    )


def _missing_source_cards(display_packet: Mapping[str, Any], source_quality_panel: Mapping[str, Any]) -> Tuple[Mapping[str, Any], ...]:
    cards: list[Mapping[str, Any]] = []
    coverage = _as_mapping(source_quality_panel.get("source_artifact_coverage"))
    missing = _unique_strings(coverage.get("missing_observed_required_source_ids"))
    if not missing:
        missing = _unique_strings(coverage.get("missing_required_source_ids"))
    family_cards = [_as_mapping(item) for item in _list(display_packet.get("family_cards"))]
    for family_card in family_cards:
        family = str(family_card.get("family") or "unknown")
        for cap in [_as_mapping(item) for item in _list(family_card.get("context_profile_source_caps"))]:
            cap_missing = _unique_strings(cap.get("missing_minimum_required_sources"))
            for source_id in cap_missing:
                if source_id not in missing:
                    missing.append(source_id)
            if cap_missing:
                cards.append(
                    {
                        "card_version": "prediction_warroom_missing_source_card.ps_q5a.v1",
                        "scope": "family_context_profile",
                        "family": family,
                        "evidence_profile_id": cap.get("evidence_profile_id") or cap.get("profile_id"),
                        "missing_source_ids": cap_missing,
                        "cap_percent": cap.get("cap_percent"),
                        "severity": "warning",
                        "label_ja": "ファミリー別の必須情報源不足",
                        "explanation_ja": "この推論ファミリーでは、文脈上必要な情報源が不足しているため参考度が制限されます。",
                        "operator_action_kind": "observe_only",
                        "read_only": True,
                        "non_executing": True,
                    }
                )
    if missing:
        cards.insert(
            0,
            {
                "card_version": "prediction_warroom_missing_source_card.ps_q5a.v1",
                "scope": "display_packet_source_artifact_coverage",
                "missing_source_ids": missing,
                "source_artifact_input_coverage_state": source_quality_panel.get("source_artifact_input_coverage_state") or coverage.get("input_coverage_state"),
                "source_artifact_input_coverage_ratio": source_quality_panel.get("source_artifact_input_coverage_ratio") or coverage.get("input_coverage_ratio"),
                "severity": "warning",
                "label_ja": "入力情報源カバレッジ不足",
                "explanation_ja": "表示された予測は、必要な情報源の一部が不足している前提で読む必要があります。",
                "operator_action_kind": "observe_only",
                "read_only": True,
                "non_executing": True,
            },
        )
    return tuple(cards)


def _family_cap_cards(display_packet: Mapping[str, Any]) -> Tuple[Mapping[str, Any], ...]:
    cards: list[Mapping[str, Any]] = []
    for family_card in [_as_mapping(item) for item in _list(display_packet.get("family_cards"))]:
        reason = family_card.get("signal_strength_cap_reason")
        caps = [_as_mapping(item) for item in _list(family_card.get("context_profile_source_caps"))]
        if not reason and not caps:
            continue
        cards.append(
            {
                "card_version": "prediction_warroom_family_cap_card.ps_q5a.v1",
                "family": family_card.get("family"),
                "horizon_sec": family_card.get("horizon_sec"),
                "primary_label": family_card.get("primary_label"),
                "estimated_signal_strength_percent": family_card.get("estimated_signal_strength_percent"),
                "estimated_reference_hit_rate_percent": family_card.get("estimated_reference_hit_rate_percent"),
                "signal_strength_cap_reason": reason,
                "signal_strength_cap_label_ja": _reason_label(str(reason)) if reason else None,
                "source_quality_gate_state": family_card.get("source_quality_gate_state"),
                "context_profile_source_caps": [dict(item) for item in caps],
                "severity": _reason_severity(str(reason)) if reason else "warning",
                "explanation_ja": "このファミリーの出力は、情報源品質または文脈別情報源不足により参考度が制限されています。",
                "operator_action_kind": "observe_only",
                "read_only": True,
                "non_executing": True,
            }
        )
    return tuple(cards)


def _watch_points(display_packet: Mapping[str, Any], explanation_count: int) -> Tuple[Mapping[str, Any], ...]:
    warning_panel = _as_mapping(display_packet.get("warning_panel"))
    warnings = _unique_strings(warning_panel.get("warnings"))
    blockers = _unique_strings(warning_panel.get("blockers"))
    points: list[Mapping[str, Any]] = []
    if blockers:
        points.append(
            {
                "card_version": "prediction_warroom_quality_watch_point.ps_q5a.v1",
                "watch_kind": "blockers_present",
                "severity": "blocker",
                "label_ja": "ブロッカーあり",
                "items": blockers,
                "operator_action_kind": "observe_only",
                "read_only": True,
                "non_executing": True,
            }
        )
    if warnings:
        points.append(
            {
                "card_version": "prediction_warroom_quality_watch_point.ps_q5a.v1",
                "watch_kind": "warnings_present",
                "severity": "warning",
                "label_ja": "警告あり",
                "items": warnings,
                "operator_action_kind": "observe_only",
                "read_only": True,
                "non_executing": True,
            }
        )
    points.append(
        {
            "card_version": "prediction_warroom_quality_watch_point.ps_q5a.v1",
            "watch_kind": "explanation_card_count",
            "severity": "info",
            "label_ja": "説明カード数",
            "items": [str(explanation_count)],
            "operator_action_kind": "observe_only",
            "read_only": True,
            "non_executing": True,
        }
    )
    return tuple(points)


def build_prediction_warroom_source_quality_explanation_panel(display_packet: Mapping[str, Any] | Any) -> PredictionWarRoomSourceQualityExplanationPanel:
    """Build read-only WarRoom explanation cards for source quality, missing inputs, and signal caps."""
    packet = _as_mapping(display_packet)
    primary_signal = _as_mapping(packet.get("primary_signal_summary"))
    source_quality_panel = _as_mapping(packet.get("source_quality_panel"))
    warning_panel = _as_mapping(packet.get("warning_panel"))
    signal_cards = _signal_cap_explanations(primary_signal, warning_panel)
    gate_cards = _source_quality_gate_cards(source_quality_panel)
    missing_cards = _missing_source_cards(packet, source_quality_panel)
    family_cards = _family_cap_cards(packet)
    explanation_count = len(signal_cards) + len(gate_cards) + len(missing_cards) + len(family_cards)
    watch_points = _watch_points(packet, explanation_count)
    cap_reason_count = len(signal_cards)
    missing_source_count = sum(len(_unique_strings(card.get("missing_source_ids"))) for card in missing_cards)
    operator_summary_ja = (
        f"参考度制限理由 {cap_reason_count} 件、情報源不足 {missing_source_count} 件、"
        f"ファミリー制限 {len(family_cards)} 件を表示します。"
    )
    return PredictionWarRoomSourceQualityExplanationPanel(
        panel_version=PANEL_VERSION,
        prediction_run_id=str(packet.get("prediction_run_id")) if packet.get("prediction_run_id") else None,
        signal_cap_explanations=signal_cards,
        source_quality_gate_cards=gate_cards,
        missing_source_cards=missing_cards,
        family_cap_cards=family_cards,
        watch_points=watch_points,
        operator_summary_ja=operator_summary_ja,
    )
