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
16. Use Heavy state-machine workflow as the default for benchmark-surpassing country wind-market reports. Standard and Lite are reductions of the same file/gate architecture, not separate logic.

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
- Full report using the 0-16 chapter structure in `references/full-report-v4.md`.
- Gate artifacts in state-machine order: phase state/artifact manifest, candidate project pool, source trace/evidence table, rich master JSON, core ledgers, canonical facts/fact freeze, derived tables/project cards, chapter input manifests, chapter drafts, cross-chapter audit/repair, full report, then lite report.
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

Heavy full reports must use the state-machine profile by default: at least 15 logical agents and a target topology of 20 roles. Do not default to the 10-agent Standard profile unless the user explicitly asks for a smaller run.

Core state-machine rule: work inside the same phase may run in parallel, but cross-phase work is serial.

| Phase | Name | Parallel? | Owner | Exit artifact/gate |
|---|---|---|---|---|
| 1 | Plan | No | main agent | `phase_state.json`, `artifact_manifest.json`, `agent_plan.json` |
| 2 | Recall | Yes | recall workers | `candidate_project_pool.json`, `search_frontier.json`, `depth/*.json` |
| 3 | Verification and Evidence | Yes | verification workers | `source_trace.json`, `evidence_table.json`, `verification/*.json` |
| 4 | Rich Master and Core Ledgers | No | main agent | `{slug}.json`, project/metric/policy/auction/OEM ledgers, capacity reconciliation |
| 5 | Canonical Reconciliation and Fact Freeze | No | main agent | `canonical_facts.json`, `fact_freeze.json`, deprecated values, repair routing |
| 6 | Chapter Input Manifest and Chapter Writing | Yes | main agent then chapter writers | `chapter_inputs/*.json`, `chapter_drafts/*.md`, chapter gap tasks |
| 7 | Cross-Chapter Audit and Repair | Yes | audit/reviewer plus main agent | `audits/*cross_chapter_audit*.json`, repaired drafts or blocking gaps, eight report-audit checks |
| 8 | Release | No | main agent | refreshed executive summary, full report, lite report derived from full after zero audit gaps |

Core artifact ownership:

- Workers may write only `depth/`, `verification/`, `chapter_inputs/`, `chapter_drafts/`, and `audits/` artifacts assigned to their phase.
- Only the main agent may write `{slug}.json`, `project_ledger.json`, `metric_ledger.json`, `policy_target_ledger.json`, `auction_ledger.json`, `oem_allocation_ledger.json`, `canonical_facts.json`, `fact_freeze.json`, `phase_state.json`, `artifact_manifest.json`, and released reports.
- Chapter writers read only `canonical_facts.json` and their `chapter-input-manifest.json`. They must not search, recalculate capacity, choose policy targets, change project status, interpret auction deltas outside frozen facts, or copy deprecated values from old reports.

Agent topology:

1. `main_orchestrator_integrator`: owns phase state, artifact manifest, task split, artifact order, aggregation, master JSON, core ledgers, canonical facts, final integration, summary refresh, and handoff.
2. `chapter_0_scope_evidence_worker`: drafts Chapter 0 from the frozen manifest.
3. `chapter_2_market_fundamentals_worker`: drafts Chapter 2 from frozen power fundamentals and metric IDs.
4. `chapter_3_policy_permitting_worker`: drafts Chapter 3 from frozen policy/PPA/permit IDs.
5. `chapter_4_capacity_segmentation_worker`: drafts Chapter 4 from frozen capacity reconciliation and ledger IDs.
6. `chapter_5_project_ledger_worker`: drafts Chapter 5 from frozen project ledger IDs.
7. `chapter_6_project_cards_worker`: drafts Chapter 6 from frozen project-card and project IDs.
8. `chapter_7_owner_decision_worker`: drafts Chapter 7 from frozen participant/project IDs.
9. `chapter_8_wind_resource_turbine_fit_worker`: drafts Chapter 8 from frozen resource, geography, and turbine-fit facts.
10. `chapter_9_oem_competition_worker`: drafts Chapter 9 with Firm MW, Committed MW, Influenced MW, Unallocated MW, and Excluded inactive MW.
11. `chapter_10_epc_finance_om_supply_worker`: drafts Chapter 10 from frozen EPC, finance, O&M, logistics, and supply-chain inputs.
12. `chapter_11_localization_worker`: drafts Chapter 11 from frozen localization and industrial-policy inputs.
13. `chapter_12_grid_storage_worker`: drafts Chapter 12 from frozen grid, storage, interconnection, and curtailment facts.
14. `chapter_13_tariff_bankability_worker`: drafts Chapter 13 from frozen tariff, economics, and bankability facts.
15. `chapter_14_procurement_window_worker`: drafts Chapter 14 from frozen procurement-window and decision-chain facts.
16. `chapter_15_risk_matrix_worker`: drafts Chapter 15 from frozen risk and constraint inputs.
17. `chapter_16_evidence_appendix_worker`: drafts Chapter 16 from evidence-table and source-confidence inputs.
18. `chapter_1_executive_summary_worker`: drafts Chapter 1 only after cross-chapter audit passes and repaired chapter drafts are current.
19. `verification_agent`: independently verifies critical project/policy/tariff/OEM/procurement/evidence fields and writes source-audit plus chapter-verification artifacts.
20. `reflection_reviewer`: independently scores each phase and chapter, lists critical blockers, writes executable gap tasks, and audits cross-chapter consistency.

If the host cannot spawn 20 real child agents, run these roles as separate sequential lanes and record `agentMode=collapsed-sequential`. The phase order, role artifacts, ownership boundaries, and verification gates remain mandatory.

Critical chapters requiring writer/verifier separation:

- Chapter 1 executive summary.
- Chapter 3 policy/PPA/development flow.
- Chapter 4 capacity segmentation.
- Chapter 5 full project ledger.
- Chapter 6 key project cards.
- Chapter 9 OEM competition landscape.
- Chapter 13 tariff/project economics/bankability.
- Chapter 14 procurement window and decision-chain status.
- Chapter 16 data-source and conclusion-confidence appendix.

Heavy Workflow stage loop:

1. Plan reflection: reviewer checks phase state, artifact manifest, local-language coverage, Chinese-capital search, new-entrant search, anomaly hunting, official-source backtrace, and mandatory evidence thresholds before workers start.
2. Recall/evidence reflection: reviewer checks depth and verification files for coverage, source quality, search passes, critical-field verification, Exa-to-Chrome handoff, and unexplained blind spots.
3. Ledger/fact-freeze reflection: reviewer checks main-agent single writing, canonical IDs, alias merging, confirmed/watchlist/duplicate/rejected buckets, split project status fields, OEM relationship fields, capacity totals, rich-field propagation, source-to-final continuity, and frozen deprecated values.
4. Chapter/audit reflection: reviewer checks the 0-16 chapter structure, chapter-input manifests, full project ledger, project cards, developer/OEM depth, logistics, tariff/bankability status, procurement-window table, source-confidence appendix, summary freshness, no deprecated values, absence of benchmark sections unless requested, and the eight release audit classes: metric consistency, scope disclosure, capacity aggregation, OEM share, project status uniqueness, parent/phase rollup, unit arithmetic, and release cleanliness.

Stage advancement rules:

- A phase may advance only when the previous phase exit gate passes.
- A stage may advance only when `critical_blockers == 0`.
- Score improvement alone is insufficient; the current stage must also meet the threshold in `review_gates.md`.
- If a stage fails, the reviewer must write `data/renewable-market/{slug}-gap-tasks.json` with owner lane, missing artifact, required evidence method, and acceptance criterion.
- If canonical facts change after chapter input manifests or drafts are written, affected manifests, chapter drafts, audits, summaries, full report, and lite report become stale until regenerated or repaired.

Heavy Workflow outputs include all Standard outputs plus:

- `data/renewable-market/{slug}-phase_state.json`
- `data/renewable-market/{slug}-artifact_manifest.json`
- `data/renewable-market/{slug}-agent_plan.json`
- `data/renewable-market/{slug}-metric_ledger.json`
- `data/renewable-market/{slug}-policy_target_ledger.json`
- `data/renewable-market/{slug}-auction_ledger.json`
- `data/renewable-market/{slug}-oem_allocation_ledger.json`
- `data/renewable-market/{slug}-capacity_reconciliation.json`
- `data/renewable-market/{slug}-canonical_facts.json`
- `data/renewable-market/{slug}-fact_freeze.json`
- `data/renewable-market/chapter_inputs/{slug}-chapter-*-input-manifest.json`
- `data/renewable-market/chapter_drafts/{slug}-chapter-*.md`
- `data/renewable-market/chapter_verification/{slug}-chapter-*-verification.json`
- `data/renewable-market/audits/{slug}-cross_chapter_audit.json`
- `data/renewable-market/{slug}-search-coverage.json`
- `data/renewable-market/{slug}-source-audit.json`
- `data/renewable-market/{slug}-reflection-review.json`
- `data/renewable-market/{slug}-gap-tasks.json` when gaps remain

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
- Full-report procurement conclusions must name the project or portfolio, MW scale, timing, procurement route, `developmentStage`, `activityStatus`, `oemRelationshipType`, `oemRelationshipStatus`, decision maker/influencer, evidence confidence, and pending verification. Recommended actions belong in a separate brief when requested.
- Do not write claims that cannot pass the review gates.
- Do not write or freeze executive summaries until canonical facts, project ledger, policy backtrace, cross-chapter audit, and repaired chapter drafts are current.
