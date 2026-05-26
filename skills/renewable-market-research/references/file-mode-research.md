# File-Mode Research Workflow

## Architecture

```text
User request
  -> main session decomposes dimensions and manages files
  -> child/sidecar researchers collect evidence per dimension
  -> each researcher writes JSON files, then replies DONE only
  -> main session merges JSON, updates index, writes MD/PDF reports
```

The main session owns orchestration, schema, deduplication, report writing, and validation. Research workers own one narrow dimension and must not stream raw pages back into chat.

## Tool Priority

1. **Exa semantic search/fetch/deep search** when available.
   - Search: broad discovery and category filtering.
   - Fetch: known URL full-text extraction.
   - Deep search: cross-source synthesis when API quota allows.
   - Prefer highlighted/limited output, for example `maxCharacters` around 3000 per result when supported.
2. **Chrome MCP / direct browser** for dynamic pages, official PDFs, tables, maps, ecommerce listings, dashboards, and pages Exa cannot extract. When the user confirms Chrome MCP is sanitized/configured, treat it as a first-class human-browser verification tool.
3. **Browser or general web search with proxy** as last resort when Exa and Chrome MCP are unavailable or insufficient.

Useful Exa-style categories:

| Category | Use | Example query |
|---|---|---|
| `news` | project updates and policy changes | `ACWA Power Uzbekistan wind farm update` |
| `research paper` | institutional reports and outlooks | `IRENA Uzbekistan renewable outlook` |
| `company` | developer/vendor profiles | `SANY Renewable Energy overseas Uzbekistan` |
| `financial report` | financing and annual reports | `ADB Uzbekistan wind financing loan` |

## Dimension Split

For a comprehensive country/technology task, use 7-15 dimensions. For commercial-entry tasks, use a demand-first order (demand gap -> replacement space -> grid delivery -> project conversion paths):

| Dimension | Search target | Example |
|---|---|---|
| demand-load-gap | power demand growth, peak, imports/exports, deficit | `Kazakhstan electricity demand peak load import export trend` |
| power-mix-replacement | current mix, retirements, thermal limits | `Kazakhstan coal retirement plan gas constraints power mix` |
| grid-storage | storage, transmission, grid bottlenecks | `Kazakhstan wind grid curtailment storage transmission plan` |
| policy-ppa-economics | auction/FIT/PPA/tariff/FX/IRR | `Kazakhstan renewable auction tariff PPA currency risk` |
| project-pipeline | all known projects and statuses | `Uzbekistan wind farm list capacity MW 2026` |
| policy-plans | targets, laws, auctions, tariffs | `Uzbekistan renewable energy target 2030` |
| developers | sponsor portfolio by company | `ACWA Power Uzbekistan portfolio wind` |
| financing | IFI/commercial/project finance | `ADB EBRD AIIB Uzbekistan wind loan` |
| technology-epc | turbines, modules, batteries, EPC | `Uzbekistan wind turbine Goldwind Envision` |
| grid-storage | storage, transmission, grid bottlenecks | `Uzbekistan renewable grid storage transmission` |
| environment-social | ESIA, land, community, biodiversity | `Zarafshan wind farm environmental impact ESIA` |
| carbon-hydrogen | I-REC, carbon, CBAM, green H2 | `Uzbekistan green hydrogen I-REC carbon CBAM` |
| china-participation | Chinese OEM/EPC/developer role | `POWERCHINA Uzbekistan wind solar EPC Goldwind` |
| regional-benchmark | compare neighboring markets | `Uzbekistan Kazakhstan wind market comparison` |
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
- source title, url, publisher, accessedAt
- confidence: high/medium/low
- uncertainty: what is estimated or unavailable
- notes/gaps

Do not return raw search results in chat. After writing and validating JSON, reply only: DONE.
Stop after 3 consecutive rounds with no meaningful new records, or when the assigned dimension is well covered.
```

## Convergence Rule

Per dimension:

```text
Round 1: search -> new records found -> continue
Round 2: search variants -> new records found -> continue
Round 3: local-language/source-specific search -> no new records -> continue
Round 4: source validation -> no new records -> continue
Round 5: targeted gap search -> no new records -> stop
```

Record convergence in `index.json` with `rounds`, `newRecords`, `stoppedReason`, and `remainingGaps`.

## Safety Limits

- Use file mode for all large evidence. Do not let 4-15 workers stream evidence back to the main chat.
- Prefer 4-8 concurrent workers. Higher concurrency risks WebSocket slow-consumer errors in some hosts.
- Store raw extracts sparingly; store source URLs and concise factual notes instead.
- If advanced Exa quota is exhausted, continue with basic search/fetch and Chrome MCP verification, then mark the limitation in `index.json`.
- On Windows native, workers should write JSON with Python or PowerShell-safe file operations; do not depend on Bash utilities.

## Chrome MCP Evidence Discipline

When using Chrome MCP as a human browser, record `collectionMethod: "chrome-mcp"` or mention Chrome MCP in `notes`. Keep only distilled facts, source URL, title, publisher, accessed date, and confidence in JSON. Do not persist cookies, credentials, private account data, or unrelated browsing history.
