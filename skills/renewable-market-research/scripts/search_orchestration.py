#!/usr/bin/env python3
"""Plan and validate renewable-market research search coverage.

This helper does not call external search APIs. It creates a deterministic,
file-mode search plan that workers can execute with Exa, Chrome MCP, or other
host search tools, then validates depth JSON files against that plan.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DIMENSIONS = [
    {
        "id": "demand-load-gap",
        "intent": "status",
        "freshness": "py",
        "focus": "electricity demand, peak load, generation, consumption, imports, exports, deficits",
        "patterns": [
            "{country} electricity demand peak load generation consumption import export {year}",
            "{country} power deficit industrial demand mining oil gas data center green hydrogen forecast",
            "{country} electricity demand forecast 2030 power balance report",
        ],
        "domainBoost": ["iea.org", "enerdata.net", "worldbank.org", "stat.gov.kz", "kegoc.kz"],
    },
    {
        "id": "market-key-indicators-timeseries",
        "intent": "status",
        "freshness": "pm",
        "focus": "generation, YoY change, latest quarterly/monthly data, wind/solar three-year trends, installed capacity, imports/exports, and market dashboard indicators",
        "patterns": [
            "{country} electricity generation year on year Q1 wind solar generation statistics {year}",
            "{country} renewable energy statistics wind solar generation 3 year trend installed capacity",
            "{country} energy ministry statistics electricity generation imports exports peak load quarterly report",
        ],
        "domainBoost": ["energy.gov.kz", "stat.gov.kz", "iea.org", "ember-climate.org", "irena.org"],
    },
    {
        "id": "power-mix-replacement",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "current generation mix, retirements, coal/gas limits, hydro flexibility, wind/solar complementarity",
        "patterns": [
            "{country} power generation mix coal gas hydro wind solar retirement plan",
            "{country} coal power plant retirement renewable target wind share",
            "{country} hydro flexibility wind solar complementarity grid balancing",
        ],
        "domainBoost": ["irena.org", "iea.org", "ember-climate.org", "energycharter.org"],
    },
    {
        "id": "grid-storage-transmission",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "grid topology, substations, high-voltage lines, curtailment, storage, cross-border corridors",
        "patterns": [
            "{country} wind grid connection transmission substations storage curtailment",
            "{country} KEGOC transmission investment plan renewable integration",
            "{country} cross-border electricity transmission green corridor wind solar storage",
        ],
        "domainBoost": ["kegoc.kz", "adb.org", "ebrd.com", "worldbank.org", "usaid.gov"],
    },
    {
        "id": "policy-ppa-economics",
        "intent": "status",
        "freshness": "py",
        "focus": "FIT, auctions, PPA, offtaker credit, tariffs, FX, guarantees, tax, land, localization, IRR/ROE",
        "patterns": [
            "{country} renewable energy auction wind tariff PPA offtaker currency guarantee",
            "{country} wind power PPA auction results tariff FIT local content tax land policy",
            "{country} renewable project IRR ROE wind financing assumptions",
        ],
        "domainBoost": ["rfc.kz", "korem.kz", "adilet.zan.kz", "ifc.org", "ebrd.com"],
    },
    {
        "id": "auction-tariff-comparison",
        "intent": "status",
        "freshness": "py",
        "focus": "project-level auction/PPA winning tariffs, award dates, PPA tenor, currency, indexation, capacity, sponsor, and comparable bid history",
        "patterns": [
            "{country} renewable auction results wind tariff cents kWh PPA project sponsor capacity",
            "{country} {technology} winning tariff PPA price auction award date developer",
            "{country} wind solar auction tariff comparison project PPA tenor currency indexation",
        ],
        "domainBoost": ["korem.kz", "rfc.kz", "energy.gov.kz", "masdar.ae", "acwapower.com"],
    },
    {
        "id": "project-pipeline-layered",
        "intent": "status",
        "freshness": "pm",
        "focus": "operational, construction, awarded/PPA, MOU/framework, early-stage wind projects",
        "patterns": [
            "{country} wind farm project pipeline operational construction PPA MOU capacity MW",
            "{country} wind power auction awarded PPA signed construction COD developer",
            "site:acwapower.com {country} wind project PPA construction COD",
        ],
        "domainBoost": ["acwapower.com", "masdar.ae", "totalenergies.com", "eni.com", "powerchina.cn"],
    },
    {
        "id": "owners-partners-routes",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "state entities, IPPs, Chinese developers, industrial offtakers, offices, partnerships",
        "patterns": [
            "{country} wind power developer IPP owner Samruk KEGOC offtaker partnership",
            "{country} ACWA Masdar TotalEnergies ENI China Energy PowerChina wind portfolio",
            "{country} corporate PPA mining metallurgy oil gas renewable electricity wind",
        ],
        "domainBoost": ["samruk-energy.kz", "samruk-kazyna.kz", "kegoc.kz", "acwapower.com"],
    },
    {
        "id": "anchor-developer-deep-dives",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "material owner/developer deep dives: ACWA, Masdar, TotalEnergies, state entities, portfolios, financials, people, partners, IRR assumptions, and China cooperation",
        "patterns": [
            "{country} ACWA Power Masdar wind solar portfolio financial results key people partnerships China EPC",
            "{country} renewable developer project portfolio revenue profit ROE PE investor presentation",
            "{country} Masdar TotalEnergies ACWA project SPV PPA financing EPC operation update",
        ],
        "domainBoost": ["acwapower.com", "masdar.ae", "totalenergies.com", "londonstockexchange.com", "argaam.com"],
    },
    {
        "id": "competitor-oem-landscape",
        "intent": "comparison",
        "freshness": "py",
        "focus": "full OEM/supplier panorama, turbine platform, capacity, rotor, hub height, product roadmap, market share trend, climate adaptation, localization, owner/EPC ties",
        "patterns": [
            "{country} wind turbine supplier Goldwind Envision SANY Mingyang Vestas GE Nordex project",
            "{country} wind farm turbine model rotor diameter hub height low temperature dust",
            "{country} wind OEM localization manufacturing tower blade nacelle",
            "{country} wind turbine market share BNEF supplier ranking product roadmap",
        ],
        "domainBoost": ["goldwind.com", "envision-group.com", "myse.com.cn", "sanyglobal.com", "vestas.com"],
    },
    {
        "id": "epc-om-logistics-lifting",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "EPC, O&M, oversized logistics routes, ports, rail/road corridors, border crossings, component dimensions/weights, heavy lifting, cranes, installation windows",
        "patterns": [
            "{country} wind farm EPC O&M logistics heavy lift crane transport route China",
            "{country} oversized cargo wind turbine blade nacelle tower rail road border crossing",
            "{country} Mammoet Sarens wind turbine installation crane project",
            "{country} wind turbine blade transport route port railway road heavy lift 4000 km 30 days",
        ],
        "domainBoost": ["mammoet.com", "sarens.com", "powerchina.cn", "ceec.net.cn"],
    },
    {
        "id": "localization-supply-chain",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "tower, blade, nacelle, BESS, converter manufacturing, local content, JV/service centers",
        "patterns": [
            "{country} wind tower blade nacelle manufacturing localization local content",
            "{country} battery energy storage manufacturing converter renewable supply chain",
            "{country} wind turbine service center training center spare parts joint venture",
        ],
        "domainBoost": ["invest.gov.kz", "kazakhinvest.gov.kz", "astanatimes.com"],
    },
    {
        "id": "esg-land-community",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "land acquisition, community, biodiversity, birds, ESIA, cultural heritage, IFI standards",
        "patterns": [
            "{country} wind farm ESIA bird migration biodiversity community land acquisition",
            "{country} wind project environmental social impact assessment cultural heritage",
            "{country} wind farm IFC EBRD environmental social action plan",
        ],
        "domainBoost": ["ebrd.com", "ifc.org", "adb.org", "worldbank.org"],
    },
    {
        "id": "carbon-greenpower-hydrogen",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "I-REC, carbon credits, CBAM, green hydrogen/ammonia, industrial decarbonization, corporate PPA",
        "patterns": [
            "{country} I-REC renewable energy certificate wind corporate PPA carbon credit",
            "{country} CBAM mining metallurgy green electricity renewable PPA",
            "{country} green hydrogen ammonia wind solar project industrial decarbonization",
        ],
        "domainBoost": ["irecstandard.org", "hydrogencouncil.com", "ebrd.com", "worldbank.org"],
    },
    {
        "id": "china-finance-ecosystem",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "Chinese developers, EPCs, financiers, Sinosure, policy banks, BRI and industrial cooperation",
        "patterns": [
            "{country} China wind project EPC developer financing Sinosure Exim Bank CDB",
            "{country} Belt and Road renewable wind power China Energy PowerChina Goldwind",
            "{country} China Kazakhstan industrial capacity cooperation renewable energy wind",
        ],
        "domainBoost": ["powerchina.cn", "ceec.net.cn", "sinosure.com.cn", "eximbank.gov.cn"],
    },
    {
        "id": "chinese-developer-deep-dives",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "Chinese developers and entrants: listed code, revenue, profit, margin, team, Sinosure/policy-bank financing, local portfolio, EPC/OEM roles",
        "patterns": [
            "{country} SANY renewable wind project revenue profit gross margin listed code",
            "{country} China renewable developer Sinosure financing team project portfolio EPC",
            "{country} CEEC PowerChina SANY Universal Energy AMEA Voltalia wind solar project financing",
        ],
        "domainBoost": ["sanyglobal.com", "powerchina.cn", "ceec.net.cn", "sinosure.com.cn", "eximbank.gov.cn"],
    },
    {
        "id": "local-language-china-capital-trace",
        "intent": "exploratory",
        "freshness": "pm",
        "focus": "Chinese capital plus official-language project names, translated names, SPVs, EPC notices, and local aliases",
        "patterns": [
            "{country} {technology} China capital EPC local project name {official_languages}",
            "{country} {technology} PowerChina CEEC Goldwind SANY Envision Chinese financing {official_languages}",
            "{known_projects} {country} {technology} local language name Chinese EPC financing",
        ],
        "domainBoost": ["powerchina.cn", "ceec.net.cn", "goldwind.com", "sanyglobal.com", "invest.gov.kz"],
    },
    {
        "id": "new-entrant-hunter",
        "intent": "news",
        "freshness": "pm",
        "focus": "new entrants, newly awarded developers, recent SPVs, local partners, corporate offtakers, and first-time market actors",
        "patterns": [
            "{country} {technology} new entrant developer awarded project PPA {year}",
            "{country} {technology} newly registered SPV renewable project local partner {official_languages}",
            "{country} {technology} first project market entry IPP EPC OEM {year}",
        ],
        "domainBoost": ["invest.gov.kz", "korem.kz", "rfc.kz", "acwapower.com", "masdar.ae"],
    },
    {
        "id": "policy-law-backtrace",
        "intent": "resource",
        "freshness": "py",
        "focus": "trace policy targets, auction numbers, tariffs, and capacity goals back to original laws, decrees, orders, and regulator documents",
        "patterns": [
            "{country} renewable energy target decree law order number {year}",
            "{country} {technology} auction tariff regulation decree original law {official_languages}",
            "{country} renewable capacity target 2030 legal basis regulator decree PDF",
        ],
        "domainBoost": ["adilet.zan.kz", "korem.kz", "rfc.kz", "energy.gov.kz", "gov.kz"],
    },
    {
        "id": "anomaly-hunter",
        "intent": "exploratory",
        "freshness": "pm",
        "focus": "odd spellings, transliterations, map/table/PDF-only mentions, local-language names, and projects outside the known developer pattern",
        "patterns": [
            "{country} {technology} farm transliteration misspelling local language PDF map",
            "{country} {technology} {official_languages} site:gov.kz filetype:pdf",
            "{known_projects} alternative spelling renamed project phase {country} {technology}",
        ],
        "domainBoost": ["gov.kz", "adilet.zan.kz", "kegoc.kz", "wikimapia.org"],
    },
    {
        "id": "regional-benchmark",
        "intent": "comparison",
        "freshness": "py",
        "focus": "peer market comparison and resource allocation priority",
        "patterns": [
            "{country} vs Uzbekistan wind market comparison renewable auction grid PPA",
            "{country} Azerbaijan Mongolia Saudi wind market comparison OEM opportunity",
            "Central Asia wind power market comparison Kazakhstan Uzbekistan Azerbaijan Mongolia",
        ],
        "domainBoost": ["irena.org", "iea.org", "ebrd.com", "adb.org"],
    },
    {
        "id": "mingyang-entry-strategy",
        "intent": "comparison",
        "freshness": "py",
        "focus": "turbine supply, hybrid systems, co-development, EPC consortium, O&M, storage, localization, 12/36/60 month actions",
        "patterns": [
            "{country} wind OEM market entry strategy turbine supply EPC O&M localization",
            "{country} wind solar storage integrated solution opportunity industrial PPA",
            "Mingyang {country} wind turbine opportunity partnership localization",
        ],
        "domainBoost": ["myse.com.cn", "invest.gov.kz", "kegoc.kz", "acwapower.com"],
    },
]

TOOL_LANES = [
    {
        "id": "exa-search",
        "priority": 1,
        "use": "broad semantic discovery with category filters and highlighted snippets",
        "record": {"collectionMethod": "exa-search", "requiredFields": ["title", "url", "publisher", "accessedAt"]},
    },
    {
        "id": "exa-fetch",
        "priority": 2,
        "use": "full-text extraction for known official URLs and PDFs indexed by Exa",
        "record": {"collectionMethod": "exa-fetch", "requiredFields": ["title", "url", "publisher", "accessedAt"]},
    },
    {
        "id": "exa-deep-search",
        "priority": 3,
        "use": "selective cross-source synthesis for complex comparison, status, and exploratory gaps when quota allows",
        "record": {"collectionMethod": "exa-deep-search", "requiredFields": ["title", "url", "publisher", "accessedAt"]},
    },
    {
        "id": "chrome-mcp",
        "priority": 4,
        "use": "sanitized human-browser verification for dynamic pages, tables, maps, PDFs, downloads, and bot-sensitive pages",
        "record": {"collectionMethod": "chrome-mcp", "requiredFields": ["title", "url", "publisher", "accessedAt"]},
    },
    {
        "id": "general-web-search",
        "priority": 5,
        "use": "last-resort fallback when Exa and Chrome MCP are unavailable or insufficient",
        "record": {"collectionMethod": "general-web-search", "requiredFields": ["title", "url", "publisher", "accessedAt"]},
    },
]

INTENT_WEIGHTS = {
    "status": {"freshness": 0.45, "authority": 0.35, "keyword": 0.20},
    "news": {"freshness": 0.60, "authority": 0.25, "keyword": 0.15},
    "comparison": {"freshness": 0.20, "authority": 0.40, "keyword": 0.40},
    "exploratory": {"freshness": 0.20, "authority": 0.50, "keyword": 0.30},
    "resource": {"freshness": 0.10, "authority": 0.40, "keyword": 0.50},
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "market"


def render_query_with_context(
    pattern: str,
    country: str,
    technology: str,
    year: int,
    audience: str,
    official_languages: list[str],
    known_projects: list[str],
) -> str:
    language_text = ", ".join(official_languages) if official_languages else "official language"
    project_text = ", ".join(known_projects) if known_projects else "known project names"
    query = pattern.format(
        country=country,
        technology=technology,
        year=year,
        audience=audience,
        official_languages=language_text,
        known_projects=project_text,
    ).strip()
    if technology.lower() not in query.lower():
        query = f"{query} {technology}"
    return query


def required_passes_for_dimension(dimension_id: str) -> list[str]:
    passes = ["english-broad", "official-language"]
    if "policy" in dimension_id:
        passes.append("source-backtrace")
    if dimension_id in {"market-key-indicators-timeseries", "auction-tariff-comparison"}:
        passes.extend(["source-backtrace", "chrome-verification"])
    if dimension_id in {"project-pipeline-layered", "owners-partners-routes", "china-finance-ecosystem"}:
        passes.append("china-capital-local-language")
    if dimension_id in {"anchor-developer-deep-dives", "chinese-developer-deep-dives"}:
        passes.extend(["official-language", "chrome-verification"])
    if dimension_id in {"competitor-oem-landscape", "epc-om-logistics-lifting"}:
        passes.append("chrome-verification")
    if dimension_id == "local-language-china-capital-trace":
        passes.extend(["china-capital-local-language", "chrome-verification"])
    if dimension_id == "new-entrant-hunter":
        passes.extend(["new-entrant", "official-language"])
    if dimension_id == "policy-law-backtrace":
        passes.extend(["source-backtrace", "chrome-verification"])
    if dimension_id == "anomaly-hunter":
        passes.extend(["anomaly-hunter", "official-language"])
    return list(dict.fromkeys(passes))


def build_plan(
    country: str,
    technology: str,
    audience: str,
    output_slug: str | None,
    official_languages: list[str] | None = None,
    known_projects: list[str] | None = None,
    include_benchmark: bool = False,
) -> dict[str, Any]:
    year = datetime.now(timezone.utc).year
    slug = output_slug or f"{slugify(country)}-{slugify(technology)}"
    official_languages = official_languages or []
    known_projects = known_projects or []
    dimensions = []
    for dimension in DIMENSIONS:
        if dimension["id"] == "regional-benchmark" and not include_benchmark:
            continue
        intent = dimension["intent"]
        queries = [
            render_query_with_context(pattern, country, technology, year, audience, official_languages, known_projects)
            for pattern in dimension["patterns"]
        ]
        dimensions.append(
            {
                "id": dimension["id"],
                "intent": intent,
                "freshness": dimension["freshness"],
                "focus": dimension["focus"],
                "queries": queries,
                "domainBoost": dimension["domainBoost"],
                "scoringWeights": INTENT_WEIGHTS[intent],
                "depthFile": f"data/renewable-market/depth/{dimension['id']}.json",
                "minimumEvidence": {
                    "records": 3,
                    "uniqueUrls": 3,
                    "collectionMethods": ["exa-search"],
                    "preferredVerificationMethods": ["chrome-mcp"],
                    "requiredPasses": required_passes_for_dimension(dimension["id"]),
                    "requiredFields": ["topic", "facts", "sources", "confidence", "uncertainty"],
                },
            }
        )
    return {
        "version": "1.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "country": country,
        "technology": technology,
        "audience": audience,
        "officialLanguages": official_languages,
        "knownProjects": known_projects,
        "includeBenchmark": include_benchmark,
        "slug": slug,
        "toolLanes": TOOL_LANES,
        "dimensions": dimensions,
        "outputs": {
            "index": "data/renewable-market/index.json",
            "mainJson": f"data/renewable-market/{slug}.json",
            "projectsCsv": f"data/renewable-market/{slug}.csv",
            "timelineCsv": f"data/renewable-market/{slug}-project-timeline.csv",
            "fullReportMd": f"data/renewable-market/{slug}-report.md",
            "liteReportMd": f"data/renewable-market/{slug}-lite.md",
            "fullReportPdf": f"data/renewable-market/{slug}-report.pdf",
            "liteReportPdf": f"data/renewable-market/{slug}-lite.pdf",
        },
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


SOURCE_REQUIRED_FIELD_ALIASES = [
    ("url",),
    ("title",),
    ("publisher",),
    ("accessedAt", "accessed_at"),
    ("sourceLanguage", "source_language"),
    ("collectionMethod", "collection_method"),
]


def get_any(mapping: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for alias in aliases:
        value = mapping.get(alias)
        if value not in (None, "", []):
            return value
    return None


def source_urls(record: dict[str, Any]) -> list[str]:
    urls = []
    sources = record.get("sources", [])
    if isinstance(sources, list):
        for source in sources:
            if isinstance(source, dict) and source.get("url"):
                urls.append(str(source["url"]))
    facts = record.get("facts", [])
    if isinstance(facts, list):
        for fact in facts:
            if isinstance(fact, dict):
                fact_sources = fact.get("sources", [])
                if isinstance(fact_sources, list):
                    for source in fact_sources:
                        if isinstance(source, dict) and source.get("url"):
                            urls.append(str(source["url"]))
    return urls



def source_missing_fields(record: dict[str, Any]) -> list[str]:
    issues = []
    sources = record.get("sources", [])
    if isinstance(sources, list):
        for source_index, source in enumerate(sources):
            if isinstance(source, dict):
                missing = []
                for aliases in SOURCE_REQUIRED_FIELD_ALIASES:
                    if get_any(source, aliases) is None and get_any(record, aliases) is None:
                        missing.append("/".join(aliases))
                if missing:
                    issues.append(f"source {source_index} missing fields: {', '.join(missing)}")
    facts = record.get("facts", [])
    if isinstance(facts, list):
        for fact_index, fact in enumerate(facts):
            if not isinstance(fact, dict):
                continue
            fact_sources = fact.get("sources", [])
            if isinstance(fact_sources, list):
                for source_index, source in enumerate(fact_sources):
                    if isinstance(source, dict):
                        missing = []
                        for aliases in SOURCE_REQUIRED_FIELD_ALIASES:
                            if get_any(source, aliases) is None and get_any(fact, aliases) is None and get_any(record, aliases) is None:
                                missing.append("/".join(aliases))
                        if missing:
                            issues.append(
                                f"fact {fact_index} source {source_index} missing fields: {', '.join(missing)}"
                            )
    return issues


def record_search_passes(record: dict[str, Any]) -> list[str]:
    passes: list[str] = []
    for key in ("searchPass", "search_pass"):
        value = record.get(key)
        if isinstance(value, str) and value:
            passes.append(value)
    for key in ("searchPasses", "search_passes", "coverageTags", "coverage_tags"):
        value = record.get(key)
        if isinstance(value, list):
            passes.extend(str(item) for item in value if item)
        elif isinstance(value, str) and value:
            passes.append(value)
    return passes


def record_collection_methods(record: dict[str, Any]) -> list[str]:
    methods: list[str] = []
    method = get_any(record, ("collectionMethod", "collection_method"))
    if isinstance(method, str) and method:
        methods.append(method)
    sources = record.get("sources", [])
    if isinstance(sources, list):
        for source in sources:
            if isinstance(source, dict):
                source_method = get_any(source, ("collectionMethod", "collection_method"))
                if isinstance(source_method, str) and source_method:
                    methods.append(source_method)
    facts = record.get("facts", [])
    if isinstance(facts, list):
        for fact in facts:
            if not isinstance(fact, dict):
                continue
            fact_sources = fact.get("sources", [])
            if isinstance(fact_sources, list):
                for source in fact_sources:
                    if isinstance(source, dict):
                        source_method = get_any(source, ("collectionMethod", "collection_method"))
                        if isinstance(source_method, str) and source_method:
                            methods.append(source_method)
    if not methods and isinstance(record.get("notes"), str) and "chrome" in record["notes"].lower():
        methods.append("chrome-mcp")
    return methods

def record_missing_fields(record: dict[str, Any], fields: list[str]) -> list[str]:
    missing = []
    for field in fields:
        value = record.get(field)
        if value in (None, "", []):
            missing.append(field)
    return missing


def validate_depth_file(path: Path, minimum: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "status": "missing", "records": 0, "uniqueUrls": 0, "issues": ["file not found"]}
    data = load_json(path)
    if not isinstance(data, list):
        return {"path": str(path), "status": "invalid", "records": 0, "uniqueUrls": 0, "issues": ["depth file must be a JSON array"]}

    required_fields = minimum.get("requiredFields", [])
    urls: set[str] = set()
    methods: Counter[str] = Counter()
    search_passes: Counter[str] = Counter()
    issues = []
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            issues.append(f"record {index} is not an object")
            continue
        missing = record_missing_fields(record, required_fields)
        if missing:
            issues.append(f"record {index} missing fields: {', '.join(missing)}")
        for source_issue in source_missing_fields(record):
            issues.append(f"record {index} {source_issue}")
        urls.update(source_urls(record))
        for method in record_collection_methods(record):
            methods[method] += 1
        for search_pass in record_search_passes(record):
            search_passes[search_pass] += 1

    min_records = int(minimum.get("records", 0))
    min_urls = int(minimum.get("uniqueUrls", 0))
    required_methods = minimum.get("collectionMethods", [])
    required_passes = minimum.get("requiredPasses", [])
    if len(data) < min_records:
        issues.append(f"record count {len(data)} below minimum {min_records}")
    if len(urls) < min_urls:
        issues.append(f"unique URL count {len(urls)} below minimum {min_urls}")
    missing_methods = [method for method in required_methods if methods.get(method, 0) == 0]
    if missing_methods:
        issues.append(f"missing required collection methods: {', '.join(missing_methods)}")
    missing_passes = [search_pass for search_pass in required_passes if search_passes.get(search_pass, 0) == 0]
    if missing_passes:
        issues.append(f"missing required search passes: {', '.join(missing_passes)}")

    status = "pass" if not issues else "needs-work"
    return {
        "path": str(path),
        "status": status,
        "records": len(data),
        "uniqueUrls": len(urls),
        "collectionMethods": dict(methods),
        "searchPasses": dict(search_passes),
        "issues": issues,
    }


def validate_plan(plan_path: Path, depth_dir: Path) -> dict[str, Any]:
    plan = load_json(plan_path)
    dimensions = plan.get("dimensions", [])
    results = []
    for dimension in dimensions:
        if not isinstance(dimension, dict):
            continue
        depth_file = Path(str(dimension.get("depthFile", "")))
        if not depth_file.is_absolute():
            depth_file = depth_dir / depth_file.name
        results.append(validate_depth_file(depth_file, dimension.get("minimumEvidence", {})))
    summary = Counter(result["status"] for result in results)
    return {
        "plan": str(plan_path),
        "depthDir": str(depth_dir),
        "validatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": dict(summary),
        "dimensions": results,
        "overallStatus": "pass" if summary and set(summary) == {"pass"} else "needs-work",
    }


def write_json(data: dict[str, Any], output: Path | None) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def split_csv_arg(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan or validate renewable market search coverage.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Generate a dimension-level search plan JSON.")
    plan_parser.add_argument("--country", required=True)
    plan_parser.add_argument("--technology", required=True)
    plan_parser.add_argument("--audience", default="commercial-entry")
    plan_parser.add_argument("--slug")
    plan_parser.add_argument("--official-languages", help="Comma-separated official/local languages to force into search passes.")
    plan_parser.add_argument("--known-projects", help="Comma-separated seed project names for alias and anomaly searches.")
    plan_parser.add_argument("--include-benchmark", action="store_true", help="Include regional/peer-country benchmark dimension only when explicitly requested.")
    plan_parser.add_argument("--output", type=Path)

    validate_parser = subparsers.add_parser("validate", help="Validate depth JSON coverage against a search plan.")
    validate_parser.add_argument("--plan", required=True, type=Path)
    validate_parser.add_argument("--depth-dir", default=Path("data/renewable-market/depth"), type=Path)
    validate_parser.add_argument("--output", type=Path)

    args = parser.parse_args()
    if args.command == "plan":
        data = build_plan(
            args.country,
            args.technology,
            args.audience,
            args.slug,
            split_csv_arg(args.official_languages),
            split_csv_arg(args.known_projects),
            args.include_benchmark,
        )
        write_json(data, args.output)
        return 0
    if args.command == "validate":
        data = validate_plan(args.plan, args.depth_dir)
        write_json(data, args.output)
        return 0 if data["overallStatus"] == "pass" else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
