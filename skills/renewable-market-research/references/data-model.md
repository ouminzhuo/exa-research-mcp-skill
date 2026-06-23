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
├── {country}-{technology}-report.md
├── {country}-{technology}-lite.md
├── {country}-{technology}-report.pdf
└── {country}-{technology}-lite.pdf
```

Also produce:

- `{country}-{technology}-pipeline-ledger.json`: canonical project registry used by all report sections.
- `{country}-{technology}-integrity.json`: output from `scripts/validate_market_integrity.py`.

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
      "status": "operational",
      "developer": "Masdar",
      "developerCountry": "UAE",
      "location": "Navoi region, Tamdy district",
      "cod": "2024-12-14",
      "ppaType": "Government PPA",
      "ppaDuration": 25,
      "investmentUSD": 593400000,
      "turbineModel": "Goldwind GW155-4.5MW",
      "turbineCount": 111,
      "epc": "POWERCHINA/SEPCOIII",
      "annualGenerationGWh": 1100,
      "annualCO2ReductionTonnes": 1100000,
      "storageMWh": null,
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

Use `{slug}-pipeline-ledger.json` as the source of truth for project pipeline records before any report writing.

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

Reports, CSV exports, timelines, and executive summaries should read project records from this ledger or from a master JSON generated from this ledger. If a later chapter discovers a new project or alias, update the ledger first and then refresh synthesis and summary.

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
