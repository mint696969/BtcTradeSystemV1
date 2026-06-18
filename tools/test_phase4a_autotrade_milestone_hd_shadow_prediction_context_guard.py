# path: ./tools/test_phase4a_autotrade_milestone_hd_shadow_prediction_context_guard.py
# desc: Guard S141 Shadow prediction context contract remains standalone, read-only, persist=False-only, non-appending, non-mode-applying, non-grant-executing, and broker-free.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus
from btcts.autotrade.shadow_prediction_context import (
    AutoTradeShadowPredictionContext,
    build_autotrade_shadow_prediction_context,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/autotrade/shadow_prediction_context.py"
INIT_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/__init__.py"
LIVE_SHADOW = REPO_ROOT / "btcts_next/src/btcts/autotrade/live_shadow.py"
FORBIDDEN_IMPORT_PREFIXES = (
    "btcts.autotrade.live_shadow",
    "btcts.autotrade.ledger",
    "btcts.autotrade.execution",
    "btcts.autotrade.strategy",
    "btcts.autotrade.risk",
    "btcts.autotrade.runtime_paths",
    "btcts.collector_vnext",
    "requests",
    "httpx",
    "ccxt",
    "pybitflyer",
    "websocket",
    "streamlit",
)
FORBIDDEN_TOKENS = (
    "append_decision_jsonl",
    "run_shadow_decision_from_snapshot",
    "run_latest_market_state_shadow_decision",
    "build_action_candidate",
    "build_shadow_decision_record",
    "evaluate_risk_gate",
    "decision_ledger_path",
    "default_shadow_decision_ledger_path",
    "persist=True",
    "persist: bool = True",
    "validate_and_append_command",
    "submit_mode_change_command_request",
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
    "would_change_shadow_candidate: bool = True",
    "would_append_shadow_decision: bool = True",
    "would_apply_mode: bool = True",
    "would_execute_prearmed_grant: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
)
EXPECTED_FALSE_FLAGS = (
    "would_change_shadow_candidate",
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


def _status(*, state="ok", blockers=(), warnings=(), weak_families=()) -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="status_s141_unit",
        generated_at="2026-06-18T00:00:00Z",
        status_state=state,
        preview_id="preview_s141_unit",
        readiness_id="readiness_s141_unit",
        readiness_state="ready" if state == "ok" else state,
        intended_mode="ARMED_DRY_RUN",
        preview_action="WATCH_LONG",
        preview_bias="long",
        preview_confidence="medium",
        validation_state="ok",
        average_score=0.88,
        label_hit_rate=0.81,
        weak_families=tuple(weak_families),
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _all_false(payload: dict[str, object]) -> bool:
    return all(payload.get(name) is False for name in EXPECTED_FALSE_FLAGS)


def main() -> int:
    failures: list[str] = []
    if not MODULE.exists():
        failures.append("missing shadow_prediction_context module")
    text = MODULE.read_text(encoding="utf-8") if MODULE.exists() else ""
    try:
        compile(text, str(MODULE), "exec")
    except Exception as exc:
        failures.append(f"compile failed: {MODULE.relative_to(REPO_ROOT)}: {exc}")
    if MODULE.exists():
        imports = _imports_from(MODULE)
        for prefix in FORBIDDEN_IMPORT_PREFIXES:
            if any(item == prefix or item.startswith(prefix + ".") for item in imports):
                failures.append(f"forbidden import in {MODULE.relative_to(REPO_ROOT)}: {prefix}")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"forbidden token in {MODULE.relative_to(REPO_ROOT)}: {token}")

    now = datetime(2026, 6, 18, 0, 5, 0, tzinfo=timezone.utc)
    ok_context = build_autotrade_shadow_prediction_context(_status(), now=now)
    review_context = build_autotrade_shadow_prediction_context(_status(state="review", warnings=("review_warning",), weak_families=("trend_bias",)), now=now)
    blocked_context = build_autotrade_shadow_prediction_context(_status(state="blocked", blockers=("blocked_by_status",)), now=now)
    missing_context = build_autotrade_shadow_prediction_context(None, now=now)
    dict_context = build_autotrade_shadow_prediction_context(_status().to_dict(), now=now)

    ok_payload = ok_context.to_dict()
    review_payload = review_context.to_dict()
    blocked_payload = blocked_context.to_dict()
    missing_payload = missing_context.to_dict()
    dict_payload = dict_context.to_dict()
    encoded = json.loads(json.dumps(ok_payload, ensure_ascii=False, sort_keys=True))

    live_shadow_text = LIVE_SHADOW.read_text(encoding="utf-8") if LIVE_SHADOW.exists() else ""
    checks = {
        "module_present_and_exported": "AutoTradeShadowPredictionContext" in text and "build_autotrade_shadow_prediction_context" in text and "shadow_prediction_context" in INIT_FILE.read_text(encoding="utf-8"),
        "exports_available": AutoTradeShadowPredictionContext is not None and build_autotrade_shadow_prediction_context is not None,
        "ok_context_visible": ok_context.context_state == "ok" and ok_context.usable_as_context is True and ok_payload["preview_action"] == "WATCH_LONG",
        "review_context_visible": review_context.context_state == "review" and review_context.warnings == ("review_warning",) and review_context.weak_families == ("trend_bias",),
        "blocked_context_visible": blocked_context.context_state == "blocked" and "blocked_by_status" in blocked_context.blockers and blocked_context.usable_as_context is False,
        "missing_status_blocks_context": missing_context.context_state == "blocked" and missing_context.blockers == ("prediction_status_missing",),
        "mapping_input_supported": dict_context.context_state == "ok" and dict_payload["source_status_id"] == "status_s141_unit",
        "json_safe": encoded["logic_version"] == "autotrade_shadow_prediction_context.s141.v1" and encoded["optional_context_only"] is True,
        "persist_false_only_visible": ok_payload["persist_false_only"] is True and ok_payload["optional_context_only"] is True,
        "execution_flags_false_ok": _all_false(ok_payload),
        "execution_flags_false_review": _all_false(review_payload),
        "execution_flags_false_blocked": _all_false(blocked_payload),
        "execution_flags_false_missing": _all_false(missing_payload),
        "read_only_non_executing": ok_payload["read_only"] is True and ok_payload["non_executing"] is True,
        "live_shadow_existing_append_path_only": "append_decision_jsonl" in live_shadow_text and "run_shadow_decision_from_snapshot" in live_shadow_text,
        "new_module_does_not_import_live_shadow": "btcts.autotrade.live_shadow" not in text,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/autotrade/__init__.py",
        "btcts_next/src/btcts/autotrade/shadow_prediction_context.py",
        "tools/test_phase4a_autotrade_milestone_hd_shadow_prediction_context_guard.py",
        "tools/test_phase4a_autotrade_milestone_hd_shadow_prediction_context_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HD: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hd_shadow_prediction_context_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "ok_context": ok_payload,
            "review_context": review_payload,
            "blocked_context": blocked_payload,
            "missing_context": missing_payload,
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_shadow_prediction_context_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
