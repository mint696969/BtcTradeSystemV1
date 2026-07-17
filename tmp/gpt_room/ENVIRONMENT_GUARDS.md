# path: ./tmp/gpt_room/ENVIRONMENT_GUARDS.md
# desc: Persistent cross-thread environment hazards and mandatory prevention checks.

# Environment Guards

Updated: 2026-07-17 JST
Status: current and binding

## Purpose

This file records only recurring, environment-dependent hazards that can affect unrelated work across threads.
Do not add task-specific bugs, one-off implementation mistakes, temporary failures, or domain decisions here.

At task startup, read this file before creating patch runners or generated source files.
When a new recurring environment hazard is confirmed, add the smallest reusable prevention rule and guard command.

## 1. Windows path-length guard

Hazard:

- Windows environments may fail with `FileNotFoundError` when a generated artifact path plus atomic-write temporary suffix becomes too long.
- A parent directory may exist and the error may still appear because the final temporary path exceeds the effective path limit.

Mandatory prevention:

- Keep generated filenames compact; prefer bounded digests such as 24-32 hex characters unless a formal contract requires more.
- Validate the full effective path, including `.tmp.<pid>` or lock suffixes used by shared I/O helpers.
- Do not modify shared atomic I/O merely to accommodate one oversized artifact name.
- Preserve full identity inside the payload even when the filename digest is shortened.
- Add a Windows-safe filename/path-length test for new generated artifact families.

## 2. Generated-code escaping guard

Hazard:

- Patch runners that embed Python, JSON, regex, Windows paths, backslashes, or newline literals can silently generate invalid source.
- Typical failures include unterminated string literals, collapsed `\` guards, and accidental literal newlines inside quoted strings.

Mandatory prevention:

- Prefer rebuilding an apply runner from verified current files over brittle partial-string replacement.
- Use raw triple-quoted literals only after checking that embedded content does not contain the chosen delimiter.
- After applying a runner, always `py_compile` every generated Python file before pytest.
- Re-run the apply runner and require `[ALREADY APPLIED]` to prove idempotency.
- When a fix changes generated files, synchronize the original apply runner so it cannot recreate the defect.
- Read back the complete runner before presenting it; verify that embedded content does not contain the selected triple-quote delimiter.
- Do not create a helper runner whose purpose is to mutate another runner. Keep one canonical apply runner per slice.

## 3. Repository file-header guard

Hazard:

- Repository Python and project-document files may require the canonical first two header lines.
- Cross-thread work can forget this convention when creating new files.

Mandatory prevention:

For applicable new files, preserve these first two lines:

```text
# path: ./repo/relative/path
# desc: concise responsibility description
```

Guard the exact first two lines in focused tests or structural checks when adding a new file family.
Do not add the header to formats whose syntax does not permit comments or where an existing formal contract forbids it.

## 4. Fail-fast PowerShell execution guard

Hazard:

- Running multiple commands without checking `$LASTEXITCODE` can continue after a failed compile or test and hide the first causal error.

Mandatory prevention:

- Use the shared `Invoke-Step` fail-fast pattern.
- Order checks as: runner compile, apply, generated-file compile, focused tests, impacted tests, `git diff --check`, `git status --short`.
- Stop at the first failure, inspect the actual generated files, and create a minimal `fix_<slice>.py`.


<!-- ROOM_ENVIRONMENT_GUARDS_2026_07_17 -->
## 5. Interactive PowerShell session-preservation guard

Hazard:

- `exit` inside a function, pasted block, or directly invoked script can terminate the user's current terminal instead of stopping only the failed work sequence.
- Invoking legacy `powershell.exe` from a PowerShell 7 workflow can introduce different native stderr and error-record behavior.

Mandatory prevention:

- Never put `exit` in user-pasted interactive command blocks or shared `Invoke-Step` helpers.
- For a `.ps1` guard script, use `throw` inside steps and one top-level `try/catch/finally`; the catch must print the failure and log path without closing the parent terminal.
- Prefer the active `pwsh` 7 host. Do not switch to `powershell.exe` 5.1 unless the compatibility difference is the explicit test target.
- A child `pwsh -File` process may return non-zero, but the parent terminal must remain open and the log path must still be printed.
- Do not depend on `$ErrorActionPreference` to interpret native process success. Capture `$LASTEXITCODE` immediately after each native command.

## 6. PowerShell parsing and expected-failure process guard

Hazard:

- Backslash (`\`) is not a PowerShell line-continuation character. Misusing it can split parameters into separate commands and may trigger unrelated application or Explorer behavior through Windows command or file association handling.
- `Start-Process` adds another parsing layer and is unsuitable as a generic verifier for a CLI that is expected to fail.
- Native stderr behavior differs across PowerShell versions and can prevent the intended return-code assertion from running.

Mandatory prevention:

- Never use `\` for PowerShell line continuation. Prefer splatting or argument arrays; use the backtick only when unavoidable.
- Before presenting a generated `.ps1`, read back the whole file and parse it without execution using the PowerShell parser API.
- Use `Start-Process` only when process-launch semantics are themselves under test.
- For an expected-failure Python CLI, prefer a small Python verifier using `subprocess.run(..., capture_output=True, check=False)`. Assert both a non-zero return code and an explicit fail-closed marker.
- Do not use shell association, `Invoke-Item`, `Start`, or bare path execution in guard scripts.
- Long output must be written under `tmp/work/<slice>/logs/`; console output should contain only the bounded summary and exact log paths.

## 7. Patch-runner handoff guard

Hazard:

- A second helper script that edits an apply runner creates nested quoting and replacement layers. This can generate a runner that fails before it reaches the repository and makes the canonical patch source ambiguous.

Mandatory prevention:

- Maintain one canonical `apply_<slice>.py` runner per slice. Rewrite that runner directly instead of creating `extend_runner`, `patch_runner`, or runner-mutating helper scripts.
- Read back the complete runner after writing it and inspect every embedded delimiter before giving the user an execution command.
- Do not nest the same triple-quote delimiter inside generated source text. Change delimiters or construct the content from explicitly verified pieces.
- The user-visible sequence must begin with `python -m py_compile <apply_runner>` and stop there on failure.
- After application, compile every generated Python file, run focused guards, rerun the apply runner, and require `[ALREADY APPLIED]` before commit qualification.

## 8. Logging rule

Add a new item only when all are true:

1. The cause is environment/tooling/repository-convention dependent.
2. It can recur in unrelated slices or future threads.
3. A concrete preventive rule or guard can be stated.
4. The rule does not duplicate an existing entry.

Do not record:

- business-logic defects
- family-specific prediction behavior
- temporary test-data mistakes
- one-off typos without a reusable environment lesson
- resolved implementation details already enforced by tests
<!-- GPT_ROOM_GIT_DURABILITY_GUARD_2026_07_17 -->
## 9. gpt_room durability guard

Hazard:

- `tmp/gpt_room` is operationally persistent but lives under the normally ignored `tmp/` workspace.
- Without selective Git tracking and remote replication, disk loss removes cross-thread project memory even when source code is recoverable.

Mandatory prevention:

- Do not move `tmp/gpt_room`; Actions and bootstrap resolve this path.
- Track only the canonical files in `config/gpt_room_tracked_files.json`.
- Keep generated/reference indexes, history, room backups, self-tests, logs, caches, and patch runners ignored.
- Run `python scripts/check_gpt_room_persistence.py` after room updates and before commit.
- Include expected tracked room changes in the same commit as the checkpoint or policy change they describe.
- Push the commit to an independent remote or backup target before claiming disaster-recovery durability.
