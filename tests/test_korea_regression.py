"""Named regression tests for known Korea wind full-report failure modes."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR))

from run_regression_fixtures import KOREA_FIXTURE, run_korea_fixture_data  # noqa: E402


class KoreaWindRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_korea_fixture_data()
        cls.summary = cls.result.get("gateSummary", {})
        cls.report_text = (KOREA_FIXTURE / "korea-wind-report.md").read_text(encoding="utf-8")

    def assert_gap(self, key: str) -> list[dict]:
        gaps = self.result.get(key, [])
        self.assertTrue(gaps, f"expected {key} to contain at least one gap")
        return gaps

    def test_scope_split_230_vs_96(self) -> None:
        self.assertIn("全国海风装机：230MW，截至2024年底", self.report_text)
        self.assertIn("韩国运营海风：96MW", self.report_text)
        gaps = self.assert_gap("scopeDisclosureGaps")
        self.assertTrue(any("韩国运营海风：96MW" in gap.get("text", "") for gap in gaps))

    def test_reject_340_as_end_2024(self) -> None:
        gaps = self.assert_gap("metricConsistencyGaps")
        self.assertTrue(any(gap.get("metricId") == "KOR-OFFSHORE-NATIONAL-2024" for gap in gaps))

    def test_oem_share_above_100(self) -> None:
        gaps = self.assert_gap("oemShareGaps")
        self.assertTrue(any(float(gap.get("sharePercentTotal", 0)) > 100 for gap in gaps))

    def test_expired_oem_active_project(self) -> None:
        gaps = self.assert_gap("projectLedgerStateGaps")
        self.assertTrue(
            any(
                gap.get("projectId") == "KOR-EXPIRED-OEM-ACTIVE"
                and "OEM relationship should flow to unallocated_mw" in gap.get("issue", "")
                for gap in gaps
            )
        )

    def test_auction_1786_vs_identified_1626(self) -> None:
        gaps = self.assert_gap("capacityArithmeticGaps")
        self.assertTrue(
            any(
                gap.get("field") == "unresolvedGapMW"
                and gap.get("officialAuctionTotalMW") == 1786.0
                and gap.get("identifiableProjectCapacityMW") == 1626.0
                and gap.get("computedUnresolvedGapMW") == 160.0
                for gap in gaps
            )
        )

    def test_geumodo_status_conflict(self) -> None:
        gaps = self.assert_gap("projectStatusConflictGaps")
        self.assertTrue(
            any(
                gap.get("projectId") == "KOR-EXPIRED-OEM-ACTIVE"
                and {"active", "paused"}.issubset(set(gap.get("statuses", [])))
                for gap in gaps
            )
        )

    def test_krw_750_vs_7500(self) -> None:
        gaps = self.assert_gap("unitArithmeticGaps")
        self.assertTrue(any("KRW 750亿" in gap.get("text", "") for gap in gaps))

    def test_release_deletion_markup(self) -> None:
        gaps = self.assert_gap("releaseCleanlinessGaps")
        pattern_ids = {gap.get("pattern") for gap in gaps}
        self.assertIn("html_deletion_tag", pattern_ids)
        self.assertIn("todo", pattern_ids)

    def test_chapter_external_fact(self) -> None:
        gaps = self.assert_gap("chapterExternalFactGaps")
        self.assertTrue(
            any("KOR-EXTERNAL-METRIC" in gap.get("externalIds", []) for gap in gaps)
        )

    def test_stale_freeze_id(self) -> None:
        gaps = self.assert_gap("releaseGaps")
        self.assertTrue(
            any(
                gap.get("freezeId") == "freeze-kor-old"
                and gap.get("expectedFreezeId") == "freeze-kor-001"
                for gap in gaps
            )
        )


if __name__ == "__main__":
    unittest.main()
