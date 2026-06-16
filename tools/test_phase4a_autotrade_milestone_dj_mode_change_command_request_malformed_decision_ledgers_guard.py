# path: ./tools/test_phase4a_autotrade_milestone_dj_mode_change_command_request_malformed_decision_ledgers_guard.py
# desc: Guard mode-change command request appends only command ledger and remains fail-soft/readiness-blocked with malformed decision ledgers.

from __future__ import annotations

import ast
import importlib
import json
import os
import subprocess
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import default_command_ledger_path, default_mode_state_ledger_path, read_command_ledger_rows, read_mode_state_records, summarize_command_ledger, summarize_mode_state  # noqa: E402
from btcts.autotrade.ledger.decision_status import default_shadow_decision_status_path, summarize_shadow_decision_ledger  # noqa: E402
from btcts.autotrade.ledger.forecast_outcome_status import summarize_forecast_outcome_ledger  # noqa: E402
from btcts.autotrade.ledger.forecast_resolution import default_forecast_outcome_ledger_path  # noqa: E402
from btcts.autotrade.ledger.observer_run_status import default_observer_run_ledger_path, summarize_observer_run_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
MODE_CHANGE_REQUEST_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_change_request.py"
READINESS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/readiness.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_REQUEST_TOKENS = (
    "append_mode_state_record",
    "append_observer_run_record",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "resolve_due_shadow_forecast_outcomes",
    "run_latest_market_state_shadow_decision",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.__path__ = []
        self.session_state: dict[str, Any] = {}


def now_z(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def seed_command_row() -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.command_request_validated",
        "command_id": "cmd_dj_existing_halt_new",
        "accepted": True,
        "blocked_by": [],
        "command": {
            "command_id": "cmd_dj_existing_halt_new",
            "command_type": "REQUEST_HALT_NEW",
            "requested_by": "operator_ui",
            "requested_at": now_z(-30),
            "current_mode": "OFF",
            "target": "halt_new",
            "confirmation": False,
            "reason_codes": ["guard", "mode_change_command_request_malformed_decision_ledgers", "seed"],
            "note": "",
            "confirmation_required": False,
        },
    }


def observer_row(run_id: str, offset_seconds: int, blocker: str = "") -> dict[str, Any]:
    return {
        "run_id": run_id,
        "started_at": now_z(offset_seconds - 1),
        "finished_at": now_z(offset_seconds),
        "requested_cycles": 1,
        "completed_cycles": 1,
        "appended_shadow_decision_count": 1,
        "appended_forecast_outcome_count": 1,
        "duplicate_snapshot_skipped_count": 0,
        "skip_duplicate_snapshot": True,
        "blocked_by": [blocker] if blocker else [],
        "would_send_to_broker": False,
        "bounded": True,
        "source": "autotrade.observer_cycle_bounded",
    }


def shadow_row(decision_id: str, action: str, blocker: str = "") -> dict[str, Any]:
    return {
        "decision_id": decision_id,
        "mode": "SHADOW",
        "snapshot_id": f"snap_{decision_id}",
        "forecast_id": f"fcst_{decision_id}",
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "forecast_5m": {"forecast_id": f"fcst_{decision_id}", "forecast_direction": "down", "confidence": "medium"},
        "candidate": {"action": action},
        "risk_gate": {"allowed": False, "executable": False},
        "final_action": action,
        "reason_codes": ["guard", "mode_change_command_request_malformed_decision_ledgers", decision_id],
        "blocked_by": [blocker] if blocker else [],
        "would_order": None,
    }


def outcome_row(forecast_id: str, result: str, confidence: str = "medium") -> dict[str, Any]:
    return {
        "forecast_id": forecast_id,
        "parameter_set_id": "params_fx_balanced_v0_1",
        "logic_version": "autotrade_logic_v0_1",
        "source_snapshot_id": f"snap_{forecast_id}",
        "target_ts": "2026-06-13T02:00:00Z",
        "actual_snapshot_id": f"actual_{forecast_id}",
        "forecast_direction": "down",
        "forecast_confidence": confidence,
        "expected_change": "strengthen_sell",
        "drivers": ["sell_pressure_or_ground"],
        "blocked_by": [],
        "result": result,
        "direction_hit": result == "hit",
        "change_type_hit": result == "hit",
        "divergence_reasons": [] if result == "hit" else ["direction_mismatch"],
    }


def write_jsonl_with_malformed(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def write_command_seed_with_malformed(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(seed_command_row(), ensure_ascii=False, sort_keys=True) + "\n{not-json\n", encoding="utf-8")


def import_autotrade_page(fake_st: FakeStreamlit) -> tuple[Any | None, str | None]:
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    fake_components = types.ModuleType("streamlit.components")
    fake_components.__path__ = []
    fake_components_v1 = types.ModuleType("streamlit.components.v1")
    fake_components_v1.html = lambda *args, **kwargs: None
    fake_components.v1 = fake_components_v1
    fake_st.components = fake_components
    try:
        sys.modules["streamlit"] = fake_st
        sys.modules["streamlit.components"] = fake_components
        sys.modules["streamlit.components.v1"] = fake_components_v1
        module = importlib.import_module("btcts.apps.operator_ui.views.autotrade_page")
        return importlib.reload(module), None
    except Exception as exc:
        return None, repr(exc)
    finally:
        if previous_components_v1 is None:
            sys.modules.pop("streamlit.components.v1", None)
        else:
            sys.modules["streamlit.components.v1"] = previous_components_v1
        if previous_components is None:
            sys.modules.pop("streamlit.components", None)
        else:
            sys.modules["streamlit.components"] = previous_components
        if previous_streamlit is None:
            sys.modules.pop("streamlit", None)
        else:
            sys.modules["streamlit"] = previous_streamlit


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_change_command_request_malformed_decision_ledgers_hot"
    ui_exception = None
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = default_observer_run_ledger_path(ensure=True)
        shadow_path = default_shadow_decision_status_path(ensure=True)
        outcome_path = default_forecast_outcome_ledger_path(ensure=True)
        for path in (command_path, mode_state_path, observer_path, shadow_path, outcome_path):
            if path.exists():
                path.unlink()
        write_command_seed_with_malformed(command_path)
        mode_state_path.parent.mkdir(parents=True, exist_ok=True)
        mode_state_path.write_text("", encoding="utf-8")
        write_jsonl_with_malformed(observer_path, [observer_row("obs_dj_old", -20), observer_row("obs_dj_latest", -5, "dj_latest_observer_blocker")])
        write_jsonl_with_malformed(shadow_path, [shadow_row("dj_old", "WAIT", "dj_old_shadow_blocker"), shadow_row("dj_latest", "WAIT", "dj_latest_shadow_blocker")])
        write_jsonl_with_malformed(outcome_path, [outcome_row("fcst_dj_old", "hit", "medium"), outcome_row("fcst_dj_latest", "miss", "high")])

        before_line_counts = {
            "command": len(command_path.read_text(encoding="utf-8").splitlines()),
            "mode_state": len(mode_state_path.read_text(encoding="utf-8").splitlines()),
            "observer": len(observer_path.read_text(encoding="utf-8").splitlines()),
            "shadow": len(shadow_path.read_text(encoding="utf-8").splitlines()),
            "outcome": len(outcome_path.read_text(encoding="utf-8").splitlines()),
        }
        command_before = summarize_command_ledger(command_path, max_lines=100).to_dict()
        mode_before = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        observer_before = summarize_observer_run_ledger(observer_path, max_lines=100).to_dict()
        shadow_before = summarize_shadow_decision_ledger(shadow_path, max_lines=100).to_dict()
        outcome_before = summarize_forecast_outcome_ledger(outcome_path, max_lines=100).to_dict()

        fake_st = FakeStreamlit()
        module, import_exception = import_autotrade_page(fake_st)
        if module is None:
            ui_exception = import_exception
            ui_result = {}
        else:
            try:
                ui_result = module._submit_mode_change_request(
                    current_mode="ARMED_DRY_RUN",
                    target_mode="LIVE_MIN_SIZE",
                    human_confirmed=True,
                    allow_warnings=False,
                )
            except Exception as exc:
                ui_exception = repr(exc)
                ui_result = {}

        command_after = summarize_command_ledger(command_path, max_lines=100).to_dict()
        command_read_after = read_command_ledger_rows(command_path, max_lines=100).to_dict()
        mode_after = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        observer_after = summarize_observer_run_ledger(observer_path, max_lines=100).to_dict()
        shadow_after = summarize_shadow_decision_ledger(shadow_path, max_lines=100).to_dict()
        outcome_after = summarize_forecast_outcome_ledger(outcome_path, max_lines=100).to_dict()
        after_line_counts = {
            "command": len(command_path.read_text(encoding="utf-8").splitlines()),
            "mode_state": len(mode_state_path.read_text(encoding="utf-8").splitlines()),
            "observer": len(observer_path.read_text(encoding="utf-8").splitlines()),
            "shadow": len(shadow_path.read_text(encoding="utf-8").splitlines()),
            "outcome": len(outcome_path.read_text(encoding="utf-8").splitlines()),
        }
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    submitted_record = ui_result.get("command_record") if isinstance(ui_result.get("command_record"), dict) else {}
    submitted_command = submitted_record.get("command") if isinstance(submitted_record.get("command"), dict) else {}
    readiness = ui_result.get("readiness") if isinstance(ui_result.get("readiness"), dict) else {}
    latest_rows = command_read_after.get("rows") or []
    latest_row = latest_rows[-1] if latest_rows else {}
    latest_command = latest_row.get("command") if isinstance(latest_row.get("command"), dict) else {}
    latest_note = latest_command.get("note") or "{}"
    try:
        latest_note_data = json.loads(latest_note)
    except Exception:
        latest_note_data = {}

    submit_source = function_source(MODE_CHANGE_REQUEST_FILE, "submit_mode_change_command_request")
    build_source = function_source(MODE_CHANGE_REQUEST_FILE, "build_mode_change_command_request_record")
    note_source = function_source(MODE_CHANGE_REQUEST_FILE, "_readiness_note")
    readiness_source = function_source(READINESS_FILE, "evaluate_autotrade_live_readiness")
    ui_submit_source = function_source(UI_FILE, "_submit_mode_change_request")
    checks = {
        "seed_ledgers_before_request_are_failsoft": command_before.get("total_rows") == 1 and command_before.get("skipped_rows") == 1 and observer_before.get("total_rows") == 2 and observer_before.get("skipped_rows") == 1 and shadow_before.get("total_rows") == 2 and shadow_before.get("skipped_rows") == 1 and outcome_before.get("total_rows") == 2,
        "ui_mode_change_request_returns_rejected_readiness_snapshot": ui_exception is None and ui_result.get("ui_action") == "mode_change_command_request_recorded" and ui_result.get("accepted") is False and "readiness_preflight_not_ready" in tuple(ui_result.get("blocked_by") or ()) and readiness.get("current_mode") == "ARMED_DRY_RUN" and readiness.get("target_mode") == "LIVE_MIN_SIZE" and readiness.get("ready") is False and readiness.get("health_state") == "warn" and readiness.get("observer_latest_run_id") == "obs_dj_latest" and "dj_latest_observer_blocker" in tuple(readiness.get("observer_latest_blocked_by") or ()) and readiness.get("observer_latest_would_send_to_broker") is False,
        "request_appended_exactly_one_command_only": after_line_counts == {"command": before_line_counts["command"] + 1, "mode_state": before_line_counts["mode_state"], "observer": before_line_counts["observer"], "shadow": before_line_counts["shadow"], "outcome": before_line_counts["outcome"]} and command_after.get("total_rows") == 2 and command_after.get("skipped_rows") == 1 and mode_after == mode_before and observer_after == observer_before and shadow_after == shadow_before and outcome_after == outcome_before,
        "latest_command_record_is_rejected_request_mode_change_with_readiness_note": latest_row.get("accepted") is False and latest_command.get("command_type") == "REQUEST_MODE_CHANGE" and latest_command.get("current_mode") == "ARMED_DRY_RUN" and latest_command.get("target") == "LIVE_MIN_SIZE" and latest_command.get("confirmation") is True and latest_note_data.get("kind") == "autotrade.mode_change_readiness_snapshot" and latest_note_data.get("ready") is False and latest_note_data.get("health_state") == "warn" and latest_note_data.get("observer_latest_run_id") == "obs_dj_latest" and latest_note_data.get("observer_latest_would_send_to_broker") is False and latest_note_data.get("would_send_to_broker") is False,
        "command_summary_after_surfaces_latest_mode_change_readiness_and_malformed_skip": command_after.get("latest_command_type") == "REQUEST_MODE_CHANGE" and command_after.get("latest_accepted") is False and command_after.get("latest_mode_change_readiness_command_id") == latest_row.get("command_id") and command_after.get("latest_mode_change_readiness_ready") is False and command_after.get("latest_mode_change_readiness_health_state") == "warn" and command_after.get("latest_mode_change_readiness_observer_run_id") == "obs_dj_latest" and command_after.get("skipped_rows") == 1 and tuple(command_after.get("error_samples") or ()) != (),
        "submit_source_appends_command_only_no_mode_state_runner_broker": bool(submit_source) and "append_command_ledger_record" in submit_source and not any(token in submit_source for token in FORBIDDEN_REQUEST_TOKENS),
        "build_request_source_uses_readiness_and_no_append": bool(build_source) and "evaluate_autotrade_live_readiness" in build_source and "readiness_preflight_not_ready" in build_source and "CommandLedgerRecord" in build_source and "append_command_ledger_record" not in build_source and not any(token in build_source for token in FORBIDDEN_REQUEST_TOKENS),
        "readiness_note_and_readiness_source_no_broker_mode_change": bool(note_source) and "would_send_to_broker" in note_source and "mode_changed" in note_source and bool(readiness_source) and "would_send_to_broker=False" in readiness_source and "mode_changed=False" in readiness_source and not any(token in readiness_source for token in FORBIDDEN_REQUEST_TOKENS),
        "ui_submit_wrapper_reports_no_mode_change_no_broker": bool(ui_submit_source) and "submit_mode_change_command_request" in ui_submit_source and "mode_changed" in ui_submit_source and "would_send_to_broker" in ui_submit_source and not any(token in ui_submit_source for token in FORBIDDEN_REQUEST_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if ui_exception:
        failures.append(f"ui_exception: {ui_exception}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DJ: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dj_mode_change_command_request_malformed_decision_ledgers_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "seed_ledgers_before_request_are_failsoft": checks["seed_ledgers_before_request_are_failsoft"],
            "ui_mode_change_request_returns_rejected_readiness_snapshot": checks["ui_mode_change_request_returns_rejected_readiness_snapshot"],
            "request_appended_exactly_one_command_only": checks["request_appended_exactly_one_command_only"],
            "latest_command_record_is_rejected_request_mode_change_with_readiness_note": checks["latest_command_record_is_rejected_request_mode_change_with_readiness_note"],
            "command_summary_after_surfaces_latest_mode_change_readiness_and_malformed_skip": checks["command_summary_after_surfaces_latest_mode_change_readiness_and_malformed_skip"],
            "submit_source_appends_command_only_no_mode_state_runner_broker": checks["submit_source_appends_command_only_no_mode_state_runner_broker"],
            "build_request_source_uses_readiness_and_no_append": checks["build_request_source_uses_readiness_and_no_append"],
            "readiness_note_and_readiness_source_no_broker_mode_change": checks["readiness_note_and_readiness_source_no_broker_mode_change"],
            "ui_submit_wrapper_reports_no_mode_change_no_broker": checks["ui_submit_wrapper_reports_no_mode_change_no_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "command_before": command_before,
        "mode_before": mode_before,
        "observer_before": observer_before,
        "shadow_before": shadow_before,
        "outcome_before": outcome_before,
        "ui_result": ui_result,
        "command_after": command_after,
        "command_read_after": command_read_after,
        "mode_after": mode_after,
        "observer_after": observer_after,
        "shadow_after": shadow_after,
        "outcome_after": outcome_after,
        "latest_note_data": latest_note_data,
        "before_line_counts": before_line_counts,
        "after_line_counts": after_line_counts,
        "ui_exception": ui_exception,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
