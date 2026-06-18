# path: ./tools/test_phase4a_autotrade_milestone_ha_prediction_preview_status_guard.py
# desc: Guard S138 AutoTrade prediction preview status remains read-only, serializable, non-writing, non-appending, non-mode-applying, non-grant-executing, and broker-free.

from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.autotrade.prediction_preview_status import (
    AutoTradePredictionPreviewStatus,
    build_autotrade_prediction_preview_status,
)
from btcts.prediction.prearmed_readiness import PredictionPreArmedReadinessSnapshot
from btcts.prediction.shadow_adapter import AutoTradeShadowSignalPreview

REPO_ROOT = Path(__file__).resolve().parents[1]
AUTOTRADE_ROOT = REPO_ROOT / "btcts_next/src/btcts/autotrade"
CHECK_FILES = (
    AUTOTRADE_ROOT / "prediction_preview_status.py",
    AUTOTRADE_ROOT / "__init__.py",
)
LIVE_SHADOW = AUTOTRADE_ROOT / "live_shadow.py"
FORBIDDEN_IMPORT_PREFIXES = (
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
    "append_decision_jsonl",
    "run_shadow_decision_from_snapshot",
    "run_latest_market_state_shadow_decision",
    "build_action_candidate",
    "btcts.autotrade.live_shadow",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "connect_and_stream",
    "write_canonical(",
    "write_raw(",
    "append_jsonl(",
    "place_order(",
    "send_order(",
    "create_order(",
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


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def _preview(*, blockers=(), warnings=(), recommended_action="WATCH_LONG", action_bias="long", confidence="medium") -> AutoTradeShadowSignalPreview:
    return AutoTradeShadowSignalPreview(
        preview_id="preview_s138_unit",
        generated_at="2026-06-18T00:00:00Z",
        intended_mode="SHADOW",
        recommended_action=recommended_action,
        action_bias=action_bias,
        confidence=confidence,
        reason_codes=("unit_preview",),
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _readiness(*, state="ready", blockers=(), warnings=(), weak_families=()) -> PredictionPreArmedReadinessSnapshot:
    return PredictionPreArmedReadinessSnapshot(
        readiness_id="readiness_s138_unit",
        generated_at="2026-06-18T00:00:00Z",
        readiness_state=state,
        validation_id="validation_s138_unit",
        preview_id="preview_s138_unit",
        calibration_report_id="calibration_s138_unit",
        intended_mode="ARMED_DRY_RUN",
        validation_state="ok",
        preview_action="WATCH_LONG",
        preview_bias="long",
        calibration_average_score=0.82,
        label_hit_rate=0.76,
        weak_families=tuple(weak_families),
        readiness_checks={"validation_present": True, "preview_present": True},
        metrics={"average_score": 0.82, "label_hit_rate": 0.76},
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _assert_false_execution_flags(data: dict[str, object]) -> bool:
    expected_false = (
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
    return all(data.get(name) is False for name in expected_false) and data.get("read_only") is True and data.get("non_executing") is True


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
        if path.name == "prediction_preview_status.py":
            for token in FORBIDDEN_TOKENS:
                if token in text:
                    failures.append(f"forbidden token in {path.relative_to(REPO_ROOT)}: {token}")

    now = datetime(2026, 6, 18, 0, 5, 0, tzinfo=timezone.utc)
    ok_status = build_autotrade_prediction_preview_status(_preview(), _readiness(), now=now)
    review_status = build_autotrade_prediction_preview_status(_preview(warnings=("preview_warning",)), _readiness(state="review", warnings=("readiness_review",), weak_families=("trend_bias",)), now=now)
    blocked_status = build_autotrade_prediction_preview_status(_preview(blockers=("preview_blocker",)), _readiness(state="blocked", blockers=("readiness_blocker",)), now=now)
    missing_preview_status = build_autotrade_prediction_preview_status(None, _readiness(), now=now)
    missing_readiness_status = build_autotrade_prediction_preview_status(_preview(), None, now=now)
    missing_both_status = build_autotrade_prediction_preview_status(None, None, now=now)

    ok_payload = ok_status.to_dict()
    review_payload = review_status.to_dict()
    blocked_payload = blocked_status.to_dict()
    missing_preview_payload = missing_preview_status.to_dict()
    missing_readiness_payload = missing_readiness_status.to_dict()
    missing_both_payload = missing_both_status.to_dict()
    encoded = json.loads(json.dumps(ok_payload, ensure_ascii=False, sort_keys=True))

    checks = {
        "exports_available": AutoTradePredictionPreviewStatus is not None and build_autotrade_prediction_preview_status is not None,
        "ok_path_visible": ok_status.status_state == "ok" and ok_status.usable is True,
        "review_path_visible": review_status.status_state == "review" and "readiness_review" in review_status.warnings and review_status.weak_families == ("trend_bias",),
        "blocked_path_visible": blocked_status.status_state == "blocked" and "prediction_readiness_blocked" in blocked_status.blockers,
        "missing_preview_blocks": missing_preview_status.status_state == "blocked" and "prediction_preview_missing" in missing_preview_status.blockers,
        "missing_readiness_blocks": missing_readiness_status.status_state == "blocked" and "prediction_readiness_missing" in missing_readiness_status.blockers,
        "missing_both_blocks": missing_both_status.status_state == "blocked" and {"prediction_preview_missing", "prediction_readiness_missing"}.issubset(set(missing_both_status.blockers)),
        "preview_fields_visible": ok_payload["preview_id"] == "preview_s138_unit" and ok_payload["preview_action"] == "WATCH_LONG" and ok_payload["preview_bias"] == "long" and ok_payload["preview_confidence"] == "medium",
        "readiness_fields_visible": ok_payload["readiness_id"] == "readiness_s138_unit" and ok_payload["readiness_state"] == "ready" and ok_payload["intended_mode"] == "ARMED_DRY_RUN",
        "metrics_visible": ok_payload["average_score"] == 0.82 and ok_payload["label_hit_rate"] == 0.76 and ok_payload["validation_state"] == "ok",
        "serializes": encoded["logic_version"] == "autotrade_prediction_preview_status.s138.v1" and encoded["usable"] is True,
        "execution_flags_false_ok": _assert_false_execution_flags(ok_payload),
        "execution_flags_false_review": _assert_false_execution_flags(review_payload),
        "execution_flags_false_blocked": _assert_false_execution_flags(blocked_payload),
        "execution_flags_false_missing_preview": _assert_false_execution_flags(missing_preview_payload),
        "execution_flags_false_missing_readiness": _assert_false_execution_flags(missing_readiness_payload),
        "execution_flags_false_missing_both": _assert_false_execution_flags(missing_both_payload),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    live_shadow_text = LIVE_SHADOW.read_text(encoding="utf-8") if LIVE_SHADOW.exists() else ""
    checks["live_shadow_not_imported_by_new_module"] = "btcts.autotrade.live_shadow" not in (AUTOTRADE_ROOT / "prediction_preview_status.py").read_text(encoding="utf-8")
    checks["live_shadow_still_contains_existing_append_path_only"] = "append_decision_jsonl" in live_shadow_text
    if not checks["live_shadow_not_imported_by_new_module"]:
        failures.append("new module imports live_shadow")

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    allowed_dirty_markers = (
        "btcts_next/src/btcts/autotrade/__init__.py",
        "btcts_next/src/btcts/autotrade/prediction_preview_status.py",
        "tools/test_phase4a_autotrade_milestone_ha_prediction_preview_status_guard.py",
        "tools/test_phase4a_autotrade_milestone_ha_prediction_preview_status_close_guard.py",
    )
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in allowed_dirty_markers)]
    failures.extend(f"unexpected dirty file during HA: {line}" for line in unexpected_dirty)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ha_prediction_preview_status_guard",
        "status": "closed" if not failures else "open",
        "contract": checks | {"only_expected_files_dirty": not unexpected_dirty},
        "sample": {
            "ok_status": ok_payload,
            "review_status": review_payload,
            "blocked_status": blocked_payload,
            "missing_both_status": missing_both_payload,
        },
        "dirty_lines": dirty_lines,
        "unexpected_dirty": unexpected_dirty,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_prediction_preview_status_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
