# Review Gates

Final outputs must pass these gates before release.

## 0. Continuity Gate

Rules:

- Final summaries, conclusions, project counts, capacity totals, procurement-window statements, and any separate recommendations must trace to the latest canonical facts, core ledgers, or reviewed synthesis.
- The executive summary must be written or refreshed after all downstream chapters, cross-chapter audit, canonical facts, and project ledger changes are complete.
- No chapter may maintain a separate project pipeline table that diverges from `{slug}-pipeline-ledger.json`, `{slug}-project_ledger.json`, canonical facts, or the master JSON.
- No chapter may use facts outside its `chapter-input-manifest.json`; key claims in source Markdown must carry manifest-allowed `{{fact:...}}`, `{{metric:...}}`, `{{project:...}}`, `{{policy:...}}`, `{{auction:...}}`, or `{{oem:...}}` markers.
- Every final project claim must include a source trace from depth record -> canonical ledger -> synthesis/report section.
- The master JSON, not the compact ledger, is the rich report data source. Depth records must be cross-read before project cards and deep-dive chapters are finalized.
- If a depth record contains a richer project-card field than the master JSON, update the master JSON first, then rebuild/refresh the ledger and synthesis.

Pass criteria:

- `metadata.sourceToFinal` records the pipeline ledger path, ledger update time, summary backpropagation time, and whether final claims were checked against the ledger.
- The report's executive summary, project cards or compact project index, procurement-window section, risk section, and source-confidence appendix use the same project count, capacity totals, status buckets, and key caveats.
- Any changed downstream chapter has either updated the summary or recorded why the summary is unaffected.
- `scripts/validate_market_integrity.py --depth-dir ...` returns no `depthPropagationGaps` or `reportCardFieldGaps`.
- `scripts/validate_market_integrity.py --phase-state ... --artifact-manifest ... --project-ledger ... --metric-ledger ... --capacity-reconciliation ... --oem-allocation-ledger ... --project-cards ... --evidence-table ... --canonical-facts ... --fact-freeze ... --chapter-input-dir ... --chapter-drafts-dir ... --audits-dir ... --full-report ...` returns a `gateSummary` with zero gaps for phase order, artifact ownership, canonical facts, fact-freeze projection, chapter input manifests, external chapter IDs, metric consistency, scope disclosure, capacity arithmetic, OEM share/recompute, numeric field contracts, project status conflicts, parent/phase rollup, unit arithmetic, release cleanliness, deprecated values in drafts, audit-content release gates, project ledger fields, project-card completeness, capacity reconciliation, evidence boundary, strategy leakage, and baseline inheritance.

Remediation:

- Rebuild or refresh the canonical ledger.
- Backfill missing rich project fields from `depth/*.json` into the master JSON, or mark them explicitly unavailable/not applicable with a gap note.
- Rerun synthesis from the latest ledger.
- Rewrite the executive summary and conclusion from the latest synthesis.
- Move stale, divergent, or untraceable claims to watchlist, appendix, or `rejected_claims`.

## 1. Evidence Gate

Rules:

- Claims without sources cannot enter final outputs.
- A single weak media source cannot support a high-confidence claim.
- Prioritize official documents, regulator sources, multilateral development bank documents, auction documents, owner announcements, grid-operator documents, and audited company materials.
- Unverified project leads must go into `watchlist` or `rejected_claims`, not the confirmed pipeline.
- Every important fact must include source URL, publisher, access date, source type, confidence, and uncertainty note.
- Exa search snippets can discover candidates but cannot by themselves verify confirmed-pipeline critical fields.

Pass criteria:

- All final claims have traceable evidence or are explicitly marked as assumptions.
- High-confidence claims are supported by official, owner, regulator, MDB, auction, grid-operator, or multiple mutually independent credible sources.
- Weakly sourced claims are downgraded or excluded.

Remediation:

- Add stronger sources.
- Downgrade confidence.
- Move the claim to watchlist, appendix, assumptions, or `rejected_claims`.

## 2. Critical Field Gate

Rules:

- Confirmed-pipeline critical fields must be verified by `chrome-mcp`, `exa-fetch`, or `manual-file`.
- Critical fields include project name/alias, capacity, status/evidence stage, owner/developer/SPV, location, COD/target COD, PPA, financing/investment, EPC/OEM/turbine, and construction start when present.
- `exa-search`, general search snippets, and secondary summaries may support discovery, but they cannot be the only support for final confirmed critical fields.
- Verification must be visible in `sourceTrace`, `sources`, `evidence`, or `criticalFieldVerification` with `collectionMethod` or `verificationMethod`.

Pass criteria:

- Each confirmed project has field-level verification for every present critical field, or the unverified field is explicitly downgraded and excluded from high-confidence final claims.
- `scripts/validate_market_integrity.py` returns no `criticalFieldGaps`.

Remediation:

- Open the original official/owner/MDB/grid/auction/PDF/table source with Chrome MCP or fetch the original file text.
- Add field-level `criticalFieldVerification` or `sourceTrace` entries.
- Downgrade the project or field to watchlist/uncertainty when original-source verification is unavailable.

## 3. Contradiction Gate

Rules:

- Check installed capacity versus planned capacity versus pipeline capacity.
- Check project status conflicts.
- Check COD and target-COD conflicts.
- Check duplicate project names, translated names, renamed projects, phase confusion, and sponsor changes.
- Check official-language aliases, Chinese translated names, Chinese EPC/OEM references, SPV names, and same-name/different-source project records.
- Check offshore, floating offshore, nearshore, and onshore classification.
- Do not aggregate duplicate phases as separate projects unless phase boundaries are evidenced.

Pass criteria:

- Pipeline records include duplicate-check notes.
- Duplicate candidates are either merged into one canonical ledger record or explicitly marked as watchlist/rejected with a reason.
- Conflicting dates, statuses, or capacities are either resolved or explicitly disclosed.
- Confirmed pipeline excludes ambiguous duplicated or renamed project records.
- Parent zones, developer portfolios, parent projects, project phases, and concrete project rows have explicit rollup treatment before any capacity sum.
- A project has only one current status across ledgers and chapter/current-status tables.

Remediation:

- Reconcile with official/owner/grid/MDB sources.
- Split into phases only when evidence supports it.
- Mark unresolved records as watchlist or rejected.

## 4. Business Gate

Rules:

- Every important fact must be converted into a report implication.
- Report implications must support project-status interpretation, capacity treatment, procurement-window clarity, product-fit relevance, risk judgment, pending verification, or executive decision context.
- Non-decision-useful information should move to appendix.
- A fact is not important merely because it is interesting; it must affect market judgment, pipeline conversion, product fit, risk, timing, or account strategy.
- Market participants must be tied to projects, MW exposure, role, procurement influence, relationship strength, factual relevance, or pending verification. Generic company profiles do not pass.
- Adjacent opportunities such as storage, solar PV, hydrogen, ammonia, methanol, I-REC, CBAM, or industrial offtake pass only when they change wind project value, PPA/tariff economics, interconnection, procurement route, OEM opportunity, bankability, or procurement-window facts.
- In the full report, do not write recommended actions. Use procurement-window, decision-chain, Mingyang/MySE relevance, risk, and pending-verification tables. If the user requested a separate action brief, sales recommendations must name actor, project or portfolio, MW scale, decision timing, `developmentStage`, `activityStatus`, `oemRelationshipType`, `oemRelationshipStatus`, procurement route, confidence, and next action.

Pass criteria:

- Each key finding has at least one implication category: `capacity_treatment`, `procurement_window`, `factual_relevance`, `product_fit`, `risk_judgment`, `pending_verification`, `executive_decision`, or `appendix_only`.
- The full report contains procurement-window and pending-verification tables instead of a recommended-action list.
- The final report includes a participant-role matrix or equivalent structured section for owners/developers, OEMs, EPC/finance actors, financiers, O&M actors, and material decision-chain participants.

Remediation:

- Add implication text.
- Move low-value information to appendix.
- Remove narrative filler and recommendation leakage from the full report.
- Convert generic participant descriptions into project-linked role and procurement-influence records.

## 5. Reflection Gate

Rules:

- The reflection/reviewer agent must review independently from the worker that produced the artifact.
- Reflection applies after Heavy Workflow phases: plan, recall/evidence, ledger/fact-freeze, chapter drafting, cross-chapter audit, and release.
- Score improvement alone is not enough to advance. A stage must meet its threshold and have zero critical blockers.
- Critical blockers include: missing mandatory search lane, confirmed critical fields supported only by discovery snippets, unreconciled duplicate projects, confirmed/watchlist leakage, missing source-to-final trace, stale executive summary, missing 0-16 full-report structure, missing full project ledger, missing project-card fields without gap notes, recommendation leakage inside the full report, generic participant profiles, missing chapter input manifests, chapter facts outside frozen inputs, metricId value conflicts, scope-less aggregate capacity metrics, failed capacity arithmetic, OEM share totals above 100%, Influenced MW mixed into Firm MW denominator, project current-status conflicts, unresolved parent/phase rollup, unit arithmetic errors, release-forbidden markup/artifacts, stale chapter drafts after canonical-facts refresh, or benchmark sections included without explicit request.
- Search/tool blockers include: treating Exa boundary as completion before Chrome verification, missing `chrome-verification` for required lanes, or failing to record `tool_unavailable=chrome-mcp` with affected fields when Chrome is unavailable.
- Agent blockers include: using the 10-agent Standard profile for a full report without explicit user reduction, fewer than 15 logical roles without a recorded collapsed-sequential reason, missing chapter owner for any Chapter 0-16 section, or missing independent verification artifacts for Chapters 1, 3, 4, 5, 6, 9, 13, 14, or 16.
- Gate blockers include nonzero `phaseOrderGaps`, `artifactOwnershipGaps`, `canonicalFactsGaps`, `factFreezeGaps`, `chapterInputManifestGaps`, `chapterExternalFactGaps`, `metricConsistencyGaps`, `scopeDisclosureGaps`, `capacityArithmeticGaps`, `oemShareGaps`, `numericFieldGaps`, `projectStatusConflictGaps`, `parentPhaseRollupGaps`, `unitArithmeticGaps`, `releaseCleanlinessGaps`, `releaseGaps`, `projectLedgerFieldGaps`, `projectCardCompletenessGaps`, `capacityReconciliationGaps`, `evidenceBoundaryGaps`, `strategyRecommendationGaps`, or `baselineInheritanceGaps` in `{slug}-integrity.json`.
- If a stage fails, the reviewer must write executable gap tasks with owner lane, missing artifact, required evidence method, and acceptance criterion.

Default score thresholds:

```json
{
  "search_plan": {
    "coverage": 85,
    "benchmark_absorption": 80
  },
  "evidence": {
    "coverage": 85,
    "verification": 90,
    "citation_audit": 85
  },
  "ledger": {
    "ledger_integrity": 95,
    "verification": 90,
    "participant_linkage": 85
  },
  "report": {
    "report_structure": 90,
    "citation_audit": 90,
    "participant_linkage": 85,
    "benchmark_absorption": 85
  }
}
```

Pass criteria:

- `critical_blockers` is empty.
- The current stage meets every applicable threshold above.
- `gap_tasks` is empty or contains only explicitly accepted residual gaps that are carried into uncertainty notes.
- The reviewer records which artifacts and timestamps were reviewed.

Remediation:

- Write or refresh `data/renewable-market/{slug}-gap-tasks.json`.
- Rerun only the affected worker lanes or aggregation step.
- Rerun verification if the fix changes critical fields.
- Rerun the same Reflection Gate before advancing.

## 6. Executive Gate

Rules:

- Final output must compress the result into three core judgments.
- Each judgment must have evidence support.
- Do not use vague claims such as “the market has great potential” unless quantified and qualified.
- Each judgment must state confidence, uncertainty, and what would change the judgment.

Pass criteria:

- The executive brief includes exactly three core judgments.
- Each judgment links to supporting evidence IDs or source references.
- The brief can be read aloud in about two minutes.

Remediation:

- Merge overlapping judgments.
- Replace vague growth language with quantified, sourced, and qualified statements.
- Add missing evidence or downgrade the judgment.

## 7. Release Audit Gate

Rules:

- Cross-chapter metric consistency: the same `metricId` must not have different normalized numeric values.
- Scope disclosure: aggregate metrics must state scope, time, and basis. `全国海风装机：230MW，截至2024年底` and `重点商业项目账本运营容量：96MW` are acceptable; `韩国运营海风：96MW` is not.
- Capacity aggregation: project subtotals equal ledger aggregates; official auction/award total minus identifiable project capacity equals unresolved gap; active pipeline excludes paused, withdrawn, cancelled, and superseded projects.
- OEM share: within one statistical layer, OEM shares total no more than 100%; Influenced MW cannot be mixed into the Firm MW denominator.
- OEM share recompute: `sharePercent` must equal `mw / denominatorMetricValue * 100`; the denominator metric ID must exist and one scope/layer group must not mix denominators.
- Numeric field contract: core ledger numeric fields must be `number` or `null`; missing public values require status/display metadata and cannot be encoded as `unknown`, `N/A`, or `not found`.
- Project status uniqueness: one project cannot be active, paused, cancelled, and watchlist across different current-status sections.
- Parent/phase rollup: government zones, developer portfolios, parent projects, phases, and concrete projects require explicit relationship treatment before any capacity sum.
- Unit arithmetic: visible calculations across MW/GW, percentages, KRW 亿/万亿, USD/KRW, project counts, and subtotals must reconcile.
- Release cleanliness: final reports cannot contain internal version labels, repairs-applied notes, `<del>`, markdown deletion, TODO/FIXME, internal iteration labels, unconverted footnotes, or raw JSON.

Pass criteria:

- `gateSummary` has zero gaps for `metricConsistencyGaps`, `scopeDisclosureGaps`, `capacityArithmeticGaps`, `oemShareGaps`, `numericFieldGaps`, `projectStatusConflictGaps`, `parentPhaseRollupGaps`, `unitArithmeticGaps`, `releaseCleanlinessGaps`, and `releaseGaps`.
- `audits/{slug}-cross_chapter_audit.json` follows `schema/cross-chapter-audit.schema.json`, has `status=passed`, zero critical/high issues, current `freezeId`, checked chapter/metric/project IDs, and no open repair tasks.

Remediation:

- Repair the ledger, canonical facts, chapter input manifests, affected chapter drafts, or final report text, then rerun the validator before release.
