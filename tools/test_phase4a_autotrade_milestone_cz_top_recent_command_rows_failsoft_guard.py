# path: ./tools/test_phase4a_autotrade_milestone_cz_top_recent_command_rows_failsoft_guard.py
# desc: Guard AutoTrade top Critical State recent command rows are fail-soft on malformed command ledger lines. Recent rows use read_command_ledger_rows and remain read-only.

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
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
RECENT_ROWS_FORBIDDEN_TOKENS = (
    "read_command_ledger(",
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
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


def command_row(command_id: str, command_type: str, accepted: bool, requested_at: str, blocker: str, *, target: str | None = "halt_new") -> dict[str, Any]:
    return {
        "ledger_event": "autotrade.command_request_validated",
        "command_id": command_id,
        "accepted": accepted,
        "blocked_by": [blocker] if blocker else [],
        "command": {
            "command_id": command_id,
            "command_type": command_type,
            "requested_by": "operator_ui",
            "requested_at": requested_at,
            "current_mode": "OFF",
            "target": target,
            "confirmation": False,
            "reason_codes": ["guard", "top_recent_command_rows_failsoft", command_id],
            "note": "",
            "confirmation_required": command_type != "REQUEST_HALT_NEW",
        },
    }


def write_malformed_mixed_command_jsonl(path: Path) -> None:
    rows = [
        command_row("cmd_cz_old_halt", "REQUEST_HALT_NEW", True, now_z(-40), ""),
        command_row("cmd_cz_rejected_halt_cancel", "REQUEST_HALT_AND_CANCEL", False, now_z(-30), "confirmation_required", target="halt_and_cancel"),
        command_row("cmd_cz_new_halt", "REQUEST_HALT_NEW", True, now_z(-10), ""),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rows[0], ensure_ascii=False, sort_keys=True) + "\n"
    text += "{not-json\n"
    text += json.dumps(rows[1], ensure_ascii=False, sort_keys=True) + "\n"
    text += json.dumps(rows[2], ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


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


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_top_recent_command_rows_failsoft_hot"
    before_command_count = -1
    after_command_count = -2
    before_mode_count = -1
    after_mode_count = -2
    before_observer_count = 0
    after_observer_count = 0
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
        write_malformed_mixed_command_jsonl(command_path)
        before_command_count = len(read_command_ledger_rows(command_path, max_lines=100).rows)
        before_mode_count = len(read_mode_state_records(mode_state_path).rows)
        before_observer_count = 0 if not observer_path.exists() else len(observer_path.read_text(encoding="utf-8").splitlines())
        summary_before = summarize_command_ledger(command_path, max_lines=100).to_dict()
        module, import_exception = import_autotrade_page()
        recent_limit_5: list[dict[str, Any]] | None = None
        recent_limit_2: list[dict[str, Any]] | None = None
        recent_exception = None
        if module is not None:
            try:
                recent_limit_5 = module._recent_command_rows(limit=5)
                recent_limit_2 = module._recent_command_rows(limit=2)
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

    recent_source = function_source(UI_FILE, "_recent_command_rows")
    checks = {
        "autotrade_page_imports": import_exception is None,
        "recent_command_rows_does_not_raise_on_malformed_line": recent_exception is None,
        "recent_command_rows_returns_only_valid_rows": recent_limit_5 is not None and tuple(row.get("command_id") for row in recent_limit_5) == ("cmd_cz_old_halt", "cmd_cz_rejected_halt_cancel", "cmd_cz_new_halt"),
        "recent_command_rows_respects_limit_on_recent_window": recent_limit_2 is not None and len(recent_limit_2) <= 2 and tuple(row.get("command_id") for row in recent_limit_2) == ("cmd_cz_rejected_halt_cancel", "cmd_cz_new_halt"),
        "command_summary_still_surfaces_skipped_error": summary_before.get("total_rows") == 3 and summary_before.get("skipped_rows") == 1 and tuple(summary_before.get("error_samples") or ()) != () and summary_after.get("skipped_rows") == 1,
        "recent_rows_read_only_no_ledger_append": before_command_count == after_command_count == 3 and before_mode_count == after_mode_count == 0 and before_observer_count == after_observer_count,
        "recent_rows_source_uses_failsoft_reader_not_strict_reader": bool(recent_source) and "read_command_ledger_rows" in recent_source and "max_lines=limit" in recent_source and not any(token in recent_source for token in RECENT_ROWS_FORBIDDEN_TOKENS),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if import_exception:
        failures.append(f"import_exception: {import_exception}")
    if recent_exception:
        failures.append(f"recent_exception: {recent_exception}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone CZ: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_cz_top_recent_command_rows_failsoft_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_page_imports": checks["autotrade_page_imports"],
            "recent_command_rows_does_not_raise_on_malformed_line": checks["recent_command_rows_does_not_raise_on_malformed_line"],
            "recent_command_rows_returns_only_valid_rows": checks["recent_command_rows_returns_only_valid_rows"],
            "recent_command_rows_respects_limit_on_recent_window": checks["recent_command_rows_respects_limit_on_recent_window"],
            "command_summary_still_surfaces_skipped_error": checks["command_summary_still_surfaces_skipped_error"],
            "recent_rows_read_only_no_ledger_append": checks["recent_rows_read_only_no_ledger_append"],
            "recent_rows_source_uses_failsoft_reader_not_strict_reader": checks["recent_rows_source_uses_failsoft_reader_not_strict_reader"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "summary_before": summary_before,
        "summary_after": summary_after,
        "recent_limit_5": recent_limit_5,
        "recent_limit_2": recent_limit_2,
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
