# AI Effect Evaluation

Use this file when an AI feature claims efficiency improvement, quality improvement, risk reduction, learning effect, behavior change, cost reduction, conversion lift, or safety/compliance impact.

Do not let AI product claims jump from "generated output" to "business impact" without an evaluation design.

## Contents

- Evidence Levels
- Evaluation Card
- Metric Types
- Locale / Regional Evaluation
- Baseline / Post Window
- Comparison Designs
- Driver Training Example
- Knowledge Learning Example
- Acceptance Checklist
- Hard Fail Conditions

## Evidence Levels

| Level | Meaning | Acceptable Claim |
|---|---|---|
| L0 output works | AI can generate/recommend/classify | "功能可运行" |
| L1 user acceptance | users complete/accept/use output | "用户愿意使用" |
| L2 short-term proxy | immediate metric improves | "相关行为有改善迹象" |
| L3 controlled evidence | baseline/post or matched comparison supports effect | "有较强效果佐证" |
| L4 causal evidence | A/B, quasi-experiment, or rigorous causal design | "可较可信归因" |

Rule: most early AI-native product releases should claim L1-L3, not L4.

## Evaluation Card

Stage rule:
- Stage 3 records only `claimed_effect`, `evidence_level_target`, and `unit_of_analysis` as an effect intent.
- Stage 5.7 completes the full evaluation card after observability fields, data sources, baseline feasibility, and measurement windows are known.
- SIM 2 must check prototype/demo copy against the evidence level; unsupported numbers or causal wording fail review.

```yaml
ai_effect_evaluation:
  id: AEE-001
  feature_id: string
  claimed_effect: string
  evidence_level_target: L1 | L2 | L3 | L4
  unit_of_analysis: driver | learner | enterprise | task | report | user_session
  baseline_window: 30d
  post_window: 30d
  primary_metrics:
    - name: same_alert_recurrence_delta
      direction: decrease
      target: -15%
  guardrail_metrics:
    - name: user_complaint_rate
      max: 2%
  segmentation:
    - vehicle_type
    - risk_level
    - enterprise
  confounders:
    - route_change
    - seasonality
    - policy_change
    - manager_intervention
  data_sources:
    - active_safety_alerts
    - training_records
    - exam_records
  review_owner: PM + Data + Sponsor + QA
```

## Metric Types

| Type | Examples | Notes |
|---|---|---|
| adoption | completion rate, acceptance rate, repeat usage | proves users use it |
| quality | schema-valid rate, human rating, correction rate | proves output usable |
| efficiency | saved minutes, fewer manual steps, faster response | needs baseline |
| behavior | recurrence delta, habit change, task completion | needs time window |
| business | conversion, retention, renewal, incident reduction | needs stronger evidence |
| safety/compliance | risk closure, audit pass, violation reduction | high-risk; avoid overclaim |

## Locale / Regional Evaluation

Do not average all markets into one global AI score. Evaluate each supported locale/market that can materially change language understanding, safety policy, knowledge sources, tools, user behavior, or legal/product claims.

Minimum evaluation slices:

| Slice | Required Evidence |
|---|---|
| locale/language | task success, human quality rating, hallucination, refusal, citation, structured-output validity |
| market/region | local knowledge/policy freshness, tool availability, escalation path, product-claim validity |
| dialect/code-switch | representative utterances, transcription/intent accuracy, unsafe misunderstanding rate |
| model/provider route | golden-case parity, tool schema compatibility, safety/refusal compatibility |
| user segment | age, accessibility, professional role, risk group where applicable and lawful |

Rules:

- Define locale-specific minimum sample size and release threshold; a high-resource language pass does not approve another locale.
- Use qualified native/domain reviewers for consequential outputs. Machine translation alone is not evaluation evidence.
- Track global aggregate and worst-locale result. A critical locale failure cannot be hidden by the global average.
- Compare error severity, not only accuracy. Mistranslating a safety instruction, legal limitation, medical warning, or financial commitment is a release blocker.
- Keep locale golden cases versioned with model, prompt, knowledge, tool, and policy dependencies.
- Product and sales claims must name the evaluated markets/locales; do not generalize pilot evidence from one country to all markets.

## Baseline / Post Window

For behavior change:

```text
baseline window -> AI intervention -> cooling window -> post window
```

Example:

```yaml
baseline_window: learning_task_created_at - 30d to learning_task_created_at
cooling_window: learning_task_completed_at to learning_task_completed_at + 3d
post_window: learning_task_completed_at + 3d to learning_task_completed_at + 33d
```

Rules:

- baseline and post windows must use the same metric definition;
- exclude periods where data collection changed;
- mark major route/job/policy changes as confounders;
- do not compare users with no comparable baseline unless explicitly marked.

## Comparison Designs

| Design | Use | Claim Strength |
|---|---|---|
| before/after same user | early pilot | weak to medium |
| matched comparison | when A/B not possible | medium |
| staggered rollout | operational rollout | medium |
| A/B test | product experiment | strong |
| expert review | content/quality judgment | supports quality, not business effect alone |

For regulated or safety scenarios, prefer staggered rollout or matched comparison before broad claims.

## Driver Training Example

```yaml
ai_effect_evaluation:
  id: AEE-DRV-TRAIN-001
  feature_id: driver_precise_training_agent
  claimed_effect: reduce recurrence of same active-safety alerts after targeted training
  evidence_level_target: L3
  unit_of_analysis: driver
  baseline_window: 30d_before_training
  cooling_window: 3d_after_training
  post_window: 30d_after_cooling
  primary_metrics:
    - name: same_alert_recurrence_delta
      direction: decrease
      target: -15%
    - name: severe_alert_count_delta
      direction: decrease
      target: -10%
  secondary_metrics:
    - training_completion_rate
    - exam_pass_rate
    - driver_acceptance_rate
  guardrail_metrics:
    - complaint_rate
    - push_opt_out_rate
    - false_profile_rate
  confounders:
    - route_change
    - vehicle_change
    - enterprise_manager_intervention
    - weather_or_seasonality
```

Allowed claim after pilot:

```text
Targeted training showed evidence of reduced same-type alert recurrence in the pilot cohort.
```

Forbidden claim without L4:

```text
AI training reduced accidents.
```

## Knowledge Learning Example

```yaml
ai_effect_evaluation:
  id: AEE-KNOW-LEARN-001
  feature_id: personalized_learning_agent
  claimed_effect: improve mastery of weak knowledge points through targeted content and quizzes
  evidence_level_target: L3
  unit_of_analysis: learner
  baseline_window: previous_quiz_window
  post_window: next_quiz_window
  primary_metrics:
    - name: weak_point_score_delta
      direction: increase
      target: +10%
    - name: repeated_mistake_rate_delta
      direction: decrease
      target: -15%
  secondary_metrics:
    - content_completion_rate
    - quiz_pass_rate
    - learner_acceptance_rate
```

## Acceptance Checklist

- [ ] Claimed effect has an evidence level.
- [ ] Unit of analysis is defined.
- [ ] Baseline/post windows are defined.
- [ ] Primary, secondary, and guardrail metrics are defined.
- [ ] Data sources and metric caliber are stable.
- [ ] Confounders are listed.
- [ ] Comparison design is selected.
- [ ] Product copy does not overclaim beyond evidence level.
- [ ] Sponsor and QA have checked demo copy, dashboard numbers, and sales-facing wording against the evaluation card.
- [ ] Pilot report separates observed correlation, effect evidence, and causal claims.

## Hard Fail Conditions

- Claiming safety, accident, revenue, or compliance impact without evaluation design.
- No baseline.
- Metric definition changes between baseline and post windows.
- No guardrail metrics.
- No data source freshness/quality check.
- No separation between AI recommendation and human/manual intervention.
