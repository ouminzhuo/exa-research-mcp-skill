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
   Use 7-15 focused dimensions depending on scope:
   - project pipeline
   - national plans and policy
   - developers and sponsors
   - IFI/project financing
   - technology/equipment/EPC/O&M
   - grid/storage/transmission
   - environmental/social/ESIA
   - carbon markets, I-REC, CBAM, green hydrogen
   - Chinese company participation
   - regional benchmark markets

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
