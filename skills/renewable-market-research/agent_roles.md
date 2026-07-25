# Agent Roles

## Role Separation

The workflow separates writers, reviewers, synthesizers, and executive compression roles.

- Writer agents collect and structure evidence for a specific domain.
- Reviewer agents challenge evidence quality and contradictions.
- The main/orchestrator agent owns phase state, artifact manifest, rich master JSON aggregation, core ledgers, canonical facts/fact freeze, chapter input manifests, released reports, and source-to-final continuity.
- Worker agents may write only assigned `depth/`, `verification/`, `chapter_inputs/`, `chapter_drafts/`, or `audits/` artifacts. They must not write core ledgers, canonical facts, or released reports.
- Chapter writers read only their frozen `chapter-input-manifest.json` plus the referenced frozen inputs. They must retain source Markdown markers such as `{{fact:...}}`, `{{metric:...}}`, `{{project:...}}`, `{{policy:...}}`, `{{auction:...}}`, and `{{oem:...}}` for key claims. Missing facts become gap tasks, not ad hoc search or recalculation.
- Synthesis agents combine only reviewed findings, the latest validated master JSON, and the canonical ledger into decision-useful outputs in the order: wind project ledger, participant/competitor map, procurement-window/factual relevance view, then optional sales judgment for a separate brief.
- Executive agents compress reviewed conclusions into management-ready judgments only after the final backpropagation pass.

## Heavy Execution Topology

For benchmark-surpassing country wind-market reports, use Heavy Workflow unless the user requests a smaller run.

Heavy Workflow uses the state-machine profile by default: at least 15 logical agents and a target topology of 20 roles.

1. `main_orchestrator_integrator`: assigns lanes, owns phase state, artifact manifest, merges depth files, maintains the rich master JSON, derives core ledgers, freezes canonical facts, creates chapter input manifests, runs validations, assembles final reports, and refreshes summary/conclusion.
2. `chapter_0_scope_evidence_worker`: writes Chapter 0 scope, capacity definitions, stage definitions, opportunity definitions, and confidence rules from its manifest.
3. `chapter_2_market_fundamentals_worker`: writes Chapter 2 national power fundamentals, demand/load gap, generation, imports/exports, and market indicators from allowed metric/fact IDs.
4. `chapter_3_policy_permitting_worker`: writes Chapter 3 policy, permitting, development flow, and PPA mechanism from allowed policy/fact IDs.
5. `chapter_4_capacity_segmentation_worker`: writes Chapter 4 capacity segmentation from frozen ledger and reconciliation IDs.
6. `chapter_5_project_ledger_worker`: writes Chapter 5 full project ledger from allowed project ledger IDs.
7. `chapter_6_project_cards_worker`: writes Chapter 6 complete project cards from project-card JSON and allowed project/depth references.
8. `chapter_7_owner_decision_worker`: writes Chapter 7 developer, owner, SPV, and decision-right structure.
9. `chapter_8_wind_resource_turbine_fit_worker`: writes Chapter 8 wind resource, geography, and turbine-fit inference.
10. `chapter_9_oem_competition_worker`: writes Chapter 9 OEM competition with Firm MW, Committed MW, Influenced MW, Unallocated MW, and Excluded inactive MW.
11. `chapter_10_epc_finance_om_supply_worker`: writes Chapter 10 EPC, financiers, O&M, logistics, and supply-chain network.
12. `chapter_11_localization_worker`: writes Chapter 11 localization and industrial policy status.
13. `chapter_12_grid_storage_worker`: writes Chapter 12 grid, storage, interconnection, and curtailment constraints.
14. `chapter_13_tariff_bankability_worker`: writes Chapter 13 tariff, project economics, and bankability status.
15. `chapter_14_procurement_window_worker`: writes Chapter 14 procurement window, decision chain, and factual Mingyang/MySE relevance.
16. `chapter_15_risk_matrix_worker`: writes Chapter 15 risk matrix and constraint conditions.
17. `chapter_16_evidence_appendix_worker`: writes Chapter 16 source table, conclusion-confidence appendix, and pending-verification table.
18. `chapter_1_executive_summary_worker`: writes Chapter 1 only after cross-chapter audit passes and repaired chapter drafts are current.
19. `verification_agent`: independently verifies critical fields through Chrome MCP, Exa fetch, or original files and writes source-audit and chapter-verification artifacts.
20. `reflection_reviewer`: independently scores stage and chapter quality, runs or interprets the release-audit gates, identifies critical blockers, and writes executable gap tasks.

If the host cannot spawn 20 real agents, run the same lanes sequentially and record `agentMode=collapsed-sequential`. Keep the file outputs and review gates identical; do not collapse core ledgers, canonical facts, verification, review, synthesis, and final report writing into worker outputs.

Chapter writers must not search, recalculate capacity, choose policy targets, change project status, explain auction deltas beyond frozen facts, or copy deprecated values from older reports. If they find missing or contradictory input, they write a chapter gap task and stop that claim.

Release review must explicitly check metricId consistency, scope disclosure, capacity aggregation, OEM share denominators, project current-status uniqueness, parent/phase rollup deduplication, unit arithmetic, and release cleanliness before the main agent assembles the final report or derives lite.

Critical chapters requiring independent `verification_agent` artifacts before release: 1, 3, 4, 5, 6, 9, 13, 14, and 16. All other chapters still require a `reflection_reviewer` pass.

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

Maps OEM, EPC, BESS, developer, and localization competitors, including installed fleet, awards, platform fit, and relationship strength. It must segment OEM exposure by `oemRelationshipType` and `oemRelationshipStatus`, then report only Firm MW, Committed MW, Influenced MW, Unallocated MW, and Excluded inactive MW.

### `product_fit_agent`

Evaluates Mingyang/MySE factual relevance and product fit against wind regime, terrain, grid, logistics, localization, turbine class, hybrid/storage demand, O&M, and bankability constraints. It must tie relevance statements to specific projects, actors, MW, procurement windows, evidence confidence, and pending verification. Recommendations belong only in separate action briefs when requested.

## Verification Agent

### `verification_agent`

Verifies critical fields independently from the worker that discovered them. It uses Chrome MCP, Exa fetch, or original files for project names/aliases, capacity, status, owner/SPV, location, COD/target COD, PPA/tariff, financing/investment, EPC/OEM/turbine, construction start, legal IDs, and policy targets.

It writes source-audit results and field-level verification notes. It does not write market conclusions or final report prose.

## Reviewer Agent

### `skeptic_agent`

Challenges writer outputs. It checks source strength, contradictions, duplicate project records, COD conflicts, status conflicts, phase confusion, unjustified confidence levels, generic company profiles, adjacent-topic drift, V4 full-report structure, recommendation leakage inside the full report, and sales conclusions in separate briefs that lack actor/project/MW/timing/entry route. It cannot write final conclusions; it produces review decisions and required fixes.

For release review, it must treat these as critical blockers: same `metricId` with different values, aggregate metrics without scope/time/basis, project subtotals that do not match ledger aggregates, official auction/project capacity gaps without unresolved-gap treatment, OEM layer shares above 100%, Influenced MW inside Firm MW denominators, one project appearing with conflicting current status, parent/phase rows summed without rollup treatment, MW/GW/%/KRW arithmetic errors, and release artifacts such as internal version labels, repairs-applied notes, deletion markup, TODO/FIXME, unconverted footnotes, or raw JSON.

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

Combines only reviewed findings into market-status judgment, confirmed pipeline, risk view, product-fit or factual relevance judgment, procurement-window facts, and optional sales-action plan for separate briefs. It must preserve evidence traceability and avoid unsupported narrative claims.

It must read rich project fields from the latest validated master JSON and use the canonical pipeline ledger for identity, dedupe, status buckets, and watchlist/rejected state.

## Executive Agent

### `executive_agent`

Compresses the reviewed synthesis into exactly three core judgments, each with evidence support, confidence, uncertainty, and a sales or resource-allocation implication.

It must refresh the executive summary after downstream chapters, master JSON, project ledger, policy backtrace, or synthesis changes.
