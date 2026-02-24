#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

if ! command -v pytest >/dev/null 2>&1; then
  echo "pytest is required. Install with: pip install -r runtime/requirements.txt pytest"
  exit 1
fi

echo "Running unit and routing tests..."

START_TS="$(date +%s)"
TMP_OUT="$(mktemp)"
RC=0

pytest -q tests 2>&1 | tee "$TMP_OUT"
PYTEST_RC=${PIPESTATUS[0]}
if [[ $PYTEST_RC -ne 0 ]]; then
  RC=$PYTEST_RC
fi

END_TS="$(date +%s)"
DURATION=$((END_TS - START_TS))
SUMMARY="$(grep -E '[0-9]+ (passed|failed|skipped|error|errors)' "$TMP_OUT" | tail -n 1 || true)"
if [[ -z "${SUMMARY}" ]]; then
  SUMMARY="pytest exit code=${PYTEST_RC}"
fi

STATUS="PASS"
if [[ $RC -ne 0 ]]; then
  STATUS="FAIL"
fi

python3 runtime/scripts/update_tests_md.py \
  --repo-root "$REPO_ROOT" \
  --runner "unit_pytest" \
  --status "$STATUS" \
  --command "bash runtime/scripts/run_unit_tests.sh" \
  --duration-s "$DURATION" \
  --summary "$SUMMARY"

rm -f "$TMP_OUT"
exit $RC

