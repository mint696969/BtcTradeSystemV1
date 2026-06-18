# path: ./tools/test_phase4a_autotrade_milestone_he_prediction_preview_artifact_preflight_guard.py
# desc: Guard S142 prediction preview/status artifact preflight remains dry-run/preflight-only with no writes, no Shadow decision append, no mode apply, no grant execution, and no broker behavior.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.autotrade.prediction_preview_artifact_preflight import (
    AutoTradePredictionPreviewArtifactPreflight,
    build_prediction_preview_artifact_preflight,
)
from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus
from btcts.autotrade.shadow_prediction_context import build_autotrade_shadow_prediction_context

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/autotrade/prediction_preview_artifact_preflight.py"
INIT_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/__init__.py"
LIVE_SHADOW = REPO_ROOT / "btcts_next/src/btcts/autotrade/live_shadow.py"
FORBIDDEN_IMPORT_PREFIXES = (
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
    "streamlit",
)
FORBIDDEN_TOKENS = (
    "append_decision_jsonl",
    "run_shadow_decision_from_snapshot",
    "run_latest_market_state_shadow_decision",
    "build_action_candidate",
    "build_shadow_decision_record",
    "decision_ledger_path",
    "default_shadow_decision_ledger_path",
    "Path(",
    "mkdir(",
    "write_text(",
    ".write(",
    "open(",
    "append_jsonl(",
    "json.dump",
    "json.dumps(",
    "persist=True",
    "persist: bool = True",
    "validate_and_append_command",
    "submit_mode_change_command_request",
    "place_order(",
    "send_order(",
    "create_order(",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "artifact_write_allowed: bool = True",
    "artifact_write_requested: bool = True",
    "would_write_preview_status_artifact: bool = True",
    "would_write_runtime_artifact: bool = True",
    "would_append_shadow_decision: bool = True",
    "would_apply_mode: bool = True",
    "would_execute_prearmed_grant: bool = True",
    "would_send_to_broker: bool = True",
    "broker_execution_requested: bool = True",
    "mode_apply_requested: bool = True",
    "command_ledger_append_requested: bool = True",
    "approval_append_requested: bool = True",
)
EXPECTED_FALSE_FLAGS = (
    "artifact_write_allowed",
    "artifact_write_requested",
    "would_write_preview_status_artifact",
    "would_write_runtime_artifact",
    "would_append_shadow_decision",
    "would_apply_mode",
    "would_execute_prearmed_grant",
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


def _status(*, state="ok", blockers=(), warnings=()) -> AutoTradePredictionPreviewStatus:
    return AutoTradePredictionPreviewStatus(
        status_id="status_s142_unit",
        generated_at="2026-06-18T00:00:00Z",
        status_state=state,
        preview_id="preview_s142_unit",
        readiness_id="readiness_s142_unit",
        readiness_state="ready" if state == "ok" else state,
        intended_mode="ARMED_DRY_RUN",
        preview_action="WATCH_LONG",
        preview_bias="long",
        preview_confidence="medium",
        validation_state="ok",
        average_score=0.89,
        label_hit_rate=0.82,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _all_false(payload: dict[str, object]) -> bool:
    return all(payload.get(name) is False for name in EXPECTED_FALSE_FLAGS)


def main() -> int:
    failures: list[str] = []
    if not MODULE.exists():
        failures.append("missing prediction_preview_artifact_preflight module")
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
    ok_status = _status()
    ok_context = build_autotrade_shadow_prediction_context(ok_status, now=now)
    ready = build_prediction_preview_artifact_preflight(ok_status, ok_context, artifact_path="artifacts/prediction_preview_status_s142.json", now=now)
    review = build_prediction_preview_artifact_preflight(_status(state="review", warnings=("status_review",)), ok_context, artifact_path="artifacts/review.json", now=now)
    blocked = build_prediction_preview_artifact_preflight(_status(state="blocked", blockers=("status_blocked",)), ok_context, artifact_path="artifacts/blocked.json", now=now)
    missing_path = build_prediction_preview_artifact_preflight(ok_status, ok_context, now=now)
    missing_status = build_prediction_preview_artifact_preflight(None, None, artifact_path="artifacts/missing.json", now=now)
    dict_input = build_prediction_preview_artifact_preflight(ok_status.to_dict(), ok_context.to_dict(), artifact_path="artifacts/dict.json", now=now)

    ready_payload = ready.to_dict()
    review_payload = review.to_dict()
    blocked_payload = blocked.to_dict()
    missing_path_payload = missing_path.to_dict()
    missing_status_payload = missing_status.to_dict()
    dict_payload = dict_input.to_dict()
    encoded = json.loads(json.dumps(ready_payload, ensure_ascii=False, sort_keys=True))

    live_shadow_text = LIVE_SHADOW.read_text(encoding="utf-8") if LIVE_SHADOW.exists() else ""
    checks = {
        "module_present_and_exported": "AutoTradePredictionPreviewArtifactPreflight" in text and "build_prediction_preview_artifact_preflight" in text and "prediction_preview_artifact_preflight" in INIT_FILE.read_text(encoding="utf-8"),
        "exports_available": AutoTradePredictionPreviewArtifactPreflight is not None and build_prediction_preview_artifact_preflight is not None,
        "ready_preflight_visible": ready.preflight_state == "ready" and ready.ready_for_future_write is True and ready.artifact_path == "artifacts/prediction_preview_status_s142.json",
        "review_preflight_visible": review.preflight_state == "review" and "status_review" in review.warnings,
        "blocked_preflight_visible": blocked.preflight_state == "blocked" and "prediction_status_blocked" in blocked.blockers,
        "missing_path_blocks": missing_path.preflight_state == "blocked" and "artifact_path_missing" in missing_path.blockers,
        "missing_status_blocks": missing_status.preflight_state == "blocked" and "prediction_status_missing" in missing_status.blockers,
        "mapping_input_supported": dict_input.preflight_state == "ready" and dict_payload["source_status_id"] == "status_s142_unit",
        "json_safe": encoded["logic_version"] == "autotrade_prediction_preview_artifact_preflight.s142.v1" and encoded["ready_for_future_write"] is True,
        "preflight_only_visible": ready_payload["preflight_only"] is True and ready_payload["artifact_write_preflight_only"] is True,
        "execution_flags_false_ready": _all_false(ready_payload),
        "execution_flags_false_review": _all_false(review_payload),
        "execution_flags_false_blocked": _all_false(blocked_payload),
        "execution_flags_false_missing_path": _all_false(missing_path_payload),
        "execution_flags_false_missing_status": _all_false(missing_status_payload),
        "read_only_non_executing": ready_payload["read_only"] is True and ready_payload["non_executing"] is True,
        "live_shadow_existing_append_path_only": "append_decision_jsonl" in live_shadow_text and "run_shadow_decision_from_snapshot" in live_shadow_text,
        "new_module_does_not_import_live_shadow": "btcts.autotrade.live_shadow" not in text,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/autotrade/__init__.py",
        "btcts_next/src/btcts/autotrade/prediction_preview_artifact_preflight.py",
        "tools/test_phase4a_autotrade_milestone_he_prediction_preview_artifact_preflight_guard.py",
        "tools/test_phase4a_autotrade_milestone_he_prediction_preview_artifact_preflight_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HE: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_he_prediction_preview_artifact_preflight_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "ready_preflight": ready_payload,
            "review_preflight": review_payload,
            "blocked_preflight": blocked_payload,
            "missing_path_preflight": missing_path_payload,
            "missing_status_preflight": missing_status_payload,
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_prediction_preview_artifact_preflight_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
