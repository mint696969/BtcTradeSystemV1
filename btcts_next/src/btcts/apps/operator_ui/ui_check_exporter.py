# path: ./btcts_next/src/btcts/apps/operator_ui/ui_check_exporter.py
# desc: Save one-file GPT-facing Operator UI diagnostics snapshots under tmp/uicheck.

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import os
import platform
import re
import subprocess
import sys

SCHEMA_VERSION = "btcts.operator_ui.uicheck.v2"
UICHK_DIR = Path("tmp/uicheck")
AUTOSAVE_STATE_FILE = UICHK_DIR / "autosave_state.json"
UICHK_MAX_SNAPSHOTS = 10

ENV_WHITELIST = (
    "BTCTS_MARKET", "BTCTS_SYMBOL", "BTCTS_INSTRUMENT_ID",
    "BTCTS_EXECUTION_PRODUCT_CODE", "BTCTS_EXECUTION_MARKET_UID",
    "BTCTS_EXECUTION_MARKET_TYPE", "BTCTS_MARKET_ENGINE_EXCHANGE",
    "BTCTS_MARKET_ENGINE_SYMBOL", "BTCTS_MARKET_ENGINE_INSTRUMENT_ID",
    "BTCTS_MARKET_ENGINE_MARKET_UID", "BTCTS_MARKET_ENGINE_PROFILE",
    "BTCTS_MARKET_ENGINE_WRITE_MARKET_STATE",
    "BTCTS_UNIFIED_MARKET_STATE_ENABLED", "BTC_TS_DATA_DIR",
    "BTC_TS_LOGS_DIR", "BTCTS_DATA_ROOT", "BTCTS_LOGS_ROOT",
    "BTCTS_STATE_ROOT", "BTCTS_WS_SSL_VERIFY", "BTCTS_WS_CA_FILE",
)
SECRET_MARKERS = ("API_KEY", "SECRET", "TOKEN", "PASSWORD", "PASSWD", "COOKIE", "AUTH", "PRIVATE", "CREDENTIAL")


def _repo_root() -> Path:
    return Path.cwd()


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._") or "unknown"


def _is_secret_key(key: object) -> bool:
    upper = str(key or "").upper()
    return any(marker in upper for marker in SECRET_MARKERS)


def _truncate(value: object, limit: int = 1200) -> str:
    text = str(value)
    return text if len(text) <= limit else text[:limit] + f"...<truncated {len(text) - limit} chars>"


def _json_safe(value: Any, *, depth: int = 0, max_items: int = 50) -> Any:
    if depth >= 4:
        return _truncate(repr(value), 400)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _truncate(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= max_items:
                out["<truncated>"] = f"remaining items omitted after {max_items}"
                break
            out[str(key)] = "<redacted>" if _is_secret_key(key) else _json_safe(item, depth=depth + 1, max_items=max_items)
        return out
    if isinstance(value, (list, tuple, set, frozenset)):
        seq = list(value)
        out = [_json_safe(item, depth=depth + 1, max_items=max_items) for item in seq[:max_items]]
        if len(seq) > max_items:
            out.append(f"<truncated {len(seq) - max_items} items>")
        return out
    return {"type": type(value).__name__, "repr": _truncate(repr(value), 400)}


def _run_git(repo_root: Path, args: Sequence[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(["git", *args], cwd=str(repo_root), text=True, capture_output=True, timeout=3, check=False)
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": _truncate(completed.stdout.strip(), 6000),
            "stderr": _truncate(completed.stderr.strip(), 2000),
        }
    except Exception as exc:
        return {"ok": False, "error": repr(exc)}


def _repo_snapshot(repo_root: Path) -> dict[str, Any]:
    branch = _run_git(repo_root, ["branch", "--show-current"])
    head = _run_git(repo_root, ["rev-parse", "--short", "HEAD"])
    status = _run_git(repo_root, ["status", "--short"])
    return {
        "root": str(repo_root),
        "branch": branch.get("stdout") if branch.get("ok") else None,
        "head": head.get("stdout") if head.get("ok") else None,
        "status_short": status.get("stdout", "").splitlines() if status.get("ok") else [],
        "git_errors": {
            "branch": None if branch.get("ok") else branch,
            "head": None if head.get("ok") else head,
            "status": None if status.get("ok") else status,
        },
    }

def _env_snapshot() -> dict[str, Any]:
    env = {key: os.environ.get(key) for key in ENV_WHITELIST if os.environ.get(key) is not None}
    return {
        "whitelist": env,
        "execution_market": {
            "product_code": os.environ.get("BTCTS_EXECUTION_PRODUCT_CODE") or os.environ.get("BTCTS_SYMBOL"),
            "market_uid": os.environ.get("BTCTS_EXECUTION_MARKET_UID") or os.environ.get("BTCTS_INSTRUMENT_ID"),
            "market_type": os.environ.get("BTCTS_EXECUTION_MARKET_TYPE") or os.environ.get("BTCTS_MARKET"),
            "symbol": os.environ.get("BTCTS_SYMBOL"),
            "read_only": True,
            "would_send_to_broker": False,
        },
        "roots": {
            "data": os.environ.get("BTCTS_DATA_ROOT") or os.environ.get("BTC_TS_DATA_DIR"),
            "logs": os.environ.get("BTCTS_LOGS_ROOT") or os.environ.get("BTC_TS_LOGS_DIR"),
            "state": os.environ.get("BTCTS_STATE_ROOT"),
        },
    }


def load_gpt_ui_check_auto_save_enabled() -> bool:
    state_path = _repo_root() / AUTOSAVE_STATE_FILE
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return False
    except Exception:
        return False
    return bool(payload.get("enabled")) if isinstance(payload, dict) else False


def save_gpt_ui_check_auto_save_enabled(enabled: bool) -> str:
    out_dir = _repo_root() / UICHK_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    state_path = _repo_root() / AUTOSAVE_STATE_FILE
    payload = {
        "schema_version": "btcts.operator_ui.uicheck.autosave_state.v1",
        "enabled": bool(enabled),
        "updated_at": datetime.now(timezone.utc).astimezone().isoformat(),
    }
    state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(state_path)


def _session_state_snapshot(session_state: Mapping[str, Any]) -> dict[str, Any]:
    keys = sorted(str(key) for key in session_state.keys())
    selected: dict[str, Any] = {}
    prefixes = ("ui_", "_ui_", "_live_shell_", "warroom_", "health_", "collector_", "ai_operator_")
    for key in keys:
        if _is_secret_key(key):
            selected[key] = "<redacted>"
        elif key.startswith(prefixes):
            try:
                selected[key] = _json_safe(session_state.get(key))
            except Exception as exc:
                selected[key] = {"type": "<snapshot_error>", "repr": repr(exc)}
    return {"key_count": len(keys), "keys": keys, "selected_safe_values": selected}


def prune_gpt_ui_check_snapshots(
    *,
    out_dir: Path | None = None,
    keep: int = UICHK_MAX_SNAPSHOTS,
) -> list[str]:
    """Delete old UI Check snapshots while preserving management files."""
    if keep < 1:
        raise ValueError("keep must be at least 1")

    target_dir = out_dir or (_repo_root() / UICHK_DIR)
    snapshots = sorted(
        (path for path in target_dir.glob("uicheck_*.json") if path.is_file()),
        key=lambda path: path.name,
        reverse=True,
    )

    deleted: list[str] = []
    for path in snapshots[keep:]:
        path.unlink()
        deleted.append(str(path))
    return deleted


def save_gpt_ui_check_snapshot(
    *,
    page_key: str,
    page_label: str,
    previous_page_key: str | None,
    page_changed: bool,
    refresh_plan: Mapping[str, Any],
    session_state: Mapping[str, Any],
    slot_registry: Sequence[Mapping[str, Any]],
    page_render_ms: int | None = None,
    human_note: str = "",
) -> str:
    repo_root = _repo_root()
    out_dir = repo_root / UICHK_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).astimezone()
    timestamp = now.strftime("%Y%m%d_%H%M%S_%f")
    out_path = out_dir / f"uicheck_{timestamp}_{_safe_name(page_key)}.json"
    if out_path.exists():
        raise FileExistsError(f"uicheck output already exists: {out_path}")

    env_snapshot = _env_snapshot()
    component_timing = _json_safe(session_state.get("_ui_render_timing_ms") or {})
    payload = {
        "schema_version": SCHEMA_VERSION,
        "created_at": now.isoformat(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "One-file GPT-facing Operator UI diagnostic snapshot. Safe to upload.",
        "page": {
            "selected_page_key": str(page_key),
            "selected_page_label": str(page_label),
            "previous_page_key": str(previous_page_key or ""),
            "page_changed": bool(page_changed),
        },
        "runtime_env": env_snapshot,
        "ui_state": {
            "ui_lang": session_state.get("ui_lang"),
            "ui_scale": session_state.get("ui_scale"),
            "ui_auto_refresh": session_state.get("ui_auto_refresh"),
            "ui_refresh_interval": session_state.get("ui_refresh_interval"),
            "refresh_plan": _json_safe(dict(refresh_plan)),
            "stale_policy_note": {
                "same_page_keep_previous_content": "desired during live rerender",
                "page_transition_clear_previous_content": "desired when page_changed=true",
            },
        },
        "session_state_safe": _session_state_snapshot(session_state),
        "slot_registry": [_json_safe(dict(row)) for row in slot_registry],
        "render_timing_ms": {
            "page_total": page_render_ms,
            "component_breakdown": component_timing,
        },
        "repo": _repo_snapshot(repo_root),
        "system": {"platform": platform.platform(), "python": sys.version, "cwd": str(Path.cwd())},
        "data_sources": {
            "note": "uicheck v1 avoids heavy file scans and does not read market data payloads.",
            "roots": env_snapshot["roots"],
        },
        "errors": {"exceptions": [], "warnings": []},
        "human_note": str(human_note or ""),
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    prune_gpt_ui_check_snapshots(out_dir=out_dir, keep=UICHK_MAX_SNAPSHOTS)
    return str(out_path)
