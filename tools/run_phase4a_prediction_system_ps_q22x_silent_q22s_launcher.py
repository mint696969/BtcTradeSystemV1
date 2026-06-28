# path: ./tools/run_phase4a_prediction_system_ps_q22x_silent_q22s_launcher.py
# desc: PS-Q22X silent launcher for Q22S scheduled tick. Use with pythonw.exe; redirects stdout/stderr to D-hot logs.

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import traceback
from typing import Any
import uuid

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_phase4a_prediction_system_ps_q21i_one_shot_bounded_manual_latest_prediction_write import DEFAULT_HOT_ROOT  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once import main as q22s_main  # noqa: E402

LAUNCHER_VERSION = "prediction_warroom.silent_q22s_scheduler_launcher.ps_q22x.v1"
LOG_DIR = DEFAULT_HOT_ROOT / "prediction/logs/q22x_silent_scheduler_launcher"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _log_path() -> Path:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    day = now.strftime("%Y%m%d")
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    return LOG_DIR / day / f"q22x_silent_q22s_{stamp}_{uuid.uuid4().hex[:8]}.log"


def _event(event: str, **extra: Any) -> str:
    payload = {"event": event, "launcher_version": LAUNCHER_VERSION, "generated_at": _utc_now(), **extra}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)


def run_silent_q22s(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", buffering=1) as log:
        with redirect_stdout(log), redirect_stderr(log):
            print(_event("q22x_silent_launcher_start", argv=args, log_path=str(path)))
            try:
                rc = int(q22s_main(args))
                print(_event("q22x_silent_launcher_finish", returncode=rc))
                return rc
            except SystemExit as exc:
                code = int(exc.code or 0) if isinstance(exc.code, int) else 1
                print(_event("q22x_silent_launcher_system_exit", returncode=code))
                return code
            except Exception as exc:  # noqa: BLE001 - scheduled launcher must log unexpected failures
                print(_event("q22x_silent_launcher_exception", exception_class=exc.__class__.__name__, exception_message=str(exc)))
                traceback.print_exc()
                return 1


def main(argv: list[str] | None = None) -> int:
    return run_silent_q22s(argv)


if __name__ == "__main__":
    raise SystemExit(main())
