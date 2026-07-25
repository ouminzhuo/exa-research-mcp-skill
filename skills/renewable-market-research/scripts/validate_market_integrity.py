#!/usr/bin/env python3
"""Validate source-to-final integrity for renewable market JSON outputs."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

SOURCE_FIELD_ALIASES = [
    ("url",),
    ("title",),
    ("publisher",),
    ("accessedAt", "accessed_at"),
    ("sourceLanguage", "source_language"),
    ("collectionMethod", "collection_method"),
]

PROJECT_NAME_FIELDS = ("canonicalProjectName", "canonicalName", "projectName", "canonical_name", "project_name", "name")
PROJECT_ID_FIELDS = ("projectId", "canonicalProjectId", "canonical_project_id", "id", "project_id")
DEDUP_FIELD_ALIASES = ("dedupeKey", "dedupe_key")
SOURCE_TRACE_ALIASES = ("sourceTrace", "source_trace")
NAME_VARIANT_ALIASES = ("nameVariants", "name_variants", "aliases")
VERIFIED_COLLECTION_METHODS = {"chrome-mcp", "exa-fetch", "manual-file"}
CRITICAL_FIELD_VERIFICATION_ALIASES = ("criticalFieldVerification", "critical_field_verification")
UNKNOWN_ALLOWED_MARKERS = {"待核", "待核实", "未公开", "未披露", "not found", "unavailable", "not applicable", "unknown"}
DEVELOPMENT_STAGES = {
    "operational",
    "partial_operation",
    "under_construction",
    "construction_ready",
    "financial_close",
    "contracted",
    "auction_awarded",
    "permitted",
    "pre_auction",
    "early_development",
    "watchlist",
    "unverified",
}
ACTIVITY_STATUSES = {"active", "delayed", "paused", "withdrawn", "cancelled", "superseded", "unknown"}
INACTIVE_ACTIVITY_STATUSES = {"paused", "withdrawn", "cancelled", "superseded"}
LEDGER_TREATMENTS = {"confirmed", "watchlist", "duplicate", "rejected", "unresolved"}
CAPACITY_TREATMENTS = {
    "confirmed_capacity",
    "opportunity_capacity",
    "watchlist_capacity",
    "excluded_inactive",
    "excluded_duplicate",
    "excluded_unverified",
    "policy_target_only",
    "auction_total_only",
}
PROJECT_CAPACITY_TREATMENTS = CAPACITY_TREATMENTS
OEM_CAPACITY_TREATMENTS = {
    "firm_mw",
    "committed_mw",
    "influenced_mw",
    "unallocated_mw",
    "excluded_inactive_mw",
    "unknown",
}
CAPACITY_SCOPES = {
    "official_auction_total",
    "identifiable_project_capacity",
    "confirmed_project_capacity",
    "opportunity_capacity",
    "watchlist_capacity",
    "suspended_or_paused_capacity",
    "national_policy_target",
    "draft_or_political_target",
    "unknown",
}
OEM_RELATIONSHIP_TYPES = {
    "firm_supply_contract",
    "preferred_supplier",
    "conditional_reservation_or_cra",
    "framework_agreement",
    "technology_partnership",
    "reported_preference",
    "unallocated",
    "unknown",
}
OEM_RELATIONSHIP_STATUSES = {"active", "conditional", "expired", "terminated", "superseded", "disputed", "unknown"}
FIRM_OEM_TYPES = {"firm_supply_contract"}
COMMITTED_OEM_TYPES = {"preferred_supplier", "conditional_reservation_or_cra"}
INFLUENCED_OEM_TYPES = {"framework_agreement", "technology_partnership", "reported_preference"}
UNALLOCATED_OEM_TYPES = {"unallocated", "unknown"}
ACTIVE_OEM_STATUSES = {"active"}
COUNTABLE_OEM_STATUSES = {"active", "conditional", "unknown"}
EXCLUDED_OEM_STATUSES = {"expired", "terminated", "superseded"}
FACT_PROFILE_DEFAULTS = {
    "wind_full_report": {
        "requiredFactTypes": [
            "confirmed_project_capacity_mw",
            "opportunity_mw",
            "watchlist_mw",
            "capacity_scope_definition",
            "project_status_definition",
            "oem_status_definition",
        ],
        "conditionalFactTypes": [
            "official_auction_total_mw",
            "identifiable_project_capacity_mw",
            "suspended_or_paused_mw",
            "enacted_policy_target",
            "draft_target",
            "political_statement_target",
            "auction_allocation",
            "oem_firm_order",
            "oem_preferred_supplier",
            "oem_conditional_reservation_or_cra",
            "oem_framework_agreement",
            "oem_technology_partnership",
            "oem_reported_preference",
            "oem_unallocated",
            "paused_or_suspended_project",
        ],
        "notApplicableFactTypes": [],
    }
}
PROJECT_LEDGER_NUMERIC_FIELDS = (
    "capacityMW",
    "opportunityMW",
    "oemExposureMW",
    "officialAuctionTotalMW",
    "identifiableProjectCapacityMW",
    "confirmedCapacityMW",
    "opportunityCapacityMW",
    "watchlistCapacityMW",
    "suspendedOrPausedMW",
    "excludedInactiveMW",
    "firmMW",
    "committedMW",
    "influencedMW",
    "unallocatedMW",
)
METRIC_LEDGER_NUMERIC_FIELDS = ("value",)
CAPACITY_RECONCILIATION_NUMERIC_FIELDS = (
    "officialAuctionTotalMW",
    "identifiableProjectCapacityMW",
    "unresolvedGapMW",
    "confirmedCapacityMW",
    "opportunityCapacityMW",
    "watchlistCapacityMW",
    "excludedInactiveMW",
    "firmMW",
    "committedMW",
    "influencedMW",
    "unallocatedMW",
)
OEM_ALLOCATION_NUMERIC_FIELDS = ("mw", "sharePercent")
V4_LEDGER_REQUIRED_FIELDS = [
    "projectId",
    "aliasGroupId",
    "canonicalProjectName",
    "capacityMW",
    "opportunityMW",
    "developmentStage",
    "activityStatus",
    "ledgerTreatment",
    "projectCapacityTreatment",
    "oemCapacityTreatment",
    "capacityScope",
    "statusBasis",
    "countedInConfirmedCapacity",
    "countedInOpportunityCapacity",
    "sponsorOwner",
    "spv",
    "equityStructure",
    "oem",
    "oemRelationshipType",
    "oemRelationshipStatus",
    "procurementStatus",
    "turbineModel",
    "epc",
    "omParty",
    "financiers",
    "ppaOfftaker",
    "tariff",
    "codTimeline",
    "nextMilestone",
    "decisionMaker",
    "keyEvidence",
    "fieldConfidence",
    "pendingVerification",
    "mingyangRelevance",
    "mainRisks",
]
V4_PROJECT_CARD_REQUIRED_PATHS = [
    "basicInformation.projectName",
    "basicInformation.capacityMW",
    "basicInformation.location",
    "basicInformation.stage",
    "basicInformation.developmentStage",
    "basicInformation.activityStatus",
    "basicInformation.ledgerTreatment",
    "basicInformation.projectCapacityTreatment",
    "basicInformation.cod",
    "ownerStructure.developer",
    "ownerStructure.spv",
    "ownerStructure.equity",
    "ownerStructure.governmentCounterparty",
    "technicalPlan.oem",
    "technicalPlan.oemRelationshipType",
    "technicalPlan.oemRelationshipStatus",
    "technicalPlan.oemCapacityTreatment",
    "technicalPlan.turbineModel",
    "technicalPlan.turbineCount",
    "technicalPlan.bess",
    "technicalPlan.transmissionLine",
    "commercialStructure.ppa",
    "commercialStructure.offtaker",
    "commercialStructure.tariff",
    "commercialStructure.tenor",
    "commercialStructure.guarantee",
    "financingStructure.totalInvestment",
    "financingStructure.lenders",
    "financingStructure.financialCloseStatus",
    "developmentFlow.land",
    "developmentFlow.esia",
    "developmentFlow.interconnection",
    "developmentFlow.constructionPermit",
    "developmentFlow.electricityLicense",
    "engineeringSupplyChain.epc",
    "engineeringSupplyChain.logistics",
    "engineeringSupplyChain.lifting",
    "engineeringSupplyChain.localizationRequirements",
    "omArrangement.omParty",
    "omArrangement.serviceTenor",
    "omArrangement.spareParts",
    "omArrangement.localServiceBase",
    "currentProgress.latestEvent",
    "currentProgress.nextNode",
    "currentProgress.procurementWindow",
    "decisionChain.decisionMaker",
    "decisionChain.influencers",
    "decisionChain.mdbGovernmentEpcRoles",
    "mingyangRelevance.opportunityMW",
    "mingyangRelevance.relevanceRationale",
    "mingyangRelevance.pendingVerification",
    "risksAndConstraints.grid",
    "risksAndConstraints.land",
    "risksAndConstraints.esg",
    "risksAndConstraints.financing",
    "risksAndConstraints.competition",
    "evidenceBoundary.verifiedFacts",
    "evidenceBoundary.reasonableAssumptions",
    "evidenceBoundary.pendingVerification",
]
V4_EVIDENCE_REQUIRED_FIELDS = [
    "developmentStage",
    "activityStatus",
    "projectCapacityTreatment",
    "oemCapacityTreatment",
    "capacityMW",
    "oem",
    "oemRelationshipType",
    "tariff",
    "financing",
    "ppaOfftaker",
    "procurementWindow",
    "mingyangRelevance",
]
NO_STRATEGY_PATTERNS = [
    "应当建厂",
    "建议建厂",
    "必须进入",
    "建议报价",
    "必须绑定",
    "应绑定",
    "应该投入资源",
    "应投入资源",
    "must enter",
    "should enter",
    "must build",
    "should build",
    "build a factory",
    "recommended bid",
    "must bind",
]
CRITICAL_PROJECT_FIELDS = [
    ("project_name", ("project_name", "name", "canonicalName", "canonical_name"), ("project", "name", "alias")),
    ("capacity_mw", ("capacityMW", "capacity_mw"), ("capacity", "mw")),
    ("status", ("status", "pipelineBucket", "pipeline_bucket", "evidenceStage", "evidence_stage"), ("status", "stage", "bucket")),
    ("owner_developer", ("developer", "owner_developer", "ownerDeveloper", "sponsor", "spv"), ("owner", "developer", "sponsor", "spv")),
    ("location", ("location", "region", "site"), ("location", "region", "site")),
    ("cod_or_target_cod", ("cod", "codOrTargetCod", "cod_or_target_cod", "targetCod", "target_cod"), ("cod", "commercial operation", "target cod")),
    ("ppa", ("ppaType", "ppa_type", "ppaDuration", "ppa_duration", "ppaDate", "ppa_date"), ("ppa",)),
    ("financing", ("financing", "investmentUSD", "investment_usd", "financingClosed", "financing_closed"), ("financing", "investment", "loan")),
    ("epc_oem", ("epc", "turbineModel", "turbine_model", "turbineCount", "turbine_count"), ("epc", "oem", "turbine")),
    ("construction", ("constructionStart", "construction_start"), ("construction", "start")),
]
RICH_PROJECT_FIELDS = [
    ("annualGenerationGWh", ("annualGenerationGWh", "annual_generation_gwh", "annualGeneration", "annual_generation")),
    (
        "annualCO2ReductionTonnes",
        ("annualCO2ReductionTonnes", "annual_co2_reduction_tonnes", "co2ReductionTonnes", "co2_reduction_tonnes"),
    ),
    ("investmentUSD", ("investmentUSD", "investment_usd", "investment", "capexUSD", "capex_usd")),
    ("turbineModel", ("turbineModel", "turbine_model", "oemModel", "oem_model")),
    ("turbineCount", ("turbineCount", "turbine_count", "numberOfTurbines", "number_of_turbines")),
    ("storageMWh", ("storageMWh", "storage_mwh", "bessMWh", "bess_mwh")),
    ("coordinates", ("coordinates", "coordinate", "latLon", "lat_lon")),
    ("siteAreaHa", ("siteAreaHa", "site_area_ha", "landAreaHa", "land_area_ha")),
    ("hubHeightM", ("hubHeightM", "hub_height_m", "hubHeight", "hub_height")),
    ("rotorDiameterM", ("rotorDiameterM", "rotor_diameter_m", "rotorDiameter", "rotor_diameter")),
    ("bladeLengthM", ("bladeLengthM", "blade_length_m", "bladeLength", "blade_length")),
    ("technologyRoute", ("technologyRoute", "technology_route", "technology")),
    (
        "jobsOrLocalEmployment",
        ("jobsOrLocalEmployment", "jobs_or_local_employment", "localEmployment", "local_employment", "jobs"),
    ),
    (
        "biodiversityBirdProtection",
        (
            "biodiversityBirdProtection",
            "biodiversity_bird_protection",
            "birdProtection",
            "bird_protection",
            "biodiversity",
        ),
    ),
    (
        "communityLandImpact",
        ("communityLandImpact", "community_land_impact", "communityImpact", "community_impact", "landImpact", "land_impact"),
    ),
    ("logisticsRoute", ("logisticsRoute", "logistics_route", "transportRoute", "transport_route")),
    ("keyPeople", ("keyPeople", "key_people", "personnel", "management")),
    ("currentOemStatus", ("currentOemStatus", "current_oem_status", "oemStatus", "oem_status")),
    ("oemShortlist", ("oemShortlist", "oem_shortlist", "shortlistedOems", "shortlisted_oems")),
    ("procurementWindow", ("procurementWindow", "procurement_window", "decisionWindow", "decision_window")),
    ("decisionMaker", ("decisionMaker", "decision_maker", "procurementDecisionMaker", "procurement_decision_maker")),
    ("procurementInfluencers", ("procurementInfluencers", "procurement_influencers", "influencers")),
    ("likelyTenderRoute", ("likelyTenderRoute", "likely_tender_route", "tenderRoute", "tender_route")),
    ("bankabilityConstraint", ("bankabilityConstraint", "bankability_constraint")),
    ("salesEntryPoint", ("salesEntryPoint", "sales_entry_point", "entryPoint", "entry_point")),
    ("adjacentOpportunityImpact", ("adjacentOpportunityImpact", "adjacent_opportunity_impact")),
]
REPORT_READY_PROJECT_FIELDS = [
    ("annualGenerationGWh", ("annualGenerationGWh", "annual_generation_gwh", "annualGeneration", "annual_generation")),
    (
        "annualCO2ReductionTonnes",
        ("annualCO2ReductionTonnes", "annual_co2_reduction_tonnes", "co2ReductionTonnes", "co2_reduction_tonnes"),
    ),
    ("investmentUSD", ("investmentUSD", "investment_usd", "investment", "capexUSD", "capex_usd")),
    ("turbineModel", ("turbineModel", "turbine_model", "oemModel", "oem_model")),
    ("turbineCount", ("turbineCount", "turbine_count", "numberOfTurbines", "number_of_turbines")),
    ("storageMWh", ("storageMWh", "storage_mwh", "bessMWh", "bess_mwh")),
]
RICH_FIELD_CONTAINER_ALIASES = (
    "cardFields",
    "card_fields",
    "projectCard",
    "project_card",
    "reportCard",
    "report_card",
    "technicalSpecs",
    "technical_specs",
    "projectDetails",
    "project_details",
)
FIELD_AVAILABILITY_ALIASES = (
    "fieldAvailability",
    "field_availability",
    "missingRichFields",
    "missing_rich_fields",
    "richFieldGaps",
    "rich_field_gaps",
    "reportCardGaps",
    "report_card_gaps",
    "remainingGaps",
    "remaining_gaps",
)
DEPTH_PROJECT_NAME_FIELDS = (
    "project",
    "projectName",
    "project_name",
    "canonicalName",
    "canonical_name",
    "name",
    "topic",
)
UNAVAILABLE_MARKERS = {"unavailable", "not found", "unknown", "n/a", "na", "none", "null", "not applicable"}
LEGAL_BASIS_FIELDS = (
    "legalBasis",
    "legal_basis",
    "lawNumber",
    "law_number",
    "decreeNumber",
    "decree_number",
    "orderNumber",
    "order_number",
    "originalLegalSource",
    "original_legal_source",
)
HEAVY_PHASE_ORDER = [
    "phase_1_plan",
    "phase_2_recall",
    "phase_3_verification_and_evidence",
    "phase_4_rich_master_and_core_ledgers",
    "phase_5_canonical_reconciliation_and_fact_freeze",
    "phase_6_chapter_input_manifest_and_writing",
    "phase_7_cross_chapter_audit_and_repair",
    "phase_8_release",
]
PHASE_INDEX = {phase: index for index, phase in enumerate(HEAVY_PHASE_ORDER)}
PHASE_PASSED_STATUSES = {"passed", "repaired"}
MAIN_ONLY_ARTIFACT_NAMES = {
    "phase_state.json",
    "artifact_manifest.json",
    "project_ledger.json",
    "metric_ledger.json",
    "policy_target_ledger.json",
    "auction_ledger.json",
    "oem_allocation_ledger.json",
    "capacity_reconciliation.json",
    "canonical_facts.json",
    "fact_freeze.json",
}
MAIN_ONLY_SUFFIXES = {
    "-project_ledger.json",
    "-pipeline-ledger.json",
    "-metric_ledger.json",
    "-policy_target_ledger.json",
    "-auction_ledger.json",
    "-oem_allocation_ledger.json",
    "-capacity_reconciliation.json",
    "-capacity_reconciliation.md",
    "-canonical_facts.json",
    "-fact_freeze.json",
    "-phase_state.json",
    "-artifact_manifest.json",
    "-report.md",
    "-lite.md",
    "-report.pdf",
    "-lite.pdf",
}
WORKER_ALLOWED_DIR_PARTS = {
    "/depth/",
    "/verification/",
    "/chapter_inputs/",
    "/chapter_drafts/",
    "/audits/",
}
CHAPTER_MANIFEST_REQUIRED_FIELDS = [
    "chapterId",
    "inputFreezeId",
    "allowedFactIds",
    "allowedMetricIds",
    "allowedProjectIds",
    "allowedPolicyTargetIds",
    "allowedAuctionIds",
    "allowedOemAllocationIds",
    "prohibitedDeprecatedValues",
    "requiredDisclosures",
    "mustNotInferBeyondManifest",
    "repairIfContradictionFound",
]
REQUIRED_FULL_REPORT_CHAPTER_IDS = {str(index) for index in range(17)}
CANONICAL_FACT_REQUIRED_LEDGER_NAMES = {
    "main_json",
    "project_ledger",
    "metric_ledger",
    "policy_target_ledger",
    "auction_ledger",
    "oem_allocation_ledger",
    "capacity_reconciliation",
}
REPORT_AUDIT_CHECK_NAMES = [
    "cross_chapter_metric_consistency",
    "scope_disclosure",
    "capacity_aggregation",
    "oem_share",
    "project_current_status_uniqueness",
    "parent_phase_rollup_deduplication",
    "unit_arithmetic",
    "release_cleanliness",
]
REFERENCE_MARKER_TYPES = {
    "fact": "allowedFactIds",
    "metric": "allowedMetricIds",
    "project": "allowedProjectIds",
    "policy": "allowedPolicyTargetIds",
    "policytarget": "allowedPolicyTargetIds",
    "policy_target": "allowedPolicyTargetIds",
    "auction": "allowedAuctionIds",
    "oem": "allowedOemAllocationIds",
    "oemallocation": "allowedOemAllocationIds",
    "oem_allocation": "allowedOemAllocationIds",
}
KEY_NUMERIC_CLAIM_RE = re.compile(
    r"\d[\d,]*(?:\.\d+)?\s*(?:GW|MW|吉瓦|兆瓦|%|percent|percentage|KRW|USD|亿|万亿|million|billion|trillion|个|项|projects?)",
    re.IGNORECASE,
)
CAPACITY_VALUE_RE = re.compile(r"~?\d[\d,]*(?:\.\d+)?\s*(?:GW|MW|吉瓦|兆瓦)", re.IGNORECASE)
AGGREGATE_SCOPE_KEYWORDS = (
    "运营海风",
    "海风装机",
    "运营中海风",
    "装机",
    "合计",
    "总计",
    "管线",
    "pipeline",
    "capacity",
    "容量",
    "中标",
    "auction",
    "confirmed",
    "opportunity",
    "watchlist",
    "运营中",
    "在建",
    "已投运",
)
EXPLICIT_SCOPE_KEYWORDS = (
    "截至",
    "as of",
    "by end",
    "年底",
    "年末",
    "项目账本",
    "ledger",
    "可识别",
    "identified",
    "official",
    "官方",
    "auction",
    "拍卖",
    "全国",
    "national",
    "scope",
    "统计范围",
    "统计口径",
    "口径",
    "本报告",
    "基准",
    "含",
    "不含",
    "includes",
    "excluding",
    "数据截止",
    "tier",
)
RELEASE_CLEANLINESS_PATTERNS = [
    ("internal_version", re.compile(r"\bv\d+(?:\.\d+)+(?:\b|\s|\))", re.IGNORECASE)),
    ("internal_iteration_token", re.compile(r"\bV4\b|\bv4\b")),
    ("repairs_applied", re.compile(r"repairs\s+applied", re.IGNORECASE)),
    ("html_deletion_tag", re.compile(r"</?del\b", re.IGNORECASE)),
    ("markdown_deletion", re.compile(r"~~[^~]+~~")),
    ("todo", re.compile(r"\bTODO\b", re.IGNORECASE)),
    ("fixme", re.compile(r"\bFIXME\b", re.IGNORECASE)),
    ("internal_iteration_label", re.compile(r"内部迭代编号|内部版本|迭代编号|internal iteration", re.IGNORECASE)),
    ("unconverted_footnote", re.compile(r"\[\^[^\]]+\]")),
    ("raw_json_claim", re.compile(r"\{[^{}\n]{0,160}\"(?:claim|sources|evidence|metricId|projectId)\"\s*:", re.IGNORECASE)),
]
DELTA_ARITHMETIC_CUES = (
    "同比",
    "环比",
    "yoy",
    "year-on-year",
    "year on year",
    "百分点",
    "增长",
    "下降",
    "increase",
    "decrease",
    "change",
)
PROJECT_STATUS_REPORT_KEYWORDS = {
    "active": ("active", "运营中", "已投运", "在建", "建设中", "中标", "active pipeline"),
    "paused": ("paused", "暂停", "搁置", "中止"),
    "cancelled": ("cancelled", "canceled", "取消"),
    "watchlist": ("watchlist", "观察名单", "待核", "未解决", "unresolved"),
}
HIERARCHY_LEVELS = {"government_zone", "developer_portfolio", "project_parent", "project_phase", "concrete_project"}
ROLLUP_RESOLVED_VALUES = {
    "parent_excluded",
    "children_excluded",
    "rollup_only",
    "phase_only",
    "concrete_project_only",
    "do_not_sum_parent",
    "deduped",
    "excluded_duplicate",
    "not_additive",
}


def get_any(mapping: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for alias in aliases:
        value = mapping.get(alias)
        if value not in (None, "", []):
            return value
    return None


def as_list(value: Any) -> list[Any]:
    if value in (None, "", []):
        return []
    if isinstance(value, list):
        return value
    return [value]


def has_value(value: Any) -> bool:
    if value in (None, "", []):
        return False
    if isinstance(value, str) and value.strip().lower() in UNAVAILABLE_MARKERS:
        return False
    if isinstance(value, dict):
        return any(has_value(item) for item in value.values())
    if isinstance(value, list):
        return any(has_value(item) for item in value)
    return True


def read_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def strip_report_markup(text: str) -> str:
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = text.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def report_sentences(text: str) -> list[str]:
    visible = strip_report_markup(text)
    parts = re.split(r"(?<=[。！？!?；;])\s+|[\r\n]+", visible)
    sentences: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) > 450:
            sentences.extend(item.strip() for item in re.split(r"\s{2,}|\|", part) if item.strip())
        else:
            sentences.append(part)
    return sentences


def unit_factor(unit: Any) -> float:
    normalized = str(unit or "").strip().lower()
    normalized = normalized.replace("兆瓦", "mw").replace("吉瓦", "gw")
    normalized = normalized.replace("krw", "").replace("usd", "").strip()
    factors = {
        "mw": 1.0,
        "gw": 1000.0,
        "%": 1.0,
        "percent": 1.0,
        "percentage": 1.0,
        "亿": 100000000.0,
        "万亿": 1000000000000.0,
        "million": 1000000.0,
        "billion": 1000000000.0,
        "trillion": 1000000000000.0,
        "个": 1.0,
        "项": 1.0,
        "projects": 1.0,
        "project": 1.0,
    }
    return factors.get(normalized, 1.0)


def parse_report_number(value: Any, unit: Any = None) -> tuple[float | None, str]:
    text = str(value or "").replace(",", "").strip()
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*(万亿|亿|GW|MW|吉瓦|兆瓦|%|percent|percentage|million|billion|trillion|个|项|projects?)?", text, re.IGNORECASE)
    if not match:
        return None, str(unit or "").strip()
    parsed_unit = str(unit or match.group(2) or "").strip()
    return float(match.group(1)) * unit_factor(parsed_unit), parsed_unit


def numbers_close(left: float | None, right: float | None, tolerance: float = 0.1) -> bool:
    if left is None or right is None:
        return False
    return abs(left - right) <= max(tolerance, abs(left) * 0.001, abs(right) * 0.001)


def extract_attrs(attr_text: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for match in re.finditer(r"([\w:-]+)\s*=\s*['\"]([^'\"]*)['\"]", attr_text):
        attrs[match.group(1)] = html.unescape(match.group(2))
    return attrs


def normalized_artifact_path(path: Any) -> str:
    return str(path or "").replace("\\", "/")


def artifact_basename(path: Any) -> str:
    return Path(str(path or "")).name


def path_is_under_allowed_worker_dir(path: Any) -> bool:
    normalized = "/" + normalized_artifact_path(path).lstrip("/")
    return any(part in normalized for part in WORKER_ALLOWED_DIR_PARTS)


def collect_chapter_input_manifests(paths: list[Path] | None, directory: Path | None) -> list[tuple[Path, Any]]:
    manifests: list[tuple[Path, Any]] = []
    for path in paths or []:
        manifests.append((path, read_json_file(path)))
    if directory and directory.exists():
        for path in sorted(directory.glob("*.json")):
            if any(existing == path for existing, _ in manifests):
                continue
            manifests.append((path, read_json_file(path)))
    return manifests


def collect_markdown_texts(directory: Path | None) -> list[tuple[Path, str]]:
    if not directory or not directory.exists():
        return []
    texts: list[tuple[Path, str]] = []
    for suffix in ("*.md", "*.html", "*.txt"):
        for path in sorted(directory.glob(suffix)):
            texts.append((path, path.read_text(encoding="utf-8-sig")))
    return texts


def nested_get(mapping: dict[str, Any], dotted_path: str) -> Any:
    current: Any = mapping
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def present_or_unknown(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return False
        return True
    if isinstance(value, list):
        return True
    if isinstance(value, dict):
        return True
    return True


def as_number(value: Any) -> float:
    if value in (None, "", []):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if match:
            return float(match.group(0))
    return 0.0


def numeric_scalar(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.fullmatch(r"\s*-?\d+(?:,\d{3})*(?:\.\d+)?\s*", value)
        if match:
            return float(value.replace(",", "").strip())
    return None


def unavailable_status_for_field(record: dict[str, Any], field: str) -> str:
    direct = record.get(f"{field}Status")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    for key in ("valueStatus", "value_status", "status"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_stage(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def normalize_enum(value: Any) -> str:
    return normalize_stage(value)


def project_capacity(project: dict[str, Any]) -> float:
    return as_number(project.get("capacityMW") or project.get("capacity_mw"))


def project_opportunity_mw(project: dict[str, Any]) -> float:
    return as_number(project.get("opportunityMW") or project.get("opportunity_mw"))


def project_oem_exposure_mw(project: dict[str, Any]) -> float:
    value = as_number(project.get("oemExposureMW") or project.get("oem_exposure_mw"))
    return value if value else project_capacity(project)


def project_capacity_treatment(project: dict[str, Any]) -> str:
    return normalize_enum(
        project.get("projectCapacityTreatment")
        or project.get("project_capacity_treatment")
        or project.get("capacityTreatment")
        or project.get("capacity_treatment")
    )


def oem_capacity_treatment(project: dict[str, Any]) -> str:
    explicit = normalize_enum(
        project.get("oemCapacityTreatment")
        or project.get("oem_capacity_treatment")
        or project.get("oemCapacityBucket")
        or project.get("oem_capacity_bucket")
    )
    if explicit:
        return explicit
    relationship_type = normalize_enum(project.get("oemRelationshipType") or project.get("oem_relationship_type"))
    relationship_status = normalize_enum(project.get("oemRelationshipStatus") or project.get("oem_relationship_status"))
    if relationship_status in EXCLUDED_OEM_STATUSES:
        return "unallocated_mw"
    if relationship_type in FIRM_OEM_TYPES and relationship_status in ACTIVE_OEM_STATUSES:
        return "firm_mw"
    if relationship_type in COMMITTED_OEM_TYPES:
        return "committed_mw"
    if relationship_type in INFLUENCED_OEM_TYPES:
        return "influenced_mw"
    if relationship_type in UNALLOCATED_OEM_TYPES:
        return "unallocated_mw"
    return "unknown"


def is_inactive_project(project: dict[str, Any]) -> bool:
    return normalize_enum(project.get("activityStatus") or project.get("activity_status")) in INACTIVE_ACTIVITY_STATUSES


def collect_v4_ledger_projects(ledger: Any) -> list[dict[str, Any]]:
    if isinstance(ledger, list):
        return [item for item in ledger if isinstance(item, dict)]
    if isinstance(ledger, dict):
        for key in ("projects", "projectLedger", "project_ledger", "items"):
            value = ledger.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def collect_v4_project_cards(cards: Any) -> list[dict[str, Any]]:
    if isinstance(cards, list):
        return [item for item in cards if isinstance(item, dict)]
    if isinstance(cards, dict):
        for key in ("projectCards", "project_cards", "cards", "items"):
            value = cards.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def collect_v4_evidence_items(evidence_table: Any) -> list[dict[str, Any]]:
    if isinstance(evidence_table, list):
        return [item for item in evidence_table if isinstance(item, dict)]
    if isinstance(evidence_table, dict):
        for key in ("items", "evidence", "evidenceTable", "evidence_table", "conclusions"):
            value = evidence_table.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def append_warning(result: dict[str, Any], message: str) -> None:
    result.setdefault("warnings", []).append(message)
    result.setdefault("counts", {})["warnings"] = len(result.get("warnings", []))


def add_gate_gap(result: dict[str, Any], key: str, gap: dict[str, Any], warning: str | None = None) -> None:
    result.setdefault(key, []).append(gap)
    if warning:
        append_warning(result, warning)


def get_nested_any(mapping: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    value = get_any(mapping, aliases)
    if value is not None:
        return value
    for container_alias in RICH_FIELD_CONTAINER_ALIASES:
        container = mapping.get(container_alias)
        if isinstance(container, dict):
            value = get_any(container, aliases)
            if value is not None:
                return value
    return None


def find_alias_value(value: Any, aliases: tuple[str, ...], depth: int = 0) -> Any:
    if depth > 4:
        return None
    if isinstance(value, dict):
        direct = get_any(value, aliases)
        if direct is not None:
            return direct
        for child_key, child_value in value.items():
            if child_key in {"sources", "evidence", "sourceTrace", "source_trace"}:
                continue
            found = find_alias_value(child_value, aliases, depth + 1)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_alias_value(item, aliases, depth + 1)
            if found is not None:
                return found
    return None


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).lower()
    text = re.sub(r"[\W_]+", " ", text, flags=re.UNICODE)
    for word in ("wind", "solar", "farm", "power", "plant", "project", "phase", "llp", "llc", "jsc", "spv"):
        text = re.sub(rf"\b{word}\b", " ", text)
    return re.sub(r"\s+", "", text)


def project_name(project: dict[str, Any]) -> str:
    return str(get_any(project, PROJECT_NAME_FIELDS) or "")


def project_id(project: dict[str, Any], index: int) -> str:
    return str(get_any(project, PROJECT_ID_FIELDS) or f"index-{index}")


def capacity_bucket(value: Any) -> str:
    try:
        return str(round(float(value)))
    except (TypeError, ValueError):
        return "unknown"


def dedupe_key(project: dict[str, Any]) -> str:
    explicit = get_any(project, DEDUP_FIELD_ALIASES)
    if explicit:
        return str(explicit)
    name_key = normalize_text(project_name(project))
    location_key = normalize_text(project.get("location"))
    capacity_key = capacity_bucket(project.get("capacityMW", project.get("capacity_mw")))
    developer_key = normalize_text(project.get("developer", project.get("owner_developer")))
    return "|".join([name_key, location_key, capacity_key, developer_key])


def collect_sources(record: dict[str, Any]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for key in ("sources", "evidence"):
        value = record.get(key)
        if isinstance(value, list):
            sources.extend(item for item in value if isinstance(item, dict))
    facts = record.get("facts")
    if isinstance(facts, list):
        for fact in facts:
            if isinstance(fact, dict) and isinstance(fact.get("sources"), list):
                sources.extend(item for item in fact["sources"] if isinstance(item, dict))
    return sources


def collect_verification_entries(record: dict[str, Any]) -> list[dict[str, Any]]:
    entries = collect_sources(record)
    for key in SOURCE_TRACE_ALIASES:
        value = record.get(key)
        if isinstance(value, list):
            entries.extend(item for item in value if isinstance(item, dict))
        elif isinstance(value, dict):
            entries.append(value)
    verification = get_any(record, CRITICAL_FIELD_VERIFICATION_ALIASES)
    if isinstance(verification, dict):
        for field, value in verification.items():
            for item in as_list(value):
                if isinstance(item, dict):
                    enriched = dict(item)
                    enriched["_verificationField"] = field
                    entries.append(enriched)
                else:
                    entries.append({"_verificationField": field, "value": item})
    return entries


def entry_collection_method(entry: dict[str, Any]) -> str:
    return str(
        get_any(
            entry,
            ("collectionMethod", "collection_method", "verificationMethod", "verification_method", "method"),
        )
        or ""
    )


def entry_verified_fields(entry: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in (
        "_verificationField",
        "verifiedField",
        "verified_field",
        "field",
        "fact",
        "claim",
    ):
        value = entry.get(key)
        if isinstance(value, str):
            values.append(value)
    for key in ("verifiedFields", "verified_fields", "fields", "facts"):
        value = entry.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value if item)
        elif isinstance(value, str):
            values.append(value)
    return values


def field_is_present(record: dict[str, Any], aliases: tuple[str, ...]) -> bool:
    return get_any(record, aliases) is not None


def rich_field_present(record: dict[str, Any], aliases: tuple[str, ...]) -> bool:
    return has_value(get_nested_any(record, aliases))


def field_marked_unavailable(record: dict[str, Any], label: str, aliases: tuple[str, ...]) -> bool:
    labels = {normalize_text(label), *(normalize_text(alias) for alias in aliases)}
    for container_alias in FIELD_AVAILABILITY_ALIASES:
        value = record.get(container_alias)
        if isinstance(value, dict):
            for key, item in value.items():
                if normalize_text(key) in labels:
                    if item in (None, "", []):
                        return True
                    if isinstance(item, str) and item.strip().lower() in UNAVAILABLE_MARKERS:
                        return True
                    if isinstance(item, dict):
                        status = str(get_any(item, ("status", "value", "note", "reason")) or "").lower()
                        if any(marker in status for marker in UNAVAILABLE_MARKERS):
                            return True
                    return True
        elif isinstance(value, list):
            for item in value:
                item_text = normalize_text(json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else item)
                if any(field_label and field_label in item_text for field_label in labels):
                    return True
        elif isinstance(value, str):
            item_text = normalize_text(value)
            if any(field_label and field_label in item_text for field_label in labels):
                return True
    return False


def collect_name_values(value: Any) -> list[str]:
    names: list[str] = []
    if isinstance(value, str) and value.strip():
        names.append(value)
    elif isinstance(value, dict):
        for key in ("value", "name", "alias", "project", "projectName", "project_name", "canonicalName", "canonical_name"):
            item = value.get(key)
            if isinstance(item, str) and item.strip():
                names.append(item)
    elif isinstance(value, list):
        for item in value:
            names.extend(collect_name_values(item))
    return names


def project_alias_values(project: dict[str, Any]) -> list[str]:
    names = [project_name(project)]
    for alias_group in (NAME_VARIANT_ALIASES, ("aliases", "projectAliases", "project_aliases")):
        value = get_any(project, alias_group)
        names.extend(collect_name_values(value))
    for field in PROJECT_ID_FIELDS:
        item = project.get(field)
        if isinstance(item, str) and item.strip():
            names.append(item)
    return [name for name in names if name]


def depth_record_names(record: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for field in DEPTH_PROJECT_NAME_FIELDS:
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            names.append(value)
    for alias_group in (NAME_VARIANT_ALIASES, ("aliases", "projectAliases", "project_aliases")):
        names.extend(collect_name_values(get_any(record, alias_group)))
    return names


def iter_json_records(value: Any, location: str = "$", depth: int = 0) -> list[tuple[dict[str, Any], str]]:
    if depth > 4:
        return []
    records: list[tuple[dict[str, Any], str]] = []
    if isinstance(value, list):
        for index, item in enumerate(value):
            item_location = f"{location}[{index}]"
            if isinstance(item, dict):
                records.append((item, item_location))
                for key in ("records", "projects", "items", "findings", "data"):
                    if key in item:
                        records.extend(iter_json_records(item[key], f"{item_location}.{key}", depth + 1))
            elif isinstance(item, list):
                records.extend(iter_json_records(item, item_location, depth + 1))
    elif isinstance(value, dict):
        records.append((value, location))
        for key in ("records", "projects", "items", "findings", "data"):
            if key in value:
                records.extend(iter_json_records(value[key], f"{location}.{key}", depth + 1))
    return records


def collect_depth_records(depth_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not depth_dir.exists():
        return records, [f"depth directory does not exist: {depth_dir}"]
    for path in sorted(depth_dir.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            warnings.append(f"depth file {path} is not valid JSON: {exc}")
            continue
        for record, location in iter_json_records(data):
            enriched = dict(record)
            enriched["_depthFile"] = str(path)
            enriched["_depthLocation"] = location
            records.append(enriched)
    return records, warnings


def build_project_match_index(projects: list[Any]) -> list[dict[str, Any]]:
    index: list[dict[str, Any]] = []
    for project_index, project in enumerate(projects):
        if not isinstance(project, dict):
            continue
        keys = {normalize_text(name) for name in project_alias_values(project)}
        keys = {key for key in keys if key}
        index.append(
            {
                "project": project,
                "projectId": project_id(project, project_index),
                "projectName": project_name(project),
                "keys": keys,
            }
        )
    return index


def match_depth_record_to_project(record: dict[str, Any], project_index: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = {normalize_text(name) for name in depth_record_names(record)}
    candidates = {candidate for candidate in candidates if candidate}
    if not candidates:
        trace = record.get("sourceTrace") or record.get("source_trace")
        if isinstance(trace, str):
            candidates.add(normalize_text(trace))
    for candidate in candidates:
        for item in project_index:
            if candidate in item["keys"]:
                return item
    for candidate in candidates:
        if len(candidate) < 5:
            continue
        for item in project_index:
            if any(len(key) >= 5 and (candidate in key or key in candidate) for key in item["keys"]):
                return item
    return None


def validate_depth_propagation(projects: list[Any], depth_dir: Path) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    gaps: list[dict[str, Any]] = []
    warnings: list[str] = []
    unmatched_records: list[dict[str, Any]] = []
    depth_records, depth_warnings = collect_depth_records(depth_dir)
    warnings.extend(depth_warnings)
    project_index = build_project_match_index(projects)

    for record in depth_records:
        rich_values = []
        for label, aliases in RICH_PROJECT_FIELDS:
            value = find_alias_value(record, aliases)
            if has_value(value):
                rich_values.append((label, aliases, value))
        if not rich_values:
            continue
        matched = match_depth_record_to_project(record, project_index)
        if matched is None:
            unmatched_records.append(
                {
                    "depthFile": record.get("_depthFile"),
                    "location": record.get("_depthLocation"),
                    "recordNames": depth_record_names(record),
                    "fields": [label for label, _, _ in rich_values],
                }
            )
            continue
        project = matched["project"]
        for label, aliases, value in rich_values:
            if not rich_field_present(project, aliases):
                gaps.append(
                    {
                        "projectId": matched["projectId"],
                        "projectName": matched["projectName"],
                        "field": label,
                        "depthFile": record.get("_depthFile"),
                        "depthLocation": record.get("_depthLocation"),
                        "depthValue": value,
                    }
                )
    return gaps, warnings, unmatched_records


def verified_entry_matches_field(
    entry: dict[str, Any],
    label: str,
    aliases: tuple[str, ...],
    keywords: tuple[str, ...],
) -> bool:
    method = entry_collection_method(entry).lower()
    if method not in VERIFIED_COLLECTION_METHODS:
        return False
    field_text = " ".join(entry_verified_fields(entry)).lower()
    if any(token in field_text for token in ("all-critical-fields", "all critical fields")):
        return True
    candidates = [label, *aliases, *keywords]
    normalized = re.sub(r"[\W_]+", " ", field_text)
    return any(re.sub(r"[\W_]+", " ", candidate.lower()).strip() in normalized for candidate in candidates)


def critical_field_verified(record: dict[str, Any], label: str, aliases: tuple[str, ...], keywords: tuple[str, ...]) -> bool:
    return any(verified_entry_matches_field(entry, label, aliases, keywords) for entry in collect_verification_entries(record))


def is_confirmed_pipeline_record(project: dict[str, Any]) -> bool:
    eligible = get_any(project, ("confirmedPipelineEligible", "confirmed_pipeline_eligible"))
    if isinstance(eligible, bool):
        return eligible
    bucket = str(get_any(project, ("pipelineBucket", "pipeline_bucket", "status", "evidenceStage", "evidence_stage")) or "").lower()
    confirmed_tokens = (
        "operational",
        "under_construction",
        "awarded",
        "ppa",
        "financing_closed",
        "financing-closed",
        "construction",
        "cod",
    )
    return any(token in bucket for token in confirmed_tokens) and "watchlist" not in bucket and "rejected" not in bucket


def source_missing_fields(source: dict[str, Any], parent: dict[str, Any]) -> list[str]:
    missing = []
    for aliases in SOURCE_FIELD_ALIASES:
        if get_any(source, aliases) is None and get_any(parent, aliases) is None:
            missing.append("/".join(aliases))
    return missing


def looks_like_policy_target(record: dict[str, Any]) -> bool:
    text = json.dumps(record, ensure_ascii=False).lower()
    indicators = ("target", "2030", "2040", "mw", "gw", "auction", "tariff", "capacity", "目标", "法令", "拍卖", "电价")
    return any(indicator in text for indicator in indicators)


def has_legal_basis(record: dict[str, Any]) -> bool:
    if get_any(record, LEGAL_BASIS_FIELDS) is not None:
        return True
    for source in collect_sources(record):
        source_type = str(get_any(source, ("sourceType", "source_type")) or "").lower()
        title = str(source.get("title", "")).lower()
        if source_type in {"official", "regulator", "auction_document"}:
            return True
        if any(token in title for token in ("law", "decree", "order", "regulation", "resolution")):
            return True
    return False


def validate_market(data: dict[str, Any], depth_dir: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    duplicate_candidates: list[dict[str, Any]] = []
    critical_field_gaps: list[dict[str, Any]] = []
    report_card_field_gaps: list[dict[str, Any]] = []
    depth_propagation_gaps: list[dict[str, Any]] = []
    unmatched_depth_rich_records: list[dict[str, Any]] = []

    projects = data.get("projects", [])
    if not isinstance(projects, list):
        errors.append("top-level projects must be a list")
        projects = []

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, project in enumerate(projects):
        if not isinstance(project, dict):
            warnings.append(f"project {index} is not an object")
            continue
        name = project_name(project)
        pid = project_id(project, index)
        if not name:
            warnings.append(f"project {pid} missing canonical project name")
        if get_any(project, NAME_VARIANT_ALIASES) is None:
            warnings.append(f"project {pid} missing nameVariants/aliases for local-language and translated names")
        if get_any(project, SOURCE_TRACE_ALIASES) is None:
            warnings.append(f"project {pid} missing sourceTrace/source_trace linking depth records to canonical record")
        if get_any(project, ("duplicateCheckNotes", "duplicate_check_notes")) is None:
            warnings.append(f"project {pid} missing duplicateCheckNotes/duplicate_check_notes")

        sources = collect_sources(project)
        if not sources:
            warnings.append(f"project {pid} has no project-level sources/evidence")
        for source_index, source in enumerate(sources):
            missing = source_missing_fields(source, project)
            if missing:
                warnings.append(f"project {pid} source {source_index} missing fields: {', '.join(missing)}")
        if is_confirmed_pipeline_record(project):
            for label, aliases, keywords in CRITICAL_PROJECT_FIELDS:
                if field_is_present(project, aliases) and not critical_field_verified(project, label, aliases, keywords):
                    critical_field_gaps.append({"projectId": pid, "projectName": name, "field": label})
                    warnings.append(
                        "project "
                        f"{pid} confirmed critical field {label} lacks chrome-mcp/exa-fetch/manual-file verification"
                    )
            for label, aliases in REPORT_READY_PROJECT_FIELDS:
                if not rich_field_present(project, aliases) and not field_marked_unavailable(project, label, aliases):
                    report_card_field_gaps.append({"projectId": pid, "projectName": name, "field": label})
                    warnings.append(
                        "project "
                        f"{pid} confirmed report-card field {label} is missing from main JSON and not marked unavailable"
                    )
        groups[dedupe_key(project)].append({"id": pid, "name": name, "index": index})

    for key, members in groups.items():
        if key and len(members) > 1:
            duplicate_candidates.append({"dedupeKey": key, "members": members})
            warnings.append(f"duplicate candidate group needs merge/rejection decision: {key}")

    for section_name in ("nationalPlans", "policyFramework", "forecasts"):
        section = data.get(section_name, [])
        if not isinstance(section, list):
            continue
        for index, record in enumerate(section):
            if isinstance(record, dict) and looks_like_policy_target(record) and not has_legal_basis(record):
                warnings.append(f"{section_name}[{index}] has target-like data without legalBasis/decree/order backtrace")

    metadata = data.get("metadata", {})
    if isinstance(metadata, dict):
        source_to_final = metadata.get("sourceToFinal") or metadata.get("source_to_final")
        if not isinstance(source_to_final, dict):
            warnings.append("metadata missing sourceToFinal/source_to_final handoff state")
        else:
            for field in ("pipelineLedger", "pipelineLedgerUpdatedAt", "summaryBackpropagationAt", "finalClaimsCheckedAgainstLedger"):
                if source_to_final.get(field) in (None, "", []):
                    warnings.append(f"metadata.sourceToFinal missing {field}")

    if depth_dir is not None:
        depth_propagation_gaps, depth_warnings, unmatched_depth_rich_records = validate_depth_propagation(projects, depth_dir)
        warnings.extend(depth_warnings)
        for gap in depth_propagation_gaps:
            warnings.append(
                "depth rich field was not propagated to main JSON: "
                f"{gap['projectId']} {gap['field']} from {gap['depthFile']}"
            )
        for record in unmatched_depth_rich_records:
            warnings.append(
                "depth rich record could not be matched to a main JSON project: "
                f"{record['depthFile']} {record['location']} fields={','.join(record['fields'])}"
            )

    status = (
        "pass"
        if not errors
        and not duplicate_candidates
        and not critical_field_gaps
        and not report_card_field_gaps
        and not depth_propagation_gaps
        else "needs-review"
    )
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "duplicateCandidates": duplicate_candidates,
        "criticalFieldGaps": critical_field_gaps,
        "reportCardFieldGaps": report_card_field_gaps,
        "depthPropagationGaps": depth_propagation_gaps,
        "unmatchedDepthRichRecords": unmatched_depth_rich_records,
        "counts": {
            "projects": len(projects),
            "warnings": len(warnings),
            "errors": len(errors),
            "duplicateCandidateGroups": len(duplicate_candidates),
            "criticalFieldGaps": len(critical_field_gaps),
            "reportCardFieldGaps": len(report_card_field_gaps),
            "depthPropagationGaps": len(depth_propagation_gaps),
            "unmatchedDepthRichRecords": len(unmatched_depth_rich_records),
        },
    }


def validate_project_ledger_gate(result: dict[str, Any], ledger: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    projects = collect_v4_ledger_projects(ledger)
    if not projects:
        gap = {"gate": "project_ledger_schema_gate", "issue": "project ledger has no projects array"}
        add_gate_gap(result, "projectLedgerFieldGaps", gap, "project ledger has no projects array")
        return gaps
    for index, project in enumerate(projects):
        pid = str(project.get("projectId") or project.get("canonicalProjectId") or project.get("id") or f"index-{index}")
        for field in V4_LEDGER_REQUIRED_FIELDS:
            if field not in project or not present_or_unknown(project.get(field)):
                gap = {"projectId": pid, "field": field}
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "projectLedgerFieldGaps",
                    gap,
                    f"project ledger {pid} missing required V4 field {field}",
                )
        enum_checks = [
            ("developmentStage", DEVELOPMENT_STAGES),
            ("activityStatus", ACTIVITY_STATUSES),
            ("ledgerTreatment", LEDGER_TREATMENTS),
            ("projectCapacityTreatment", PROJECT_CAPACITY_TREATMENTS),
            ("oemCapacityTreatment", OEM_CAPACITY_TREATMENTS),
            ("capacityScope", CAPACITY_SCOPES),
            ("oemRelationshipType", OEM_RELATIONSHIP_TYPES),
            ("oemRelationshipStatus", OEM_RELATIONSHIP_STATUSES),
        ]
        for field, allowed_values in enum_checks:
            if field in project and present_or_unknown(project.get(field)):
                value = normalize_enum(project.get(field))
                if value not in allowed_values:
                    gap = {"projectId": pid, "field": field, "value": project.get(field)}
                    gaps.append(gap)
                    add_gate_gap(
                        result,
                        "projectLedgerFieldGaps",
                        gap,
                        f"project ledger {pid} has invalid {field}: {project.get(field)}",
                    )
        activity_status = normalize_enum(project.get("activityStatus"))
        project_treatment = project_capacity_treatment(project)
        oem_treatment = oem_capacity_treatment(project)
        oem_relationship_status = normalize_enum(project.get("oemRelationshipStatus"))
        if activity_status in INACTIVE_ACTIVITY_STATUSES:
            if project_treatment != "excluded_inactive":
                gap = {
                    "projectId": pid,
                    "activityStatus": activity_status,
                    "projectCapacityTreatment": project_treatment,
                    "issue": "inactive project must use excluded_inactive projectCapacityTreatment",
                }
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "projectLedgerStateGaps",
                    gap,
                    f"project ledger {pid} inactive activityStatus must be excluded from active project capacity treatment",
                )
            if project.get("countedInConfirmedCapacity") is True or project.get("countedInOpportunityCapacity") is True:
                gap = {
                    "projectId": pid,
                    "activityStatus": activity_status,
                    "countedInConfirmedCapacity": project.get("countedInConfirmedCapacity"),
                    "countedInOpportunityCapacity": project.get("countedInOpportunityCapacity"),
                    "issue": "inactive project cannot enter confirmed or opportunity capacity totals",
                }
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "projectLedgerStateGaps",
                    gap,
                    f"project ledger {pid} inactive project is counted in active capacity totals",
                )
        elif project_treatment == "excluded_inactive":
            gap = {
                "projectId": pid,
                "activityStatus": activity_status,
                "projectCapacityTreatment": project_treatment,
                "issue": "active/delayed project cannot be excluded inactive without inactive activityStatus",
            }
            gaps.append(gap)
            add_gate_gap(
                result,
                "projectLedgerStateGaps",
                gap,
                f"project ledger {pid} uses excluded_inactive project treatment without inactive activity status",
            )
        if oem_relationship_status in EXCLUDED_OEM_STATUSES and activity_status not in INACTIVE_ACTIVITY_STATUSES:
            if project_treatment == "excluded_inactive":
                gap = {
                    "projectId": pid,
                    "activityStatus": activity_status,
                    "oemRelationshipStatus": oem_relationship_status,
                    "projectCapacityTreatment": project_treatment,
                    "issue": "expired/terminated/superseded OEM relationship cannot drive project inactive treatment",
                }
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "projectLedgerStateGaps",
                    gap,
                    f"project ledger {pid} treats an OEM-status issue as project inactive capacity",
                )
            if oem_treatment != "unallocated_mw":
                gap = {
                    "projectId": pid,
                    "oemRelationshipStatus": oem_relationship_status,
                    "oemCapacityTreatment": oem_treatment,
                    "issue": "expired/terminated/superseded OEM relationship should flow to unallocated_mw unless the project itself is inactive",
                }
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "projectLedgerStateGaps",
                    gap,
                    f"project ledger {pid} expired OEM relationship must be separated from project capacity treatment",
                )
        if activity_status in INACTIVE_ACTIVITY_STATUSES and oem_treatment != "excluded_inactive_mw":
            gap = {
                "projectId": pid,
                "oemRelationshipStatus": oem_relationship_status,
                "oemCapacityTreatment": oem_treatment,
                "issue": "inactive project OEM MW should flow to excluded_inactive_mw",
            }
            gaps.append(gap)
            add_gate_gap(
                result,
                "projectLedgerStateGaps",
                gap,
                f"project ledger {pid} inactive project OEM capacity must use excluded_inactive_mw",
            )
    return gaps


def validate_project_card_completeness_gate(result: dict[str, Any], cards_data: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    cards = collect_v4_project_cards(cards_data)
    if not cards:
        gap = {"gate": "project_card_completeness_gate", "issue": "project cards file has no cards array"}
        add_gate_gap(result, "projectCardCompletenessGaps", gap, "project cards file has no cards array")
        return gaps
    for index, card in enumerate(cards):
        pid = str(card.get("projectId") or card.get("id") or f"index-{index}")
        for path in V4_PROJECT_CARD_REQUIRED_PATHS:
            if not present_or_unknown(nested_get(card, path)):
                gap = {"projectId": pid, "fieldPath": path}
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "projectCardCompletenessGaps",
                    gap,
                    f"project card {pid} missing required V4 field {path}",
                )
    return gaps


def ledger_capacity_reconciliation(ledger: Any) -> dict[str, float]:
    projects = collect_v4_ledger_projects(ledger)
    confirmed = 0.0
    opportunity = 0.0
    watchlist = 0.0
    excluded_inactive = 0.0
    firm = 0.0
    committed = 0.0
    influenced = 0.0
    unallocated = 0.0
    for project in projects:
        capacity = project_capacity(project)
        opportunity_mw = project_opportunity_mw(project)
        oem_exposure_mw = project_oem_exposure_mw(project)
        stage = normalize_stage(project.get("projectStage") or project.get("pipelineBucket") or project.get("status"))
        activity_status = normalize_enum(project.get("activityStatus") or project.get("activity_status"))
        project_treatment = project_capacity_treatment(project)
        oem_treatment = oem_capacity_treatment(project)
        inactive = activity_status in INACTIVE_ACTIVITY_STATUSES or project_treatment == "excluded_inactive"
        if project.get("countedInConfirmedCapacity") is True:
            confirmed += capacity
        if project.get("countedInOpportunityCapacity") is True:
            opportunity += opportunity_mw
        if project_treatment == "watchlist_capacity" or "watchlist" in stage:
            watchlist += capacity
        if inactive:
            excluded_inactive += capacity
            if oem_treatment == "excluded_inactive_mw":
                continue
            continue
        if oem_treatment == "firm_mw":
            firm += oem_exposure_mw
        elif oem_treatment == "committed_mw":
            committed += oem_exposure_mw
        elif oem_treatment == "influenced_mw":
            influenced += oem_exposure_mw
        elif oem_treatment in {"unallocated_mw", "unknown"}:
            unallocated += oem_exposure_mw
    return {
        "computedConfirmedCapacityMW": confirmed,
        "computedOpportunityCapacityMW": opportunity,
        "computedWatchlistCapacityMW": watchlist,
        "computedExcludedInactiveMW": excluded_inactive,
        "computedFirmMW": firm,
        "computedCommittedMW": committed,
        "computedInfluencedMW": influenced,
        "computedUnallocatedMW": unallocated,
    }


def validate_capacity_reconciliation_gate(result: dict[str, Any], ledger: Any, tolerance: float = 0.1) -> dict[str, float]:
    computed = ledger_capacity_reconciliation(ledger)
    declared = ledger.get("capacityReconciliation") if isinstance(ledger, dict) else None
    if not isinstance(declared, dict):
        add_gate_gap(
            result,
            "capacityReconciliationGaps",
            {"issue": "ledger missing capacityReconciliation object", **computed},
            "ledger missing capacityReconciliation object",
        )
        return computed
    expected_fields = [
        ("confirmedCapacityMW", "computedConfirmedCapacityMW"),
        ("opportunityCapacityMW", "computedOpportunityCapacityMW"),
        ("watchlistCapacityMW", "computedWatchlistCapacityMW"),
        ("excludedInactiveMW", "computedExcludedInactiveMW"),
        ("firmMW", "computedFirmMW"),
        ("committedMW", "computedCommittedMW"),
        ("influencedMW", "computedInfluencedMW"),
        ("unallocatedMW", "computedUnallocatedMW"),
    ]
    for declared_field, computed_field in expected_fields:
        if declared_field not in declared:
            add_gate_gap(
                result,
                "capacityReconciliationGaps",
                {"field": declared_field, "issue": "missing", "computed": computed[computed_field]},
                f"capacity reconciliation missing {declared_field}",
            )
            continue
        declared_value = as_number(declared.get(declared_field))
        if abs(declared_value - computed[computed_field]) > tolerance:
            add_gate_gap(
                result,
                "capacityReconciliationGaps",
                {
                    "field": declared_field,
                    "declared": declared_value,
                    "computed": computed[computed_field],
                },
                f"capacity reconciliation mismatch for {declared_field}: declared {declared_value}, computed {computed[computed_field]}",
            )
    result["computedCapacityReconciliation"] = computed
    return computed


def has_null_value_contract(record: dict[str, Any], field: str) -> bool:
    status_keys = (
        f"{field}Status",
        f"{field}_status",
        "valueStatus",
        "value_status",
    )
    display_keys = (
        f"{field}DisplayValue",
        f"{field}_display_value",
        "displayValue",
        "display_value",
    )
    has_status = any(present_or_unknown(record.get(key)) for key in status_keys)
    has_display = any(present_or_unknown(record.get(key)) for key in display_keys)
    return has_status and has_display


def validate_numeric_field_gate(
    result: dict[str, Any],
    artifact_name: str,
    data: Any,
    field_names: tuple[str, ...],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for record, location in iter_json_records(data):
        record_id = str(
            get_any(
                record,
                (
                    "projectId",
                    "metricId",
                    "allocationId",
                    "auctionId",
                    "policyTargetId",
                    "factId",
                    "id",
                    "slug",
                ),
            )
            or location
        )
        for field in field_names:
            if field not in record:
                continue
            value = record.get(field)
            if isinstance(value, bool) or isinstance(value, str) or (value is not None and numeric_scalar(value) is None):
                gap = {
                    "artifact": artifact_name,
                    "location": location,
                    "recordId": record_id,
                    "field": field,
                    "value": value,
                    "issue": "core numeric field must be number or null, not string/object/list/bool",
                }
                gaps.append(gap)
                add_gate_gap(result, "numericFieldGaps", gap, f"{artifact_name} {record_id} has non-numeric core field {field}")
            elif value is None and not has_null_value_contract(record, field):
                gap = {
                    "artifact": artifact_name,
                    "location": location,
                    "recordId": record_id,
                    "field": field,
                    "issue": "null core numeric field requires valueStatus and displayValue contract",
                }
                gaps.append(gap)
                add_gate_gap(result, "numericFieldGaps", gap, f"{artifact_name} {record_id} null {field} lacks valueStatus/displayValue")
    return gaps


def validate_evidence_boundary_gate(result: dict[str, Any], evidence_table: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    items = collect_v4_evidence_items(evidence_table)
    if not items:
        gap = {"gate": "evidence_boundary_gate", "issue": "evidence table has no conclusion evidence items"}
        add_gate_gap(result, "evidenceBoundaryGaps", gap, "evidence table has no conclusion evidence items")
        return gaps
    related_fields = {normalize_text(item.get("relatedField") or item.get("related_field")) for item in items}
    related_fields.update(normalize_text(item.get("conclusionType") or item.get("conclusion_type")) for item in items)
    for field in V4_EVIDENCE_REQUIRED_FIELDS:
        key = normalize_text(field)
        if not any(key in related or related in key for related in related_fields if related):
            gap = {"relatedField": field}
            gaps.append(gap)
            add_gate_gap(
                result,
                "evidenceBoundaryGaps",
                gap,
                f"evidence table missing conclusion-level evidence for {field}",
            )
    for index, item in enumerate(items):
        for required in (
            "conclusion",
            "conclusionType",
            "source",
            "sourceGrade",
            "directlyProves",
            "confidence",
            "relatedField",
            "pendingVerificationAction",
        ):
            if required not in item or not present_or_unknown(item.get(required)):
                gap = {"itemIndex": index, "field": required}
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "evidenceBoundaryGaps",
                    gap,
                    f"evidence table item {index} missing {required}",
                )
    return gaps


def collect_fact_freeze_items(fact_freeze: Any) -> list[dict[str, Any]]:
    if isinstance(fact_freeze, list):
        return [item for item in fact_freeze if isinstance(item, dict)]
    if isinstance(fact_freeze, dict):
        for key in ("facts", "factFreeze", "fact_freeze", "items"):
            value = fact_freeze.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def fact_freeze_type(item: dict[str, Any]) -> str:
    return normalize_enum(item.get("factType") or item.get("fact_type") or item.get("type") or item.get("category"))


def fact_id(item: dict[str, Any], index: int | None = None) -> str:
    value = item.get("factId") or item.get("fact_id") or item.get("id")
    if value:
        return str(value)
    return f"index-{index}" if index is not None else ""


def fact_freeze_type_set(fact_freeze: Any) -> set[str]:
    types = {fact_freeze_type(item) for item in collect_fact_freeze_items(fact_freeze)}
    return {item for item in types if item}


def configured_fact_types(*artifacts: Any) -> dict[str, set[str] | str]:
    profile_name = ""
    explicit_config_seen = False
    required: set[str] = set()
    conditional: set[str] = set()
    not_applicable: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        raw_profile = artifact.get("factProfile") or artifact.get("fact_profile")
        if isinstance(raw_profile, str) and raw_profile.strip():
            profile_name = raw_profile.strip()
        elif isinstance(raw_profile, dict):
            profile_name = str(raw_profile.get("profileId") or raw_profile.get("id") or profile_name)
            for key, target in (
                ("requiredFactTypes", required),
                ("conditionalFactTypes", conditional),
                ("notApplicableFactTypes", not_applicable),
            ):
                if key in raw_profile:
                    explicit_config_seen = True
                    target.update(normalize_enum(item) for item in as_list(raw_profile.get(key)) if normalize_enum(item))
        for key, target in (
            ("requiredFactTypes", required),
            ("conditionalFactTypes", conditional),
            ("notApplicableFactTypes", not_applicable),
        ):
            snake_key = re.sub(r"([A-Z])", r"_\1", key).lower()
            if key in artifact or snake_key in artifact:
                explicit_config_seen = True
                target.update(normalize_enum(item) for item in as_list(artifact.get(key) or artifact.get(snake_key)) if normalize_enum(item))
    if not explicit_config_seen:
        defaults = FACT_PROFILE_DEFAULTS.get(profile_name or "wind_full_report", {})
        required.update(normalize_enum(item) for item in as_list(defaults.get("requiredFactTypes")) if normalize_enum(item))
        conditional.update(normalize_enum(item) for item in as_list(defaults.get("conditionalFactTypes")) if normalize_enum(item))
        not_applicable.update(normalize_enum(item) for item in as_list(defaults.get("notApplicableFactTypes")) if normalize_enum(item))
    return {
        "profile": profile_name or "wind_full_report",
        "required": required - not_applicable,
        "conditional": conditional - not_applicable,
        "notApplicable": not_applicable,
    }


def stable_json_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def canonical_fact_hash_payload(canonical_facts: Any) -> dict[str, Any]:
    if not isinstance(canonical_facts, dict):
        return {}
    facts = collect_fact_freeze_items(canonical_facts)
    facts_by_id = {
        fact_id(fact, index): normalized_fact_compare_payload(fact)
        for index, fact in enumerate(facts)
        if isinstance(fact, dict)
    }
    return {
        "freezeId": canonical_freeze_id(canonical_facts),
        "facts": facts_by_id,
        "deprecatedValues": canonical_facts.get("deprecatedValues") or canonical_facts.get("deprecated_values") or [],
        "repairRouting": canonical_facts.get("repairRouting") or canonical_facts.get("repair_routing") or {},
    }


def canonical_facts_hash(canonical_facts: Any) -> str:
    return stable_json_hash(canonical_fact_hash_payload(canonical_facts))


def normalized_fact_compare_payload(fact: dict[str, Any]) -> dict[str, Any]:
    return {
        "factId": fact.get("factId") or fact.get("fact_id") or fact.get("id"),
        "factType": fact.get("factType") or fact.get("fact_type") or fact.get("type") or fact.get("category"),
        "statement": fact.get("statement"),
        "value": fact.get("value"),
        "valueStatus": fact.get("valueStatus") or fact.get("value_status"),
        "displayValue": fact.get("displayValue") or fact.get("display_value"),
        "unit": fact.get("unit"),
        "scope": fact.get("scope"),
        "includedIds": fact.get("includedIds") or fact.get("includedProjectIds") or fact.get("included_ids") or fact.get("included_project_ids") or [],
        "excludedIds": fact.get("excludedIds") or fact.get("excludedProjectIds") or fact.get("excluded_ids") or fact.get("excluded_project_ids") or [],
        "evidenceIds": fact.get("evidenceIds") or fact.get("evidence_ids") or [],
        "confidence": fact.get("confidence"),
    }


def compare_fact_freeze_projection(
    result: dict[str, Any],
    fact_freeze: dict[str, Any],
    canonical_facts: Any | None,
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    generated_from = str(fact_freeze.get("generatedFrom") or fact_freeze.get("generated_from") or "")
    if not generated_from.endswith("canonical_facts.json"):
        gap = {"field": "generatedFrom", "value": generated_from, "issue": "fact_freeze must declare canonical_facts.json as source"}
        gaps.append(gap)
        add_gate_gap(result, "factFreezeGaps", gap, "fact_freeze missing generatedFrom canonical_facts.json projection marker")
    canonical_freeze = str(fact_freeze.get("canonicalFreezeId") or fact_freeze.get("canonical_freeze_id") or "")
    if not canonical_freeze:
        gap = {"field": "canonicalFreezeId", "issue": "missing canonical freeze id"}
        gaps.append(gap)
        add_gate_gap(result, "factFreezeGaps", gap, "fact_freeze missing canonicalFreezeId")
    projected_hash = str(fact_freeze.get("canonicalFactsHash") or fact_freeze.get("canonical_facts_hash") or "")
    if not projected_hash:
        gap = {"field": "canonicalFactsHash", "issue": "missing canonical facts hash"}
        gaps.append(gap)
        add_gate_gap(result, "factFreezeGaps", gap, "fact_freeze missing canonicalFactsHash")
    if not isinstance(canonical_facts, dict):
        return gaps
    expected_freeze = canonical_freeze_id(canonical_facts)
    if canonical_freeze and expected_freeze and canonical_freeze != expected_freeze:
        gap = {"field": "canonicalFreezeId", "value": canonical_freeze, "expected": expected_freeze}
        gaps.append(gap)
        add_gate_gap(result, "factFreezeGaps", gap, "fact_freeze canonicalFreezeId does not match canonical_facts freezeId")
    freeze_id = canonical_freeze_id(fact_freeze)
    if freeze_id and expected_freeze and freeze_id != expected_freeze:
        gap = {"field": "freezeId", "value": freeze_id, "expected": expected_freeze}
        gaps.append(gap)
        add_gate_gap(result, "factFreezeGaps", gap, "fact_freeze freezeId does not match canonical_facts freezeId")
    expected_hash = canonical_facts_hash(canonical_facts)
    if projected_hash and projected_hash != expected_hash:
        gap = {"field": "canonicalFactsHash", "value": projected_hash, "expected": expected_hash}
        gaps.append(gap)
        add_gate_gap(result, "factFreezeGaps", gap, "fact_freeze canonicalFactsHash does not match canonical_facts")
    canonical_items = {
        fact_id(item, index): normalized_fact_compare_payload(item)
        for index, item in enumerate(collect_fact_freeze_items(canonical_facts))
        if isinstance(item, dict)
    }
    freeze_items = {
        fact_id(item, index): normalized_fact_compare_payload(item)
        for index, item in enumerate(collect_fact_freeze_items(fact_freeze))
        if isinstance(item, dict)
    }
    canonical_ids = set(canonical_items)
    freeze_ids = set(freeze_items)
    if canonical_ids != freeze_ids:
        gap = {
            "missingInFactFreeze": sorted(canonical_ids - freeze_ids),
            "extraInFactFreeze": sorted(freeze_ids - canonical_ids),
            "issue": "fact_freeze facts must be a one-to-one projection of canonical_facts",
        }
        gaps.append(gap)
        add_gate_gap(result, "factFreezeGaps", gap, "fact_freeze fact IDs do not match canonical_facts")
    for item_id in sorted(canonical_ids & freeze_ids):
        if stable_json_hash(canonical_items[item_id]) != stable_json_hash(freeze_items[item_id]):
            gap = {"factId": item_id, "issue": "projected fact differs from canonical fact"}
            gaps.append(gap)
            add_gate_gap(result, "factFreezeGaps", gap, f"fact_freeze fact {item_id} differs from canonical_facts")
    for field in ("deprecatedValues", "repairRouting"):
        canonical_value = canonical_facts.get(field) or canonical_facts.get(re.sub(r"([A-Z])", r"_\1", field).lower()) or ([] if field == "deprecatedValues" else {})
        freeze_value = fact_freeze.get(field) or fact_freeze.get(re.sub(r"([A-Z])", r"_\1", field).lower()) or ([] if field == "deprecatedValues" else {})
        if stable_json_hash(canonical_value) != stable_json_hash(freeze_value):
            gap = {"field": field, "issue": "projection field differs from canonical_facts"}
            gaps.append(gap)
            add_gate_gap(result, "factFreezeGaps", gap, f"fact_freeze {field} differs from canonical_facts")
    return gaps


def validate_fact_freeze_gate(
    result: dict[str, Any],
    fact_freeze: Any,
    canonical_facts: Any | None = None,
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if not isinstance(fact_freeze, dict):
        gap = {"gate": "fact_freeze_gate", "issue": "fact_freeze must be a JSON object"}
        add_gate_gap(result, "factFreezeGaps", gap, "fact_freeze must be a JSON object")
        return gaps
    items = collect_fact_freeze_items(fact_freeze)
    if not items:
        gap = {"gate": "fact_freeze_gate", "issue": "fact_freeze has no facts array"}
        gaps.append(gap)
        add_gate_gap(result, "factFreezeGaps", gap, "fact_freeze has no facts array")
    present_types = fact_freeze_type_set(fact_freeze)
    profile = configured_fact_types(fact_freeze, canonical_facts)
    if not (fact_freeze.get("factProfile") or fact_freeze.get("fact_profile")):
        gap = {"field": "factProfile", "issue": "missing run-level fact profile"}
        gaps.append(gap)
        add_gate_gap(result, "factFreezeGaps", gap, "fact_freeze missing factProfile configuration")
    for required_type in sorted(profile["required"]):
        if required_type not in present_types:
            gap = {"factType": required_type, "issue": "missing required frozen fact type"}
            gaps.append(gap)
            add_gate_gap(
                result,
                "factFreezeGaps",
                gap,
                f"fact_freeze missing required fact type {required_type}",
            )
    for not_applicable_type in sorted(profile["notApplicable"]):
        if not_applicable_type in present_types:
            gap = {"factType": not_applicable_type, "issue": "fact type is marked not applicable but appears in freeze"}
            gaps.append(gap)
            add_gate_gap(
                result,
                "factFreezeGaps",
                gap,
                f"fact_freeze contains notApplicable fact type {not_applicable_type}",
            )
    for index, item in enumerate(items):
        for required in ("factId", "factType", "statement", "value", "scope", "confidence", "frozenAt"):
            if required == "value":
                value_missing = required not in item or (
                    item.get(required) is None and not has_null_value_contract(item, required)
                )
            else:
                value_missing = required not in item or not present_or_unknown(item.get(required))
            if value_missing:
                gap = {"itemIndex": index, "field": required}
                gaps.append(gap)
                add_gate_gap(result, "factFreezeGaps", gap, f"fact_freeze item {index} missing {required}")
        if not as_list(item.get("evidenceIds") or item.get("evidence_ids")) and not as_list(
            item.get("sourceTrace") or item.get("source_trace")
        ):
            gap = {"itemIndex": index, "field": "evidenceIds/sourceTrace"}
            gaps.append(gap)
            add_gate_gap(
                result,
                "factFreezeGaps",
                gap,
                f"fact_freeze item {index} lacks evidenceIds or sourceTrace",
            )
    gaps.extend(compare_fact_freeze_projection(result, fact_freeze, canonical_facts))
    return gaps


def validate_no_strategy_recommendation_gate(result: dict[str, Any], report_text: str) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    lowered = report_text.lower()
    for pattern in NO_STRATEGY_PATTERNS:
        if pattern.lower() in lowered:
            gap = {"pattern": pattern}
            gaps.append(gap)
            add_gate_gap(
                result,
                "strategyRecommendationGaps",
                gap,
                f"full report contains strategy/recommendation phrase blocked by V4: {pattern}",
            )
    return gaps


def collect_candidate_records(candidate_pool: Any) -> list[dict[str, Any]]:
    if isinstance(candidate_pool, list):
        return [item for item in candidate_pool if isinstance(item, dict)]
    if isinstance(candidate_pool, dict):
        for key in ("candidates", "projects", "items", "candidateProjectPool", "candidate_project_pool"):
            value = candidate_pool.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def candidate_names(record: dict[str, Any]) -> list[str]:
    names = []
    for key in ("projectName", "project_name", "name", "canonicalProjectName", "canonicalName", "project"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            names.append(value)
    for key in ("aliases", "projectAliases", "project_aliases", "nameVariants", "name_variants"):
        names.extend(collect_name_values(record.get(key)))
    return names


def ledger_outcome_names(ledger: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(ledger, dict):
        containers = [ledger.get("projects")]
        containers.extend(
            ledger.get(key)
            for key in (
                "watchlist",
                "duplicate",
                "duplicates",
                "duplicateCandidates",
                "rejected",
                "rejectedClaims",
                "unresolved",
            )
        )
    else:
        containers = [ledger]
    for container in containers:
        for item in as_list(container):
            if isinstance(item, dict):
                for name in candidate_names(item):
                    key = normalize_text(name)
                    if key:
                        names.add(key)
                for field in ("projectId", "canonicalProjectId", "id", "aliasGroupId"):
                    value = item.get(field)
                    if value:
                        names.add(normalize_text(value))
    return names


def validate_baseline_inheritance_gate(result: dict[str, Any], candidate_pool: Any, ledger: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    candidates = collect_candidate_records(candidate_pool)
    if not candidates:
        append_warning(result, "candidate pool is empty or missing; baseline_inheritance_gate could not verify recall retention")
        return gaps
    outcome_names = ledger_outcome_names(ledger)
    for index, candidate in enumerate(candidates):
        names = [normalize_text(name) for name in candidate_names(candidate)]
        names = [name for name in names if name]
        if not names:
            continue
        if not any(name in outcome_names for name in names):
            gap = {"candidateIndex": index, "candidateNames": candidate_names(candidate)}
            gaps.append(gap)
            add_gate_gap(
                result,
                "baselineInheritanceGaps",
                gap,
                f"candidate pool record {index} did not flow into confirmed/watchlist/duplicate/rejected/unresolved ledger outcomes",
            )
    return gaps


def phase_status_map(phase_state: Any) -> dict[str, str]:
    statuses: dict[str, str] = {}
    if not isinstance(phase_state, dict):
        return statuses
    for phase in as_list(phase_state.get("completedPhases") or phase_state.get("completed_phases")):
        if phase:
            statuses[str(phase)] = "passed"
    for item in as_list(phase_state.get("phaseHistory") or phase_state.get("phase_history")):
        if isinstance(item, dict):
            phase = item.get("phase")
            status = item.get("status")
            if phase and status:
                statuses[str(phase)] = str(status)
    current = phase_state.get("currentPhase") or phase_state.get("current_phase")
    if current and current not in statuses:
        statuses[str(current)] = "in_progress"
    return statuses


def validate_phase_order_gate(result: dict[str, Any], phase_state: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if not isinstance(phase_state, dict):
        gap = {"gate": "phase_order_gate", "issue": "phase_state must be a JSON object"}
        add_gate_gap(result, "phaseOrderGaps", gap, "phase_state must be a JSON object")
        return gaps
    current_phase = str(phase_state.get("currentPhase") or phase_state.get("current_phase") or "")
    if current_phase not in PHASE_INDEX:
        gap = {"field": "currentPhase", "value": current_phase, "issue": "unknown or missing phase"}
        gaps.append(gap)
        add_gate_gap(result, "phaseOrderGaps", gap, "phase_state currentPhase is missing or not in the heavy workflow")
    statuses = phase_status_map(phase_state)
    for phase, status in statuses.items():
        if phase not in PHASE_INDEX:
            gap = {"phase": phase, "status": status, "issue": "unknown phase id"}
            gaps.append(gap)
            add_gate_gap(result, "phaseOrderGaps", gap, f"phase_state contains unknown phase {phase}")
            continue
        if status in PHASE_PASSED_STATUSES:
            for earlier in HEAVY_PHASE_ORDER[: PHASE_INDEX[phase]]:
                earlier_status = statuses.get(earlier)
                if earlier_status not in PHASE_PASSED_STATUSES:
                    gap = {
                        "phase": phase,
                        "status": status,
                        "missingEarlierPhase": earlier,
                        "earlierStatus": earlier_status or "missing",
                    }
                    gaps.append(gap)
                    add_gate_gap(
                        result,
                        "phaseOrderGaps",
                        gap,
                        f"{phase} is marked {status} before earlier phase {earlier} passed",
                    )
                    break
    if current_phase in PHASE_INDEX:
        for earlier in HEAVY_PHASE_ORDER[: PHASE_INDEX[current_phase]]:
            earlier_status = statuses.get(earlier)
            if earlier_status not in PHASE_PASSED_STATUSES:
                gap = {
                    "currentPhase": current_phase,
                    "missingEarlierPhase": earlier,
                    "earlierStatus": earlier_status or "missing",
                }
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "phaseOrderGaps",
                    gap,
                    f"current phase {current_phase} cannot start before {earlier} passed",
                )
                break
    return gaps


def collect_artifacts(manifest: Any) -> list[dict[str, Any]]:
    if isinstance(manifest, list):
        return [item for item in manifest if isinstance(item, dict)]
    if isinstance(manifest, dict):
        for key in ("artifacts", "items", "artifactManifest", "artifact_manifest"):
            value = manifest.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def artifact_is_main_only(path: str, artifact_id: str) -> bool:
    basename = artifact_basename(path)
    if basename in MAIN_ONLY_ARTIFACT_NAMES:
        return True
    if any(basename.endswith(suffix) for suffix in MAIN_ONLY_SUFFIXES):
        return True
    normalized_id = normalize_enum(artifact_id)
    return normalized_id in {
        "main_json",
        "project_ledger",
        "metric_ledger",
        "policy_target_ledger",
        "auction_ledger",
        "oem_allocation_ledger",
        "canonical_facts",
        "fact_freeze",
        "phase_state",
        "artifact_manifest",
        "full_report",
        "lite_report",
    }


def validate_artifact_manifest_gate(result: dict[str, Any], manifest: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if not isinstance(manifest, dict):
        gap = {"gate": "single_writer_core_ledger_gate", "issue": "artifact_manifest must be a JSON object"}
        add_gate_gap(result, "artifactOwnershipGaps", gap, "artifact_manifest must be a JSON object")
        return gaps
    artifacts = collect_artifacts(manifest)
    if not artifacts:
        gap = {"gate": "single_writer_core_ledger_gate", "issue": "artifact manifest has no artifacts array"}
        gaps.append(gap)
        add_gate_gap(result, "artifactOwnershipGaps", gap, "artifact_manifest has no artifacts array")
    for index, artifact in enumerate(artifacts):
        path = normalized_artifact_path(artifact.get("path"))
        artifact_id = str(artifact.get("artifactId") or artifact.get("artifact_id") or "")
        owner = str(artifact.get("ownerClass") or artifact.get("owner_class") or "")
        write_policy = str(artifact.get("writePolicy") or artifact.get("write_policy") or "")
        if artifact_is_main_only(path, artifact_id):
            if owner != "main_agent" or write_policy != "single_writer":
                gap = {
                    "artifactIndex": index,
                    "artifactId": artifact_id,
                    "path": path,
                    "ownerClass": owner,
                    "writePolicy": write_policy,
                    "issue": "main-only artifact must be written by main_agent with single_writer policy",
                }
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "artifactOwnershipGaps",
                    gap,
                    f"main-only artifact {path or artifact_id} is not owned by main_agent/single_writer",
                )
        if owner in {"worker_agent", "verification_agent", "chapter_writer", "audit_agent"} and path:
            if not path_is_under_allowed_worker_dir(path):
                gap = {
                    "artifactIndex": index,
                    "artifactId": artifact_id,
                    "path": path,
                    "ownerClass": owner,
                    "issue": "worker-owned artifact outside allowed worker directories",
                }
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "artifactOwnershipGaps",
                    gap,
                    f"worker-owned artifact {path} is outside depth/ verification/ chapter_inputs/ chapter_drafts/ audits/",
                )
    return gaps


def canonical_freeze_id(canonical_facts: Any) -> str:
    if isinstance(canonical_facts, dict):
        return str(canonical_facts.get("freezeId") or canonical_facts.get("freeze_id") or "")
    return ""


def validate_canonical_facts_gate(result: dict[str, Any], canonical_facts: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if not isinstance(canonical_facts, dict):
        gap = {"gate": "canonical_fact_freeze_gate", "issue": "canonical_facts must be a JSON object"}
        add_gate_gap(result, "canonicalFactsGaps", gap, "canonical_facts must be a JSON object")
        return gaps
    freeze_id = canonical_freeze_id(canonical_facts)
    if not freeze_id:
        gap = {"field": "freezeId", "issue": "missing canonical freeze id"}
        gaps.append(gap)
        add_gate_gap(result, "canonicalFactsGaps", gap, "canonical_facts missing freezeId")
    based_on = {normalize_enum(item) for item in as_list(canonical_facts.get("basedOnLedgers") or canonical_facts.get("based_on_ledgers"))}
    missing_ledgers = sorted(item for item in CANONICAL_FACT_REQUIRED_LEDGER_NAMES if item not in based_on)
    if missing_ledgers:
        gap = {"field": "basedOnLedgers", "missing": missing_ledgers}
        gaps.append(gap)
        add_gate_gap(
            result,
            "canonicalFactsGaps",
            gap,
            f"canonical_facts basedOnLedgers missing {', '.join(missing_ledgers)}",
        )
    if not collect_fact_freeze_items(canonical_facts):
        gap = {"field": "facts", "issue": "missing or empty facts array"}
        gaps.append(gap)
        add_gate_gap(result, "canonicalFactsGaps", gap, "canonical_facts has no facts array")
    if not (canonical_facts.get("factProfile") or canonical_facts.get("fact_profile")):
        gap = {"field": "factProfile", "issue": "missing run-level fact profile"}
        gaps.append(gap)
        add_gate_gap(result, "canonicalFactsGaps", gap, "canonical_facts missing factProfile configuration")
    profile = configured_fact_types(canonical_facts)
    present_types = fact_freeze_type_set(canonical_facts)
    for required_type in sorted(profile["required"]):
        if required_type not in present_types:
            gap = {"factType": required_type, "issue": "missing required canonical fact type"}
            gaps.append(gap)
            add_gate_gap(
                result,
                "canonicalFactsGaps",
                gap,
                f"canonical_facts missing required fact type {required_type}",
            )
    for not_applicable_type in sorted(profile["notApplicable"]):
        if not_applicable_type in present_types:
            gap = {"factType": not_applicable_type, "issue": "fact type is marked not applicable but appears in canonical facts"}
            gaps.append(gap)
            add_gate_gap(
                result,
                "canonicalFactsGaps",
                gap,
                f"canonical_facts contains notApplicable fact type {not_applicable_type}",
            )
    return gaps


def deprecated_value_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("value", "text", "deprecatedValue", "deprecated_value", "display"):
            item = value.get(key)
            if isinstance(item, str) and item.strip():
                return item.strip()
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value or "").strip()


def validate_chapter_input_manifest_gate(
    result: dict[str, Any],
    manifests: list[tuple[Path, Any]],
    expected_freeze_id: str | None = None,
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if not manifests:
        gap = {"gate": "chapter_input_manifest_gate", "issue": "no chapter input manifests provided"}
        add_gate_gap(result, "chapterInputManifestGaps", gap, "no chapter input manifests provided")
        return gaps
    seen_chapters: set[str] = set()
    for path, manifest in manifests:
        if not isinstance(manifest, dict):
            gap = {"path": str(path), "issue": "manifest must be a JSON object"}
            gaps.append(gap)
            add_gate_gap(result, "chapterInputManifestGaps", gap, f"{path} is not a JSON object")
            continue
        chapter_id = str(manifest.get("chapterId") or manifest.get("chapter_id") or "")
        if chapter_id.isdigit():
            chapter_id = str(int(chapter_id))
        if chapter_id:
            seen_chapters.add(chapter_id)
        for field in CHAPTER_MANIFEST_REQUIRED_FIELDS:
            if field not in manifest:
                gap = {"path": str(path), "chapterId": chapter_id, "field": field, "issue": "missing required field"}
                gaps.append(gap)
                add_gate_gap(result, "chapterInputManifestGaps", gap, f"{path} missing {field}")
        if manifest.get("mustNotInferBeyondManifest") is not True:
            gap = {
                "path": str(path),
                "chapterId": chapter_id,
                "field": "mustNotInferBeyondManifest",
                "issue": "must be true",
            }
            gaps.append(gap)
            add_gate_gap(result, "chapterInputManifestGaps", gap, f"{path} does not lock chapter inference to manifest")
        input_freeze_id = str(manifest.get("inputFreezeId") or manifest.get("input_freeze_id") or "")
        if expected_freeze_id and input_freeze_id and input_freeze_id != expected_freeze_id:
            gap = {
                "path": str(path),
                "chapterId": chapter_id,
                "inputFreezeId": input_freeze_id,
                "expectedFreezeId": expected_freeze_id,
            }
            gaps.append(gap)
            add_gate_gap(
                result,
                "chapterInputManifestGaps",
                gap,
                f"{path} uses freeze {input_freeze_id}, expected {expected_freeze_id}",
            )
    result.setdefault("counts", {})["chapterInputManifestCount"] = len(manifests)
    result.setdefault("counts", {})["chapterInputManifestChapterCount"] = len(seen_chapters)
    missing_chapters = sorted(REQUIRED_FULL_REPORT_CHAPTER_IDS - seen_chapters, key=int)
    if missing_chapters:
        gap = {"missingChapterIds": missing_chapters, "issue": "missing chapter input manifests"}
        gaps.append(gap)
        add_gate_gap(
            result,
            "chapterInputManifestGaps",
            gap,
            f"chapter input manifests missing chapters: {', '.join(missing_chapters)}",
        )
    return gaps


def chapter_id_from_path(path: Path) -> str:
    normalized = path.stem.lower()
    match = re.search(r"chapter[-_ ]?(\d{1,2})(?:\D|$)", normalized)
    if match:
        return str(int(match.group(1)))
    match = re.search(r"(?:^|[-_])ch[-_]?(\d{1,2})(?:\D|$)", normalized)
    if match:
        return str(int(match.group(1)))
    return ""


def chapter_manifest_by_id(manifests: list[tuple[Path, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for path, manifest in manifests:
        if not isinstance(manifest, dict):
            continue
        chapter_id = str(manifest.get("chapterId") or manifest.get("chapter_id") or chapter_id_from_path(path) or "")
        if chapter_id.isdigit():
            chapter_id = str(int(chapter_id))
        if chapter_id:
            index[chapter_id] = manifest
    return index


def normalize_marker_type(value: str) -> str:
    return normalize_enum(value).replace("-", "_")


def extract_reference_markers(text: str) -> dict[str, set[str]]:
    markers: dict[str, set[str]] = {field: set() for field in set(REFERENCE_MARKER_TYPES.values())}
    marker_pattern = re.compile(
        r"(?:\{\{(?P<brace_type>fact|metric|project|policy(?:_?target)?|auction|oem(?:_?allocation)?):(?P<brace_id>[^}|]+)(?:\|[^}]*)?\}\}"
        r"|\[(?P<bracket_type>fact|metric|project|policy(?:_?target)?|auction|oem(?:_?allocation)?):(?P<bracket_id>[^\]|]+)(?:\|[^\]]*)?\]"
        r"|<!--\s*(?P<comment_type>fact|metric|project|policy(?:_?target)?|auction|oem(?:_?allocation)?):(?P<comment_id>.*?)\s*-->)",
        re.IGNORECASE | re.DOTALL,
    )
    for match in marker_pattern.finditer(text):
        raw_type = match.group("brace_type") or match.group("bracket_type") or match.group("comment_type") or ""
        raw_id = match.group("brace_id") or match.group("bracket_id") or match.group("comment_id") or ""
        allowed_field = REFERENCE_MARKER_TYPES.get(normalize_marker_type(raw_type))
        reference_id = raw_id.strip()
        if allowed_field and reference_id:
            markers.setdefault(allowed_field, set()).add(reference_id)
    attr_pattern = re.compile(
        r"data-(fact|metric|project|policy-target|policy|auction|oem-allocation|oem)-id\s*=\s*['\"]([^'\"]+)['\"]",
        re.IGNORECASE,
    )
    for match in attr_pattern.finditer(text):
        raw_type = match.group(1).replace("-", "_")
        allowed_field = REFERENCE_MARKER_TYPES.get(normalize_marker_type(raw_type))
        reference_id = match.group(2).strip()
        if allowed_field and reference_id:
            markers.setdefault(allowed_field, set()).add(reference_id)
    return markers


def validate_chapter_no_external_fact_gate(
    result: dict[str, Any],
    manifests: list[tuple[Path, Any]],
    draft_texts: list[tuple[Path, str]],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if not draft_texts:
        return gaps
    prohibited: list[str] = []
    for _, manifest in manifests:
        if isinstance(manifest, dict):
            prohibited.extend(
                item
                for item in (deprecated_value_text(value) for value in as_list(manifest.get("prohibitedDeprecatedValues")))
                if item
                )
    manifests_by_id = chapter_manifest_by_id(manifests)
    for path, text in draft_texts:
        chapter_id = chapter_id_from_path(path)
        manifest = manifests_by_id.get(chapter_id) if chapter_id else None
        if manifest is None:
            gap = {"draft": str(path), "chapterId": chapter_id, "issue": "no matching chapter input manifest"}
            gaps.append(gap)
            add_gate_gap(result, "chapterExternalFactGaps", gap, f"{path} has no matching chapter input manifest")
            continue
        used_markers = extract_reference_markers(text)
        for allowed_field in sorted(set(REFERENCE_MARKER_TYPES.values())):
            allowed_ids = {str(item) for item in as_list(manifest.get(allowed_field)) if str(item)}
            external_ids = sorted(used_markers.get(allowed_field, set()) - allowed_ids)
            if external_ids:
                gap = {
                    "draft": str(path),
                    "chapterId": chapter_id,
                    "manifestField": allowed_field,
                    "externalIds": external_ids,
                    "issue": "chapter cites IDs outside its manifest allow-list",
                }
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "chapterExternalFactGaps",
                    gap,
                    f"{path} uses {allowed_field} outside its chapter input manifest",
                )
        if KEY_NUMERIC_CLAIM_RE.search(text) and as_list(manifest.get("allowedMetricIds")) and not used_markers.get("allowedMetricIds"):
            gap = {
                "draft": str(path),
                "chapterId": chapter_id,
                "manifestField": "allowedMetricIds",
                "issue": "numeric claims require explicit metric reference markers",
            }
            gaps.append(gap)
            add_gate_gap(
                result,
                "chapterExternalFactGaps",
                gap,
                f"{path} contains key numeric claims without metric reference markers",
            )
        for value in prohibited:
            if value and value in text:
                gap = {"draft": str(path), "deprecatedValue": value}
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "chapterExternalFactGaps",
                    gap,
                    f"{path} contains prohibited deprecated value from chapter manifest: {value}",
                )
    return gaps


def audit_issue_count(value: Any) -> int:
    if value in (None, "", []):
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        count = get_any(value, ("count", "total", "length"))
        if isinstance(count, (int, float)):
            return int(count)
        return len(value)
    if isinstance(value, str):
        parsed = numeric_scalar(value)
        if parsed is not None:
            return int(parsed)
        return 1
    return 1


def validate_release_gate(
    result: dict[str, Any],
    phase_state: Any | None,
    audits_dir: Path | None,
    full_report_path: Path | None,
    expected_freeze_id: str | None = None,
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    if not full_report_path:
        return gaps
    audit_files: list[Path] = []
    if audits_dir and audits_dir.exists():
        audit_files = sorted(audits_dir.glob("*audit*.json"))
    statuses = phase_status_map(phase_state) if phase_state is not None else {}
    release_status = statuses.get("phase_8_release")
    audit_status = statuses.get("phase_7_cross_chapter_audit_and_repair")
    if audit_status not in PHASE_PASSED_STATUSES:
        gap = {"gate": "release_gate", "phase": "phase_7_cross_chapter_audit_and_repair", "status": audit_status or "missing"}
        gaps.append(gap)
        add_gate_gap(result, "releaseGaps", gap, "full report provided before cross-chapter audit passed")
    if release_status not in PHASE_PASSED_STATUSES and release_status != "in_progress":
        gap = {"gate": "release_gate", "phase": "phase_8_release", "status": release_status or "missing"}
        gaps.append(gap)
        add_gate_gap(result, "releaseGaps", gap, "full report provided without release phase state")
    if audits_dir is None:
        gap = {"gate": "cross_chapter_audit_gate", "issue": "audits directory argument is required for full-report release"}
        gaps.append(gap)
        add_gate_gap(result, "releaseGaps", gap, "full report provided without --audits-dir for cross-chapter audit content")
    elif not audit_files:
        gap = {"gate": "cross_chapter_audit_gate", "path": str(audits_dir), "issue": "no audit json files found"}
        gaps.append(gap)
        add_gate_gap(result, "releaseGaps", gap, "full report provided but audits directory has no audit JSON")
    if audit_files:
        cross_audits: list[tuple[Path, Any]] = []
        for audit_file in audit_files:
            try:
                audit_data = read_json_file(audit_file)
            except Exception as exc:  # noqa: BLE001
                gap = {"gate": "cross_chapter_audit_gate", "path": str(audit_file), "issue": f"invalid audit JSON: {exc}"}
                gaps.append(gap)
                add_gate_gap(result, "releaseGaps", gap, f"{audit_file} is not readable audit JSON")
                continue
            audit_type = normalize_enum(get_any(audit_data, ("auditType", "audit_type", "type")) or "") if isinstance(audit_data, dict) else ""
            if "cross_chapter" in audit_type or "cross_chapter_audit" in audit_file.name.lower():
                cross_audits.append((audit_file, audit_data))
        if not cross_audits:
            gap = {
                "gate": "cross_chapter_audit_gate",
                "path": str(audits_dir),
                "issue": "no formal cross_chapter_audit JSON found",
            }
            gaps.append(gap)
            add_gate_gap(result, "releaseGaps", gap, "audits directory has audit JSON but no cross_chapter_audit artifact")
        for audit_file, audit_data in cross_audits:
            if not isinstance(audit_data, dict):
                gap = {"gate": "cross_chapter_audit_gate", "path": str(audit_file), "issue": "audit must be a JSON object"}
                gaps.append(gap)
                add_gate_gap(result, "releaseGaps", gap, f"{audit_file} audit content is not a JSON object")
                continue
            status = normalize_enum(audit_data.get("status"))
            if status not in PHASE_PASSED_STATUSES:
                gap = {"gate": "cross_chapter_audit_gate", "path": str(audit_file), "status": status or "missing"}
                gaps.append(gap)
                add_gate_gap(result, "releaseGaps", gap, f"{audit_file} cross-chapter audit did not pass")
            critical_count = audit_issue_count(audit_data.get("criticalIssues") or audit_data.get("critical_issues"))
            high_count = audit_issue_count(audit_data.get("highIssues") or audit_data.get("high_issues"))
            if critical_count:
                gap = {"gate": "cross_chapter_audit_gate", "path": str(audit_file), "criticalIssues": critical_count}
                gaps.append(gap)
                add_gate_gap(result, "releaseGaps", gap, f"{audit_file} cross-chapter audit has critical issues")
            if high_count:
                gap = {"gate": "cross_chapter_audit_gate", "path": str(audit_file), "highIssues": high_count}
                gaps.append(gap)
                add_gate_gap(result, "releaseGaps", gap, f"{audit_file} cross-chapter audit has high issues")
            audit_freeze_id = str(audit_data.get("freezeId") or audit_data.get("freeze_id") or "")
            if expected_freeze_id and audit_freeze_id != expected_freeze_id:
                gap = {
                    "gate": "cross_chapter_audit_gate",
                    "path": str(audit_file),
                    "freezeId": audit_freeze_id or "missing",
                    "expectedFreezeId": expected_freeze_id,
                }
                gaps.append(gap)
                add_gate_gap(result, "releaseGaps", gap, f"{audit_file} cross-chapter audit freezeId does not match current freeze")
            checked_chapters = {str(int(item)) if str(item).isdigit() else str(item) for item in as_list(audit_data.get("checkedChapterIds") or audit_data.get("checked_chapter_ids"))}
            missing_chapters = sorted(REQUIRED_FULL_REPORT_CHAPTER_IDS - checked_chapters, key=int)
            if missing_chapters:
                gap = {"gate": "cross_chapter_audit_gate", "path": str(audit_file), "missingChapterIds": missing_chapters}
                gaps.append(gap)
                add_gate_gap(result, "releaseGaps", gap, f"{audit_file} cross-chapter audit did not check every required chapter")
            for field in ("checkedMetricIds", "checkedProjectIds"):
                if field not in audit_data and re.sub(r"([A-Z])", r"_\1", field).lower() not in audit_data:
                    gap = {"gate": "cross_chapter_audit_gate", "path": str(audit_file), "field": field}
                    gaps.append(gap)
                    add_gate_gap(result, "releaseGaps", gap, f"{audit_file} cross-chapter audit missing {field}")
            open_repairs = [
                task
                for task in as_list(audit_data.get("repairTasks") or audit_data.get("repair_tasks"))
                if not isinstance(task, dict)
                or normalize_enum(task.get("status")) not in {"closed", "resolved", "applied", "passed", "not_applicable"}
            ]
            if open_repairs:
                gap = {"gate": "cross_chapter_audit_gate", "path": str(audit_file), "openRepairTasks": len(open_repairs)}
                gaps.append(gap)
                add_gate_gap(result, "releaseGaps", gap, f"{audit_file} has unresolved repair tasks")
    return gaps


def collect_metric_records(metric_ledger: Any) -> list[dict[str, Any]]:
    if isinstance(metric_ledger, list):
        return [item for item in metric_ledger if isinstance(item, dict)]
    if isinstance(metric_ledger, dict):
        for key in ("metrics", "items", "metricLedger", "metric_ledger", "facts"):
            value = metric_ledger.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def extract_metric_occurrences_from_text(text: str, label: str) -> list[dict[str, Any]]:
    occurrences: list[dict[str, Any]] = []
    tag_pattern = re.compile(
        r"<(?P<tag>\w+)\b(?P<attrs>[^>]*data-metric-id\s*=\s*['\"][^'\"]+['\"][^>]*)>(?P<body>.*?)</(?P=tag)>",
        re.IGNORECASE | re.DOTALL,
    )
    for match in tag_pattern.finditer(text):
        attrs = extract_attrs(match.group("attrs"))
        metric_id = attrs.get("data-metric-id") or attrs.get("metricId")
        raw_value = attrs.get("data-value") or strip_report_markup(match.group("body"))
        raw_unit = attrs.get("data-unit")
        scope_id = attrs.get("data-scope-id") or attrs.get("data-scope") or attrs.get("scope")
        parsed_value, parsed_unit = parse_report_number(raw_value, raw_unit)
        occurrences.append(
            {
                "metricId": metric_id,
                "value": parsed_value,
                "unit": raw_unit or parsed_unit,
                "scopeId": scope_id,
                "raw": strip_report_markup(match.group(0))[:220],
                "source": label,
            }
        )
    marker_pattern = re.compile(r"(?:\{\{metric:([^\}|]+)(?:\|([^}]+))?\}\}|\[metric:([^\]\|]+)(?:\|([^\]]+))?\])")
    for match in marker_pattern.finditer(text):
        metric_id = (match.group(1) or match.group(3) or "").strip()
        payload = (match.group(2) or match.group(4) or "").strip()
        payload_attrs: dict[str, str] = {}
        for key, value in re.findall(r"([\w:-]+)\s*=\s*([^|,]+)", payload):
            payload_attrs[key] = value.strip()
        raw_value = payload_attrs.get("value") or payload
        raw_unit = payload_attrs.get("unit")
        parsed_value, parsed_unit = parse_report_number(raw_value, raw_unit)
        occurrences.append(
            {
                "metricId": metric_id,
                "value": parsed_value,
                "unit": raw_unit or parsed_unit,
                "scopeId": payload_attrs.get("scope") or payload_attrs.get("scopeId"),
                "raw": match.group(0)[:220],
                "source": label,
            }
        )
    return [item for item in occurrences if item.get("metricId")]


def metric_record_occurrence(record: dict[str, Any], label: str) -> dict[str, Any] | None:
    metric_id = get_any(record, ("metricId", "metric_id", "id", "factId", "fact_id"))
    if not metric_id:
        return None
    raw_value = get_any(record, ("value", "metricValue", "metric_value", "amount"))
    raw_unit = get_any(record, ("unit", "metricUnit", "metric_unit"))
    parsed_value, parsed_unit = parse_report_number(raw_value, raw_unit)
    return {
        "metricId": str(metric_id),
        "value": parsed_value,
        "unit": raw_unit or parsed_unit,
        "scopeId": get_any(record, ("scopeId", "scope_id", "scope", "statisticalScope", "statistical_scope")),
        "raw": raw_value,
        "source": label,
    }


def validate_metric_consistency_gate(
    result: dict[str, Any],
    report_texts: list[tuple[str, str]],
    metric_ledger: Any | None = None,
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    occurrences: list[dict[str, Any]] = []
    for label, text in report_texts:
        occurrences.extend(extract_metric_occurrences_from_text(text, label))
    for record in collect_metric_records(metric_ledger):
        occurrence = metric_record_occurrence(record, "metric_ledger")
        if occurrence:
            occurrences.append(occurrence)
    by_metric: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for occurrence in occurrences:
        if occurrence.get("value") is not None:
            by_metric[str(occurrence["metricId"])].append(occurrence)
    for metric_id, items in by_metric.items():
        values = {round(float(item["value"]), 6) for item in items if item.get("value") is not None}
        if len(values) > 1:
            gap = {"metricId": metric_id, "occurrences": items}
            gaps.append(gap)
            add_gate_gap(
                result,
                "metricConsistencyGaps",
                gap,
                f"metricId {metric_id} has conflicting numeric values across report/ledger occurrences",
            )
    result.setdefault("counts", {})["metricOccurrencesChecked"] = len(occurrences)
    return gaps


def validate_scope_disclosure_gate(result: dict[str, Any], report_text: str) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for index, sentence in enumerate(report_sentences(report_text)):
        lowered = sentence.lower()
        if not CAPACITY_VALUE_RE.search(sentence):
            continue
        if not any(keyword.lower() in lowered for keyword in AGGREGATE_SCOPE_KEYWORDS):
            continue
        if any(keyword.lower() in lowered for keyword in EXPLICIT_SCOPE_KEYWORDS):
            continue
        gap = {"sentenceIndex": index, "text": sentence[:260], "issue": "capacity/aggregate metric lacks explicit scope"}
        gaps.append(gap)
        add_gate_gap(
            result,
            "scopeDisclosureGaps",
            gap,
            "aggregate capacity metric lacks explicit statistical scope/time/basis",
        )
    return gaps


def declared_capacity_container(ledger: Any, external: Any | None = None) -> dict[str, Any] | None:
    if isinstance(external, dict):
        return external
    if isinstance(ledger, dict) and isinstance(ledger.get("capacityReconciliation"), dict):
        return ledger["capacityReconciliation"]
    return None


def compare_capacity_declared_values(
    result: dict[str, Any],
    computed: dict[str, float],
    declared: dict[str, Any] | None,
    tolerance: float = 0.1,
) -> None:
    if not isinstance(declared, dict):
        return
    field_pairs = [
        (("confirmedCapacityMW", "confirmed_capacity_mw"), "computedConfirmedCapacityMW"),
        (("opportunityCapacityMW", "opportunity_capacity_mw"), "computedOpportunityCapacityMW"),
        (("watchlistCapacityMW", "watchlist_capacity_mw"), "computedWatchlistCapacityMW"),
        (("excludedInactiveMW", "excluded_inactive_mw"), "computedExcludedInactiveMW"),
        (("firmMW", "firm_mw"), "computedFirmMW"),
        (("committedMW", "committed_mw"), "computedCommittedMW"),
        (("influencedMW", "influenced_mw"), "computedInfluencedMW"),
        (("unallocatedMW", "unallocated_mw"), "computedUnallocatedMW"),
    ]
    for aliases, computed_field in field_pairs:
        declared_raw = find_alias_value(declared, aliases)
        if declared_raw is None:
            continue
        declared_value = as_number(declared_raw)
        if abs(declared_value - computed[computed_field]) > tolerance:
            add_gate_gap(
                result,
                "capacityArithmeticGaps",
                {
                    "field": aliases[0],
                    "declared": declared_value,
                    "computed": computed[computed_field],
                    "issue": "declared aggregate does not equal project-ledger sum",
                },
                f"capacity arithmetic mismatch for {aliases[0]}: declared {declared_value}, computed {computed[computed_field]}",
            )


def validate_capacity_arithmetic_gate(
    result: dict[str, Any],
    ledger: Any,
    capacity_reconciliation: Any | None = None,
    tolerance: float = 0.1,
) -> list[dict[str, Any]]:
    before = len(result.get("capacityArithmeticGaps", []))
    computed = ledger_capacity_reconciliation(ledger)
    declared = declared_capacity_container(ledger, capacity_reconciliation)
    compare_capacity_declared_values(result, computed, declared, tolerance)
    if isinstance(declared, dict):
        official = find_alias_value(declared, ("officialAuctionTotalMW", "officialAwardedMW", "auctionTotalMW", "official_awarded_mw"))
        identified = find_alias_value(
            declared,
            ("identifiableProjectCapacityMW", "identifiedProjectCapacityMW", "identifiable_project_capacity_mw", "identified_project_mw"),
        )
        unresolved = find_alias_value(declared, ("unresolvedGapMW", "unresolvedCapacityGapMW", "auctionUnresolvedGapMW", "unresolved_gap_mw"))
        if official is not None and identified is not None and unresolved is not None:
            official_value = as_number(official)
            identified_value = as_number(identified)
            unresolved_value = as_number(unresolved)
            expected_gap = official_value - identified_value
            if abs(expected_gap - unresolved_value) > tolerance:
                add_gate_gap(
                    result,
                    "capacityArithmeticGaps",
                    {
                        "field": "unresolvedGapMW",
                        "officialAuctionTotalMW": official_value,
                        "identifiableProjectCapacityMW": identified_value,
                        "declaredUnresolvedGapMW": unresolved_value,
                        "computedUnresolvedGapMW": expected_gap,
                    },
                    "official auction total minus identifiable project capacity does not equal unresolved gap",
                )
    return result.get("capacityArithmeticGaps", [])[before:]


def collect_oem_allocation_records(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("allocations", "items", "oemAllocations", "oem_allocation_ledger", "rows"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def metric_value_lookup(metric_ledger: Any | None) -> dict[str, float]:
    lookup: dict[str, float] = {}
    for record in collect_metric_records(metric_ledger):
        metric_id = get_any(record, ("metricId", "metric_id", "id", "factId", "fact_id"))
        if not metric_id:
            continue
        raw_value = get_any(record, ("value", "metricValue", "metric_value", "amount"))
        parsed, _ = parse_report_number(raw_value, get_any(record, ("unit", "metricUnit", "metric_unit")))
        if parsed is not None:
            lookup[str(metric_id)] = parsed
    return lookup


def validate_oem_share_gate(
    result: dict[str, Any],
    oem_allocation_ledger: Any | None,
    metric_ledger: Any | None = None,
    tolerance: float = 0.1,
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    records = collect_oem_allocation_records(oem_allocation_ledger)
    denominators = metric_value_lookup(metric_ledger)
    share_groups: dict[str, float] = defaultdict(float)
    group_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    group_denominators: dict[str, set[str]] = defaultdict(set)
    for index, record in enumerate(records):
        scope = str(
            get_any(record, ("scopeId", "scope_id", "statisticalScope", "statistical_scope", "denominatorMetricId", "denominator_metric_id"))
            or "default"
        )
        layer = normalize_enum(get_any(record, ("capacityLayer", "capacity_layer", "mwBucket", "mw_bucket", "bucket", "relationshipBucket")))
        share_group_key = f"{scope}|{layer or 'all'}"
        share = find_alias_value(record, ("sharePercent", "share_percent", "percentage", "percent", "marketSharePercent"))
        denominator = str(get_any(record, ("denominatorMetricId", "denominator_metric_id", "denominator", "shareDenominator")) or "")
        mw = find_alias_value(record, ("mw", "capacityMW", "capacity_mw", "allocationMW", "allocation_mw"))
        if share is not None:
            share_groups[share_group_key] += as_number(share)
            group_records[share_group_key].append({"index": index, "sharePercent": as_number(share), "record": record})
        if denominator:
            group_denominators[share_group_key].add(denominator)
            if denominator not in denominators and metric_ledger is not None:
                gap = {
                    "recordIndex": index,
                    "scope": scope,
                    "bucket": layer,
                    "denominatorMetricId": denominator,
                    "issue": "denominatorMetricId is not present in metric_ledger",
                }
                gaps.append(gap)
                add_gate_gap(result, "oemShareGaps", gap, "OEM share denominatorMetricId missing from metric_ledger")
            elif denominator in denominators and share is not None and mw is not None:
                denominator_value = denominators[denominator]
                if denominator_value:
                    expected_share = as_number(mw) / denominator_value * 100
                    declared_share = as_number(share)
                    if abs(expected_share - declared_share) > max(tolerance, 0.05):
                        gap = {
                            "recordIndex": index,
                            "scope": scope,
                            "bucket": layer,
                            "mw": as_number(mw),
                            "denominatorMetricId": denominator,
                            "denominatorValue": denominator_value,
                            "declaredSharePercent": declared_share,
                            "computedSharePercent": expected_share,
                            "issue": "sharePercent does not equal mw / denominatorMetricValue * 100",
                        }
                        gaps.append(gap)
                        add_gate_gap(result, "oemShareGaps", gap, "OEM sharePercent does not reconcile to MW and denominator metric")
        denominator_text = normalize_text(denominator)
        if layer in {"firm_mw", "firm", "firm_supply_contract"} and "influenced" in denominator_text:
            gap = {
                "recordIndex": index,
                "scope": scope,
                "bucket": layer,
                "denominator": denominator,
                "issue": "Firm MW share cannot use Influenced MW denominator",
            }
            gaps.append(gap)
            add_gate_gap(result, "oemShareGaps", gap, "OEM Firm MW share uses Influenced MW denominator")
    for scope, total_share in share_groups.items():
        if total_share > 100 + tolerance:
            gap = {"scope": scope, "sharePercentTotal": total_share, "records": group_records[scope]}
            gaps.append(gap)
            add_gate_gap(result, "oemShareGaps", gap, f"OEM share total exceeds 100% for scope {scope}: {total_share}")
    for scope, denominator_ids in group_denominators.items():
        if len(denominator_ids) > 1:
            gap = {"scope": scope, "denominatorMetricIds": sorted(denominator_ids)}
            gaps.append(gap)
            add_gate_gap(result, "oemShareGaps", gap, f"OEM share group {scope} uses mixed denominators")
    return gaps


def project_report_status_hits(project: dict[str, Any], report_text: str) -> set[str]:
    names = [name for name in project_alias_values(project) if len(normalize_text(name)) >= 4]
    if not names:
        return set()
    hits: set[str] = set()
    for sentence in report_sentences(report_text):
        normalized_sentence = normalize_text(sentence)
        if not any(normalize_text(name) in normalized_sentence for name in names):
            continue
        lowered = sentence.lower()
        for status, keywords in PROJECT_STATUS_REPORT_KEYWORDS.items():
            if any(keyword.lower() in lowered for keyword in keywords):
                hits.add(status)
    return hits


def validate_project_status_uniqueness_gate(
    result: dict[str, Any],
    ledger: Any,
    report_text: str | None = None,
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    status_by_project: dict[str, set[str]] = defaultdict(set)
    project_lookup: dict[str, dict[str, Any]] = {}
    for index, project in enumerate(collect_v4_ledger_projects(ledger)):
        pid = project_id(project, index)
        project_lookup[pid] = project
        activity = normalize_enum(project.get("activityStatus") or project.get("activity_status"))
        if activity:
            status_by_project[pid].add(activity)
    if report_text:
        for pid, project in project_lookup.items():
            status_by_project[pid].update(project_report_status_hits(project, report_text))
    conflict_groups = [
        {"active", "paused"},
        {"active", "cancelled"},
        {"active", "watchlist"},
        {"paused", "watchlist"},
        {"cancelled", "watchlist"},
        {"withdrawn", "active"},
    ]
    for pid, statuses in status_by_project.items():
        for conflict in conflict_groups:
            if conflict <= statuses:
                gap = {"projectId": pid, "statuses": sorted(statuses), "conflict": sorted(conflict)}
                gaps.append(gap)
                add_gate_gap(result, "projectStatusConflictGaps", gap, f"project {pid} has conflicting current statuses")
                break
    return gaps


def project_parent_id(project: dict[str, Any]) -> str:
    return str(
        get_any(
            project,
            ("parentProjectId", "parent_project_id", "projectParentId", "project_parent_id", "parentId", "parent_id"),
        )
        or ""
    )


def project_hierarchy_level(project: dict[str, Any]) -> str:
    return normalize_enum(
        get_any(
            project,
            ("hierarchyLevel", "hierarchy_level", "projectHierarchyLevel", "project_hierarchy_level", "projectLevel", "project_level"),
        )
    )


def project_rollup_treatment(project: dict[str, Any]) -> str:
    return normalize_enum(
        get_any(
            project,
            ("relationshipResolution", "relationship_resolution", "rollupTreatment", "rollup_treatment", "aggregationTreatment", "aggregation_treatment"),
        )
    )


def project_counted_in_any_capacity(project: dict[str, Any]) -> bool:
    return project.get("countedInConfirmedCapacity") is True or project.get("countedInOpportunityCapacity") is True


def validate_parent_phase_rollup_gate(result: dict[str, Any], ledger: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    projects = collect_v4_ledger_projects(ledger)
    by_id = {project_id(project, index): project for index, project in enumerate(projects)}
    children_by_parent: dict[str, list[str]] = defaultdict(list)
    for index, project in enumerate(projects):
        pid = project_id(project, index)
        parent_id = project_parent_id(project)
        if parent_id:
            children_by_parent[parent_id].append(pid)
        hierarchy = project_hierarchy_level(project)
        if hierarchy in HIERARCHY_LEVELS and project_counted_in_any_capacity(project) and not project_rollup_treatment(project):
            gap = {
                "projectId": pid,
                "hierarchyLevel": hierarchy,
                "issue": "hierarchical project requires explicit relationship/rollup treatment before capacity aggregation",
            }
            gaps.append(gap)
            add_gate_gap(result, "parentPhaseRollupGaps", gap, f"hierarchical project {pid} lacks rollup treatment")
    for parent_id, child_ids in children_by_parent.items():
        parent = by_id.get(parent_id)
        if not parent or not project_counted_in_any_capacity(parent):
            continue
        counted_children = [child_id for child_id in child_ids if project_counted_in_any_capacity(by_id.get(child_id, {}))]
        if counted_children and project_rollup_treatment(parent) not in ROLLUP_RESOLVED_VALUES:
            gap = {
                "parentProjectId": parent_id,
                "countedChildProjectIds": counted_children,
                "parentRollupTreatment": project_rollup_treatment(parent),
                "issue": "parent and child/phase projects are both counted without explicit dedupe/rollup resolution",
            }
            gaps.append(gap)
            add_gate_gap(result, "parentPhaseRollupGaps", gap, f"parent project {parent_id} and phases are both counted")
    return gaps


def parse_unit_terms(text: str) -> list[tuple[float, str, str]]:
    terms: list[tuple[float, str, str]] = []
    for match in re.finditer(r"(-?\d[\d,]*(?:\.\d+)?)\s*(万亿|亿|GW|MW|吉瓦|兆瓦|%|percent|percentage|million|billion|trillion|个|项|projects?)", text, re.IGNORECASE):
        raw = match.group(0)
        value, unit = parse_report_number(raw)
        if value is not None:
            terms.append((value, unit, raw))
    return terms


def validate_unit_arithmetic_gate(result: dict[str, Any], report_text: str, tolerance: float = 0.1) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for sentence in report_sentences(report_text):
        if "+" not in sentence and "＋" not in sentence:
            continue
        plus_normalized = sentence.replace("＋", "+")
        value_pattern = re.compile(
            r"(?P<total>-?\d[\d,]*(?:\.\d+)?)\s*(?P<unit>万亿|亿|GW|MW|吉瓦|兆瓦|%|percent|percentage|million|billion|trillion|个|项|projects?)",
            flags=re.IGNORECASE,
        )
        for inside_match in re.finditer(r"[\(（](?P<inside>[^()（）]{0,220}\+[^()（）]{0,220})[\)）]", plus_normalized):
            inside = inside_match.group("inside")
            lowered_inside = inside.lower()
            if any(cue.lower() in lowered_inside for cue in DELTA_ARITHMETIC_CUES):
                continue
            prefix = plus_normalized[: inside_match.start()]
            prefix_window = prefix[-90:]
            total_candidates = list(value_pattern.finditer(prefix_window))
            if not total_candidates:
                continue
            total_match = total_candidates[-1]
            terms = parse_unit_terms(inside)
            if len(terms) < 2:
                continue
            total_value, total_unit = parse_report_number(total_match.group("total"), total_match.group("unit"))
            if total_value is None:
                continue
            term_sum = sum(term[0] for term in terms)
            if not numbers_close(total_value, term_sum, tolerance):
                gap = {
                    "text": sentence[:320],
                    "declaredTotal": total_match.group(0),
                    "computedSumBase": term_sum,
                    "declaredTotalBase": total_value,
                    "terms": [term[2] for term in terms],
                    "issue": "visible arithmetic total does not equal component sum after unit normalization",
                }
                gaps.append(gap)
                add_gate_gap(result, "unitArithmeticGaps", gap, "visible unit arithmetic mismatch in final report")
    return gaps


def validate_release_cleanliness_gate(result: dict[str, Any], report_text: str) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for pattern_id, pattern in RELEASE_CLEANLINESS_PATTERNS:
        for match in pattern.finditer(report_text):
            snippet_start = max(0, match.start() - 80)
            snippet_end = min(len(report_text), match.end() + 120)
            snippet = strip_report_markup(report_text[snippet_start:snippet_end])
            gap = {"pattern": pattern_id, "match": match.group(0)[:120], "snippet": snippet[:260]}
            gaps.append(gap)
            add_gate_gap(result, "releaseCleanlinessGaps", gap, f"final report contains release-forbidden artifact: {pattern_id}")
            break
    return gaps


def update_v4_gate_status(result: dict[str, Any]) -> None:
    gate_keys = [
        "phaseOrderGaps",
        "artifactOwnershipGaps",
        "canonicalFactsGaps",
        "chapterInputManifestGaps",
        "chapterExternalFactGaps",
        "releaseGaps",
        "metricConsistencyGaps",
        "scopeDisclosureGaps",
        "capacityArithmeticGaps",
        "oemShareGaps",
        "numericFieldGaps",
        "projectStatusConflictGaps",
        "parentPhaseRollupGaps",
        "unitArithmeticGaps",
        "releaseCleanlinessGaps",
        "projectLedgerFieldGaps",
        "projectLedgerStateGaps",
        "projectCardCompletenessGaps",
        "capacityReconciliationGaps",
        "factFreezeGaps",
        "evidenceBoundaryGaps",
        "strategyRecommendationGaps",
        "baselineInheritanceGaps",
    ]
    result["gateSummary"] = {key: len(result.get(key, [])) for key in gate_keys}
    result["v4GateSummary"] = result["gateSummary"]
    if any(result["gateSummary"].values()):
        result["status"] = "needs-review"
    result.setdefault("counts", {}).update(result["gateSummary"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate renewable market source-to-final integrity.")
    parser.add_argument("market_json", type=Path)
    parser.add_argument("--depth-dir", type=Path, help="Depth JSON directory used to verify rich-field propagation.")
    parser.add_argument("--project-ledger", type=Path, help="V4 project_ledger.json or {slug}-pipeline-ledger.json.")
    parser.add_argument("--metric-ledger", type=Path, help="metric_ledger.json for cross-chapter metric consistency checks.")
    parser.add_argument("--capacity-reconciliation", type=Path, help="capacity_reconciliation.json for capacity arithmetic checks.")
    parser.add_argument("--oem-allocation-ledger", type=Path, help="oem_allocation_ledger.json for OEM share and denominator checks.")
    parser.add_argument("--project-cards", type=Path, help="V4 project_cards.json with full project-card modules.")
    parser.add_argument("--evidence-table", type=Path, help="V4 evidence_table.json with conclusion-level evidence.")
    parser.add_argument("--fact-freeze", type=Path, help="fact_freeze.json with frozen capacity, policy, project-status, and OEM-relation facts.")
    parser.add_argument("--canonical-facts", type=Path, help="canonical_facts.json produced after core ledgers and reconciliation.")
    parser.add_argument("--phase-state", type=Path, help="phase_state.json for the heavy workflow state machine.")
    parser.add_argument("--artifact-manifest", type=Path, help="artifact_manifest.json declaring writer ownership and phase.")
    parser.add_argument(
        "--chapter-input-manifest",
        type=Path,
        action="append",
        default=[],
        help="One chapter input manifest. May be passed multiple times.",
    )
    parser.add_argument("--chapter-input-dir", type=Path, help="Directory containing chapter input manifests.")
    parser.add_argument("--chapter-drafts-dir", type=Path, help="Directory containing chapter draft Markdown/HTML/text files.")
    parser.add_argument("--audits-dir", type=Path, help="Directory containing cross-chapter audit artifacts.")
    parser.add_argument("--candidate-pool", type=Path, help="candidate_project_pool.json for baseline inheritance checks.")
    parser.add_argument("--full-report", type=Path, help="Full report Markdown/HTML text for no-strategy recommendation checks.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings as well as errors.")
    args = parser.parse_args()

    data = json.loads(args.market_json.read_text(encoding="utf-8-sig"))
    result = validate_market(data, args.depth_dir)

    ledger_data: Any | None = None
    metric_ledger_data: Any | None = None
    capacity_reconciliation_data: Any | None = None
    oem_allocation_ledger_data: Any | None = None
    phase_state_data: Any | None = None
    canonical_facts_data: Any | None = None
    chapter_manifests: list[tuple[Path, Any]] = []
    chapter_draft_texts: list[tuple[Path, str]] = []
    full_report_text: str | None = None
    if args.phase_state:
        phase_state_data = read_json_file(args.phase_state)
        validate_phase_order_gate(result, phase_state_data)
    if args.artifact_manifest:
        validate_artifact_manifest_gate(result, read_json_file(args.artifact_manifest))
    if args.project_ledger:
        ledger_data = read_json_file(args.project_ledger)
        validate_project_ledger_gate(result, ledger_data)
        validate_numeric_field_gate(result, "project_ledger", ledger_data, PROJECT_LEDGER_NUMERIC_FIELDS)
        validate_capacity_reconciliation_gate(result, ledger_data)
        validate_parent_phase_rollup_gate(result, ledger_data)
    if args.metric_ledger:
        metric_ledger_data = read_json_file(args.metric_ledger)
        validate_numeric_field_gate(result, "metric_ledger", metric_ledger_data, METRIC_LEDGER_NUMERIC_FIELDS)
    if args.capacity_reconciliation:
        capacity_reconciliation_data = read_json_file(args.capacity_reconciliation)
        validate_numeric_field_gate(
            result,
            "capacity_reconciliation",
            capacity_reconciliation_data,
            CAPACITY_RECONCILIATION_NUMERIC_FIELDS,
        )
    if args.oem_allocation_ledger:
        oem_allocation_ledger_data = read_json_file(args.oem_allocation_ledger)
        validate_numeric_field_gate(result, "oem_allocation_ledger", oem_allocation_ledger_data, OEM_ALLOCATION_NUMERIC_FIELDS)
        validate_oem_share_gate(result, oem_allocation_ledger_data, metric_ledger_data)
    if args.project_cards:
        validate_project_card_completeness_gate(result, read_json_file(args.project_cards))
    if args.evidence_table:
        validate_evidence_boundary_gate(result, read_json_file(args.evidence_table))
    if args.canonical_facts:
        canonical_facts_data = read_json_file(args.canonical_facts)
        validate_canonical_facts_gate(result, canonical_facts_data)
    if args.fact_freeze:
        validate_fact_freeze_gate(result, read_json_file(args.fact_freeze), canonical_facts_data)
    if args.chapter_input_manifest or args.chapter_input_dir:
        chapter_manifests = collect_chapter_input_manifests(args.chapter_input_manifest, args.chapter_input_dir)
        validate_chapter_input_manifest_gate(result, chapter_manifests, canonical_freeze_id(canonical_facts_data))
    if args.chapter_drafts_dir:
        chapter_draft_texts = collect_markdown_texts(args.chapter_drafts_dir)
        validate_chapter_no_external_fact_gate(
            result,
            chapter_manifests,
            chapter_draft_texts,
        )
    if args.full_report:
        full_report_text = args.full_report.read_text(encoding="utf-8-sig")
        validate_no_strategy_recommendation_gate(result, full_report_text)
        validate_scope_disclosure_gate(result, full_report_text)
        validate_unit_arithmetic_gate(result, full_report_text)
        validate_release_cleanliness_gate(result, full_report_text)
        validate_release_gate(result, phase_state_data, args.audits_dir, args.full_report, canonical_freeze_id(canonical_facts_data))
        if ledger_data is not None:
            validate_project_status_uniqueness_gate(result, ledger_data, full_report_text)
    metric_texts: list[tuple[str, str]] = []
    if full_report_text is not None:
        metric_texts.append(("full_report", full_report_text))
    metric_texts.extend((str(path), text) for path, text in chapter_draft_texts)
    if metric_texts or metric_ledger_data is not None:
        validate_metric_consistency_gate(result, metric_texts, metric_ledger_data)
    if ledger_data is not None:
        if full_report_text is None:
            validate_project_status_uniqueness_gate(result, ledger_data)
        validate_capacity_arithmetic_gate(result, ledger_data, capacity_reconciliation_data)
    if args.candidate_pool:
        if ledger_data is None:
            append_warning(result, "candidate pool was provided without --project-ledger; baseline_inheritance_gate skipped")
        else:
            validate_baseline_inheritance_gate(result, read_json_file(args.candidate_pool), ledger_data)
    update_v4_gate_status(result)

    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

    if (
        result["errors"]
        or result["duplicateCandidates"]
        or result["criticalFieldGaps"]
        or result["reportCardFieldGaps"]
        or result["depthPropagationGaps"]
        or result.get("projectLedgerFieldGaps")
        or result.get("projectLedgerStateGaps")
        or result.get("projectCardCompletenessGaps")
        or result.get("capacityReconciliationGaps")
        or result.get("factFreezeGaps")
        or result.get("evidenceBoundaryGaps")
        or result.get("strategyRecommendationGaps")
        or result.get("baselineInheritanceGaps")
        or result.get("phaseOrderGaps")
        or result.get("artifactOwnershipGaps")
        or result.get("canonicalFactsGaps")
        or result.get("chapterInputManifestGaps")
        or result.get("chapterExternalFactGaps")
        or result.get("releaseGaps")
        or result.get("metricConsistencyGaps")
        or result.get("scopeDisclosureGaps")
        or result.get("capacityArithmeticGaps")
        or result.get("oemShareGaps")
        or result.get("numericFieldGaps")
        or result.get("projectStatusConflictGaps")
        or result.get("parentPhaseRollupGaps")
        or result.get("unitArithmeticGaps")
        or result.get("releaseCleanlinessGaps")
        or (args.strict and result["warnings"])
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
