# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q23S_SILENT_LAUNCHER_NO_WINDOW_SUBPROCESS_PATCH_2026-06-29.md
# desc: PS-Q23S suppress transient console windows from Q22X/Q22S child subprocesses.
# PS-Q23S silent launcher no-window subprocess patch

Updated: 2026-06-29 JST
Base: Q22X pythonw silent scheduler launcher, Q23Q/R scheduled distributed sidecar + compact legacy steady state
Mode: scheduler launcher code fix / no scheduler action replacement

```text
ps_q23s_silent_launcher_no_window_subprocess_patch=true
scheduler_action_changed=false
q22x_pythonw_action_retained=true
subprocess_child_console_windows_suppressed=true
uses_create_no_window=true
uses_sw_hide_startupinfo=true
broker_autotrade=false
```

## Problem

The scheduled task action already runs `pythonw.exe`, but the Q22X/Q22S scheduled tick invokes child processes through `subprocess`, including clean-tree checks such as `git status`. A GUI parent process without a console can cause Windows console subsystem children to briefly create visible console windows.

Observed symptom: every scheduled tick, many transient PowerShell/Windows Terminal-like windows open and close for tens of seconds.

## Fix

Install a process-local monkey patch in `run_phase4a_prediction_system_ps_q22x_silent_q22s_launcher.py` before invoking Q22S. On Windows, all `subprocess.Popen` calls inside the scheduled launcher process receive:

```text
creationflags |= CREATE_NO_WINDOW
startupinfo.dwFlags |= STARTF_USESHOWWINDOW
startupinfo.wShowWindow = SW_HIDE
```

This keeps the existing scheduler action unchanged and suppresses child console windows across Q22S/Q21I/Q23B/readiness helper subprocess calls.

## Safety boundaries

```text
scheduler_action_changed=false
scheduler_enabled_by_this_tool=false
trigger_added=false
latest_prediction_artifact_write_behavior_changed=false
latest_manifest_sidecar_behavior_changed=false
broker_private_api_allowed=false
autotrade_trigger_allowed=false
approval_or_ledger_allowed=false
parameter_apply_allowed=false
parameter_staging_write_allowed=false
would_send_to_broker=false
```
