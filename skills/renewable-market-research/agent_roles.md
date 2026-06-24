# Agent Roles

## Role Separation

The workflow separates writers, reviewers, synthesizers, and executive compression roles.

- Writer agents collect and structure evidence for a specific domain.
- Reviewer agents challenge evidence quality and contradictions.
- The main/orchestrator agent owns rich master JSON aggregation, the canonical project ledger, and source-to-final continuity.
- Synthesis agents combine only reviewed findings, the latest validated master JSON, and the canonical ledger into decision-useful outputs in the order: wind project ledger, participant/competitor map, then sales judgment.
- Executive agents compress reviewed conclusions into management-ready judgments only after the final backpropagation pass.

## Heavy Execution Topology

For benchmark-surpassing country wind-market reports, use Heavy Workflow unless the user requests a smaller run.

Heavy Workflow uses 14 logical execution roles:

1. `main_orchestrator_integrator`: assigns lanes, owns harness state, merges depth files, maintains the rich master JSON, derives the canonical ledger, runs validations, writes final reports, and refreshes summary/conclusion.
2. `market_indicators_worker`: demand/load gap, generation, installed capacity, imports/exports, latest monthly/quarterly data, and time-series market indicators.
3. `pipeline_worker`: project pipeline, auctions, PPA/COD/status, aliases, phase boundaries, and confirmed/watchlist/duplicate/rejected classification.
4. `owner_developer_worker`: owners, developers, state entities, IPPs, SPVs, partner networks, key people, procurement influence, and local presence.
5. `china_capital_new_entrant_worker`: Chinese capital, Chinese/local project names, first-time entrants, local-language blind spots, and anomaly candidates.
6. `oem_competitor_worker`: OEM awards, turbine models/specs, product roadmaps, framework agreements, shortlist clues, absent/displaced competitors, and unallocated MW.
7. `epc_logistics_localization_worker`: EPC, O&M, logistics routes, heavy-lift/crane firms, installation constraints, localization, and supply-chain bottlenecks.
8. `policy_law_tariff_worker`: policy targets, decrees, legal IDs, regulator orders, auction rules, PPA/FIT/tariff history, and source backtrace.
9. `finance_bankability_worker`: MDB/DFI finance, project finance, guarantees, FX/indexation, sponsor financials, IRR/ROE where supportable, and bankability constraints.
10. `grid_storage_worker`: transmission, substations, grid-code, curtailment, balancing, storage, hybrid constraints, and interconnection risk.
11. `adjacent_opportunity_worker`: solar, BESS, hydrogen, ammonia, methanol, green-power demand, I-REC, CBAM, and industrial offtake only where they alter wind value, PPA, grid, procurement, or sales entry.
12. `product_fit_sales_worker`: Mingyang/MySE fit, priority accounts, procurement windows, current OEM status, route-to-entry, and sales-action hypotheses.
13. `verification_agent`: independently verifies critical fields through Chrome MCP, Exa fetch, or original files and writes source-audit artifacts.
14. `reflection_reviewer`: independently scores stage quality, identifies critical blockers, and writes executable gap tasks.

If the host cannot spawn 14 real agents, run the same lanes sequentially. Keep the file outputs and review gates identical; do not collapse the canonical ledger, verification, review, synthesis, and final report writing into worker outputs.

## Common Agent Output Contract

Every agent output must be machine-readable and include:

```json
{
  "agent_name": "...",
  "task_scope": "...",
  "findings": [],
  "evidence": [],
  "confidence": "high | medium | low | unknown",
  "uncertainty": [],
  "rejected_claims": [],
  "business_implications": [],
  "next_questions": []
}
```

## Writer Agents

### `policy_agent`

Collects policy targets, renewable laws, auction mechanisms, PPA structures, FITs, tariff history, local-content rules, permitting requirements, and government plans.

### `pipeline_agent`

Verifies wind, solar, storage, and hybrid project pipelines. It must separate installed capacity, official targets, auction capacity, confirmed projects, MOU-stage leads, and unverified watchlist leads.

It must capture official/local-language names, Chinese translated names, SPV names, aliases, duplicate clues, source traces, search passes, and rich project-card fields so the main agent can merge records into the master JSON and derive the canonical pipeline ledger.

### `owner_agent`

Maps owners, developers, IPPs, EPC firms, state entities, utilities, and potential channel partners. It must tie material actors to projects, MW exposure, role, procurement influence, existing ties, and sales entry path.

### `grid_agent`

Analyzes transmission, interconnection, curtailment, balancing, storage needs, grid-code requirements, and grid-operator constraints.

### `finance_agent`

Analyzes financing structures, MDB participation, project-finance status, PPA bankability, FX risks, tariff support, guarantees, and local financing constraints.

### `competitor_agent`

Maps OEM, EPC, BESS, developer, and localization competitors, including installed fleet, awards, platform fit, and relationship strength. It must segment competitors by awarded/supplied, framework agreement, likely entrant, absent/displaced, and unallocated-MW opportunity.

### `product_fit_agent`

Evaluates Mingyang/MySE product fit against wind regime, terrain, grid, logistics, localization, turbine class, hybrid/storage demand, O&M, and bankability constraints. It must tie recommendations to specific projects, actors, MW, procurement windows, and entry routes.

## Verification Agent

### `verification_agent`

Verifies critical fields independently from the worker that discovered them. It uses Chrome MCP, Exa fetch, or original files for project names/aliases, capacity, status, owner/SPV, location, COD/target COD, PPA/tariff, financing/investment, EPC/OEM/turbine, construction start, legal IDs, and policy targets.

It writes source-audit results and field-level verification notes. It does not write market conclusions or final report prose.

## Reviewer Agent

### `skeptic_agent`

Challenges writer outputs. It checks source strength, contradictions, duplicate project records, COD conflicts, status conflicts, phase confusion, unjustified confidence levels, generic company profiles, adjacent-topic drift, and sales conclusions that lack actor/project/MW/timing/entry route. It cannot write final conclusions; it produces review decisions and required fixes.

For Heavy Workflow, the reviewer also acts as `reflection_reviewer` and must score stage quality:

```json
{
  "agent_name": "reflection_reviewer",
  "stage": "search_plan | evidence | ledger | report",
  "scores": {
    "coverage": 0,
    "verification": 0,
    "ledger_integrity": 0,
    "participant_linkage": 0,
    "report_structure": 0,
    "citation_audit": 0,
    "benchmark_absorption": 0
  },
  "critical_blockers": [],
  "gap_tasks": [],
  "pass": false
}
```

The reviewer must not release a stage merely because the score improved. A stage passes only when it meets the relevant thresholds in `review_gates.md` and has zero critical blockers.

## Synthesis Agent

### `synthesis_agent`

Combines only reviewed findings into market judgment, confirmed pipeline, risk view, product-fit judgment, and sales-action plan. It must preserve evidence traceability and avoid unsupported narrative claims.

It must read rich project fields from the latest validated master JSON and use the canonical pipeline ledger for identity, dedupe, status buckets, and watchlist/rejected state.

## Executive Agent

### `executive_agent`

Compresses the reviewed synthesis into exactly three core judgments, each with evidence support, confidence, uncertainty, and a sales or resource-allocation implication.

It must refresh the executive summary after downstream chapters, master JSON, project ledger, policy backtrace, or synthesis changes.
