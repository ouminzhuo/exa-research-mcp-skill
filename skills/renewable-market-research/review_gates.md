# Review Gates

Final outputs must pass these gates before release.

## 0. Continuity Gate

Rules:

- Final summaries, conclusions, project counts, capacity totals, and recommendations must trace to the latest canonical project ledger or reviewed synthesis.
- The executive summary must be written or refreshed after all downstream chapters and project ledger changes are complete.
- No chapter may maintain a separate project pipeline table that diverges from `{slug}-pipeline-ledger.json` or the master JSON.
- Every final project claim must include a source trace from depth record -> canonical ledger -> synthesis/report section.
- The master JSON, not the compact ledger, is the rich report data source. Depth records must be cross-read before project cards and deep-dive chapters are finalized.
- If a depth record contains a richer project-card field than the master JSON, update the master JSON first, then rebuild/refresh the ledger and synthesis.

Pass criteria:

- `metadata.sourceToFinal` records the pipeline ledger path, ledger update time, summary backpropagation time, and whether final claims were checked against the ledger.
- The report's executive summary, project cards or compact project index, risk section, and sales-action section use the same project count, capacity totals, status buckets, and key caveats.
- Any changed downstream chapter has either updated the summary or recorded why the summary is unaffected.
- `scripts/validate_market_integrity.py --depth-dir ...` returns no `depthPropagationGaps` or `reportCardFieldGaps`.

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

Remediation:

- Reconcile with official/owner/grid/MDB sources.
- Split into phases only when evidence supports it.
- Mark unresolved records as watchlist or rejected.

## 4. Business Gate

Rules:

- Every important fact must be converted into a business implication.
- Business implications must support sales action, product-fit judgment, risk judgment, or executive decision-making.
- Non-decision-useful information should move to appendix.
- A fact is not important merely because it is interesting; it must affect market judgment, pipeline conversion, product fit, risk, timing, or account strategy.
- Market participants must be tied to projects, MW exposure, role, procurement influence, relationship strength, or sales entry route. Generic company profiles do not pass.
- Adjacent opportunities such as storage, solar PV, hydrogen, ammonia, methanol, I-REC, CBAM, or industrial offtake pass only when they change wind project value, PPA/tariff economics, interconnection, procurement route, OEM opportunity, or sales entry.
- Sales recommendations must name actor, project or portfolio, MW scale, decision timing, current OEM status, procurement route, confidence, and next action.

Pass criteria:

- Each key finding has at least one implication category: `sales_action`, `product_fit`, `risk_judgment`, `executive_decision`, or `appendix_only`.
- The final report contains a concrete next-action list.
- The final report includes a participant-role matrix or equivalent structured section for owners/developers, OEMs, EPC/finance actors, and priority sales targets.

Remediation:

- Add implication text.
- Move low-value information to appendix.
- Remove narrative filler.
- Convert generic participant descriptions into project-linked role and procurement-influence records.

## 5. Executive Gate

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
