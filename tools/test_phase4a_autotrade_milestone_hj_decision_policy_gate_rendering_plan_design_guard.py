# path: ./tools/test_phase4a_autotrade_milestone_hj_decision_policy_gate_rendering_plan_design_guard.py
# desc: Guard S147 rendering plan remains design/status-only with no Streamlit implementation, commands, runtime wiring, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.apps.operator_ui.hub.decision_policy_gate_visibility import (
    build_decision_policy_gate_dashboard_registry_visibility_packet,
)
from btcts.apps.operator_ui.components.autotrade_decision_ledger_policy_gate_display import (
    AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/architecture/OPERATOR_UI_DECISION_POLICY_GATE_READ_ONLY_RENDERING_PLAN_2026-06-18.md"
DISPLAY_PACKET = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_decision_ledger_policy_gate_display.py"
VISIBILITY_PACKET = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility.py"
FORBIDDEN_CODE_TARGETS = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_decision_ledger_policy_gate_display.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility.py",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "streamlit",
    "btcts.autotrade.live_shadow",
    "btcts.autotrade.ledger",
    "btcts.autotrade.execution",
    "btcts.autotrade.runtime_paths",
    "btcts.collector_vnext",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
)
FORBIDDEN_DOC_PHRASES = (
    "S147 permits",
    "append_decision_jsonl usage is allowed",
    "decision append is authorized",
    "persist=True authorized",
    "broker execution authorized",
    "command buttons are allowed",
)
REQUIRED_DOC_PHRASES = (
    "design-only / non-rendering / non-executing",
    "DECISION APPEND NOT AUTHORIZED",
    "PERSIST TRUE NOT AUTHORIZED",
    "LIVE SHADOW CHANGE NOT AUTHORIZED",
    "NO COMMAND BUTTONS",
    "S147 does not permit",
    "Streamlit rendering implementation",
    "append_decision_jsonl usage",
    "Shadow decision append",
    "persist=True path",
    "live_shadow.py behavior modification",
    "broker execution",
)
EXPECTED_FALSE_FLAGS = (
    "decision_append_allowed",
    "decision_ledger_integration_allowed",
    "live_shadow_behavior_change_allowed",
    "persist_true_allowed",
    "would_append_shadow_decision",
    "would_apply_mode",
    "would_execute_prearmed_grant",
    "would_write_runtime_artifact",
    "would_write_preview_status_artifact",
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


def _all_false(payload: dict[str, object]) -> bool:
    return all(payload.get(name) is False for name in EXPECTED_FALSE_FLAGS)


def main() -> int:
    failures: list[str] = []
    if not DOC.exists():
        failures.append("missing S147 rendering plan document")
    doc_text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase not in doc_text:
            failures.append(f"required phrase missing from S147 doc: {phrase}")
    for phrase in FORBIDDEN_DOC_PHRASES:
        if phrase in doc_text:
            failures.append(f"forbidden phrase present in S147 doc: {phrase}")

    for target in FORBIDDEN_CODE_TARGETS:
        text = target.read_text(encoding="utf-8")
        try:
            compile(text, str(target), "exec")
        except Exception as exc:
            failures.append(f"compile failed: {target.relative_to(REPO_ROOT)}: {exc}")
        imports = _imports_from(target)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            if any(item == prefix or item.startswith(prefix + ".") for item in imports):
                failures.append(f"forbidden import in {target.relative_to(REPO_ROOT)}: {prefix}")

    visibility_packet = build_decision_policy_gate_dashboard_registry_visibility_packet()
    checks = {
        "doc_present": DOC.exists(),
        "doc_is_design_only": "This document does not implement rendering" in doc_text and "does not modify runtime code" in doc_text,
        "future_fields_defined": "Safe display fields from the display packet" in doc_text and "Safe display fields from registry visibility packet" in doc_text,
        "section_order_defined": "Proposed section order" in doc_text and "Required approvals" in doc_text and "Non-permissions" in doc_text,
        "explicit_non_permissions_defined": "S147 does not permit" in doc_text and "UI command buttons" in doc_text and "runtime wiring" in doc_text,
        "display_packet_still_non_rendering": AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT["not_ui_rendering"] is True and AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT["no_command_buttons"] is True,
        "visibility_packet_flags_false": _all_false(visibility_packet),
        "visibility_packet_still_visible": visibility_packet["source_entry_available"] is True and visibility_packet["health_page_visible"] is True,
        "json_safe": json.loads(json.dumps({"doc": DOC.name, "visible_pages": visibility_packet["visible_pages"]}, ensure_ascii=False))["doc"] == DOC.name,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "docs/architecture/OPERATOR_UI_DECISION_POLICY_GATE_READ_ONLY_RENDERING_PLAN_2026-06-18.md",
        "tools/test_phase4a_autotrade_milestone_hj_decision_policy_gate_rendering_plan_design_guard.py",
        "tools/test_phase4a_autotrade_milestone_hj_decision_policy_gate_rendering_plan_design_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HJ: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hj_decision_policy_gate_rendering_plan_design_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "doc": str(DOC.relative_to(REPO_ROOT)),
            "visible_pages": visibility_packet.get("visible_pages"),
            "health_page_visible": visibility_packet.get("health_page_visible"),
            "future_widget_page_visible": visibility_packet.get("future_widget_page_visible"),
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_rendering_plan_design_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
