# Search Orchestration and Coverage Gates

This skill uses a lightweight Python orchestration layer to keep long-form market research search coverage complete without turning the repository into a fixed crawler.

## Borrowed Pattern

The external `search-layer` project demonstrates several useful ideas for search completeness:

- classify the search intent before choosing a tool lane;
- expand one user question into multiple subqueries;
- run multiple search lanes instead of trusting one provider;
- deduplicate and rank by keyword match, freshness, and authority;
- keep fallback behavior explicit so one provider failure does not block the run;
- validate outputs with code instead of relying on chat memory.

For this repository, adapt those ideas to renewable-market research rather than copying provider-specific code. The standard lanes are:

1. Exa semantic search for broad discovery.
2. Exa fetch for known URL extraction.
3. Exa deep search only for complex comparison/status/exploratory gaps when quota allows.
4. Sanitized Chrome MCP for dynamic pages, tables, maps, official PDFs, and visual verification.
5. General browser/search fallback only when the previous lanes are insufficient.

The search plan also requires explicit search passes, not just tool lanes:

- `english-broad`: English discovery and source mapping.
- `official-language`: country official/local language search.
- `china-capital-local-language`: Chinese capital, EPC/OEM/developer/financier terms plus local project names.
- `new-entrant`: new SPVs, new developers, recent awards, corporate offtakers, and first-time market actors.
- `source-backtrace`: reverse target/tariff/capacity claims to original law, decree, order, auction, regulator, or grid documents.
- `anomaly-hunter`: transliterations, misspellings, renamed phases, map/table/PDF-only mentions, and records outside known developer patterns.
- `chrome-verification`: browser verification for dynamic, PDF, table, map, or bot-sensitive sources discovered by Exa or general search.

For confirmed-pipeline critical fields, only `chrome-mcp`, `exa-fetch`, or `manual-file` count as final verification. `exa-search` is discovery-only for those fields.

## Planning Script

Use `scripts/search_orchestration.py` to generate a deterministic search plan. It does not call external APIs; it creates the dimensions, query variants, intended freshness, domain boosts, scoring weights, output files, and minimum evidence gates that workers must satisfy.

Example:

```text
python skills/renewable-market-research/scripts/search_orchestration.py plan \
  --country Kazakhstan \
  --technology wind \
  --audience "Mingyang OEM commercial entry" \
  --official-languages "Kazakh,Russian" \
  --known-projects "Sho'rkul,Zhanatas,Arkalyk" \
  --slug kazakhstan-wind \
  --output data/renewable-market/kazakhstan-wind-search-plan.json
```

Windows PowerShell:

```powershell
.\skills\renewable-market-research\scripts\search_orchestration.ps1 plan `
  --country Kazakhstan `
  --technology wind `
  --audience "Mingyang OEM commercial entry" `
  --official-languages "Kazakh,Russian" `
  --known-projects "Sho'rkul,Zhanatas,Arkalyk" `
  --slug kazakhstan-wind `
  --output data\renewable-market\kazakhstan-wind-search-plan.json
```

## Worker Execution Contract

For each plan dimension, the worker should:

- run the listed query variants;
- use Exa first, then Chrome MCP for source verification and dynamic/PDF/table evidence;
- write only its assigned `data/renewable-market/depth/<dimension>.json` file;
- include `topic`, `facts`, `sources`, `confidence`, and `uncertainty`;
- record `collectionMethod` as `exa-search`, `exa-fetch`, `exa-deep-search`, `chrome-mcp`, or `general-web-search`;
- record `searchPass` or `searchPasses` for the search pass that found or verified the record;
- record `criticalFieldVerification` for confirmed-pipeline fields verified by Chrome MCP or original-file fetch;
- stop only when the dimension meets the plan's minimum evidence gate, completes required search passes, or records remaining gaps with confidence downgrades.

## Coverage Validation

After workers finish, validate search completeness before writing reports:

```text
python skills/renewable-market-research/scripts/search_orchestration.py validate \
  --plan data/renewable-market/kazakhstan-wind-search-plan.json \
  --depth-dir data/renewable-market/depth \
  --output data/renewable-market/kazakhstan-wind-search-coverage.json
```

The validation report checks that:

- every planned dimension has a depth JSON file;
- depth files are JSON arrays;
- records include required evidence fields;
- each dimension has the minimum record count and unique source URL count;
- collection methods are observable for coverage review.
- required search passes such as official-language, Chinese-capital/local-name, new-entrant, source-backtrace, anomaly-hunter, and Chrome verification are observable where the plan requires them.

A `needs-work` validation result does not mean the run failed; it means the main agent must either assign gap-search workers or explicitly document why evidence is unavailable.

If validation says a required pass is missing, do not write final high-confidence conclusions for that dimension. Either run a focused gap-search worker or record a visible limitation in `index.json`, synthesis, and the report confidence notes.

## Scoring and Ranking Guidance

Use the plan's `scoringWeights` to prioritize candidate evidence:

- status/news dimensions emphasize freshness;
- comparison dimensions emphasize keyword match plus authority;
- exploratory dimensions emphasize authoritative institutional sources;
- resource-style searches emphasize exact-match official sources.

Authority boosts are only hints. Do not suppress contradictory sources. Preserve disagreements in `uncertainty` and in the final report's confidence notes.
