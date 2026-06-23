#!/usr/bin/env python3
"""Validate source-to-final integrity for renewable market JSON outputs."""

from __future__ import annotations

import argparse
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

PROJECT_NAME_FIELDS = ("canonicalName", "canonical_name", "project_name", "name")
PROJECT_ID_FIELDS = ("canonicalProjectId", "canonical_project_id", "id", "project_id")
DEDUP_FIELD_ALIASES = ("dedupeKey", "dedupe_key")
SOURCE_TRACE_ALIASES = ("sourceTrace", "source_trace")
NAME_VARIANT_ALIASES = ("nameVariants", "name_variants", "aliases")
VERIFIED_COLLECTION_METHODS = {"chrome-mcp", "exa-fetch", "manual-file"}
CRITICAL_FIELD_VERIFICATION_ALIASES = ("criticalFieldVerification", "critical_field_verification")
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


def validate_market(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    duplicate_candidates: list[dict[str, Any]] = []
    critical_field_gaps: list[dict[str, Any]] = []

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

    status = "pass" if not errors and not duplicate_candidates and not critical_field_gaps else "needs-review"
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "duplicateCandidates": duplicate_candidates,
        "criticalFieldGaps": critical_field_gaps,
        "counts": {
            "projects": len(projects),
            "warnings": len(warnings),
            "errors": len(errors),
            "duplicateCandidateGroups": len(duplicate_candidates),
            "criticalFieldGaps": len(critical_field_gaps),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate renewable market source-to-final integrity.")
    parser.add_argument("market_json", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings as well as errors.")
    args = parser.parse_args()

    data = json.loads(args.market_json.read_text(encoding="utf-8"))
    result = validate_market(data)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

    if result["errors"] or result["duplicateCandidates"] or result["criticalFieldGaps"] or (args.strict and result["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
