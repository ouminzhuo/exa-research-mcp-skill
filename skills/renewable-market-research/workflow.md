# Workflow Modes

`renewable-market-research` is a workflow-oriented market intelligence skill. It should collect broadly, verify carefully, and write final outputs only from confirmed or clearly qualified claims.

## Core Workflow Principles

1. Follow the hard order: wind first, ledger first, sales judgment last.
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
- Immediate next sales actions.
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
- Full report using the 15-chapter deep structure in `references/pdf-pipeline.md`.
- Standalone market key-indicator dashboard with time-series comparisons.
- Rich master JSON and canonical project pipeline ledger.
- Project pipeline cards in the report body, plus CSV/appendix tables when useful.
- Owner/developer/EPC/competitor map.
- Anchor developer deep dives when material to the market, such as ACWA, Masdar, state entities, or dominant IPPs.
- OEM/equipment supplier panorama, logistics/installation analysis, and auction/PPA tariff comparison.
- Participant-role matrix tying every material owner, OEM, EPC, financier, and channel actor to project roles, MW exposure, procurement influence, relationship strength, and sales entry point.
- Product-fit assessment for Mingyang/MySE solutions.
- Sales-action plan.
- Executive brief based only on conclusions that passed the Continuity, Evidence, and Contradiction gates.
- Evidence archive and rejected-claims register.

## Deep Workflow

Use for strategic questions such as NEOM energy configuration, Saudi localization factory strategy, floating offshore wind strategy, market-entry M&A, or integrated energy pricing logic.

Additional requirements:

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
- Sales conclusions must name the target actor, project or portfolio, MW scale, timing, procurement route, and recommended entry action.
- Do not write claims that cannot pass the review gates.
- Do not write or freeze executive summaries until the final master JSON, project ledger, policy backtrace, and synthesis are current.
