# Agent Roles

## Role Separation

The workflow separates writers, reviewers, synthesizers, and executive compression roles.

- Writer agents collect and structure evidence for a specific domain.
- Reviewer agents challenge evidence quality and contradictions.
- The main/orchestrator agent owns the canonical project ledger and source-to-final continuity.
- Synthesis agents combine only reviewed findings and the latest canonical ledger into decision-useful outputs.
- Executive agents compress reviewed conclusions into management-ready judgments only after the final backpropagation pass.

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

It must capture official/local-language names, Chinese translated names, SPV names, aliases, duplicate clues, source traces, and search passes so the main agent can merge records into the canonical pipeline ledger.

### `owner_agent`

Maps owners, developers, IPPs, EPC firms, state entities, utilities, and potential channel partners.

### `grid_agent`

Analyzes transmission, interconnection, curtailment, balancing, storage needs, grid-code requirements, and grid-operator constraints.

### `finance_agent`

Analyzes financing structures, MDB participation, project-finance status, PPA bankability, FX risks, tariff support, guarantees, and local financing constraints.

### `competitor_agent`

Maps OEM, EPC, BESS, developer, and localization competitors, including installed fleet, awards, platform fit, and relationship strength.

### `product_fit_agent`

Evaluates Mingyang/MySE product fit against wind regime, terrain, grid, logistics, localization, turbine class, hybrid/storage demand, O&M, and bankability constraints.

## Reviewer Agent

### `skeptic_agent`

Challenges writer outputs. It checks source strength, contradictions, duplicate project records, COD conflicts, status conflicts, phase confusion, and unjustified confidence levels. It cannot write final conclusions; it produces review decisions and required fixes.

## Synthesis Agent

### `synthesis_agent`

Combines only reviewed findings into market judgment, confirmed pipeline, risk view, product-fit judgment, and sales-action plan. It must preserve evidence traceability and avoid unsupported narrative claims.

It must read project claims from the latest canonical pipeline ledger or master JSON generated from that ledger.

## Executive Agent

### `executive_agent`

Compresses the reviewed synthesis into exactly three core judgments, each with evidence support, confidence, uncertainty, and a sales or resource-allocation implication.

It must refresh the executive summary after downstream chapters, project ledger, policy backtrace, or synthesis changes.
