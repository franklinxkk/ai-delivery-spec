# Strategic Discovery Handoff

Use this reference when strategic discovery must be converted into an executable product-delivery decision.

This is a handoff contract, not a full strategy methodology. Upstream work may come from Product-Manager-Skills, internal research, consulting reports, customer interviews, sales evidence, policy analysis, or executive workshops. AI Delivery Spec checks whether the evidence is sufficient to enter Stage 1 and delivery planning.

## Contents

- 1. Trigger
- 2. Required Handoff
- 3. Evidence Rules
- 4. TAM / SAM / SOM Contract
- 5. Competitive Alternative Matrix
- 6. Positioning And Differentiation
- 7. Decision Outcomes
- 8. Handoff Template
- 9. Gate Acceptance
- 10. Relationship To Delivery

## 1. Trigger

Apply this gate when at least one is true:

- launching a new product, business line, industry, region, or customer segment;
- making a major investment, annual roadmap, board, fundraising, or commercialization decision;
- repositioning an existing product or changing its primary buyer/category;
- choosing build vs buy vs partner for a strategic capability;
- the business case depends on market size, competitor gap, or differentiated positioning.

Do not require this gate for:

- ordinary CRUD, fields, reports, permissions, bug fixes, and workflow optimizations;
- mandatory compliance changes with no product-market decision;
- already-approved roadmap items whose problem, segment, and outcome are stable;
- small experiments where the purpose is to learn before building a business case.

## 2. Required Handoff

| Area | Minimum Output | Required When |
|---|---|---|
| Opportunity | problem, affected customer/business outcome, why now, evidence | always |
| Target Segment | primary buyer/user, firmographic or behavioral boundary, JTBD | always |
| Market Size | TAM/SAM/SOM, method, sources, assumptions, date, confidence | new market, investment, fundraising, board decision |
| Competitive Alternatives | direct competitors, indirect alternatives, status quo, switching barriers | new product, positioning, build/buy |
| Differentiation | target, category, alternative, differentiated outcome, proof | commercialization or repositioning |
| Strategic Choice | chosen option, rejected options, tradeoffs, non-goals | always |
| Validation Plan | riskiest assumptions, experiment, evidence threshold, owner, deadline | when evidence is incomplete |
| Delivery Handoff | proposed tier, initial scope, success metrics, triggered gates | before Stage 1 |

## 3. Evidence Rules

Every material claim must declare:

```yaml
claim:
  statement:
  type: fact | estimate | assumption | hypothesis
  source:
  source_date:
  confidence: high | medium | low
  decision_impact:
  validation_needed: true | false
```

Rules:

- Separate facts, estimates, assumptions, and hypotheses.
- Use current, attributable sources for market and competitor claims.
- TAM/SAM/SOM must show calculation logic, not only three numbers.
- SOM must reflect channel, sales capacity, geography, product readiness, price, and time horizon. It cannot simply be a percentage of SAM without justification.
- Competitor analysis must include the customer's current workaround or status quo.
- Differentiation must describe a provable customer outcome, not an adjective list such as "smarter", "leading", or "all-in-one".
- Missing evidence does not automatically block exploration, but it must change the decision to `VALIDATE_FIRST` or `GO_WITH_ASSUMPTIONS`.

## 4. TAM / SAM / SOM Contract

Use market sizing only when it changes a strategic decision.

| Level | Definition | Required Constraint |
|---|---|---|
| TAM | total theoretical demand for the problem/category | define unit, geography, customer population, price/revenue basis |
| SAM | portion serviceable by current/planned product and geography | subtract unsupported segments, regulation, language, delivery constraints |
| SOM | realistically obtainable within a stated period | include GTM capacity, sales cycle, channel reach, competition, implementation capacity |

Minimum record:

```yaml
market_size:
  unit: customers | users | revenue | transactions
  method: top_down | bottom_up | value_theory
  tam:
  sam:
  som:
  horizon:
  formulas:
  sources:
  assumptions:
  confidence:
```

## 5. Competitive Alternative Matrix

| Alternative | Target Segment | Core Outcome | Strength | Weakness | Switching Cost | Evidence | Implication |
|---|---|---|---|---|---|---|---|
| Status quo / manual process | | | | | | | |
| Direct competitor | | | | | | | |
| Indirect substitute | | | | | | | |
| Build internally / partner | | | | | | | |

Do not score competitors only by feature count. Compare customer outcome, adoption friction, integration, trust, total cost, service model, and operational fit.

## 6. Positioning And Differentiation

```text
For [specific target segment]
who need [validated job/problem],
[product] is a [recognizable category]
that delivers [measurable outcome].
Unlike [actual alternative],
we [provable differentiation], because [evidence/capability].
```

Stress tests:

- Can the target customer recognize themselves?
- Is the compared alternative real?
- Can the claim be demonstrated or measured?
- Does the positioning help reject out-of-scope features?
- Is the differentiation durable enough for the decision horizon?

## 7. Decision Outcomes

| Decision | Meaning | Next Step |
|---|---|---|
| `GO` | evidence supports investment and scope | enter Stage 1 |
| `GO_WITH_ASSUMPTIONS` | direction is acceptable but assumptions remain | enter Stage 1 with validation milestones and guardrails |
| `VALIDATE_FIRST` | riskiest assumption could invalidate investment | run discovery/experiment before full PRD |
| `NO_GO` | opportunity, economics, differentiation, or feasibility is insufficient | archive decision and revisit conditions |

## 8. Handoff Template

```yaml
strategy_discovery_handoff:
  decision: GO | GO_WITH_ASSUMPTIONS | VALIDATE_FIRST | NO_GO
  opportunity:
    problem:
    target_outcome:
    why_now:
    evidence:
  target_segment:
    buyer:
    user:
    boundaries:
    jtbd:
  market_size:
    required: true | false
    tam:
    sam:
    som:
    method:
    sources:
    assumptions:
    confidence:
  alternatives:
    - name:
      type: status_quo | direct | indirect | build | partner
      customer_outcome:
      switching_barrier:
      evidence:
  positioning:
    category:
    differentiated_outcome:
    proof:
  strategic_choice:
    selected_option:
    rejected_options:
    non_goals:
  validation_plan:
    riskiest_assumptions:
    experiments:
    pass_threshold:
    owner:
    deadline:
  delivery_entry:
    proposed_tier: L0 | L1 | L2 | L3
    initial_scope:
    success_metrics:
    triggered_gates:
```

## 9. Gate Acceptance

- [ ] The decision is one of `GO`, `GO_WITH_ASSUMPTIONS`, `VALIDATE_FIRST`, or `NO_GO`.
- [ ] Facts, estimates, assumptions, and hypotheses are distinguishable.
- [ ] TAM/SAM/SOM is present only when it affects the decision and includes formulas/sources.
- [ ] Competitor analysis includes status quo and switching barriers.
- [ ] Differentiation is outcome-based and has proof or a validation plan.
- [ ] Rejected options and non-goals are recorded.
- [ ] The handoff declares proposed delivery tier, initial scope, metrics, and conditional gates.

## 10. Relationship To Delivery

- The handoff feeds Stage 1 opportunity/scope; it does not replace the PRD.
- `GO` and `GO_WITH_ASSUMPTIONS` may enter the delivery pipeline.
- `VALIDATE_FIRST` should use discovery or experiment workflows before L2/L3 commitment.
- Normal feature PRDs should not be forced to repeat TAM/SAM/SOM or positioning when this gate is not triggered.
- Product-Manager-Skills may be used as an optional upstream toolkit, but AI Delivery Spec must remain independently usable.
