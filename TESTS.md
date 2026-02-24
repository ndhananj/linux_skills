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

Detailed behavior:
- Requires local llama.cpp server reachable at `http://127.0.0.1:8080`.
- Prints progress for each contract case as:
  - `start id=<case> tools=<n>`
  - `done id=<case> latency=<s> calls=[...]`
- For each case, asserts:
  - At least one tool call is produced.
  - At least one call belongs to the expected skill family (`<skill>__*`).
  - At least one call matches `expected_any_tools` for that case.
- Writes PASS/FAIL + duration + summary into the `Latest Runner Status` table below.

Prompts covered by `run_prompt_contract_tests.sh` (from `tests/fixtures/llm_prompt_contracts.yaml`):
1. `boot_and_kernel`: "Check this host kernel version and show currently loaded kernel modules."
2. `containerization`: "List Docker containers and images on this machine."
3. `file_system`: "Find files larger than 50MB under /var/log and show disk usage for /var."
4. `iac_and_cicd`: "In this working directory, run Terraform init then Terraform plan."
5. `logging`: "Show the last 50 lines of syslog and then view recent journal entries."
6. `networking`: "Show current interfaces and routing table, then do a DNS lookup for openai.com."
7. `package_management`: "Update apt metadata and search for nginx packages."
8. `performance`: "Show CPU, memory, and top CPU-consuming processes right now."
9. `process_and_service`: "Check ssh service status and list the top running processes."
10. `scheduling`: "List current cron jobs and active systemd timers."
11. `security`: "Check UFW status and list current iptables rules."
12. `shell_scripting`: "Create a simple shell script that prints disk usage and check its syntax."
13. `ssh`: "Generate a new SSH key and display SSH client configuration."
14. `storage`: "List block devices and mounted filesystems, then show swap usage."
15. `text_processing`: "Sort lines in a file and count unique lines in the result."
16. `troubleshooting`: "Troubleshoot DNS by checking name resolution and testing connectivity to 8.8.8.8."
17. `user_and_group`: "Show user info for root and list groups on this system."
18. `version_control`: "Show git status and recent git log in this repository."

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
