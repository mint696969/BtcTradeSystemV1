# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q22X_SILENT_SCHEDULER_LAUNCHER_2026-06-28.md
# desc: PS-Q22X silent Windows scheduled launcher for Q22S using pythonw.exe with log redirection.
# PS-Q22X silent scheduler launcher

Updated: 2026-06-28 JST
Base: Q22W recurring refresh stable, but visible console window appears every 5 minutes.

```text
ps_q22x_silent_scheduler_launcher=true
uses_pythonw_exe=true
redirects_stdout_stderr_to_d_hot_log=true
scheduler_action_replacement_explicit_only=true
trigger_addition_executed=false
broker_autotrade=false
```

## Why

The current Windows Scheduled Task starts `.venv\\Scripts\\python.exe` directly. Because `python.exe` is a console application, a small shell window appears at every scheduled invocation.

PS-Q22X introduces a silent launcher:

```text
Task Scheduler -> pythonw.exe -> Q22X silent launcher -> Q22S actual tick
```

The launcher redirects stdout/stderr to D-hot logs before calling Q22S, so Q22S can continue to print its JSON result without requiring a visible console window.

## Safety

The repo patch does not modify the scheduler. The actual switch is a separate exact-token action replacement runner. It preserves the existing trigger, cadence, and Q22S semantics. It does not call broker, AutoTrade, ledger, or parameter apply.
