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

## Planning Script

Use `scripts/search_orchestration.py` to generate a deterministic search plan. It does not call external APIs; it creates the dimensions, query variants, intended freshness, domain boosts, scoring weights, output files, and minimum evidence gates that workers must satisfy.

Example:

```text
python skills/renewable-market-research/scripts/search_orchestration.py plan \
  --country Kazakhstan \
  --technology wind \
  --audience "Mingyang OEM commercial entry" \
  --slug kazakhstan-wind \
  --output data/renewable-market/kazakhstan-wind-search-plan.json
```

Windows PowerShell:

```powershell
.\skills\renewable-market-research\scripts\search_orchestration.ps1 plan `
  --country Kazakhstan `
  --technology wind `
  --audience "Mingyang OEM commercial entry" `
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
- stop only when the dimension meets the plan's minimum evidence gate or records remaining gaps.

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

A `needs-work` validation result does not mean the run failed; it means the main agent must either assign gap-search workers or explicitly document why evidence is unavailable.

## Scoring and Ranking Guidance

Use the plan's `scoringWeights` to prioritize candidate evidence:

- status/news dimensions emphasize freshness;
- comparison dimensions emphasize keyword match plus authority;
- exploratory dimensions emphasize authoritative institutional sources;
- resource-style searches emphasize exact-match official sources.

Authority boosts are only hints. Do not suppress contradictory sources. Preserve disagreements in `uncertainty` and in the final report's confidence notes.
