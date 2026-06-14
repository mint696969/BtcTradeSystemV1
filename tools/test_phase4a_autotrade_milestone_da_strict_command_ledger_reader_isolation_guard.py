# path: ./tools/test_phase4a_autotrade_milestone_da_strict_command_ledger_reader_isolation_guard.py
# desc: Guard strict read_command_ledger is isolated away from AutoTrade read-only UI/status/apply-preview paths. Fail-soft read_command_ledger_rows is required for status/render paths.

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

from btcts.autotrade.execution import default_command_ledger_path, default_mode_state_ledger_path, read_command_ledger_rows, read_mode_state_records, summarize_command_ledger  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
COMMAND_LEDGER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_ledger.py"
COMMAND_STATUS_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py"
APPLIER_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py"
EXEC_INIT_FILE = REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/__init__.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
READ_ONLY_UI_FUNCTIONS = (
    "_recent_command_rows",
    "_render_top_critical_state",
    "_render_mode_change_apply_preview_status",
    "_render_command_request_status",
    "_render_runtime_health_status",
    "_render_observer_run_status",
    "_render_shadow_decision_status",
    "_render_forecast_calibration_status",
)
STRICT_CALL_TOKEN = "read_command_ledger("
FAILSOFT_TOKEN = "read_command_ledger_rows"
FORBIDDEN_READ_ONLY_TOKENS = (
    "append_mode_state_record",
    "append_observer_run_record",
    "append_command_ledger_record",
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


def command_row(command_id: str, requested_at: str) -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.command_request_validated",
        "command_id": command_id,
        "accepted": True,
        "blocked_by": [],
        "command": {
            "command_id": command_id,
            "command_type": "REQUEST_HALT_NEW",
            "requested_by": "operator_ui",
            "requested_at": requested_at,
            "current_mode": "OFF",
            "target": "halt_new",
            "confirmation": False,
            "reason_codes": ["guard", "strict_command_ledger_reader_isolation", command_id],
            "note": "",
            "confirmation_required": False,
        },
    }


def write_malformed_command_jsonl(path: Path) -> None:
    rows = [
        command_row("cmd_da_old_halt", now_z(-20)),
        command_row("cmd_da_new_halt", now_z(-10)),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
        + "{not-json\n"
        + json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def import_autotrade_page() -> tuple[Any | None, str | None]:
    fake_st = FakeStreamlit()
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


def strict_reader_usage_hits() -> list[str]:
    hits: list[str] = []
    for path in (SRC_ROOT / "btcts").rglob("*.py"):
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if path == COMMAND_LEDGER_FILE:
            continue
        if path == EXEC_INIT_FILE:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if STRICT_CALL_TOKEN in line:
                hits.append(f"{rel}:{lineno}:{line.strip()}")
    return hits


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_strict_command_ledger_reader_isolation_hot"
    before_command_count = -1
    after_command_count = -2
    before_mode_count = -1
    after_mode_count = -2
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
        write_malformed_command_jsonl(command_path)
        before_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        before_mode_count = len(read_mode_state_records(mode_state_path).rows)
        before_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        summary_before = summarize_command_ledger(command_path, max_lines=100).to_dict()
        module, import_exception = import_autotrade_page()
        recent_rows = None
        recent_exception = None
        if module is not None:
            try:
                recent_rows = module._recent_command_rows(limit=5)
            except Exception as exc:
                recent_exception = repr(exc)
        summary_after = summarize_command_ledger(command_path, max_lines=100).to_dict()
        after_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        after_mode_count = len(read_mode_state_records(mode_state_path).rows)
        after_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    ui_text = UI_FILE.read_text(encoding="utf-8")
    command_status_text = COMMAND_STATUS_FILE.read_text(encoding="utf-8")
    applier_text = APPLIER_FILE.read_text(encoding="utf-8")
    strict_hits = strict_reader_usage_hits()
    read_only_sources = {name: function_source(UI_FILE, name) for name in READ_ONLY_UI_FUNCTIONS}
    recent_source = read_only_sources["_recent_command_rows"]
    command_summary_source = function_source(COMMAND_STATUS_FILE, "summarize_command_ledger")
    command_rows_source = function_source(COMMAND_STATUS_FILE, "read_command_ledger_rows")
    checks = {
        "strict_reader_isolated_to_persistence_definition_and_export": strict_hits == [],
        "ui_imports_failsoft_reader_not_strict_reader": FAILSOFT_TOKEN in ui_text and "read_command_ledger," not in ui_text and "read_command_ledger\n" not in ui_text,
        "recent_command_rows_uses_failsoft_reader_with_limit": bool(recent_source) and FAILSOFT_TOKEN in recent_source and "max_lines=limit" in recent_source and STRICT_CALL_TOKEN not in recent_source,
        "command_status_summary_uses_failsoft_rows": bool(command_summary_source) and FAILSOFT_TOKEN in command_summary_source and bool(command_rows_source),
        "applier_uses_failsoft_rows_and_surfaces_skipped_counts": FAILSOFT_TOKEN in applier_text and "command_read.skipped_count" in applier_text and "command_read_skipped_count" in applier_text and STRICT_CALL_TOKEN not in applier_text,
        "read_only_ui_functions_do_not_use_strict_reader_or_append_runner_broker": all(bool(source) and STRICT_CALL_TOKEN not in source and not any(token in source for token in FORBIDDEN_READ_ONLY_TOKENS) for source in read_only_sources.values()),
        "failsoft_dynamic_recent_rows_handles_malformed_line": import_exception is None and recent_exception is None and recent_rows is not None and tuple(row.get("command_id") for row in recent_rows) == ("cmd_da_old_halt", "cmd_da_new_halt"),
        "summary_still_surfaces_skipped_error": summary_before.get("total_rows") == 2 and summary_before.get("skipped_rows") == 1 and tuple(summary_before.get("error_samples") or ()) != () and summary_after.get("skipped_rows") == 1,
        "dynamic_read_only_no_ledger_append": before_command_count == after_command_count == 2 and before_mode_count == after_mode_count == 0 and before_observer_count == after_observer_count,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if import_exception:
        failures.append(f"import_exception: {import_exception}")
    if recent_exception:
        failures.append(f"recent_exception: {recent_exception}")
    failures.extend(f"strict read_command_ledger usage outside allowed boundary: {hit}" for hit in strict_hits)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DA: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_da_strict_command_ledger_reader_isolation_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "strict_reader_isolated_to_persistence_definition_and_export": checks["strict_reader_isolated_to_persistence_definition_and_export"],
            "ui_imports_failsoft_reader_not_strict_reader": checks["ui_imports_failsoft_reader_not_strict_reader"],
            "recent_command_rows_uses_failsoft_reader_with_limit": checks["recent_command_rows_uses_failsoft_reader_with_limit"],
            "command_status_summary_uses_failsoft_rows": checks["command_status_summary_uses_failsoft_rows"],
            "applier_uses_failsoft_rows_and_surfaces_skipped_counts": checks["applier_uses_failsoft_rows_and_surfaces_skipped_counts"],
            "read_only_ui_functions_do_not_use_strict_reader_or_append_runner_broker": checks["read_only_ui_functions_do_not_use_strict_reader_or_append_runner_broker"],
            "failsoft_dynamic_recent_rows_handles_malformed_line": checks["failsoft_dynamic_recent_rows_handles_malformed_line"],
            "summary_still_surfaces_skipped_error": checks["summary_still_surfaces_skipped_error"],
            "dynamic_read_only_no_ledger_append": checks["dynamic_read_only_no_ledger_append"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "strict_hits": strict_hits,
        "summary_before": summary_before,
        "summary_after": summary_after,
        "recent_rows": recent_rows,
        "before_command_count": before_command_count,
        "after_command_count": after_command_count,
        "before_mode_count": before_mode_count,
        "after_mode_count": after_mode_count,
        "before_observer_count": before_observer_count,
        "after_observer_count": after_observer_count,
        "import_exception": import_exception,
        "recent_exception": recent_exception,
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
