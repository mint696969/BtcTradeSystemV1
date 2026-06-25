# path: ./tools/check_prediction_source_quality_gaps_ps_q19k.py
# desc: PS-Q19K read-only source-quality gap audit for latest prediction artifact. Summarizes warnings and missing evidence sources without writing artifacts or changing runtime behavior.

from __future__ import annotations

import argparse
from collections import Counter
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT  # noqa: E402
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH  # noqa: E402

PS_Q19K_GAP_AUDIT_VERSION = "prediction_warroom.ps_q19k_source_quality_gap_audit.v1"


def _artifact_path(root: str) -> Path:
    return Path(str(root).rstrip("\\/")) / LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH


def _walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, Mapping):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _token_counter_values(counter: Counter[str], limit: int = 20) -> list[dict[str, Any]]:
    return [{"token": token, "count": count} for token, count in counter.most_common(limit)]


def build_prediction_source_quality_gap_audit_packet(*, payload: Mapping[str, Any], source_path: str = "") -> dict[str, Any]:
    warning_counter: Counter[str] = Counter()
    missing_source_counter: Counter[str] = Counter()
    cap_reason_counter: Counter[str] = Counter()
    family_warning_counter: Counter[str] = Counter()
    driver_counter: Counter[str] = Counter()
    family_counter: Counter[str] = Counter()
    label_counter: Counter[str] = Counter()
    record_count = 0

    for node in _walk(payload):
        if not isinstance(node, Mapping):
            continue
        family = str(node.get("family") or "")
        label = str(node.get("primary_label") or node.get("label") or "")
        if "horizon_sec" in node and family:
            record_count += 1
            family_counter[family] += 1
            if label:
                label_counter[label] += 1
        for warning in node.get("warnings") or []:
            text = str(warning)
            warning_counter[text] += 1
            if family:
                family_warning_counter[f"{family}:{text}"] += 1
        for reason in node.get("signal_strength_cap_reasons") or []:
            cap_reason_counter[str(reason)] += 1
        for missing in node.get("missing_minimum_required_sources") or []:
            missing_source_counter[str(missing)] += 1
        for driver in node.get("drivers") or []:
            driver_counter[str(driver)] += 1

    blocker_like = [
        key
        for key in warning_counter
        if key.startswith("tier0_source_quality") or "minimum_sources_missing" in key or "source_quality" in key
    ]
    packet = {
        "ok": True,
        "ps_q19k_gap_audit_version": PS_Q19K_GAP_AUDIT_VERSION,
        "source_path": source_path,
        "prediction_record_like_count": record_count,
        "warning_kind_count": len(warning_counter),
        "missing_source_kind_count": len(missing_source_counter),
        "cap_reason_kind_count": len(cap_reason_counter),
        "family_kind_count": len(family_counter),
        "label_kind_count": len(label_counter),
        "top_warnings": _token_counter_values(warning_counter),
        "top_missing_minimum_required_sources": _token_counter_values(missing_source_counter),
        "top_signal_strength_cap_reasons": _token_counter_values(cap_reason_counter),
        "top_family_warnings": _token_counter_values(family_warning_counter),
        "top_drivers": _token_counter_values(driver_counter),
        "top_families": _token_counter_values(family_counter),
        "top_labels": _token_counter_values(label_counter),
        "priority_gap_summary": {
            "tier0_source_quality_warnings_present": any(key.startswith("tier0_source_quality") for key in warning_counter),
            "context_evidence_profile_minimum_sources_missing_present": any("minimum_sources_missing" in key for key in warning_counter) or bool(missing_source_counter),
            "missing_bitflyer_board_summary": missing_source_counter.get("bitflyer_board_summary", 0),
            "missing_bitflyer_trades": missing_source_counter.get("bitflyer_trades", 0),
            "missing_bitflyer_spot_reference": missing_source_counter.get("bitflyer_spot_reference", 0),
            "blocker_like_warning_kinds": blocker_like[:20],
        },
        "next_recommended_slice": "PS-Q19L_SOURCE_QUALITY_INPUT_REPAIR",
        "read_only_gap_audit": True,
        "runtime_artifact_write_performed_by_gap_audit": False,
        "status_artifact_write_performed_by_gap_audit": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "ledger_append_allowed": False,
        "would_send_to_broker": False,
    }
    return packet


def load_and_build_gap_audit_packet(*, root: str = DEFAULT_HOT_LATEST_ROOT_HINT) -> dict[str, Any]:
    path = _artifact_path(root)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "ps_q19k_gap_audit_version": PS_Q19K_GAP_AUDIT_VERSION,
            "source_path": str(path),
            "blocked_reasons": ["latest_prediction_artifact_unreadable:" + exc.__class__.__name__],
            "read_only_gap_audit": True,
            "runtime_artifact_write_performed_by_gap_audit": False,
            "status_artifact_write_performed_by_gap_audit": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "would_send_to_broker": False,
        }
    if not isinstance(payload, Mapping):
        payload = {}
    return build_prediction_source_quality_gap_audit_packet(payload=payload, source_path=str(path))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19K source-quality gap audit for latest prediction artifact")
    parser.add_argument("--root", default=DEFAULT_HOT_LATEST_ROOT_HINT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    packet = load_and_build_gap_audit_packet(root=str(args.root))
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
