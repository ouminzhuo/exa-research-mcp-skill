"""Run deterministic regression fixtures for renewable-market integrity gates."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "renewable-market-research" / "scripts" / "validate_market_integrity.py"
KOREA_FIXTURE = ROOT / "tests" / "fixtures" / "korea-wind"


EXPECTED_MINIMUM_GAPS = {
    "projectLedgerStateGaps": 1,
    "capacityReconciliationGaps": 1,
    "capacityArithmeticGaps": 1,
    "factFreezeGaps": 1,
    "chapterExternalFactGaps": 1,
    "releaseGaps": 1,
    "scopeDisclosureGaps": 1,
    "unitArithmeticGaps": 1,
    "releaseCleanlinessGaps": 1,
    "numericFieldGaps": 1,
    "oemShareGaps": 1,
    "metricConsistencyGaps": 1,
    "projectStatusConflictGaps": 1
}


def run_korea_fixture_data() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="renewable-regression-") as temp_dir:
        output = Path(temp_dir) / "korea-wind-integrity.json"
        command = [
            sys.executable,
            str(VALIDATOR),
            str(KOREA_FIXTURE / "korea-wind.json"),
            "--phase-state",
            str(KOREA_FIXTURE / "korea-wind-phase_state.json"),
            "--project-ledger",
            str(KOREA_FIXTURE / "korea-wind-project_ledger.json"),
            "--metric-ledger",
            str(KOREA_FIXTURE / "korea-wind-metric_ledger.json"),
            "--capacity-reconciliation",
            str(KOREA_FIXTURE / "korea-wind-capacity_reconciliation.json"),
            "--oem-allocation-ledger",
            str(KOREA_FIXTURE / "korea-wind-oem_allocation_ledger.json"),
            "--canonical-facts",
            str(KOREA_FIXTURE / "korea-wind-canonical_facts.json"),
            "--fact-freeze",
            str(KOREA_FIXTURE / "korea-wind-fact_freeze.json"),
            "--chapter-input-dir",
            str(KOREA_FIXTURE / "chapter_inputs"),
            "--chapter-drafts-dir",
            str(KOREA_FIXTURE / "chapter_drafts"),
            "--audits-dir",
            str(KOREA_FIXTURE / "audits"),
            "--full-report",
            str(KOREA_FIXTURE / "korea-wind-report.md"),
            "--output",
            str(output),
        ]
        completed = subprocess.run(command, cwd=ROOT, check=False, text=True, capture_output=True)
        if completed.returncode == 0:
            raise AssertionError("korea-wind bad fixture unexpectedly passed integrity validation")
        data = json.loads(output.read_text(encoding="utf-8"))
        return data


def run_korea_fixture() -> dict[str, int]:
    data = run_korea_fixture_data()
    summary = data.get("gateSummary", {})
    missing = {
        key: {"expectedAtLeast": expected, "actual": summary.get(key, 0)}
        for key, expected in EXPECTED_MINIMUM_GAPS.items()
        if summary.get(key, 0) < expected
    }
    if missing:
        raise AssertionError(json.dumps({"missingExpectedGaps": missing, "gateSummary": summary}, indent=2))
    return {key: int(summary.get(key, 0)) for key in sorted(EXPECTED_MINIMUM_GAPS)}


def main() -> int:
    summary = run_korea_fixture()
    print(json.dumps({"korea-wind": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
