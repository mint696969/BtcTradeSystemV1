# path: ./tools/test_phase4a_autotrade_milestone_bo_autotrade_tab_readiness_observer_blocked_visibility_guard.py
# desc: Guard AutoTrade tab surfaces readiness observer latest blocked fields read-only. No runner/broker execution.

from __future__ import annotations

import ast
import importlib
import json
import os
import subprocess
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import (  # noqa: E402
    CommandRequest,
    CommandType,
    append_mode_state_record,
    default_command_ledger_path,
    default_mode_state_ledger_path,
    read_command_ledger,
    read_mode_state_records,
    validate_and_append_command,
)
from btcts.autotrade.execution.mode_state import ModeStateRecord  # noqa: E402
from btcts.autotrade.ledger import ObserverRunRecord, append_observer_run_record, default_observer_run_ledger_path  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
READINESS_OBSERVER_FIELDS = (
    "readiness_observer_latest_run_id",
    "readiness_observer_latest_blocked_by",
    "readiness_observer_latest_would_send_to_broker",
    "readiness_observer_latest_bounded",
)
STATUS_FORBIDDEN_TOKENS = (
    "append_mode_state_record",
    "append_observer_run_record",
    "append_command_ledger_record",
    "validate_and_append_command",
    "submit_mode_change_command_request",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "resolve_due_shadow_forecast_outcomes",
    "run_latest_market_state_shadow_decision",
    "apply_latest_mode_change_command_once",
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

    def __enter__(self) -> "FakeColumn":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False

    def metric(self, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.metric_call_count += 1
        return None

    def checkbox(self, *args: Any, **kwargs: Any) -> bool:
        if self.owner is not None:
            self.owner.checkbox_call_count += 1
        return bool(kwargs.get("value", False))

    def button(self, *args: Any, **kwargs: Any) -> bool:
        if self.owner is not None:
            self.owner.button_call_count += 1
        return False

    def selectbox(self, label: str, options: list[str] | tuple[str, ...], *, index: int = 0, **kwargs: Any) -> str:
        if self.owner is not None:
            self.owner.selectbox_call_count += 1
        if not options:
            return ""
        return str(options[index])

    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None

    def caption(self, *args: Any, **kwargs: Any) -> None:
        return None

    def subheader(self, text: str, *args: Any, **kwargs: Any) -> None:
        if self.owner is not None:
            self.owner.subheaders.append(str(text))
        return None


class FakeStreamlit(types.ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.__path__ = []
        self.session_state: dict[str, Any] = {}
        self.button_call_count = 0
        self.checkbox_call_count = 0
        self.selectbox_call_count = 0
        self.metric_call_count = 0
        self.subheaders: list[str] = []

    def title(self, *args: Any, **kwargs: Any) -> None:
        return None

    def caption(self, *args: Any, **kwargs: Any) -> None:
        return None

    def subheader(self, text: str, *args: Any, **kwargs: Any) -> None:
        self.subheaders.append(str(text))
        return None

    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None

    def divider(self, *args: Any, **kwargs: Any) -> None:
        return None

    def columns(self, count: int) -> list[FakeColumn]:
        return [FakeColumn(self) for _ in range(int(count))]

    def checkbox(self, *args: Any, **kwargs: Any) -> bool:
        self.checkbox_call_count += 1
        return bool(kwargs.get("value", False))

    def button(self, *args: Any, **kwargs: Any) -> bool:
        self.button_call_count += 1
        return False

    def selectbox(self, label: str, options: list[str] | tuple[str, ...], *, index: int = 0, **kwargs: Any) -> str:
        self.selectbox_call_count += 1
        if not options:
            return ""
        return str(options[index])


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def seed_runtime() -> tuple[Path, Path, Path]:
    command_path = default_command_ledger_path(ensure=True)
    mode_state_path = default_mode_state_ledger_path(ensure=True)
    observer_path = default_observer_run_ledger_path(ensure=True)
    for path in (command_path, mode_state_path, observer_path):
        if path.exists():
            path.unlink()
    append_mode_state_record(
        mode_state_path,
        ModeStateRecord(
            current_mode=AutoTradeMode.ARMED_DRY_RUN,
            previous_mode=AutoTradeMode.PAPER_OR_REPLAY,
            changed_at=now_z(),
            source_command_id="cmd_bo_seed_armed",
            requested_by="guard",
            accepted=True,
            mode_changed=True,
            reason_codes=("guard", "seed_armed"),
            blocked_by=(),
            would_send_to_broker=False,
        ),
    )
    validate_and_append_command(
        command_path,
        CommandRequest(
            command_id="cmd_bo_live_min_size_from_armed",
            command_type=CommandType.REQUEST_MODE_CHANGE,
            requested_by="guard",
            requested_at=now_z(),
            current_mode=AutoTradeMode.ARMED_DRY_RUN.value,
            target=AutoTradeMode.LIVE_MIN_SIZE.value,
            confirmation=True,
            reason_codes=("guard", "ui_readiness_observer_blocked_visibility"),
            note="guard only",
        ),
    )
    z = now_z()
    append_observer_run_record(
        observer_path,
        ObserverRunRecord(
            run_id="obs_bo_blocked_off",
            started_at=z,
            finished_at=z,
            requested_cycles=2,
            completed_cycles=2,
            appended_shadow_decision_count=0,
            appended_forecast_outcome_count=0,
            duplicate_snapshot_skipped_count=0,
            skip_duplicate_snapshot=True,
            blocked_by=("mode_off", "mode_runtime_gate_blocked_shadow_decision_append", "mode_runtime_gate_blocked_forecast_outcome_resolution"),
            would_send_to_broker=False,
            bounded=True,
        ),
    )
    return command_path, mode_state_path, observer_path


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    previous_streamlit = sys.modules.get("streamlit")
    previous_components = sys.modules.get("streamlit.components")
    previous_components_v1 = sys.modules.get("streamlit.components.v1")
    fake_st = FakeStreamlit()
    hot_root = REPO_ROOT / "tmp/btc_ts_ui_readiness_observer_blocked_visibility_hot"
    import_exception = None
    render_exception = None
    before_command_count = -1
    after_command_count = -2
    before_mode_count = -1
    after_mode_count = -2
    before_observer_count = -1
    after_observer_count = -2
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path, mode_state_path, observer_path = seed_runtime()
        before_command_count = len(read_command_ledger(command_path))
        before_mode_count = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
        before_observer_count = len(observer_path.read_text(encoding="utf-8").splitlines())
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
                module.render()
            except Exception as exc:
                render_exception = repr(exc)
        after_command_count = len(read_command_ledger(command_path))
        after_mode_count = len(read_mode_state_records(mode_state_path, max_lines=100).rows)
        after_observer_count = len(observer_path.read_text(encoding="utf-8").splitlines())
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

    live_source = function_source(UI_FILE, "_render_live_readiness_preflight")
    preview_source = function_source(UI_FILE, "_render_mode_change_apply_preview_status")
    checks = {
        "live_readiness_displays_observer_latest_blocked_fields": all(field in live_source for field in READINESS_OBSERVER_FIELDS) and "health_observer_runs" in live_source,
        "mode_change_preview_displays_observer_latest_blocked_fields": all(field in preview_source for field in READINESS_OBSERVER_FIELDS) and "readiness_observer_runs" in preview_source,
        "readiness_visibility_status_read_only": bool(live_source) and bool(preview_source) and not any(token in live_source or token in preview_source for token in STATUS_FORBIDDEN_TOKENS),
        "render_smoke_ok": import_exception is None and render_exception is None,
        "render_did_not_append_commands": before_command_count == 1 and after_command_count == before_command_count,
        "render_did_not_append_mode_state": before_mode_count == 1 and after_mode_count == before_mode_count,
        "render_did_not_append_observer_runs": before_observer_count == 1 and after_observer_count == before_observer_count,
        "fake_streamlit_exercised": fake_st.button_call_count >= 4 and fake_st.checkbox_call_count >= 6 and fake_st.selectbox_call_count >= 2,
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
    failures.extend(f"protected lower-layer dirty during milestone BO: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_bo_autotrade_tab_readiness_observer_blocked_visibility_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "live_readiness_displays_observer_latest_blocked_fields": checks["live_readiness_displays_observer_latest_blocked_fields"],
            "mode_change_preview_displays_observer_latest_blocked_fields": checks["mode_change_preview_displays_observer_latest_blocked_fields"],
            "readiness_visibility_status_read_only_no_runner_no_broker": checks["readiness_visibility_status_read_only"],
            "render_did_not_append_commands": checks["render_did_not_append_commands"],
            "render_did_not_append_mode_state": checks["render_did_not_append_mode_state"],
            "render_did_not_append_observer_runs": checks["render_did_not_append_observer_runs"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "subheaders": fake_st.subheaders,
        "button_call_count": fake_st.button_call_count,
        "checkbox_call_count": fake_st.checkbox_call_count,
        "selectbox_call_count": fake_st.selectbox_call_count,
        "before_command_count": before_command_count,
        "after_command_count": after_command_count,
        "before_mode_count": before_mode_count,
        "after_mode_count": after_mode_count,
        "before_observer_count": before_observer_count,
        "after_observer_count": after_observer_count,
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
