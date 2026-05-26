---
name: renewable-market-research
description: Comprehensive renewable-energy market intelligence workflow for any country plus technology, using effective-harnesses style state tracking, file-mode parallel research, Exa/web search, structured JSON/CSV data, convergence detection, and full/lite MD-to-PDF report outputs. Use when asked to research wind, solar, storage, hydrogen, grid, or other clean-energy markets and produce reusable data plus two report versions.
---

# Renewable Market Research

## Goal

Research **any country + any renewable/new-energy technology** and produce reusable market data plus two deliverables:

1. **Full report**: deep internal report with project pipeline, policy, developers, financing, technology, environment, carbon/hydrogen, risks, and sources.
2. **Lite report**: shorter delivery version with polished structure, project pipeline essentials, and reduced deep/proprietary analysis.

Use an effective-harnesses mindset: persist state to files, make progress resumable, validate outputs, and avoid returning large raw search payloads through chat.

## Required Reading

Load only the reference needed for the current step:

- `references/file-mode-research.md`: parallel/file-mode collection workflow, tool priority, convergence rules, and child-agent prompt template.
- `references/data-model.md`: directory layout, `index.json`, main JSON schema, depth JSON schema, and CSV columns.
- `references/pdf-pipeline.md`: full/lite report structure, MD-to-PDF pipeline, Chinese font handling, and output risks.
- `references/windows-native.md`: Windows native PowerShell/Python startup commands, CSV export wrapper, PDF caveats, and Chrome MCP browser rules.

## Standard Workflow

1. **Normalize task**
   - Extract `country`, `technology`, language, report depth, and target audience.
   - Slugify to `{country_slug}-{technology_slug}` such as `uzbekistan-wind`.
   - Create `data/renewable-market/` and `data/renewable-market/depth/` if missing.

2. **Resume or initialize harness state**
   - Read `data/renewable-market/index.json` if present.
   - If `{country_slug}-{technology_slug}.json` exists, run an incremental update; otherwise run first-time collection.
   - Optionally add/maintain `feature_list.json` entries for: collection, aggregation, full report, lite report, PDF rendering.

3. **Split research dimensions**
   Use 7-15 focused dimensions depending on scope. For OEM/commercial-entry asks (for example Mingyang), use **demand-first framing**: start from electricity demand gap and monetizable offtake, then validate resource/technology constraints.
   - demand-load-gap (generation, consumption, peak load, imports/exports, 5-10 year outlook)
   - power-mix-replacement (retirements, thermal constraints, hydro flexibility, wind/solar complementarity)
   - grid-storage-transmission (curtailment risk, substations/lines, storage requirement, cross-border corridors)
   - policy-ppa-economics (auction/FIT/PPA, tariff history, FX risk, localization, IRR/ROE if estimable)
   - project-pipeline-layered (operational, under-construction, awarded/PPA, MOU, early stage)
   - owners-partners-routes (state entities, IPPs, EPC/developer networks, contact pathways)
   - competitor-oem-landscape (OEM supply, turbine platforms, localization and tie strength)
   - epc-om-logistics-lifting (transport routes, heavy-lift constraints, installation window risks)
   - localization-supply-chain (tower/blade/nacelle/BESS ecosystem and JV options)
   - esg-land-community (ESIA, biodiversity, land/community, IFI social constraints)
   - carbon-greenpower-hydrogen (I-REC, CBAM, enterprise PPA, hydrogen/ammonia links)
   - china-finance-ecosystem (Chinese EPC/developers/financiers and policy-bank support)
   - regional-benchmark (Kazakhstan vs peer markets)
   - mingyang-entry-strategy (12/36/60 month actions across turbine, hybrid, EPC, O&M, local manufacturing)

4. **Collect in file mode**
   - Prefer Exa semantic search/fetch/deep-search tools for broad discovery.
   - Use Chrome MCP as the first fallback/verification browser when Exa misses dynamic, PDF, table, map, ecommerce, or JavaScript-rendered evidence.
   - Fall back to general browser/search tools only after Exa and Chrome MCP are insufficient.
   - When host policy and user request allow parallel agents, assign each dimension to a child agent that writes JSON under `depth/` and replies only `DONE`.
   - If parallel agents are unavailable, perform the same dimensions sequentially and still write per-dimension JSON files.
   - Never paste large raw search results into the main response.

5. **Detect convergence**
   - Each dimension performs multiple rounds until 3 consecutive rounds add no meaningful new records, or the evidence target is met.
   - Record convergence and gaps in `index.json`.

6. **Aggregate data**
   - Merge depth files into `{slug}.json` using the schema in `references/data-model.md`.
   - Export project rows to `{slug}.csv`; use `scripts/export_projects_csv.py` when convenient.
   - Deduplicate by project name, location, sponsor, capacity, and source URL.
   - For project pipeline, classify each project evidence layer as one of: `news-announcement`, `mou-framework`, `ppa-signed`, `financing-closed`, `construction-started`, `cod-operational`.

7. **Generate reports**
   - Write `{slug}-report.md` for the full internal report.
   - Write `{slug}-lite.md` for the lite delivery report.
   - Render PDFs when the environment has a working PDF stack; otherwise deliver MD and explain the limitation. On Windows native, prefer PowerShell/Python steps over Bash or `make.sh`.
   - Full/lite reports must cite sources and include data-confidence notes.

8. **Validate and hand off**
   - Validate JSON syntax and CSV row count.
   - Confirm both report files exist.
   - If PDFs were requested, confirm both PDFs exist or document why PDF rendering was skipped.
   - Summarize new files, coverage, gaps, and next update path.
   - Ensure every key fact contains source URL, date, confidence, and uncertainty notes.

## Default Output Paths

For `{slug}=uzbekistan-wind`:

```text
data/renewable-market/
├── index.json
├── uzbekistan-wind.json
├── uzbekistan-wind.csv
├── depth/
│   ├── project-pipeline.json
│   ├── ifi-financing.json
│   ├── technology-epc.json
│   └── carbon-hydrogen.json
├── uzbekistan-wind-report.md
├── uzbekistan-wind-lite.md
├── uzbekistan-wind-report.pdf
└── uzbekistan-wind-lite.pdf
```

## Quality Gates

Run these checks when files are produced. Use the host's Python launcher (`python3` on Unix-like systems, `py -3` on Windows):

```text
python -m json.tool data/renewable-market/index.json > <temp>/renewable-index.validated.json
python -m json.tool data/renewable-market/{slug}.json > <temp>/renewable-main.validated.json
python skills/renewable-market-research/scripts/export_projects_csv.py data/renewable-market/{slug}.json data/renewable-market/{slug}.csv
```

On Windows native, use the PowerShell commands in `references/windows-native.md`. Mark unavailable checks as skipped only with an explicit environment reason.

## Windows Native Quick Commands

When running on Windows native, read `references/windows-native.md` and use PowerShell/Python commands such as:

```powershell
New-Item -ItemType Directory -Force data/renewable-market/depth | Out-Null
py -3 -m json.tool data/renewable-market/index.json > $env:TEMP\renewable-index.validated.json
.\skills\renewable-market-research\scripts\export_projects_csv.ps1 -InputJson .\data\renewable-market\{slug}.json -OutputCsv .\data\renewable-market\{slug}.csv
```

Do not require WSL, Git Bash, `make.sh`, or Bash-only syntax for the standard workflow.

## Multi-Agent Harness Rules

When running long-form market research, use a harness-based multi-agent file workflow.

### Required Skills (when available)

1. `effective-harnesses`
   - Manage feature decomposition, task status, recovery points, and validation state.
   - Maintain `feature_list.json` and `agent-progress.md`.
2. `renewable-market-research`
   - Run market research file mode.
   - Produce depth JSON files, master JSON, CSV, project timeline CSV, full report, lite report, and PDFs.
3. `company-research`
   - Support owner/developer/competitor/EPC/logistics/crane/financing/partner analysis.

### Agent Roles and File Ownership

Main agent responsibilities:
- initialize harness and schemas
- create/update build scripts
- assign worker modules
- normalize worker outputs
- merge depth files
- produce master JSON, CSV, timeline CSV, markdown reports, and PDFs
- run validations and final business judgment

Worker agent responsibilities:
- only the assigned research module
- only the assigned `data/renewable-market/depth/*.json` files
- only evidence-backed findings

Worker agents MUST NOT:
- edit master JSON
- edit final Markdown reports
- edit PDF outputs
- edit build scripts
- edit harness files
- edit other workers' depth files

### Required Evidence and Facts Schema

Every key fact must include:
- `statement`
- `sources[]` with `url`, `title`, `publisher`, `accessedAt`, `sourceLanguage`, `collectionMethod`
- `confidence`
- `uncertainty`

Facts schema:

```json
{
  "topic": "...",
  "facts": [
    {
      "statement": "...",
      "sources": [],
      "confidence": "high | medium | low",
      "uncertainty": "..."
    }
  ]
}
```

Project pipeline timeline schema:

```json
{
  "project": "...",
  "stage": "...",
  "auctionDate": "...",
  "ppaDate": "...",
  "fidDate": "...",
  "constructionStart": "...",
  "codOrTargetCod": "...",
  "timingConfidence": "...",
  "timingUncertainty": "..."
}
```

### Required Outputs (Kazakhstan wind example)

- `data/renewable-market/index.json`
- `data/renewable-market/kazakhstan-wind.json`
- `data/renewable-market/kazakhstan-wind.csv`
- `data/renewable-market/kazakhstan-wind-project-timeline.csv`
- `data/renewable-market/kazakhstan-wind-report.md`
- `data/renewable-market/kazakhstan-wind-lite.md`
- `data/renewable-market/kazakhstan-wind-report.pdf`
- `data/renewable-market/kazakhstan-wind-lite.pdf`

### Main-Agent Normalization Layer

Main agent should implement/maintain:
- `normalize_sources`
- `normalize_facts`
- `humanize_value`
- `dedupe_projects`
- `project_timeline_records`
- `validate_depth_files`

### Report Quality Gates

- Markdown/CSV/PDF must be human-readable outputs, not raw JSON object dumps.
- Do not render raw structures such as `{\"claim\": ...}` or `{\"sources\": ...}` directly in reports.
- Keep structured evidence in JSON/depth files only.
- Missing values must be `unavailable` or `not found`.
- Any inference must be marked as `assumption`.
- Never fabricate sources.

### Acceptance Commands

Use commands like:

```text
uv run python scripts/build_kazakhstan_wind_outputs.py
uv run python -m json.tool data/renewable-market/index.json
uv run python -m json.tool data/renewable-market/kazakhstan-wind.json
```

And verify:
- all depth JSON files parse
- master JSON parses
- CSV opens
- project timeline CSV exists
- full and lite Markdown reports exist
- PDFs exist when PDF toolchain is available
- reports do not contain raw JSON object artifacts
