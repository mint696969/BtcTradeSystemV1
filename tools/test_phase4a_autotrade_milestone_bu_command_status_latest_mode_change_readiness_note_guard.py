# path: ./tools/test_phase4a_autotrade_milestone_bu_command_status_latest_mode_change_readiness_note_guard.py
# desc: Guard Command Requests status keeps latest mode-change readiness observer note even after newer non-mode command. Read-only; no append/runner/broker.

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

from btcts.autotrade.execution import default_command_ledger_path, read_command_ledger, summarize_command_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

STATUS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py"
UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
MODE_CHANGE_NOTE_FIELDS = (
    "latest_mode_change_readiness_command_id",
    "latest_mode_change_readiness_observer_run_id",
    "latest_mode_change_readiness_observer_blocked_by",
    "latest_mode_change_readiness_observer_would_send_to_broker",
    "latest_mode_change_readiness_observer_bounded",
)
FORBIDDEN_STATUS_TOKENS = (
    "append_command_ledger_record",
    "validate_and_append_command",
    "append_mode_state_record",
    "append_observer_run_record",
    "submit_mode_change_command_request",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "resolve_due_shadow_forecast_outcomes",
    "run_latest_market_state_shadow_decision",
    "apply_latest_mode_change_command_once",
    "streamlit",
    "btcts.apps.operator_ui",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)
FORBIDDEN_UI_STATUS_TOKENS = (
    "append_command_ledger_record",
    "validate_and_append_command",
    "append_mode_state_record",
    "append_observer_run_record",
    "submit_mode_change_command_request",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "resolve_due_shadow_forecast_outcomes",
    "run_latest_market_state_shadow_decision",
    "apply_latest_mode_change_command_once",
    "st.button(",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)
EXPECTED_BLOCKED_BY = [
    "mode_off",
    "mode_runtime_gate_blocked_shadow_decision_append",
    "mode_runtime_gate_blocked_forecast_outcome_resolution",
]


class FakeColumn:
    def __init__(self, owner: "FakeStreamlit | None" = None) -> None:
        self.owner = owner

    def metric(self, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.metric_count += 1
        return None


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.__path__ = []
        self.session_state: dict[str, Any] = {}
        self.metric_count = 0
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
            "blocked_by": ["observer_run_latest_blocked_for_live_target", *EXPECTED_BLOCKED_BY],
            "warnings": ["guard"],
            "health_state": "warn",
            "observer_run_fresh": True,
            "observer_latest_run_id": "obs_bu_blocked_off",
            "observer_latest_blocked_by": EXPECTED_BLOCKED_BY,
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "runtime_live_ready": True,
            "mode_changed": False,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def command_row(*, command_id: str, command_type: str, accepted: bool, requested_at: str, current_mode: str, target: str | None, blocked_by: list[str], note: str) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated" if command_type == "REQUEST_MODE_CHANGE" else "autotrade.command_request_validated",
        "command_id": command_id,
        "accepted": accepted,
        "blocked_by": blocked_by,
        "command": {
            "command_id": command_id,
            "command_type": command_type,
            "requested_by": "guard",
            "requested_at": requested_at,
            "current_mode": current_mode,
            "target": target,
            "confirmation": True,
            "reason_codes": ["guard"],
            "note": note,
            "confirmation_required": True,
        },
    }


def write_command_rows(path: Path) -> None:
    rows = [
        command_row(
            command_id="cmd_bu_live_request",
            command_type="REQUEST_MODE_CHANGE",
            accepted=False,
            requested_at=now_z(-10),
            current_mode="ARMED_DRY_RUN",
            target="LIVE_MIN_SIZE",
            blocked_by=["readiness_preflight_not_ready", "observer_run_latest_blocked_for_live_target", *EXPECTED_BLOCKED_BY],
            note=readiness_note(),
        ),
        command_row(
            command_id="cmd_bu_halt_new_after_live_request",
            command_type="REQUEST_HALT_NEW",
            accepted=True,
            requested_at=now_z(0),
            current_mode="ARMED_DRY_RUN",
            target="halt_new",
            blocked_by=[],
            note="{}",
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    fake_st = FakeStreamlit()
    hot_root = REPO_ROOT / "tmp/btc_ts_command_status_latest_mode_change_readiness_note_hot"
    render_exception = None
    import_exception = None
    before_count = -1
    after_summary_count = -2
    after_render_count = -3
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        if command_path.exists():
            command_path.unlink()
        write_command_rows(command_path)
        before_count = len(read_command_ledger(command_path))
        summary = summarize_command_ledger(command_path, max_lines=100)
        after_summary_count = len(read_command_ledger(command_path))
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
                module._render_command_request_status()
            except Exception as exc:
                render_exception = repr(exc)
        after_render_count = len(read_command_ledger(command_path))
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

    summary_data = summary.to_dict()
    status_text = STATUS_FILE.read_text(encoding="utf-8")
    summarize_source = function_source(STATUS_FILE, "summarize_command_ledger")
    ui_source = function_source(UI_FILE, "_render_command_request_status")
    checks = {
        "summary_dataclass_has_latest_mode_change_readiness_fields": all(field in status_text for field in MODE_CHANGE_NOTE_FIELDS),
        "summary_latest_command_is_newer_non_mode_command": summary_data.get("latest_command_id") == "cmd_bu_halt_new_after_live_request" and summary_data.get("latest_command_type") == "REQUEST_HALT_NEW",
        "summary_latest_row_readiness_fields_empty_for_non_mode_latest": summary_data.get("latest_readiness_observer_run_id") is None and tuple(summary_data.get("latest_readiness_observer_blocked_by") or ()) == (),
        "summary_preserves_latest_mode_change_readiness_note": summary_data.get("latest_mode_change_readiness_command_id") == "cmd_bu_live_request" and summary_data.get("latest_mode_change_readiness_observer_run_id") == "obs_bu_blocked_off" and tuple(summary_data.get("latest_mode_change_readiness_observer_blocked_by") or ()) == tuple(EXPECTED_BLOCKED_BY) and summary_data.get("latest_mode_change_readiness_observer_would_send_to_broker") is False and summary_data.get("latest_mode_change_readiness_observer_bounded") is True,
        "ui_command_requests_displays_latest_mode_change_readiness_fields": all(field in ui_source for field in MODE_CHANGE_NOTE_FIELDS),
        "summary_read_only_no_append_runner_broker": bool(summarize_source) and not any(token in status_text for token in FORBIDDEN_STATUS_TOKENS),
        "ui_command_status_read_only_no_append_runner_broker": bool(ui_source) and not any(token in ui_source for token in FORBIDDEN_UI_STATUS_TOKENS),
        "summary_did_not_append_command": before_count == 2 and after_summary_count == before_count,
        "render_did_not_append_command": before_count == 2 and after_render_count == before_count,
        "render_smoke_ok": import_exception is None and render_exception is None and "Command Requests" in fake_st.subheaders,
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
    failures.extend(f"protected lower-layer dirty during milestone BU: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bu_command_status_latest_mode_change_readiness_note_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "summary_dataclass_has_latest_mode_change_readiness_fields": checks["summary_dataclass_has_latest_mode_change_readiness_fields"],
            "summary_latest_command_is_newer_non_mode_command": checks["summary_latest_command_is_newer_non_mode_command"],
            "summary_latest_row_readiness_fields_empty_for_non_mode_latest": checks["summary_latest_row_readiness_fields_empty_for_non_mode_latest"],
            "summary_preserves_latest_mode_change_readiness_note": checks["summary_preserves_latest_mode_change_readiness_note"],
            "ui_command_requests_displays_latest_mode_change_readiness_fields": checks["ui_command_requests_displays_latest_mode_change_readiness_fields"],
            "summary_read_only_no_append_runner_broker": checks["summary_read_only_no_append_runner_broker"],
            "ui_command_status_read_only_no_append_runner_broker": checks["ui_command_status_read_only_no_append_runner_broker"],
            "summary_did_not_append_command": checks["summary_did_not_append_command"],
            "render_did_not_append_command": checks["render_did_not_append_command"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "summary": summary_data,
        "before_count": before_count,
        "after_summary_count": after_summary_count,
        "after_render_count": after_render_count,
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
