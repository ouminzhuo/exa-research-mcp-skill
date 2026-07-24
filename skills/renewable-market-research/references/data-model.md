# Renewable Market Data Model

## Directory Layout

```text
data/renewable-market/
├── index.json
├── {country}-{technology}.json
├── {country}-{technology}.csv
├── depth/
│   ├── project-pipeline.json
│   ├── ifi-financing.json
│   ├── technology-epc.json
│   └── carbon-hydrogen.json
├── verification/
├── chapter_inputs/
├── chapter_drafts/
├── audits/
├── {country}-{technology}-report.md
├── {country}-{technology}-lite.md
├── {country}-{technology}-report.pdf
└── {country}-{technology}-lite.pdf
```

Also produce:

- `{country}-{technology}-phase_state.json`: state-machine phase tracker using `schema/phase-state.schema.json`.
- `{country}-{technology}-artifact_manifest.json`: writer ownership and artifact dependency manifest using `schema/artifact-manifest.schema.json`.
- `{country}-{technology}-agent_plan.json`: generated role/phase assignment plan for the run.
- `{country}-{technology}-pipeline-ledger.json`: compact canonical project registry for identity, dedupe, evidence layers, and confirmed/watchlist/rejected state.
- `{country}-{technology}-project_ledger.json`: full project ledger using `schema/project-ledger.schema.json`; this is the project database core.
- `{country}-{technology}-metric_ledger.json`, `{country}-{technology}-policy_target_ledger.json`, `{country}-{technology}-auction_ledger.json`, and `{country}-{technology}-oem_allocation_ledger.json`: core ledgers for reusable facts that should not be recomputed by chapters. Metric and OEM allocation ledgers should follow `schema/metric-ledger.schema.json` and `schema/oem-allocation-ledger.schema.json`.
- `{country}-{technology}-capacity_reconciliation.json`: machine-readable capacity arithmetic using `schema/capacity-reconciliation.schema.json`, including project subtotals, official auction/award totals, identifiable project capacity, unresolved gap, and active/inactive exclusions.
- `{country}-{technology}-canonical_facts.json`: post-ledger fact freeze using `schema/canonical-facts.schema.json`.
- `{country}-{technology}-project_cards.json`: complete project cards using `schema/project-card.schema.json`; report prose may summarize, but this file must preserve all card fields.
- `{country}-{technology}-evidence_table.json`: conclusion-level evidence table using `schema/evidence-table.schema.json`; this is required for evidence-boundary checks.
- `{country}-{technology}-fact_freeze.json`: compatibility frozen fact contract using `schema/fact-freeze.schema.json`; chapters must cite frozen IDs and must not recalculate capacity, policy status, project activity status, auction/project deltas, or OEM relationship categories.
- `chapter_inputs/{slug}-chapter-*-input-manifest.json`: per-chapter frozen input contract using `schema/chapter-input-manifest.schema.json`.
- `chapter_drafts/{slug}-chapter-*.md`: per-chapter drafts written from manifests before final assembly.
- `audits/{slug}-cross_chapter_audit.json`: cross-chapter consistency audit and repair state.
- `{country}-{technology}-participant_ledger.json`, `{country}-{technology}-oem_competition.json`, `{country}-{technology}-procurement_window.json`, `{country}-{technology}-risk_matrix.json`, and `{country}-{technology}-tracking_watchlist.json` when enough data exists.
- `{country}-{technology}-integrity.json`: output from `scripts/validate_market_integrity.py`.

## File Roles and Source Priority

| File | Role | Enough to write final reports? |
|---|---|---|
| `{slug}.json` | Rich master data source. It must preserve the full schema fields needed for project cards, market indicators, developer deep dives, OEM/specs, logistics, policy, tariff, carbon, and conclusions. | Yes. This is the primary report source after validation. |
| `depth/*.json` | Detailed per-dimension evidence and raw structured findings. Use it to cross-read card/chapter details and backfill the master JSON. | Yes as fallback/evidence, but normalize into `{slug}.json` before final writing. |
| `verification/*.json` | Source-specific checks and critical-field verification artifacts. | No. These support ledger admission and chapter verification. |
| `{slug}-pipeline-ledger.json` | Canonical project registry for dedupe, aliases, evidence layers, confirmed/watchlist/rejected decisions, and source-trace control. | No. It is intentionally compact and must not replace the rich master JSON for report cards. |
| `{slug}-project_ledger.json` | Full ledger with capacity MW, Opportunity MW, count flags, owner/SPV/equity, OEM/procurement/turbine, EPC/O&M, finance, PPA/tariff, COD, evidence, confidence, pending verification, and Mingyang relevance. | Yes for ledger tables and capacity reconciliation. |
| `{slug}-metric_ledger.json`, `{slug}-policy_target_ledger.json`, `{slug}-auction_ledger.json`, `{slug}-oem_allocation_ledger.json` | Core ledgers for cross-chapter metrics, targets, auction allocations, and OEM MW buckets. Metric and OEM allocation ledgers must keep scope, denominator, included/excluded IDs, source IDs, and confidence explicit. | Yes as frozen inputs after main-agent reconciliation. |
| `{slug}-capacity_reconciliation.json` | Machine-readable reconciliation for project subtotals, official award totals, identifiable project capacity, unresolved gap, active pipeline exclusions, and OEM MW bucket arithmetic. | Yes for capacity and audit gates. |
| `{slug}-canonical_facts.json` | Unified fact freeze built after rich master JSON and core ledgers. It owns contested capacity scopes, policy status, auction/project differences, project status split, OEM relationship split, deprecated values, and repair routing. | Yes as the main chapter dependency contract. |
| `{slug}-project_cards.json` | Complete project-card objects. Unknown values are allowed only as explicit `待核`, `unavailable`, `not found`, or equivalent markers. | Yes for Chapter 6/project-card appendix. |
| `{slug}-evidence_table.json` | Conclusion-level evidence records linking claims to source grade, direct proof, confidence, related field, and pending verification action. | Yes for Chapter 16/source-confidence appendix. |
| `{slug}-fact_freeze.json` | Compatibility view of frozen facts for runners that still expect the old filename. | Yes as a precondition, but it must be generated after core ledgers. |
| `chapter_inputs/*.json` | Per-chapter allowed fact/project/metric/policy/auction/OEM IDs, prohibited deprecated values, and required disclosures. | Yes. A chapter cannot draft outside its manifest. |
| `chapter_drafts/*.md` | Chapter prose drafts produced from frozen manifests. | No. Drafts require verification/audit and main-agent assembly before release. |
| `audits/*.json` | Cross-chapter audit, stale artifact detection, repair routing, and release blockers. | No. It gates release. |

Source priority for writing reports:

1. Read `{slug}.json` for report-ready fields.
2. Cross-read the matching `depth/*.json` records named in `sourceTrace` or `mergedFromDepthRecords`.
3. Use `{slug}-pipeline-ledger.json` only for canonical project identity, status grouping, dedupe decisions, evidence layers, and watchlist/rejected state.
4. Use `{slug}-project_ledger.json`, core ledgers, `{slug}-canonical_facts.json`, `{slug}-fact_freeze.json`, `{slug}-project_cards.json`, `{slug}-evidence_table.json`, chapter input manifests, and cross-chapter audit as the gate artifacts before final report prose is released.

## Gate Artifacts

The full report generation order is fixed:

```text
phase_state / artifact_manifest / agent_plan
  -> candidate_project_pool
  -> source_trace / evidence_table
  -> rich_master_json
  -> project_ledger / metric_ledger / policy_target_ledger / auction_ledger / oem_allocation_ledger / capacity_reconciliation
  -> canonical_facts / fact_freeze
  -> participant_ledger / oem_competition_matrix / procurement_window_table / detailed_project_cards / risk_matrix
  -> chapter_input_manifests
  -> chapter_drafts
  -> cross_chapter_audit / repair
  -> full_report
  -> lite_report
```

Do not let an agent write `{slug}-report.md` directly from notes or depth files. The report writer reads the gate artifacts and expresses the current market status; it does not become the database.

Before any chapter draft, generate `{slug}-canonical_facts.json` and `{slug}-fact_freeze.json` after the rich master JSON and core ledgers. They must freeze:

- capacity scopes: official auction total, identifiable project capacity, confirmed project capacity, Opportunity MW, watchlist MW, suspended/paused MW;
- policy status: enacted target, draft target, political statement target, and auction allocation;
- project state: `developmentStage`, `activityStatus`, `ledgerTreatment`, and `capacityTreatment`;
- OEM relationship: `oemRelationshipType` and `oemRelationshipStatus`.
- deprecated values from older reports, plus repair routing when a chapter finds a contradiction.

Hard boundaries:

- official auction total is not identifiable project capacity;
- policy target is not draft target or political statement;
- firm OEM order is not strategic preference;
- paused, withdrawn, cancelled, or superseded projects cannot enter active opportunity totals;
- do not use ambiguous `locked MW`; use only Firm MW, Committed MW, Influenced MW, Unallocated MW, and Excluded inactive MW.

Release audit boundaries:

- same `metricId` cannot have different normalized values across chapters;
- aggregate capacity metrics must disclose scope, time, and basis;
- project subtotals must equal ledger aggregates, and official auction/award total minus identifiable project capacity must equal unresolved gap;
- OEM shares in the same statistical layer must total no more than 100%, and Firm MW denominators cannot include Influenced MW;
- a project cannot appear with conflicting current statuses across chapter tables;
- government zones, developer portfolios, parent projects, phases, and concrete projects cannot be summed without explicit rollup treatment;
- visible arithmetic must reconcile across MW/GW, percentages, KRW 亿/万亿, USD/KRW, project counts, and subtotals;
- release output must not contain internal version labels, repairs-applied notes, deletion markup, TODO/FIXME, unconverted footnotes, or raw JSON.

For full reports, also generate or maintain these agent-control artifacts:

- `{slug}-agent_plan.json`: copied or distilled from the generated plan's `fullReportAgentProfile`, `agentTopology`, `chapterVerificationPolicy`, and `chapterAgentPlan`.
- `{slug}-phase_state.json` and `{slug}-artifact_manifest.json`: phase-order and writer-ownership control.
- `chapter_inputs/{slug}-chapter-*-input-manifest.json`: per-chapter frozen inputs.
- `chapter_drafts/{slug}-chapter-*.md`: per-chapter writer outputs before final assembly.
- `chapter_verification/{slug}-chapter-*-verification.json`: independent verification outputs for critical chapters 1, 3, 4, 5, 6, 9, 13, 14, and 16.
- `audits/{slug}-cross_chapter_audit.json`: cross-chapter consistency, stale-artifact, and deprecated-value audit.

The validator can enforce the gates:

```text
python skills/renewable-market-research/scripts/validate_market_integrity.py data/renewable-market/{slug}.json --depth-dir data/renewable-market/depth --phase-state data/renewable-market/{slug}-phase_state.json --artifact-manifest data/renewable-market/{slug}-artifact_manifest.json --candidate-pool data/renewable-market/{slug}-candidate_project_pool.json --project-ledger data/renewable-market/{slug}-project_ledger.json --metric-ledger data/renewable-market/{slug}-metric_ledger.json --capacity-reconciliation data/renewable-market/{slug}-capacity_reconciliation.json --oem-allocation-ledger data/renewable-market/{slug}-oem_allocation_ledger.json --project-cards data/renewable-market/{slug}-project_cards.json --evidence-table data/renewable-market/{slug}-evidence_table.json --canonical-facts data/renewable-market/{slug}-canonical_facts.json --fact-freeze data/renewable-market/{slug}-fact_freeze.json --chapter-input-dir data/renewable-market/chapter_inputs --chapter-drafts-dir data/renewable-market/chapter_drafts --audits-dir data/renewable-market/audits --full-report data/renewable-market/{slug}-report.md --output data/renewable-market/{slug}-integrity.json
```

The `gateSummary` in `{slug}-integrity.json` must show zero gaps before release. `v4GateSummary` may also appear as a backward-compatible alias. If any gate is nonzero, the report must explicitly remain in draft/gap status.

## Rich Field Propagation Contract

During aggregation, every rich project field found in depth records must be propagated into the matching project in `{slug}.json`, or explicitly marked as `not found`, `unavailable`, or `not applicable` with a gap note. This applies especially to:

- `annualGenerationGWh`, `annualCO2ReductionTonnes`, `investmentUSD`;
- `turbineModel`, `turbineCount`, `hubHeightM`, `rotorDiameterM`, `bladeLengthM`;
- `storageMWh`, coordinates, site area, technology route;
- logistics route, jobs/local employment, biodiversity/bird protection, community/land impact;
- key people and developer/deep-dive fields when project-specific;
- procurement and sales-opportunity fields such as currentOemStatus, oemShortlist, procurementWindow, decisionMaker, procurementInfluencers, likelyTenderRoute, bankabilityConstraint, salesEntryPoint, and adjacentOpportunityImpact.

Run `scripts/validate_market_integrity.py --depth-dir data/renewable-market/depth` before report writing. A `depthPropagationGaps` or `reportCardFieldGaps` result means the master JSON is not report-ready.

## `index.json`

```json
{
  "version": "1.0",
  "lastUpdated": "2026-05-16T16:35:00+08:00",
  "markets": [
    {
      "slug": "uzbekistan-wind",
      "country": "uzbekistan",
      "technology": "wind",
      "status": "collected",
      "mainData": "data/renewable-market/uzbekistan-wind.json",
      "csv": "data/renewable-market/uzbekistan-wind.csv",
      "fullReport": "data/renewable-market/uzbekistan-wind-report.md",
      "liteReport": "data/renewable-market/uzbekistan-wind-lite.md",
      "fullPdf": "data/renewable-market/uzbekistan-wind-report.pdf",
      "litePdf": "data/renewable-market/uzbekistan-wind-lite.pdf",
      "coverage": {
        "projectPipeline": "high",
        "policy": "medium",
        "financing": "high",
        "technology": "medium"
      },
      "convergence": [
        {
          "dimension": "ifi-financing",
          "rounds": 5,
          "newRecords": 28,
          "stoppedReason": "3 consecutive rounds without material new records",
          "remainingGaps": ["commercial bank tranche details not fully public"]
        }
      ]
    }
  ]
}
```

## Main JSON Schema

```json
{
  "metadata": {
    "country": "uzbekistan",
    "technology": "wind",
    "lastUpdated": "2026-05-16T16:35:00+08:00",
    "dataSources": [{"name": "ADB", "url": "https://..."}],
    "projectCount": 25,
    "confirmedPipelineMW": 17000,
    "allPhasesMW": 25000,
    "sourceToFinal": {
      "pipelineLedger": "data/renewable-market/uzbekistan-wind-pipeline-ledger.json",
      "pipelineLedgerUpdatedAt": "2026-05-16T16:35:00+08:00",
      "summaryBackpropagationAt": "2026-05-16T18:10:00+08:00",
      "finalClaimsCheckedAgainstLedger": true,
      "remainingContinuityGaps": []
    },
    "note": "Collection status and caveats"
  },
  "projects": [
    {
      "id": "uzbekistan-wind-001",
      "name": "Zarafshan Wind Farm",
      "canonicalName": "Zarafshan Wind Farm",
      "nameVariants": [
        {"language": "en", "value": "Zarafshan Wind Farm", "sourceUrl": "https://..."}
      ],
      "dedupeKey": "zarafshan|navoi-tamdy|522|masdar",
      "capacityMW": 521.7,
      "opportunityMW": 0,
      "status": "operational",
      "developmentStage": "operational",
      "activityStatus": "active",
      "ledgerTreatment": "confirmed",
      "capacityTreatment": "confirmed_capacity",
      "capacityScope": "confirmed_project_capacity",
      "developer": "Masdar",
      "developerCountry": "UAE",
      "location": "Navoi region, Tamdy district",
      "coordinates": {"lat": null, "lon": null},
      "siteAreaHa": null,
      "cod": "2024-12-14",
      "ppaType": "Government PPA",
      "ppaDuration": 25,
      "investmentUSD": 593400000,
      "turbineModel": "Goldwind GW155-4.5MW",
      "turbineCount": 111,
      "hubHeightM": null,
      "rotorDiameterM": null,
      "bladeLengthM": null,
      "technologyRoute": "onshore wind",
      "epc": "POWERCHINA/SEPCOIII",
      "annualGenerationGWh": 1100,
      "annualCO2ReductionTonnes": 1100000,
      "jobsOrLocalEmployment": null,
      "biodiversityBirdProtection": "unavailable",
      "communityLandImpact": "unavailable",
      "storageMWh": null,
      "currentOemStatus": "awarded to Goldwind",
      "oemRelationshipType": "firm_supply_contract",
      "oemRelationshipStatus": "active",
      "oemShortlist": ["Goldwind"],
      "procurementWindow": "closed",
      "decisionMaker": "developer/SPV procurement team",
      "procurementInfluencers": ["EPC", "lenders", "offtaker"],
      "likelyTenderRoute": "awarded package",
      "bankabilityConstraint": "MDB/owner technical acceptance",
      "salesEntryPoint": "closed project; use as reference case for future owner pipeline",
      "adjacentOpportunityImpact": [
        {
          "topic": "storage / solar / green hydrogen / ammonia / methanol / industrial offtake if relevant",
          "impactOnWindOpportunity": "explain only when it changes PPA value, interconnection, procurement scope, OEM opportunity, or sales entry",
          "sourceUrl": "https://..."
        }
      ],
      "financing": "ADB $95M, EBRD $74M, IFC $42M...",
      "sources": [
        {
          "url": "https://...",
          "title": "Source title",
          "publisher": "Publisher",
          "accessedAt": "2026-05-16",
          "sourceLanguage": "en",
          "collectionMethod": "exa-fetch"
        }
      ],
      "sourceTrace": [
        {
          "depthFile": "data/renewable-market/depth/project-pipeline-layered.json",
          "recordIndex": 0,
          "fact": "capacity and COD",
          "sourceUrl": "https://..."
        }
      ],
      "criticalFieldVerification": {
        "capacity_mw": {
          "sourceUrl": "https://...",
          "collectionMethod": "exa-fetch",
          "verifiedAt": "2026-05-16",
          "note": "Capacity verified from owner/MDB/original file text."
        },
        "status": {
          "sourceUrl": "https://...",
          "collectionMethod": "chrome-mcp",
          "verifiedAt": "2026-05-16",
          "note": "Operational/construction/PPA status verified from original page/PDF/table."
        },
        "cod_or_target_cod": {
          "sourceUrl": "https://...",
          "collectionMethod": "chrome-mcp",
          "verifiedAt": "2026-05-16",
          "note": "COD or target COD verified; unresolved conflicts remain in uncertainty."
        }
      },
      "duplicateCheckNotes": "Merged English and local-language references; no separate phase boundary found.",
      "confidence": "high",
      "evidenceStage": "ppa-signed",
      "mingyangOpportunityWindow": "Medium-term turbine + EPC consortium window",
      "uncertainty": "SPV equity split not fully disclosed",
      "lastVerified": "2026-05-16"
    }
  ],
  "demandLoadGap": [],
  "nationalPlans": [],
  "policyFramework": [],
  "forecasts": [],
  "developers": [],
  "financing": [],
  "technology": [],
  "environmentSocial": [],
  "carbonHydrogen": [],
  "risks": [],
  "entryStrategy": []
}
```

## Canonical Project Ledger

Use `{slug}-pipeline-ledger.json` as the canonical registry for project identity, deduplication, evidence layers, and confirmed/watchlist/rejected decisions. Do not use it as the only source for final project cards; final card fields must come from the validated `{slug}.json` and cross-checked `depth/*.json`.

```json
{
  "version": "1.0",
  "slug": "uzbekistan-wind",
  "updatedAt": "2026-05-16T16:35:00+08:00",
  "sourceDepthFiles": [
    "data/renewable-market/depth/project-pipeline-layered.json",
    "data/renewable-market/depth/local-language-china-capital-trace.json",
    "data/renewable-market/depth/anomaly-hunter.json"
  ],
  "projects": [
    {
      "canonicalProjectId": "uzbekistan-wind-001",
      "canonicalName": "Zarafshan Wind Farm",
      "nameVariants": [
        {"language": "en", "value": "Zarafshan Wind Farm", "sourceUrl": "https://..."},
        {"language": "local", "value": "local-language project name if found", "sourceUrl": "https://..."},
        {"language": "zh", "value": "Chinese translated/project name if found", "sourceUrl": "https://..."}
      ],
      "dedupeKey": "zarafshan|navoi-tamdy|522|masdar",
      "cardFields": {
        "coordinates": {"lat": null, "lon": null},
        "siteAreaHa": null,
        "hubHeightM": null,
        "rotorDiameterM": null,
        "bladeLengthM": null,
        "technologyRoute": "onshore wind",
        "annualGenerationGWh": null,
        "annualCO2ReductionTonnes": null,
        "jobsOrLocalEmployment": null,
        "biodiversityBirdProtection": "unavailable",
        "communityLandImpact": "unavailable",
        "currentOemStatus": "awarded / undecided / framework / unknown",
        "procurementWindow": "closed / 2026-2027 / not found",
        "salesEntryPoint": "project-specific route if relevant"
      },
      "mergedFromDepthRecords": [
        {"depthFile": "project-pipeline-layered.json", "recordIndex": 0},
        {"depthFile": "local-language-china-capital-trace.json", "recordIndex": 2}
      ],
      "sourceTrace": [
        {"fact": "capacityMW", "sourceUrl": "https://...", "sourceLanguage": "en", "collectionMethod": "exa-fetch"}
      ],
      "criticalFieldVerification": {
        "capacity_mw": {"collectionMethod": "exa-fetch", "sourceUrl": "https://...", "verifiedAt": "2026-05-16"},
        "status": {"collectionMethod": "chrome-mcp", "sourceUrl": "https://...", "verifiedAt": "2026-05-16"}
      },
      "pipelineBucket": "cod-operational",
      "developmentStage": "operational",
      "activityStatus": "active",
      "ledgerTreatment": "confirmed",
      "capacityTreatment": "confirmed_capacity",
      "capacityScope": "confirmed_project_capacity",
      "oemRelationshipType": "firm_supply_contract",
      "oemRelationshipStatus": "active",
      "confirmedPipelineEligible": true,
      "evidenceLayers": ["owner-announcement", "financing-closed", "cod-operational"],
      "duplicateResolution": "merged",
      "exclusionReason": null,
      "remainingGaps": []
    }
  ],
  "duplicateCandidates": [],
  "watchlist": [],
  "rejectedClaims": []
}
```

Reports, CSV exports, timelines, and executive summaries should read rich project fields from the validated master JSON. Use the ledger to keep canonical IDs, status buckets, duplicate decisions, and watchlist/rejected records consistent. If a later chapter discovers a new project, alias, or richer project field, update the master JSON first, rebuild/refresh the ledger, then refresh synthesis and summary.

## Depth File Record Shape

Depth files are arrays. Keep them narrow and source-rich:

```json
[
  {
    "dimension": "ifi-financing",
    "topic": "Zarafshan Wind Farm financing",
    "project": "Zarafshan Wind Farm",
    "company": "Masdar",
    "amountUSD": 95000000,
    "facts": ["ADB committed ...", "Loan tenor ..."],
    "sources": [
      {
        "title": "...",
        "url": "https://...",
        "publisher": "ADB",
        "accessedAt": "2026-05-16",
        "sourceLanguage": "en",
        "collectionMethod": "exa-search"
      }
    ],
    "searchPasses": ["english-broad", "chrome-verification"],
    "sourceTrace": "Candidate maps to canonical project ID uzbekistan-wind-001 after alias/dedupe review.",
    "confidence": "high",
    "uncertainty": "Public source lacks complete term-sheet details",
    "evidenceStage": "financing-closed",
    "notes": "Any conflict or gap"
  }
]
```

## CSV Columns

Use this exact order for project export:

```text
id,name,capacityMW,status,developer,developerCountry,location,cod,investmentUSD,turbineModel,turbineCount,annualGenerationGWh,annualCO2ReductionTonnes,ppaDuration,storageMWh,epc
```
