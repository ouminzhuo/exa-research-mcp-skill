# Review Gates

Final outputs must pass these gates before release.

## 1. Evidence Gate

Rules:

- Claims without sources cannot enter final outputs.
- A single weak media source cannot support a high-confidence claim.
- Prioritize official documents, regulator sources, multilateral development bank documents, auction documents, owner announcements, grid-operator documents, and audited company materials.
- Unverified project leads must go into `watchlist` or `rejected_claims`, not the confirmed pipeline.
- Every important fact must include source URL, publisher, access date, source type, confidence, and uncertainty note.

Pass criteria:

- All final claims have traceable evidence or are explicitly marked as assumptions.
- High-confidence claims are supported by official, owner, regulator, MDB, auction, grid-operator, or multiple mutually independent credible sources.
- Weakly sourced claims are downgraded or excluded.

Remediation:

- Add stronger sources.
- Downgrade confidence.
- Move the claim to watchlist, appendix, assumptions, or `rejected_claims`.

## 2. Contradiction Gate

Rules:

- Check installed capacity versus planned capacity versus pipeline capacity.
- Check project status conflicts.
- Check COD and target-COD conflicts.
- Check duplicate project names, translated names, renamed projects, phase confusion, and sponsor changes.
- Check offshore, floating offshore, nearshore, and onshore classification.
- Do not aggregate duplicate phases as separate projects unless phase boundaries are evidenced.

Pass criteria:

- Pipeline records include duplicate-check notes.
- Conflicting dates, statuses, or capacities are either resolved or explicitly disclosed.
- Confirmed pipeline excludes ambiguous duplicated or renamed project records.

Remediation:

- Reconcile with official/owner/grid/MDB sources.
- Split into phases only when evidence supports it.
- Mark unresolved records as watchlist or rejected.

## 3. Business Gate

Rules:

- Every important fact must be converted into a business implication.
- Business implications must support sales action, product-fit judgment, risk judgment, or executive decision-making.
- Non-decision-useful information should move to appendix.
- A fact is not important merely because it is interesting; it must affect market judgment, pipeline conversion, product fit, risk, timing, or account strategy.

Pass criteria:

- Each key finding has at least one implication category: `sales_action`, `product_fit`, `risk_judgment`, `executive_decision`, or `appendix_only`.
- The final report contains a concrete next-action list.

Remediation:

- Add implication text.
- Move low-value information to appendix.
- Remove narrative filler.

## 4. Executive Gate

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
