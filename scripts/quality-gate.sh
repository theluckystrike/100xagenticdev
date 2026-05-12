#!/bin/bash
# Quality Gate — Fail-fast pipeline for agent output
# Order: cheapest checks first, most expensive last
set -euo pipefail

echo "=== 1/7 Prettier (format) ==="
npx prettier --check src/

echo "=== 2/7 ESLint (lint, zero warnings) ==="
npx eslint --max-warnings 0 src/

echo "=== 3/7 TypeScript (type check) ==="
npx tsc --noEmit

echo "=== 4/7 Vitest (tests + coverage) ==="
npx vitest run --coverage

echo "=== 5/7 Semgrep (OWASP SAST) ==="
semgrep --config "p/owasp-top-ten" --error src/

echo "=== 6/7 Gitleaks (secret detection) ==="
gitleaks detect --source . --no-git --no-banner

echo "=== 7/7 npm audit (dependency CVEs) ==="
npm audit --audit-level=high

echo ""
echo "=== ALL 7 QUALITY GATES PASSED ==="
