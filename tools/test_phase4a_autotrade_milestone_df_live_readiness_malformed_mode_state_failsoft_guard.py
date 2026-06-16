# path: ./tools/test_phase4a_autotrade_milestone_df_live_readiness_malformed_mode_state_failsoft_guard.py
# desc: Guard Live Readiness Preflight uses latest valid mode_state row and remains read-only when mode_state contains malformed rows.

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

from btcts.autotrade.execution import current_mode_state, default_command_ledger_path, default_mode_state_ledger_path, read_command_ledger_rows, read_mode_state_records, summarize_mode_state  # noqa: E402
from btcts.autotrade.readiness import evaluate_autotrade_live_readiness  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

READINESS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/readiness.py"
MODE_STATE_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_state.py"
UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
LATEST_SOURCE = "cmd_df_armed_dry_run_valid"
OLD_SOURCE = "cmd_df_off_old_valid"
LIVE_READINESS_PANEL_FIELDS = (
    "mode_state_current_mode",
    "mode_state_source",
    "target_mode",
    "ready",
    "transition_allowed",
    "human_confirmation_required",
    "human_confirmed",
    "allow_warnings",
    "blocked_by",
    "warnings",
    "health_state",
    "observer_run_fresh",
    "runtime_live_ready",
    "runtime_hot_detected",
    "runtime_cold_detected",
    "would_send_to_broker",
    "read_only",
    "mode_changed",
)
FORBIDDEN_READINESS_TOKENS = (
    "append_mode_state_record",
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
# The UI preflight intentionally has a button that records a command only when clicked.
# FakeStreamlit.button returns False, and the function body delegates to _submit_mode_change_request.
UI_PREFLIGHT_FORBIDDEN_TOKENS = tuple(token for token in FORBIDDEN_READINESS_TOKENS if token not in {"submit_mode_change_command_request", "validate_and_append_command"})


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
            self.owner.selectbox_values.append(str(options[index]) if options else "")
        return str(options[index]) if options else ""
    def markdown(self, *args: Any, **kwargs: Any) -> None:
        return None
    def caption(self, *args: Any, **kwargs: Any) -> None:
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
        self.selectbox_values: list[str] = []
    def subheader(self, text: str, *args: Any, **kwargs: Any) -> None:
        self.subheaders.append(str(text))
    def caption(self, *args: Any, **kwargs: Any) -> None:
        return None
    def markdown(self, *args: Any, **kwargs: Any) -> None:
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
        value = str(options[index]) if options else ""
        self.selectbox_values.append(value)
        return value


def now_z(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


def mode_state_row(*, current_mode: str, previous_mode: str, source_command_id: str, changed_at: str, accepted: bool = True, mode_changed: bool = True) -> dict[str, Any]:
    return {
        "current_mode": current_mode,
        "previous_mode": previous_mode,
        "changed_at": changed_at,
        "source_command_id": source_command_id,
        "requested_by": "operator_ui",
        "accepted": accepted,
        "mode_changed": mode_changed,
        "reason_codes": ["guard", "live_readiness_malformed_mode_state_failsoft", source_command_id],
        "blocked_by": [],
        "ledger_event": "autotrade.mode_state_recorded",
        "would_send_to_broker": False,
    }


def write_mode_state_with_malformed_and_latest_armed(path: Path) -> None:
    rows = [
        mode_state_row(current_mode="OFF", previous_mode="OFF", source_command_id=OLD_SOURCE, changed_at=now_z(-30), accepted=True, mode_changed=False),
        mode_state_row(current_mode="ARMED_DRY_RUN", previous_mode="PAPER_OR_REPLAY", source_command_id=LATEST_SOURCE, changed_at=now_z(-10), accepted=True, mode_changed=True),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


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
    hot_root = REPO_ROOT / "tmp/btc_ts_live_readiness_malformed_mode_state_failsoft_hot"
    fake_st = FakeStreamlit()
    before_command_count = 0
    after_ui_command_count = 0
    before_mode_count = -1
    after_ui_mode_count = -2
    before_observer_count = 0
    after_observer_count = 0
    ui_exception = None
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_state_path = default_mode_state_ledger_path(ensure=True)
        observer_path = hot_root / "autotrade/decisions/observer_runs.jsonl"
        for path in (command_path, mode_state_path, observer_path):
            if path.exists():
                path.unlink()
        write_mode_state_with_malformed_and_latest_armed(mode_state_path)
        before_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        mode_read_before = read_mode_state_records(mode_state_path, max_lines=100)
        before_mode_count = len(mode_read_before.rows)
        before_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        current = current_mode_state(mode_state_path, max_lines=100).to_dict()
        summary_before = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        readiness_confirmed = evaluate_autotrade_live_readiness(
            current_mode=current["current_mode"],
            target_mode="LIVE_MIN_SIZE",
            human_confirmed=True,
            allow_warnings=False,
            max_observer_run_age_sec=120,
            max_lines=100,
        ).to_dict()
        module, import_exception = import_autotrade_page(fake_st)
        if module is not None:
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
                module._render_live_readiness_preflight()
            except Exception as exc:
                ui_exception = repr(exc)
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
        else:
            ui_exception = import_exception
        after_ui_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        mode_read_after = read_mode_state_records(mode_state_path, max_lines=100)
        after_ui_mode_count = len(mode_read_after.rows)
        summary_after = summarize_mode_state(mode_state_path, max_lines=100).to_dict()
        after_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    readiness_source = function_source(READINESS_FILE, "evaluate_autotrade_live_readiness")
    current_mode_source = function_source(MODE_STATE_FILE, "current_mode_state")
    read_mode_source = function_source(MODE_STATE_FILE, "read_mode_state_records")
    ui_preflight_source = function_source(UI_FILE, "_render_live_readiness_preflight")
    checks = {
        "mode_state_reader_skips_malformed_but_keeps_latest_valid_armed_row": before_mode_count == 2 and mode_read_before.skipped_count == 1 and tuple(mode_read_before.error_samples) != () and current.get("current_mode") == "ARMED_DRY_RUN" and current.get("source_command_id") == LATEST_SOURCE,
        "mode_state_summary_surfaces_skipped_and_latest_valid_armed_row": summary_before.get("total_rows") == 2 and summary_before.get("skipped_rows") == 1 and tuple(summary_before.get("error_samples") or ()) != () and summary_before.get("current_mode") == "ARMED_DRY_RUN" and summary_before.get("latest_source_command_id") == LATEST_SOURCE and summary_before.get("read_only") is True,
        "direct_readiness_uses_latest_valid_mode_and_is_blocked_read_only": readiness_confirmed.get("current_mode") == "ARMED_DRY_RUN" and readiness_confirmed.get("target_mode") == "LIVE_MIN_SIZE" and readiness_confirmed.get("transition_allowed") is True and readiness_confirmed.get("human_confirmation_required") is True and readiness_confirmed.get("human_confirmed") is True and readiness_confirmed.get("ready") is False and "runtime_health_blocked" in tuple(readiness_confirmed.get("blocked_by") or ()) and "observer_run_missing" in tuple(readiness_confirmed.get("blocked_by") or ()) and readiness_confirmed.get("would_send_to_broker") is False and readiness_confirmed.get("read_only") is True and readiness_confirmed.get("mode_changed") is False,
        "ui_live_readiness_preflight_uses_latest_valid_mode_in_selectbox": ui_exception is None and "Live Readiness Preflight" in fake_st.subheaders and fake_st.selectbox_call_count >= 2 and fake_st.selectbox_values[:2] == ["ARMED_DRY_RUN", "LIVE_MIN_SIZE"],
        "ui_live_readiness_preflight_is_read_only_no_ledger_append": after_ui_command_count == before_command_count == 0 and after_ui_mode_count == before_mode_count == 2 and mode_read_after.skipped_count == 1 and after_observer_count == before_observer_count,
        "mode_state_after_ui_still_latest_valid_armed_row": summary_after.get("current_mode") == "ARMED_DRY_RUN" and summary_after.get("latest_source_command_id") == LATEST_SOURCE and summary_after.get("skipped_rows") == 1,
        "readiness_source_is_read_only_no_append_runner_broker": bool(readiness_source) and "build_autotrade_runtime_health_snapshot" in readiness_source and "would_send_to_broker=False" in readiness_source and "read_only=True" in readiness_source and "mode_changed=False" in readiness_source and not any(token in readiness_source for token in FORBIDDEN_READINESS_TOKENS),
        "mode_state_current_mode_uses_failsoft_reader": bool(current_mode_source) and "read_mode_state_records" in current_mode_source and "read.rows[-1]" in current_mode_source and bool(read_mode_source) and "skipped += 1" in read_mode_source,
        "ui_live_readiness_panel_displays_fields_and_no_runner_broker_apply": bool(ui_preflight_source) and all(field in ui_preflight_source for field in LIVE_READINESS_PANEL_FIELDS) and "current_mode_state" in ui_preflight_source and "evaluate_autotrade_live_readiness" in ui_preflight_source and not any(token in ui_preflight_source for token in UI_PREFLIGHT_FORBIDDEN_TOKENS),
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
    failures.extend(f"protected lower-layer dirty during milestone DF: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_df_live_readiness_malformed_mode_state_failsoft_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_state_reader_skips_malformed_but_keeps_latest_valid_armed_row": checks["mode_state_reader_skips_malformed_but_keeps_latest_valid_armed_row"],
            "mode_state_summary_surfaces_skipped_and_latest_valid_armed_row": checks["mode_state_summary_surfaces_skipped_and_latest_valid_armed_row"],
            "direct_readiness_uses_latest_valid_mode_and_is_blocked_read_only": checks["direct_readiness_uses_latest_valid_mode_and_is_blocked_read_only"],
            "ui_live_readiness_preflight_uses_latest_valid_mode_in_selectbox": checks["ui_live_readiness_preflight_uses_latest_valid_mode_in_selectbox"],
            "ui_live_readiness_preflight_is_read_only_no_ledger_append": checks["ui_live_readiness_preflight_is_read_only_no_ledger_append"],
            "mode_state_after_ui_still_latest_valid_armed_row": checks["mode_state_after_ui_still_latest_valid_armed_row"],
            "readiness_source_is_read_only_no_append_runner_broker": checks["readiness_source_is_read_only_no_append_runner_broker"],
            "mode_state_current_mode_uses_failsoft_reader": checks["mode_state_current_mode_uses_failsoft_reader"],
            "ui_live_readiness_panel_displays_fields_and_no_runner_broker_apply": checks["ui_live_readiness_panel_displays_fields_and_no_runner_broker_apply"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "mode_read_before": mode_read_before.to_dict(),
        "current": current,
        "summary_before": summary_before,
        "readiness_confirmed": readiness_confirmed,
        "summary_after": summary_after,
        "mode_read_after": mode_read_after.to_dict(),
        "fake_ui": {
            "subheaders": fake_st.subheaders,
            "selectbox_values": fake_st.selectbox_values,
            "selectbox_call_count": fake_st.selectbox_call_count,
            "checkbox_call_count": fake_st.checkbox_call_count,
            "button_call_count": fake_st.button_call_count,
            "metric_call_count": fake_st.metric_call_count,
        },
        "before_command_count": before_command_count,
        "after_ui_command_count": after_ui_command_count,
        "before_mode_count": before_mode_count,
        "after_ui_mode_count": after_ui_mode_count,
        "before_observer_count": before_observer_count,
        "after_observer_count": after_observer_count,
        "ui_exception": ui_exception,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
