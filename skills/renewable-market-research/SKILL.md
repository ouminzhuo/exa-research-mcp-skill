---
name: renewable-market-research
description: Workflow skill for evidence-based renewable energy market judgment, source-to-final continuity, project pipeline verification, deduplication, product-fit analysis, sales-action generation, and executive briefing compression. Use for overseas wind, solar, storage, hydrogen, grid, or clean-energy market research where evidence quality, source traceability, omission control, uncertainty control, and decision usefulness matter more than long reports.
---

# Renewable Market Research

## Goal

Research **any country + any renewable/new-energy technology** as an evidence-driven market intelligence workflow for market judgment, project pipeline verification, product-fit analysis, sales-action generation, and executive reporting. Preserve reusable market data plus traditional report deliverables:

1. **Full report**: deep internal report with project pipeline, policy, developers, financing, technology, environment, carbon/hydrogen, risks, and sources.
2. **Lite report**: shorter delivery version with polished structure, project pipeline essentials, and reduced deep/proprietary analysis.

Use an effective-harnesses mindset: persist state to files, make progress resumable, validate outputs, and avoid returning large raw search payloads through chat.

## Required Reading

Load only the reference needed for the current step:

- `references/file-mode-research.md`: parallel/file-mode collection workflow, tool priority, convergence rules, and child-agent prompt template.
- `references/data-model.md`: directory layout, `index.json`, main JSON schema, canonical project ledger, depth JSON schema, and CSV columns.
- `workflow.md`: Lite, Standard, and Deep workflow modes for decision-oriented market intelligence.
- `agent_roles.md`: writer, reviewer, synthesis, and executive role separation.
- `review_gates.md`: Evidence, Contradiction, Business, and Executive gates that final claims must pass.
- `schema/*.schema.json`: machine-readable schemas for evidence, findings, projects, decisions, reviews, and reports.
- `prompts/*.md`: role-specific prompts for orchestrator, policy, pipeline, owner, product-fit, grid, finance, competitor, skeptic, synthesis, and executive agents.
- `references/pdf-pipeline.md`: full/lite report structure, Markdown/HTML/PDF pipeline, Chinese/English font handling, table alignment, and output risks.
- `references/windows-native.md`: Windows native PowerShell/Python startup commands, CSV export wrapper, PDF caveats, and Chrome MCP browser rules.
- `references/search-orchestration.md`: intent-aware query planning, search-lane coverage gates, local-language/china-capital/anomaly passes, validation script usage, and evidence-ranking guidance.

## Workflow Modes

Choose the mode in `workflow.md` before collecting data:

- **Lite Workflow**: quick market checks using policy, pipeline, product-fit, skeptic, synthesis, and executive agents. Output a one-page market judgment, confirmed leads, risks, and next actions.
- **Standard Workflow**: country-level reports using policy, pipeline, owner, grid, product-fit, finance, competitor, skeptic, synthesis, and executive agents. Output lite report, full report, project pipeline cards, sales-action plan, and executive brief.
- **Deep Workflow**: strategic questions requiring multiple review loops, scenario comparison, assumptions register, evidence archive, and human review gates.

## Standard Workflow

1. **Normalize task**
   - Extract `country`, `technology`, language, report depth, and target audience.
   - Identify official/local languages plus English before search. If unknown, add an early query to identify official language names and scripts.
   - Collect known project aliases, translated names, local names, developer names, and Chinese company names as seed terms for later anomaly and deduplication passes.
   - Slugify to `{country_slug}-{technology_slug}` such as `uzbekistan-wind`.
   - Create `data/renewable-market/` and `data/renewable-market/depth/` if missing.
   - For long-form research, generate a search plan with `scripts/search_orchestration.py plan` before assigning workers.

2. **Resume or initialize harness state**
   - Read `data/renewable-market/index.json` if present.
   - If `{country_slug}-{technology_slug}.json` exists, run an incremental update; otherwise run first-time collection.
   - Optionally add/maintain `feature_list.json` entries for: collection, aggregation, full report, lite report, PDF rendering.

3. **Split research dimensions**
   Use focused dimensions depending on scope. For OEM/commercial-entry asks (for example Mingyang), use **demand-first framing**: start from electricity demand gap and monetizable offtake, then validate resource/technology constraints.
   - demand-load-gap (generation, consumption, peak load, imports/exports, 5-10 year outlook)
   - market-key-indicators-timeseries (generation YoY, latest Q/month data, wind/solar 3-year trend, installed capacity, imports/exports, pipeline MW)
   - power-mix-replacement (retirements, thermal constraints, hydro flexibility, wind/solar complementarity)
   - grid-storage-transmission (curtailment risk, substations/lines, storage requirement, cross-border corridors)
   - policy-ppa-economics (auction/FIT/PPA, tariff history, FX risk, localization, IRR/ROE if estimable)
   - auction-tariff-comparison (project-level winning tariffs, PPA tenor, currency/indexation, sponsor, capacity, source confidence)
   - project-pipeline-layered (operational, under-construction, awarded/PPA, MOU, early stage)
   - owners-partners-routes (state entities, IPPs, EPC/developer networks, contact pathways)
   - anchor-developer-deep-dives (material developers such as ACWA/Masdar/state entities: financials, full local portfolio, key people, partners, IRR assumptions when supportable)
   - competitor-oem-landscape (full OEM/supplier panorama, turbine platforms/specs, product roadmap, BNEF or credible market-share trend when available, localization and tie strength)
   - epc-om-logistics-lifting (route length/time, ports/rail/road/border crossings, component dimensions/weights, crane/heavy-lift firms, installation window risks)
   - localization-supply-chain (tower/blade/nacelle/BESS ecosystem and JV options)
   - esg-land-community (ESIA, biodiversity, land/community, IFI social constraints)
   - carbon-greenpower-hydrogen (I-REC, CBAM, enterprise PPA, hydrogen/ammonia links)
   - china-finance-ecosystem (Chinese EPC/developers/financiers and policy-bank support)
   - chinese-developer-deep-dives (listed code, revenue/profit/margin, team/local presence, financing innovation, project roles)
   - local-language-china-capital-trace (Chinese capital + local-language project names + Chinese EPC/OEM/SPV traces)
   - new-entrant-hunter (new IPPs, new SPVs, first-time EPC/OEM entries, corporate offtakers)
   - policy-law-backtrace (reverse policy targets, auctions, tariffs, and capacity numbers to original laws, decrees, orders, and regulator documents)
   - anomaly-hunter (misspellings, transliterations, PDF/table/map-only mentions, renamed phases, and projects outside known patterns)
   - optional-single-country-benchmark (only if explicitly requested; keep default analysis on the target country, not another country comparison)
   - mingyang-entry-strategy (12/36/60 month actions across turbine, hybrid, EPC, O&M, local manufacturing)

4. **Collect in file mode**
   - Prefer Exa semantic search/fetch/deep-search tools for broad discovery.
   - Use Chrome MCP as the first fallback/verification browser when Exa misses dynamic, PDF, table, map, ecommerce, or JavaScript-rendered evidence.
   - Fall back to general browser/search tools only after Exa and Chrome MCP are insufficient.
   - When host policy and user request allow parallel agents, assign each dimension to a child agent that writes JSON under `depth/` and replies only `DONE`.
   - If parallel agents are unavailable, perform the same dimensions sequentially and still write per-dimension JSON files.
   - Never paste large raw search results into the main response.
   - Workers should follow the generated search plan: use query variants, domain boosts, freshness hints, and minimum evidence gates per dimension.
   - Every depth record should include `searchPass` or `searchPasses` such as `english-broad`, `official-language`, `china-capital-local-language`, `new-entrant`, `source-backtrace`, `anomaly-hunter`, or `chrome-verification`.
   - Treat Chrome MCP as an integrated verification lane, not only a debug check: when Exa finds a candidate official PDF/table/map/dynamic page, verify it in Chrome MCP when available and record the verification method.
   - Key confirmed-pipeline fields must be verified by `chrome-mcp`, `exa-fetch`, or `manual-file`; `exa-search` discovery alone is not enough for final use.

5. **Detect convergence**
   - Do not stop because of 3 quiet rounds until mandatory search passes are complete: English broad search, official/local-language search, source-specific search, Chinese-capital/local-name search, new-entrant search, anomaly hunt, and legal/source backtrace where relevant.
   - After mandatory passes, stop only when additional rounds add neither new canonical project candidates nor evidence upgrades to existing projects, or when remaining gaps are explicitly recorded.
   - Record convergence and gaps in `index.json`.

6. **Aggregate data**
   - Split aggregation into two required passes. First, merge all depth files into the full `{slug}.json` using the rich schema in `references/data-model.md`; preserve project-card fields such as coordinates, site area, annual generation, annual CO2 reduction, investment, turbine model/count/specs, storage, logistics, community impact, and personnel/developer data when found.
   - Validate the full `{slug}.json` before deriving downstream files. If a rich field exists in a depth file but is absent from the matching main JSON project, update the main JSON or mark the field explicitly as `not found`, `unavailable`, or `not applicable` with a gap note.
   - Build `{slug}-pipeline-ledger.json` from the validated main JSON, not directly as a replacement for it. The ledger owns canonical project IDs, local/English/Chinese aliases, dedupe keys, source traces, evidence layers, confirmed/watchlist/rejected state, and merge/reject decisions.
   - Treat `{slug}.json` as the rich report data source, `depth/*.json` as the required cross-read/fallback evidence layer, and `{slug}-pipeline-ledger.json` as the canonical dedupe/evidence registry. The ledger alone is not sufficient to write final project cards or deep-dive chapters.
   - Export project rows to `{slug}.csv`; use `scripts/export_projects_csv.py` when convenient.
   - Deduplicate by canonical name, local-language aliases, translated names, location, sponsor/SPV, capacity, coordinates if available, phase boundaries, and source URL. Same-name/different-source records must be merged or explicitly rejected/watchlisted.
   - For project pipeline, classify each project evidence layer as one of: `news-announcement`, `mou-framework`, `ppa-signed`, `financing-closed`, `construction-started`, `cod-operational`.
   - Policy targets, auction targets, tariff numbers, and capacity goals must include an original legal/regulator/auction backtrace or be downgraded with an uncertainty note.
   - For confirmed projects, verify these critical fields with `chrome-mcp`, `exa-fetch`, or `manual-file` before final writing when the field is present: project name/alias, capacity, status/evidence stage, owner/developer/SPV, location, COD/target COD, PPA, financing/investment, EPC/OEM/turbine, and construction start.

7. **Generate reports**
   - Write `{slug}-report.md` for the full internal report.
   - Write `{slug}-lite.md` for the lite delivery report.
   - Full reports should follow the 15-chapter structure in `references/pdf-pipeline.md`, including weekly update timestamp, standalone market indicators, tariff comparison, developer deep dives, OEM panorama, logistics/installation, and conclusion/outlook.
   - Present the project pipeline in the report body as project cards grouped by status/evidence stage. Use tables only for appendices, CSV exports, or compact summary indexes.
   - Before writing each project card or project/developer chapter, cross-read the matching `depth/*.json` records named in `sourceTrace` or `mergedFromDepthRecords`. Check at minimum annualGenerationGWh, annualCO2ReductionTonnes, investmentUSD, turbineModel, turbineCount, storageMWh, coordinates, turbine specs, logistics route, community/land impact, biodiversity/bird protection, jobs/local employment, and personnel/developer data.
   - If a depth file contains a richer field than `{slug}.json`, update `{slug}.json` and rerun integrity validation before writing the report. Do not silently downgrade to `{slug}-pipeline-ledger.json` when the main JSON is incomplete.
   - Do not include a Regional Benchmark Comparison section unless the user explicitly requests a benchmark.
   - For controlled PDF layout, prefer Markdown as the authoring source, convert Markdown to HTML with a controlled template, then render HTML to PDF. Direct HTML authoring is acceptable only for highly designed final decks or when Markdown cannot represent required layout.
   - Report CSS should use Microsoft YaHei (`微软雅黑`, `Microsoft YaHei`) for Chinese text and Times New Roman for English/Latin text; tables should use fixed widths, explicit column alignment, and print CSS to avoid broken pipeline tables.
   - Render PDFs when the environment has a working HTML/PDF stack; otherwise deliver MD and HTML and explain the limitation. On Windows native, prefer PowerShell/Python steps over Bash or `make.sh`.
   - Full/lite reports must cite sources and include data-confidence notes.
   - Write the executive summary and conclusion after all chapters, then run a backpropagation pass: compare every summary number, project count, risk, and recommendation against the latest canonical ledger and synthesis. If any downstream chapter changed, update the summary before release.

8. **Validate and hand off**
   - Validate JSON syntax, CSV row count, and search coverage; use `scripts/search_orchestration.py validate` when a search plan exists.
   - Run `scripts/validate_market_integrity.py` or its PowerShell wrapper to identify duplicate candidates, missing source fields, missing source-to-final metadata, and policy target records without legal backtrace.
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

Also produce:

- `data/renewable-market/{slug}-pipeline-ledger.json`
- `data/renewable-market/{slug}-integrity.json`

## Review Gates

Before final writing, apply `review_gates.md`:

1. **Continuity Gate**: every final summary claim must trace back to the latest canonical ledger or reviewed synthesis, and stale summaries must be rewritten after downstream chapter updates.
2. **Evidence Gate**: unsupported claims and weak single-source claims cannot become high-confidence final claims; every final conclusion must pass this gate.
3. **Critical Field Gate**: confirmed-pipeline critical fields must have `chrome-mcp`, `exa-fetch`, or `manual-file` verification. Otherwise downgrade the project/field to watchlist or uncertainty; do not leave it as a final confirmed fact.
4. **Contradiction Gate**: reconcile installed/planned/pipeline capacity, status conflicts, COD conflicts, duplicates, translated names, local-language aliases, phase confusion, and offshore/floating/onshore classification; every final conclusion must pass this gate before synthesis.
5. **Business Gate**: convert important facts into implications for sales action, product fit, risk judgment, or executive decision-making.
6. **Executive Gate**: compress final output into three evidence-backed core judgments and avoid vague potential claims unless quantified and qualified.

## Quality Gates

Run these checks when files are produced. Use the host's Python launcher (`python3` on Unix-like systems, `py -3` on Windows):

```text
python -m json.tool data/renewable-market/index.json > <temp>/renewable-index.validated.json
python -m json.tool data/renewable-market/{slug}.json > <temp>/renewable-main.validated.json
python skills/renewable-market-research/scripts/export_projects_csv.py data/renewable-market/{slug}.json data/renewable-market/{slug}.csv
python skills/renewable-market-research/scripts/validate_market_integrity.py data/renewable-market/{slug}.json --depth-dir data/renewable-market/depth --output data/renewable-market/{slug}-integrity.json
```

On Windows native, use the PowerShell commands in `references/windows-native.md`. Mark unavailable checks as skipped only with an explicit environment reason.

## Windows Native Quick Commands

When running on Windows native, read `references/windows-native.md` and use PowerShell/Python commands such as:

```powershell
New-Item -ItemType Directory -Force data/renewable-market/depth | Out-Null
py -3 -m json.tool data/renewable-market/index.json > $env:TEMP\renewable-index.validated.json
.\skills\renewable-market-research\scripts\export_projects_csv.ps1 -InputJson .\data\renewable-market\{slug}.json -OutputCsv .\data\renewable-market\{slug}.csv
.\skills\renewable-market-research\scripts\validate_market_integrity.ps1 -MarketJson .\data\renewable-market\{slug}.json -DepthDir .\data\renewable-market\depth -Output .\data\renewable-market\{slug}-integrity.json
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
- build and maintain the canonical project pipeline ledger
- produce master JSON, CSV, timeline CSV, markdown reports, and PDFs
- rerun summary/conclusion backpropagation after downstream section updates
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
- `data/renewable-market/kazakhstan-wind-pipeline-ledger.json`
- `data/renewable-market/kazakhstan-wind-integrity.json`
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
- `merge_project_aliases`
- `build_pipeline_ledger`
- `policy_legal_backtrace`
- `refresh_summary_from_latest_ledger`
- `project_timeline_records`
- `validate_depth_files`
- `build_search_plan`
- `validate_search_coverage`
- `validate_market_integrity`

### Report Quality Gates

- Markdown/CSV/PDF must be human-readable outputs, not raw JSON object dumps.
- Standard and Deep full reports must follow the 15-chapter structure in `references/pdf-pipeline.md`; a 6-section compressed structure is acceptable only for Lite mode.
- Report-body project pipeline must be rendered as project cards grouped by status/evidence stage, not as a large table.
- Regional benchmark sections are omitted by default and included only when the user explicitly requests a benchmark.
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
uv run python skills/renewable-market-research/scripts/search_orchestration.py validate --plan data/renewable-market/kazakhstan-wind-search-plan.json --depth-dir data/renewable-market/depth --output data/renewable-market/kazakhstan-wind-search-coverage.json
uv run python skills/renewable-market-research/scripts/validate_market_integrity.py data/renewable-market/kazakhstan-wind.json --depth-dir data/renewable-market/depth --output data/renewable-market/kazakhstan-wind-integrity.json
```

And verify:
- all depth JSON files parse
- master JSON parses
- rich project-card fields found in depth files are propagated into the master JSON or explicitly marked unavailable
- CSV opens
- canonical pipeline ledger exists and duplicate candidates are resolved or explicitly watchlisted/rejected
- project timeline CSV exists
- full and lite Markdown reports exist
- PDFs exist when PDF toolchain is available
- executive summary was refreshed after the latest project ledger and synthesis updates
- reports do not contain raw JSON object artifacts
