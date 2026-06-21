# Workflow Modes

`renewable-market-research` is a workflow-oriented market intelligence skill. It should collect broadly, verify carefully, and write final outputs only from confirmed or clearly qualified claims.

## Core Workflow Principles

1. Separate collection, review, synthesis, and executive compression.
2. Keep writer agents and reviewer agents separate.
3. Store evidence in files before writing conclusions.
4. Never place unverified leads in the confirmed pipeline.
5. Separate official plans, auction targets, installed capacity, confirmed project pipeline, and optimistic scenarios.
6. Convert important facts into decision-useful implications.
7. Mark assumptions explicitly and keep unsupported claims in `rejected_claims` or watchlists.

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
- Top policy, grid, product-fit, and execution risks.
- Immediate next sales actions.
- Three executive judgments with evidence support.

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
- Full report.
- Project pipeline table.
- Owner/developer/EPC/competitor map.
- Product-fit assessment for Mingyang/MySE solutions.
- Sales-action plan.
- Executive brief.
- Evidence archive and rejected-claims register.

## Deep Workflow

Use for strategic questions such as NEOM energy configuration, Saudi localization factory strategy, floating offshore wind strategy, market-entry M&A, or integrated energy pricing logic.

Additional requirements:

- Multiple evidence-review loops.
- Scenario comparison.
- Assumptions register.
- Evidence archive.
- Human review gates before final external delivery.
- Sensitivity analysis for uncertain policy, grid, tariff, FX, localization, and demand assumptions.

Deep Workflow outputs should include all Standard Workflow outputs plus:

- Scenario matrix.
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
- Do not write claims that cannot pass the review gates.
