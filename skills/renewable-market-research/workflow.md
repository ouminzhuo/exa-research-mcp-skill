# Workflow Modes

`renewable-market-research` is a workflow-oriented market intelligence skill. It should collect broadly, verify carefully, and write final outputs only from confirmed or clearly qualified claims.

## Core Workflow Principles

1. Follow the hard order: wind first, ledger first, full report descriptive, strategy/action briefs separate.
2. Separate collection, review, synthesis, and executive compression.
3. Keep writer agents and reviewer agents separate.
4. Store evidence in files before writing conclusions.
5. Keep a rich master JSON between depth files and reports, then derive a compact canonical project ledger for identity, dedupe, status buckets, and watchlist/rejected decisions. Chapters must read rich fields from the master JSON and use the ledger only as the project-control registry.
6. Never place unverified leads in the confirmed pipeline.
7. Separate official plans, auction targets, installed capacity, confirmed project pipeline, all-phase pipeline, watchlist, duplicate, and rejected records.
8. Preserve broad discovery coverage, but make final capacity/project counts narrower through verified ledger buckets.
9. Search in English plus the country's official/local language(s); record the language coverage in the search plan or `index.json`.
10. Convert important facts into decision-useful implications.
11. Mark assumptions explicitly and keep unsupported claims in `rejected_claims` or watchlists.
12. Keep the default analysis focused on one target country; add peer-country comparisons only when the user explicitly requests a benchmark.
13. Treat storage, solar PV, grid, hydrogen, ammonia, methanol, I-REC, CBAM, and industrial offtake as adjacent opportunity context only when they affect wind project value, PPA/tariff economics, interconnection, procurement, or sales entry.
14. Route all final conclusions through the Continuity, Evidence, and Contradiction gates before synthesis or executive compression.
15. After downstream chapters change, rerun a summary/conclusion backpropagation pass so the executive section reflects the latest master JSON, ledger, and synthesis.
16. Use Heavy Workflow as the default for benchmark-surpassing country wind-market reports; Standard and Lite are reductions of the same file/gate architecture, not separate logic.

## Lite Workflow

Use for quick market checks and early go/no-go screening.

Agents:

1. `policy_agent`
2. `pipeline_agent`
3. `product_fit_agent`
4. `skeptic_agent`
5. `synthesis_agent`
6. `executive_agent`

Outputs:

- One-page market judgment.
- Confirmed leads and watchlist leads.
- Rich master JSON plus a canonical project ledger or compact project registry for any project claims.
- Top policy, grid, product-fit, and execution risks.
- Immediate next actions only when the user asks for strategy or sales follow-up.
- Three executive judgments with evidence support after Continuity, Evidence, and Contradiction Gate review.

## Standard Workflow

Use for country-level wind, solar, storage, or integrated renewable market reports.

Agents:

1. `policy_agent`
2. `pipeline_agent`
3. `owner_agent`
4. `grid_agent`
5. `product_fit_agent`
6. `finance_agent`
7. `competitor_agent`
8. `skeptic_agent`
9. `synthesis_agent`
10. `executive_agent`

Outputs:

- Lite report.
- Full report using the V4 0-16 chapter structure in `references/full-report-v4.md`.
- V4 gate artifacts in order: candidate project pool, source trace/evidence table, project ledger, capacity reconciliation, participant ledger, OEM competition matrix, procurement window table, detailed project cards, full report, then lite report.
- Standalone market key-indicator dashboard with time-series comparisons.
- Rich master JSON and canonical project pipeline ledger.
- Project pipeline cards in the report body, plus CSV/appendix tables when useful.
- Owner/developer/EPC/competitor map.
- Anchor developer deep dives when material to the market, such as ACWA, Masdar, state entities, or dominant IPPs.
- OEM/equipment supplier panorama, logistics/installation analysis, and auction/PPA tariff comparison.
- Participant-role matrix tying every material owner, OEM, EPC, financier, and channel actor to project roles, MW exposure, procurement influence, relationship strength, and evidence confidence.
- Product-fit assessment for Mingyang/MySE solutions.
- Separate sales-action plan only when the user asks for strategy or next actions.
- Executive brief based only on conclusions that passed the Continuity, Evidence, and Contradiction gates.
- Evidence archive and rejected-claims register.

## Heavy Workflow

Use for benchmark-surpassing country wind-market reports where pipeline accuracy, participant depth, OEM competition, procurement-window clarity, citation auditability, and evidence-bound market status are more important than speed.

Agent topology:

1. `main_orchestrator_integrator`: owns run state, task split, aggregation, master JSON, canonical ledger, synthesis, reports, summary refresh, and final handoff.
2. `market_indicators_worker`: demand/load gap, generation, installed capacity, imports/exports, latest monthly/quarterly data, and time-series market indicators.
3. `pipeline_worker`: project pipeline, auctions, PPA/COD/status, aliases, phase boundaries, and confirmed/watchlist/duplicate/rejected classification.
4. `owner_developer_worker`: owners, developers, state entities, IPPs, SPVs, partner networks, key people, procurement influence, and local presence.
5. `china_capital_new_entrant_worker`: Chinese capital, Chinese/local project names, new entrants, first-time SPVs, local-language blind spots, and anomaly candidates.
6. `oem_competitor_worker`: OEM awards, turbine models/specs, product roadmaps, framework agreements, shortlist clues, absent/displaced competitors, and unallocated MW.
7. `epc_logistics_localization_worker`: EPC, O&M, port/rail/road route constraints, heavy-lift/crane firms, transport windows, localization, and supply-chain bottlenecks.
8. `policy_law_tariff_worker`: policy targets, decrees, legal IDs, regulator orders, auction rules, PPA/FIT/tariff history, and source backtrace.
9. `finance_bankability_worker`: MDB/DFI finance, project finance, guarantees, FX/indexation, sponsor financials, IRR/ROE where supportable, and bankability constraints.
10. `grid_storage_worker`: transmission, substations, grid-code, curtailment, balancing, storage, hybrid constraints, and interconnection risk.
11. `adjacent_opportunity_worker`: solar, BESS, hydrogen, ammonia, methanol, green-power demand, I-REC, CBAM, and industrial offtake only where they change wind opportunity.
12. `product_fit_sales_worker`: Mingyang/MySE factual fit, priority accounts, procurement windows, current OEM status, decision-chain clues, relevance rationale, and optional sales-action hypotheses for separate briefs.
13. `verification_agent`: verifies critical project/policy/tariff/participant fields through Chrome MCP, Exa fetch, or original files and writes source-audit artifacts.
14. `reflection_reviewer`: independently scores each stage, lists critical blockers, and writes executable gap tasks.

Heavy Workflow stage loop:

1. Search plan reflection: reviewer checks local-language coverage, Chinese-capital search, new-entrant search, anomaly hunting, official-source backtrace, and mandatory evidence thresholds before workers start.
2. Evidence reflection: reviewer checks depth files for coverage, source quality, search passes, critical-field verification, and unexplained blind spots.
3. Ledger reflection: reviewer checks canonical IDs, alias merging, confirmed/watchlist/duplicate/rejected buckets, capacity totals, rich-field propagation, and source-to-final continuity.
4. Report reflection: reviewer checks the V4 0-16 chapter structure, full project ledger, project cards, developer/OEM depth, logistics, tariff/bankability status, procurement-window table, source-confidence appendix, summary freshness, and absence of benchmark sections unless requested.

Stage advancement rules:

- A stage may advance only when `critical_blockers == 0`.
- Score improvement alone is insufficient; the current stage must also meet the threshold in `review_gates.md`.
- If a stage fails, the reviewer must write `data/renewable-market/{slug}-gap-tasks.json` with owner lane, missing artifact, required evidence method, and acceptance criterion.
- The main agent reruns only the affected lanes, then reruns verification/review for that stage.

Heavy Workflow outputs include all Standard outputs plus:

- `data/renewable-market/{slug}-search-coverage.json`
- `data/renewable-market/{slug}-source-audit.json`
- `data/renewable-market/{slug}-reflection-review.json`
- `data/renewable-market/{slug}-gap-tasks.json` when gaps remain
- Optional `data/renewable-market/{slug}-run-status.json` for a JS scheduler or resumable harness

## Deep Workflow

Use for strategic questions such as NEOM energy configuration, Saudi localization factory strategy, floating offshore wind strategy, market-entry M&A, or integrated energy pricing logic.

Additional requirements:

- Start from the Heavy Workflow topology unless the user explicitly chooses a smaller profile.
- Multiple evidence-review loops.
- Scenario comparison.
- Assumptions register.
- Evidence archive.
- Omission audit covering local-language, Chinese-capital, new-entrant, legal-backtrace, and anomaly-hunter search passes.
- Human review gates before final external delivery.
- Sensitivity analysis for uncertain policy, grid, tariff, FX, localization, and demand assumptions.

Deep Workflow outputs should include all Standard Workflow outputs plus:

- Scenario matrix focused on the target country unless an explicit benchmark scope is requested.
- Assumptions register.
- Decision tree.
- Risk-trigger watchlist.
- Management recommendation memo.

## Output Discipline

Research collection can be broad. Final writing must be narrow:

- Use confirmed facts where possible.
- Qualify uncertain facts.
- Label assumptions.
- Move interesting but non-decision-useful information to appendices.
- Do not let adjacent-energy topics displace wind project pipeline, market participants, OEM competition, or procurement-window analysis.
- Do not list participants as generic company profiles; tie each material company to projects, role, MW exposure, procurement influence, and sales relevance.
- Full-report procurement conclusions must name the project or portfolio, MW scale, timing, procurement route, current OEM status, decision maker/influencer, evidence confidence, and pending verification. Recommended actions belong in a separate brief when requested.
- Do not write claims that cannot pass the review gates.
- Do not write or freeze executive summaries until the final master JSON, project ledger, policy backtrace, and synthesis are current.
