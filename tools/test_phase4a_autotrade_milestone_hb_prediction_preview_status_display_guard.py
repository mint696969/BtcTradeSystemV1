# path: ./tools/test_phase4a_autotrade_milestone_hb_prediction_preview_status_display_guard.py
# desc: Guard S139 Operator/UI prediction preview status display packet remains read-only, display-only, layout-free, non-rendering, non-writing, and broker-free.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.autotrade_prediction_preview_status_display import (
    AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT,
    build_autotrade_prediction_preview_status_display_packet,
    prediction_preview_status_compact_line,
    prediction_preview_status_snapshot_lines,
)
from btcts.autotrade.prediction_preview_status import build_autotrade_prediction_preview_status
from btcts.prediction.prearmed_readiness import PredictionPreArmedReadinessSnapshot
from btcts.prediction.shadow_adapter import AutoTradeShadowSignalPreview

REPO_ROOT = Path(__file__).resolve().parents[1]
DISPLAY_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_preview_status_display.py"
AUTOTRADE_STATUS_MODULE = REPO_ROOT / "btcts_next/src/btcts/autotrade/prediction_preview_status.py"
CHECK_FILES = (
    DISPLAY_MODULE,
)
FORBIDDEN_IMPORT_PREFIXES = (
    "streamlit",
    "btcts.apps.operator_ui.views",
    "btcts.autotrade.live_shadow",
    "btcts.autotrade.ledger",
    "btcts.autotrade.execution",
    "btcts.collector_vnext",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
)
FORBIDDEN_TOKENS = (
    "st.button",
    "st.checkbox",
    "streamlit",
    "append_decision_jsonl",
    "run_shadow_decision_from_snapshot",
    "run_latest_market_state_shadow_decision",
    "build_action_candidate",
    "submit_mode_change_command_request",
    "validate_and_append_command",
    "append_command",
    "append_jsonl(",
    "write_text(",
    ".write(",
    "open(",
    "place_order(",
    "send_order(",
    "create_order(",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    '"would_append_shadow_decision": True',
    '"would_apply_mode": True',
    '"would_execute_prearmed_grant": True',
    '"would_write_runtime_artifact": True',
    '"would_send_to_broker": True',
    '"broker_execution_requested": True',
    '"mode_apply_requested": True',
    '"command_ledger_append_requested": True',
    '"approval_append_requested": True',
)
EXPECTED_FALSE_FLAGS = (
    "would_append_shadow_decision",
    "would_apply_mode",
    "would_execute_prearmed_grant",
    "would_write_runtime_artifact",
    "would_send_to_broker",
    "broker_execution_requested",
    "mode_apply_requested",
    "command_ledger_append_requested",
    "approval_append_requested",
)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def _preview(*, blockers=(), warnings=()) -> AutoTradeShadowSignalPreview:
    return AutoTradeShadowSignalPreview(
        preview_id="preview_s139_unit",
        generated_at="2026-06-18T00:00:00Z",
        intended_mode="SHADOW",
        recommended_action="WATCH_SHORT",
        action_bias="short",
        confidence="high",
        reason_codes=("unit_preview",),
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _readiness(*, state="ready", blockers=(), warnings=(), weak_families=()) -> PredictionPreArmedReadinessSnapshot:
    return PredictionPreArmedReadinessSnapshot(
        readiness_id="readiness_s139_unit",
        generated_at="2026-06-18T00:00:00Z",
        readiness_state=state,
        validation_id="validation_s139_unit",
        preview_id="preview_s139_unit",
        calibration_report_id="calibration_s139_unit",
        intended_mode="ARMED_DRY_RUN",
        validation_state="ok",
        preview_action="WATCH_SHORT",
        preview_bias="short",
        calibration_average_score=0.91,
        label_hit_rate=0.84,
        weak_families=tuple(weak_families),
        readiness_checks={"validation_present": True, "preview_present": True},
        metrics={"average_score": 0.91, "label_hit_rate": 0.84},
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _all_false(packet: dict[str, object]) -> bool:
    return all(packet.get(name) is False for name in EXPECTED_FALSE_FLAGS)


def main() -> int:
    failures: list[str] = []
    for path in CHECK_FILES:
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        try:
            compile(text, str(path), "exec")
        except Exception as exc:
            failures.append(f"compile failed: {path.relative_to(REPO_ROOT)}: {exc}")
        imports = _imports_from(path)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            if any(item == prefix or item.startswith(prefix + ".") for item in imports):
                failures.append(f"forbidden import in {path.relative_to(REPO_ROOT)}: {prefix}")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"forbidden token in {path.relative_to(REPO_ROOT)}: {token}")

    now = datetime(2026, 6, 18, 0, 5, 0, tzinfo=timezone.utc)
    ok_status = build_autotrade_prediction_preview_status(_preview(), _readiness(), now=now)
    review_status = build_autotrade_prediction_preview_status(_preview(warnings=("preview_warning",)), _readiness(state="review", warnings=("readiness_review",), weak_families=("trend_bias",)), now=now)
    blocked_status = build_autotrade_prediction_preview_status(_preview(blockers=("preview_blocker",)), _readiness(state="blocked", blockers=("readiness_blocker",)), now=now)
    missing_status = build_autotrade_prediction_preview_status(None, None, now=now)

    ok_packet = build_autotrade_prediction_preview_status_display_packet(ok_status)
    review_packet = build_autotrade_prediction_preview_status_display_packet(review_status.to_dict())
    blocked_packet = build_autotrade_prediction_preview_status_display_packet(blocked_status)
    missing_packet = build_autotrade_prediction_preview_status_display_packet(missing_status)
    unavailable_packet = build_autotrade_prediction_preview_status_display_packet(None)
    encoded = json.loads(json.dumps(ok_packet, ensure_ascii=False, sort_keys=True))

    checks = {
        "contract_shape": AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT["section_type"] == "autotrade_prediction_preview_status_display_packet" and AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT["read_only_contract"] is True,
        "ok_display_packet_visible": ok_packet["display_state"] == "ok" and ok_packet["preview_action"] == "WATCH_SHORT" and ok_packet["preview_bias"] == "short" and ok_packet["preview_confidence"] == "high",
        "review_display_packet_visible": review_packet["display_state"] == "review" and review_packet["warnings"] == ("preview_warning", "readiness_review") and review_packet["weak_families"] == ("trend_bias",),
        "blocked_display_packet_visible": blocked_packet["display_state"] == "blocked" and "prediction_readiness_blocked" in blocked_packet["blockers"],
        "missing_display_packet_visible": missing_packet["display_state"] == "blocked" and {"prediction_preview_missing", "prediction_readiness_missing"}.issubset(set(missing_packet["blockers"])),
        "none_display_packet_unavailable": unavailable_packet["display_state"] == "unavailable" and unavailable_packet["status_available"] is False,
        "compact_line_display_only": prediction_preview_status_compact_line(ok_status).endswith("display_only") and "WATCH_SHORT" in prediction_preview_status_compact_line(ok_status),
        "snapshot_lines_include_safety_flags": "no_command_buttons=true" in prediction_preview_status_snapshot_lines(ok_status) and "not_runtime_wiring=true" in prediction_preview_status_snapshot_lines(ok_status),
        "json_safe": encoded["section_type"] == "autotrade_prediction_preview_status_display_packet" and encoded["snapshot_lines"],
        "read_only_display_flags": ok_packet["read_only_contract"] is True and ok_packet["non_executing"] is True and ok_packet["widget_reusable"] is True and ok_packet["layout_decision_free"] is True and ok_packet["not_runtime_wiring"] is True and ok_packet["not_ui_rendering"] is True and ok_packet["no_command_buttons"] is True,
        "execution_flags_false_ok": _all_false(ok_packet),
        "execution_flags_false_review": _all_false(review_packet),
        "execution_flags_false_blocked": _all_false(blocked_packet),
        "execution_flags_false_missing": _all_false(missing_packet),
        "autotrade_status_contract_still_present": AUTOTRADE_STATUS_MODULE.exists() and "AutoTradePredictionPreviewStatus" in AUTOTRADE_STATUS_MODULE.read_text(encoding="utf-8"),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_preview_status_display.py",
        "tools/test_phase4a_autotrade_milestone_hb_prediction_preview_status_display_guard.py",
        "tools/test_phase4a_autotrade_milestone_hb_prediction_preview_status_display_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HB: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hb_prediction_preview_status_display_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "ok_packet": ok_packet,
            "review_packet": review_packet,
            "blocked_packet": blocked_packet,
            "unavailable_packet": unavailable_packet,
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_prediction_preview_status_display_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
