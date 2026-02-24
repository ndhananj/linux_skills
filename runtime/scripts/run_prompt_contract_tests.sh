#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

if ! command -v pytest >/dev/null 2>&1; then
  echo "pytest is required. Install with: pip install -r runtime/requirements.txt pytest"
  exit 1
fi

echo "Running live LLM prompt contract tests against http://127.0.0.1:8080 ..."
echo "This validates natural-language prompts -> expected tool calls for all skills."

RUN_LLM_PROMPT_CONTRACT=1 pytest -q tests/test_llm_prompt_contract_live.py "$@"
