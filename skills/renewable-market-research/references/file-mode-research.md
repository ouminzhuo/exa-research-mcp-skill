# File-Mode Research Workflow

## Architecture

```text
User request
  -> main session decomposes dimensions and manages files
  -> child/sidecar researchers collect evidence per dimension
  -> each researcher writes JSON files, then replies DONE only
  -> main session merges JSON into a rich master JSON
  -> main session derives the canonical project ledger from the validated master JSON
  -> main session updates synthesis from the master JSON plus ledger, then writes MD/PDF reports
  -> main session reruns summary/conclusion backpropagation before release
```

The main session owns orchestration, schema, master JSON aggregation, deduplication, canonical project ledger, source-to-final continuity, report writing, and validation. Research workers own one narrow dimension and must not stream raw pages back into chat.

For wind-market work, file mode should maximize search breadth while keeping final judgment narrow. Workers may discover many project-like records and adjacent opportunity facts, but the main session must classify them through the master JSON and ledger before any final count, MW total, participant ranking, or sales action is written.

## Tool Priority

1. **Exa semantic search/fetch/deep search** when available.
   - Search: broad discovery and category filtering.
   - Fetch: known URL full-text extraction.
   - Deep search: cross-source synthesis when API quota allows.
   - Prefer highlighted/limited output, for example `maxCharacters` around 3000 per result when supported.
2. **Chrome MCP / direct browser** for dynamic pages, official PDFs, tables, maps, ecommerce listings, dashboards, and pages Exa cannot extract. When the user confirms Chrome MCP is sanitized/configured, treat it as a first-class human-browser verification tool, not merely a debug check. Use it to verify Exa-discovered official URLs, PDF tables, map-only project mentions, regulator databases, and local-language pages.
3. **Browser or general web search with proxy** as last resort when Exa and Chrome MCP are unavailable or insufficient.

Useful Exa-style categories:

| Category | Use | Example query |
|---|---|---|
| `news` | project updates and policy changes | `ACWA Power Uzbekistan wind farm update` |
| `research paper` | institutional reports and outlooks | `IRENA Uzbekistan renewable outlook` |
| `company` | developer/vendor profiles | `SANY Renewable Energy overseas Uzbekistan` |
| `financial report` | financing and annual reports | `ADB Uzbekistan wind financing loan` |

## Dimension Split

For a comprehensive country/technology task, use enough dimensions to cover standard lanes plus blind-spot hunters. For commercial-entry tasks, use a demand-first order (demand gap -> replacement space -> grid delivery -> project conversion paths):

| Dimension | Search target | Example |
|---|---|---|
| demand-load-gap | power demand growth, peak, imports/exports, deficit | `Kazakhstan electricity demand peak load import export trend` |
| market-key-indicators-timeseries | generation YoY, Q1/monthly data, wind/solar three-year trends, installed capacity, imports/exports | `Kazakhstan wind solar generation Q1 YoY statistics` |
| power-mix-replacement | current mix, retirements, thermal limits | `Kazakhstan coal retirement plan gas constraints power mix` |
| grid-storage | storage, transmission, grid bottlenecks | `Kazakhstan wind grid curtailment storage transmission plan` |
| policy-ppa-economics | auction/FIT/PPA/tariff/FX/IRR | `Kazakhstan renewable auction tariff PPA currency risk` |
| auction-tariff-comparison | project-level winning tariffs, PPA tenor, currency/indexation, award dates | `Kazakhstan wind auction winning tariff PPA cents kWh` |
| project-pipeline | all known projects and statuses | `Uzbekistan wind farm list capacity MW 2026` |
| policy-plans | targets, laws, auctions, tariffs | `Uzbekistan renewable energy target 2030` |
| developers | sponsor portfolio by company | `ACWA Power Uzbekistan portfolio wind` |
| anchor-developer-deep-dives | material developer financials, portfolio, people, partners, China cooperation, IRR assumptions | `ACWA Power Uzbekistan portfolio financials key people China EPC` |
| financing | IFI/commercial/project finance | `ADB EBRD AIIB Uzbekistan wind loan` |
| technology-epc | turbines, modules, batteries, EPC, full OEM panorama and product roadmap | `Uzbekistan wind turbine Goldwind Envision BNEF market share` |
| grid-storage | storage, transmission, grid bottlenecks | `Uzbekistan renewable grid storage transmission` |
| logistics-installation | route length/time, component dimensions/weights, crane/heavy-lift, ports/rail/road/borders | `Uzbekistan wind turbine blade transport route heavy lift crane` |
| environment-social | ESIA, land, community, biodiversity | `Zarafshan wind farm environmental impact ESIA` |
| carbon-hydrogen | I-REC, carbon, CBAM, green H2 | `Uzbekistan green hydrogen I-REC carbon CBAM` |
| china-participation | Chinese OEM/EPC/developer role | `POWERCHINA Uzbekistan wind solar EPC Goldwind` |
| chinese-developer-deep-dives | Chinese developer financials, listed code, team, Sinosure/policy-bank structures | `SANY Uzbekistan wind project revenue profit Sinosure` |
| local-language-china-capital-trace | Chinese capital plus local-language project names, SPVs, EPC notices, aliases | `Kazakhstan wind PowerChina local project name Kazakh Russian` |
| new-entrant-hunter | newly awarded developers, SPVs, first-time market actors, corporate offtakers | `Kazakhstan wind new entrant SPV PPA 2026` |
| policy-law-backtrace | reverse targets, tariffs, auctions, and capacity numbers to original laws/decrees/orders | `Kazakhstan renewable target 2030 decree order number` |
| anomaly-hunter | misspellings, transliterations, table/PDF/map-only mentions, renamed phases | `Kazakhstan wind local language misspelling PDF map` |
| regional-benchmark | optional only when the user explicitly asks to compare neighboring markets | `Uzbekistan Kazakhstan wind market comparison` |
| entry-strategy | OEM/system/developer/EPC/O&M/localization pathways | `Kazakhstan wind OEM localization manufacturing opportunities` |

## Child Agent Prompt Template

Use only when the host allows child agents and the user has requested/authorized parallel research.

```text
Task: Research [dimension] for [country] [technology].
Tools: Prefer Exa semantic search/fetch/deep-search if available; fall back to browser/search.
Output file: data/renewable-market/depth/[dimension].json

Write an array of records. Each record must include:
- topic/project/company
- key facts with numbers and dates when available
- project or participant linkage when relevant: project name, MW, actor role, procurement influence, OEM/EPC/finance tie, and sales relevance
- source title, url, publisher, accessedAt
- sourceLanguage and collectionMethod
- searchPass or searchPasses
- sourceTrace note explaining how this record should map into the canonical ledger or policy/legal backtrace
- criticalFieldVerification for confirmed-pipeline fields verified by Chrome MCP or original-file fetch
- confidence: high/medium/low
- uncertainty: what is estimated or unavailable
- notes/gaps

If the assigned dimension finds storage, solar PV, hydrogen, ammonia, methanol, I-REC, CBAM, or industrial offtake facts, record how the fact changes a wind project, portfolio, PPA/tariff, interconnection, procurement route, OEM opportunity, or sales entry. If there is no wind-market implication, mark it as adjacent context.

Do not return raw search results in chat. After writing and validating JSON, reply only: DONE.
Do not stop until mandatory search passes for the dimension are complete. Record remaining gaps instead of silently stopping.
```

## Convergence Rule

Per dimension:

```text
Round 1: English broad discovery with Exa semantic search.
Round 2: source-specific search against official/regulator/owner/MDB/grid domains.
Round 3: official/local-language search using the country's official languages and local scripts.
Round 4: Chinese-capital + local-language project-name search using Chinese EPC/OEM/developer/financier terms.
Round 5: new-entrant search for new SPVs, first-time developers, corporate offtakers, and recent awards.
Round 6: anomaly-hunter search for transliterations, misspellings, renamed phases, PDF/table/map-only mentions.
Round 7: source-backtrace search for any policy target, auction number, tariff, or capacity goal that lacks original law/decree/order/regulator evidence.
```

Do not stop before rounds 1-4 for project pipeline work, and do not stop before round 7 for policy target claims. After mandatory rounds, stop only when two additional gap-search rounds add neither new canonical project candidates nor evidence upgrades, or when the remaining gap is explicitly recorded and downgraded.

Record convergence in `index.json` with `rounds`, `newRecords`, `searchPasses`, `stoppedReason`, and `remainingGaps`.

## Master JSON and Canonical Project Ledger

Before report writing, merge all project-like records into the rich `{slug}.json` first. This master JSON is the report-ready data source and must preserve rich card fields from depth records, including annual generation, annual CO2 reduction, investment, turbine model/count/specs, storage, coordinates, site area, logistics, jobs/community/ESG, and personnel/developer data when found.

After the master JSON is complete, derive `{slug}-pipeline-ledger.json` from it.

Each canonical project should include:

- canonical project ID and canonical English name;
- official-language names, Chinese names, transliterations, and known aliases;
- dedupe key and duplicate-resolution notes;
- merged depth records and sourceTrace entries;
- criticalFieldVerification for present key fields, using `chrome-mcp`, `exa-fetch`, or `manual-file`;
- evidence layers such as `mou-framework`, `ppa-signed`, `financing-closed`, `construction-started`, or `cod-operational`;
- confirmed-pipeline eligibility and exclusion reason when not eligible.

No chapter may maintain an independent project list after aggregation. Chapters read rich report fields from the master JSON and use the ledger for canonical IDs, status buckets, dedupe decisions, and watchlist/rejected state. If a new chapter discovers a project candidate, alias, or richer field, it must update the master JSON first, refresh the ledger, then refresh synthesis and summary.

## Critical Field Verification

For confirmed-pipeline projects, field-level verification is mandatory. `exa-search` can discover a field, but it cannot be the final verification method.

Verify present critical fields with `chrome-mcp`, `exa-fetch`, or `manual-file`:

- project name/alias;
- capacity;
- status/evidence stage;
- owner/developer/SPV;
- location;
- COD or target COD;
- PPA;
- financing/investment;
- EPC/OEM/turbine;
- construction start.

Record the verification in `criticalFieldVerification`, `sourceTrace`, `sources`, or `evidence` with a field name and `collectionMethod`. If a critical field cannot be verified from an original page/file/browser pass, either remove the field from final confirmed claims or downgrade it to watchlist/uncertainty.

## Safety Limits

- Use file mode for all large evidence. Do not let 4-15 workers stream evidence back to the main chat.
- Prefer 4-8 concurrent workers. Higher concurrency risks WebSocket slow-consumer errors in some hosts.
- Store raw extracts sparingly; store source URLs and concise factual notes instead.
- If advanced Exa quota is exhausted, continue with basic search/fetch and Chrome MCP verification, then mark the limitation in `index.json`.
- On Windows native, workers should write JSON with Python or PowerShell-safe file operations; do not depend on Bash utilities.

## Chrome MCP Evidence Discipline

When using Chrome MCP as a human browser, record `collectionMethod: "chrome-mcp"` or mention Chrome MCP in `notes`. Keep only distilled facts, source URL, title, publisher, accessed date, and confidence in JSON. Do not persist cookies, credentials, private account data, or unrelated browsing history.
