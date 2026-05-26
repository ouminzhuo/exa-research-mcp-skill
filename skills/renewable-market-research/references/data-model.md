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
    "note": "Collection status and caveats"
  },
  "projects": [
    {
      "id": "uzbekistan-wind-001",
      "name": "Zarafshan Wind Farm",
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
          "accessedAt": "2026-05-16"
        }
      ],
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
        "accessedAt": "2026-05-16"
      }
    ],
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
