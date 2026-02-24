# TESTS
This file documents the current test suites and records the latest script-driven run status.

## Live Prompt Contract Runner (Top Priority)
Command:
```bash
bash runtime/scripts/run_prompt_contract_tests.sh
```
What it does:
- Runs a direct local LLM sanity check (`runtime/scripts/llm_sanity_check.py`).
- Runs live contract tests (`pytest -q -s -m live_contract tests/test_llm_prompt_contract_live.py`).
- Verifies natural-language prompts map to expected tool calls for all tracked skills.
- Updates this file with latest PASS/FAIL status and summary.

## Latest Runner Status
<!-- TEST_RUN_STATUS_START -->

| Runner | Last Status | Last Run (UTC) | Duration | Command | Summary |
|---|---|---|---:|---|---|
| `live_prompt_contract` | `NEVER` | - | - | - | - |
| `unit_pytest` | `PASS` | 2026-02-24 22:15:31Z | 2s | `bash runtime/scripts/run_unit_tests.sh` | 11 passed, 1 skipped in 1.19s |

<!-- TEST_RUN_STATUS_END -->

## Unit / Static Test Runner
Command:
```bash
bash runtime/scripts/run_unit_tests.sh
```
What it does:
- Runs non-live pytest suites under `tests/`.
- Covers routing, tool-selection behavior, and security baseline checks.
- Updates this file with latest PASS/FAIL status and summary.

## Test Files
- `tests/test_llm_prompt_contract_live.py`:
  - Live LLM prompt contracts (`@pytest.mark.live_contract`).
  - Requires local llama.cpp server at `127.0.0.1:8080`.
  - Validates expected skill/tool call selection for 18 contract prompts.
- `tests/test_llm_tool_call_routing.py`:
  - Static routing and selection tests for intent shortlisting and tool slices.
  - Validates dedicated behavior for largest files and directory listing intents.
  - Confirms trace events for tool calls/results exist.
- `tests/test_security_baseline.py`:
  - Enforces safe subprocess usage (no `shell=True` in first-party code).
  - Confirms SSH strict host key checking defaults.
  - Checks localhost bind default for server startup.
  - Ensures default config does not embed Groq API keys.

## Fixtures
- `tests/fixtures/llm_prompt_contracts.yaml`: live prompt -> expected skill/tool contracts.
- `tests/fixtures/llm_tool_call_expectations.yaml`: routing matrix for expected skill families.

## Notes
- Runner status is auto-updated by:
  - `runtime/scripts/run_prompt_contract_tests.sh`
  - `runtime/scripts/run_unit_tests.sh`
- Status metadata source: `runtime/logs/test_runner_status.json`.
