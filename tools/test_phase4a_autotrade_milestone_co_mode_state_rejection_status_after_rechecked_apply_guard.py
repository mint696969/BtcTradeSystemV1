# path: ./tools/test_phase4a_autotrade_milestone_co_mode_state_rejection_status_after_rechecked_apply_guard.py
# desc: Guard mode_state summary/UI surfaces rechecked apply rejection metadata. Mode State panel is read-only; no command/observer append, runner, or broker.

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

from btcts.autotrade.execution import apply_latest_mode_change_command_once_with_readiness_recheck, default_command_ledger_path, default_mode_state_ledger_path, read_command_ledger, read_mode_state_records, summarize_mode_state  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
MODE_STATE_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_state.py"
APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
MODE_STATE_REJECTION_FIELDS = (
    "latest_source_command_id",
    "latest_requested_by",
    "latest_accepted",
    "latest_mode_changed",
    "latest_ledger_event",
    "latest_reason_codes",
    "latest_blocked_by",
    "latest_would_send_to_broker",
)
MODE_STATE_FORBIDDEN_TOKENS = (
    "apply_latest_mode_change_command_once",
    "append_mode_state_record",
    "append_observer_run_record",
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
    "st.button(",
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
APPLY_FORBIDDEN_TOKENS = (
    "append_observer_run_record",
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
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


class FakeColumn:
    def __init__(self, owner: "FakeStreamlit | None" = None) -> None:
        self.owner = owner

    def metric(self, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.metric_call_count += 1
        return None


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.__path__ = []
        self.session_state: dict[str, Any] = {}
        self.metric_call_count = 0
        self.subheaders: list[str] = []

    def subheader(self, text: str, *args: Any, **kwargs: Any) -> None:
        self.subheaders.append(str(text))
        return None

    def caption(self, *args: Any, **kwargs: Any) -> None:
        return None

    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None

    def columns(self, count: int) -> list[FakeColumn]:
        return [FakeColumn(self) for _ in range(int(count))]


def now_z(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def readiness_note() -> str:
    return json.dumps(
        {
            "kind": "autotrade.mode_change_readiness_snapshot",
            "ready": False,
            "current_mode": "ARMED_DRY_RUN",
            "target_mode": "LIVE_MIN_SIZE",
            "blocked_by": ["observer_run_latest_blocked_for_live_target", "mode_off"],
            "warnings": ["mode_state_rejection_status_guard"],
            "health_state": "warn",
            "observer_latest_run_id": "obs_co_candidate_note",
            "observer_latest_blocked_by": ["mode_off"],
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def command_row(command_id: str) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated",
        "command_id": command_id,
        "accepted": True,
        "blocked_by": ["co_candidate_command_blocker"],
        "command": {
            "command_id": command_id,
            "command_type": "REQUEST_MODE_CHANGE",
            "requested_by": "operator_ui",
            "requested_at": now_z(-10),
            "current_mode": "ARMED_DRY_RUN",
            "target": "LIVE_MIN_SIZE",
            "confirmation": True,
            "reason_codes": ["guard", "mode_state_rejection_status"],
            "note": readiness_note(),
            "confirmation_required": True,
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    fake_st = FakeStreamlit()
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_state_rejection_status_after_rechecked_apply_hot"
    render_exception = None
    import_exception = None
    before_command_count = -1
    after_apply_command_count = -2
    after_render_command_count = -3
    before_mode_count = -1
    after_apply_mode_count = -2
    after_render_mode_count = -3
    observer_count_before = 0
    observer_count_after_apply = 0
    observer_count_after_render = 0
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = hot_root / "autotrade/decisions/observer_runs.jsonl"
        if command_path.exists():
            command_path.unlink()
        if mode_state_path.exists():
            mode_state_path.unlink()
        if observer_path.exists():
            observer_path.unlink()
        write_jsonl(command_path, [command_row("cmd_co_candidate_live_request")])
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_before = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        result = apply_latest_mode_change_command_once_with_readiness_recheck(max_lines=100, max_observer_run_age_sec=120, allow_warnings=False)
        after_apply_command_count = len(read_command_ledger(command_path))
        after_apply_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_after_apply = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        summary = summarize_mode_state(mode_state_path, max_lines=100)
        fake_components = types.ModuleType("streamlit.components")
        fake_components.__path__ = []
        fake_components_v1 = types.ModuleType("streamlit.components.v1")
        fake_components_v1.html = lambda *args, **kwargs: None
        fake_components.v1 = fake_components_v1
        fake_st.components = fake_components
        sys.modules["streamlit"] = fake_st
        sys.modules["streamlit.components"] = fake_components
        sys.modules["streamlit.components.v1"] = fake_components_v1
        try:
            module = importlib.import_module("btcts.apps.operator_ui.views.autotrade_page")
            module = importlib.reload(module)
        except Exception as exc:
            import_exception = repr(exc)
            module = None
        if module is not None:
            try:
                module._render_mode_state_status()
            except Exception as exc:
                render_exception = repr(exc)
        after_render_command_count = len(read_command_ledger(command_path))
        after_render_mode_count = len(read_mode_state_records(mode_state_path).rows)
        observer_count_after_render = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
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
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    result_data = result.to_dict()
    summary_data = summary.to_dict()
    mode_state_text = MODE_STATE_FILE.read_text(encoding="utf-8")
    summarize_source = function_source(MODE_STATE_FILE, "summarize_mode_state")
    ui_source = function_source(UI_FILE, "_render_mode_state_status")
    apply_source = function_source(APPLIER_FILE, "apply_latest_mode_change_command_once_with_readiness_recheck")
    checks = {
        "apply_rejection_appended_exactly_one_mode_state": before_mode_count == 0 and after_apply_mode_count == 1 and result_data.get("record_appended") is True and result_data.get("rejected_by_readiness") is True and (result_data.get("mode_state_record") or {}).get("source_command_id") == "cmd_co_candidate_live_request",
        "mode_state_summary_dataclass_has_rejection_fields": all(field in mode_state_text for field in MODE_STATE_REJECTION_FIELDS),
        "summarize_mode_state_surfaces_latest_rejection_fields": summary_data.get("latest_source_command_id") == "cmd_co_candidate_live_request" and summary_data.get("latest_requested_by") == "operator_ui" and summary_data.get("latest_accepted") is False and summary_data.get("latest_mode_changed") is False and summary_data.get("latest_ledger_event") == "autotrade.mode_state_readiness_recheck_rejected" and "readiness_recheck" in tuple(summary_data.get("latest_reason_codes") or ()) and "readiness_recheck_not_ready" in tuple(summary_data.get("latest_blocked_by") or ()) and "co_candidate_command_blocker" in tuple(summary_data.get("latest_blocked_by") or ()) and summary_data.get("latest_would_send_to_broker") is False and summary_data.get("current_mode") == "OFF",
        "summarize_mode_state_counts_rejection_blockers": (summary_data.get("blocked_by_counts") or {}).get("readiness_recheck_not_ready") == 1 and (summary_data.get("blocked_by_counts") or {}).get("co_candidate_command_blocker") == 1,
        "ui_mode_state_displays_rejection_fields": all(field in ui_source for field in MODE_STATE_REJECTION_FIELDS),
        "ui_mode_state_render_smoke_ok": import_exception is None and render_exception is None and "Mode State" in fake_st.subheaders and fake_st.metric_call_count >= 5,
        "ui_mode_state_panel_read_only_no_append_runner_broker": bool(ui_source) and not any(token in ui_source for token in MODE_STATE_FORBIDDEN_TOKENS),
        "apply_no_command_or_observer_append_no_runner_broker": bool(apply_source) and not any(token in apply_source for token in APPLY_FORBIDDEN_TOKENS) and before_command_count == 1 and after_apply_command_count == before_command_count and observer_count_after_apply == observer_count_before,
        "render_did_not_append_command_mode_or_observer": after_render_command_count == after_apply_command_count and after_render_mode_count == after_apply_mode_count and observer_count_after_render == observer_count_after_apply,
        "summarize_mode_state_read_only_source": bool(summarize_source) and "append_mode_state_record" not in summarize_source and "with path.open(\"a\"" not in summarize_source and "would_send_to_broker=False" in summarize_source and "read_only=True" in summarize_source,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if import_exception:
        failures.append(f"import_exception: {import_exception}")
    if render_exception:
        failures.append(f"render_exception: {render_exception}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone CO: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_co_mode_state_rejection_status_after_rechecked_apply_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "apply_rejection_appended_exactly_one_mode_state": checks["apply_rejection_appended_exactly_one_mode_state"],
            "mode_state_summary_dataclass_has_rejection_fields": checks["mode_state_summary_dataclass_has_rejection_fields"],
            "summarize_mode_state_surfaces_latest_rejection_fields": checks["summarize_mode_state_surfaces_latest_rejection_fields"],
            "summarize_mode_state_counts_rejection_blockers": checks["summarize_mode_state_counts_rejection_blockers"],
            "ui_mode_state_displays_rejection_fields": checks["ui_mode_state_displays_rejection_fields"],
            "ui_mode_state_render_smoke_ok": checks["ui_mode_state_render_smoke_ok"],
            "ui_mode_state_panel_read_only_no_append_runner_broker": checks["ui_mode_state_panel_read_only_no_append_runner_broker"],
            "apply_no_command_or_observer_append_no_runner_broker": checks["apply_no_command_or_observer_append_no_runner_broker"],
            "render_did_not_append_command_mode_or_observer": checks["render_did_not_append_command_mode_or_observer"],
            "summarize_mode_state_read_only_source": checks["summarize_mode_state_read_only_source"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "result": result_data,
        "mode_state_summary": summary_data,
        "before_command_count": before_command_count,
        "after_apply_command_count": after_apply_command_count,
        "after_render_command_count": after_render_command_count,
        "before_mode_count": before_mode_count,
        "after_apply_mode_count": after_apply_mode_count,
        "after_render_mode_count": after_render_mode_count,
        "observer_count_before": observer_count_before,
        "observer_count_after_apply": observer_count_after_apply,
        "observer_count_after_render": observer_count_after_render,
        "import_exception": import_exception,
        "render_exception": render_exception,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
