# Mobile Product Delivery

Use this file for mini-program, H5, mobile web, or app products. Load it when the feature has mobile users, field users, drivers, learners, customers, sales, inspectors, or any workflow where the user operates on a phone.

Mobile delivery is not a compressed desktop page. The PRD/prototype must define mobile role paths, device constraints, authorization, notification rules, weak-network behavior, and testable mobile UI patterns.

## Contents

- Mobile Scope
- Mobile Role Path Matrix
- Navigation Patterns
- Mobile Testid Naming
- Mini-Program Authorization
- Video Learning Pattern
- AI Digital Human / Conversational Tutor Pattern
- Quiz / Exam Pattern
- Weak Network and Offline
- Required Mobile Artifact Schemas
- Safety / Non-Interruption Gate
- Mobile Acceptance Checklist

## Mobile Scope

Declare the target surface:

```yaml
mobile_surface:
  platform: mini_program | h5 | app | mobile_web
  primary_user: driver | learner | enterprise_user | inspector | customer | sales | other
  device_context:
    network: stable | weak | offline_possible
    usage_context: resting | driving | field_work | indoor | customer_visit | learning
    input_modes: touch | camera | scan | microphone | speaker | voice | keyboard | location | avatar_stream
  auth_context:
    login: phone | wechat | sso | account_password
    consent_required: true
    sensitive_data: [location, behavior_profile, training_record]
```

Hard rule: if the usage context can involve driving, operating equipment, medical work, financial confirmation, or safety-critical field work, interruptive prompts and non-essential push messages are forbidden during active work.

## Mobile Role Path Matrix

Every mobile role needs a mobile-specific path. Do not reuse desktop paths without validating touch, navigation depth, and network state.

| Role | Entry | Core Path | State Change | Offline/Weak Network | Exit |
|---|---|---|---|---|---|
| driver | subscription message / home task card | open task -> watch video -> quiz -> submit | learning_task: notified -> completed | cache video metadata; retry exam submit | effect tracking |
| enterprise_user | dashboard alert | view driver risk -> assign learning -> review completion | task: created -> monitored | list loads skeleton; retry actions | report |
| field_inspector | scan / task list | open inspection -> upload evidence -> submit | inspection: draft -> submitted | local draft | audit timeline |

## Navigation Patterns

Recommended:

- Use bottom tabs for persistent top-level areas: `home`, `tasks`, `messages`, `profile`.
- Keep critical task flows within 3 levels from entry.
- Use sticky bottom action for primary submit/confirm actions.
- Use bottom sheet for contextual choices, not full modal stacks.
- Use stepper for multi-step forms or exams.
- Use skeleton loading for lists and cards.
- Use empty/error states with explicit retry actions.

Avoid:

- desktop-like dense tables;
- hover-only interactions;
- tiny inline links as primary actions;
- long modals with hidden bottom buttons;
- pushing users into a new top-level page for every minor action.

## Mobile Testid Naming

Required naming:

| Element | Pattern |
|---|---|
| bottom tab | `bottom-tab-{tabKey}` |
| page root | `page-{pageKey}` |
| sticky action bar | `sticky-action-{flow}` |
| primary sticky button | `btn-sticky-{action}-{flow}` |
| bottom sheet | `sheet-{purpose}` |
| sheet option | `sheet-option-{purpose}-{optionKey}` |
| pull refresh container | `pull-refresh-{scope}` |
| infinite list | `list-infinite-{scope}` |
| list item | `list-item-{scope}-{id}` |
| empty state | `empty-{scope}` |
| retry button | `btn-retry-{scope}` |
| video player | `video-player-{contentId}` |
| video progress | `video-progress-{contentId}` |
| quiz container | `quiz-{quizId}` |
| quiz question | `quiz-question-{quizId}-{questionNo}` |
| answer option | `quiz-option-{quizId}-{questionNo}-{optionKey}` |
| AI digital human/avatar | `ai-avatar-{agentId}` |
| avatar status | `ai-avatar-status-{agentId}` |
| voice input | `voice-input-{agentId}` |
| transcript panel | `transcript-{sessionId}` |
| interrupt button | `btn-interrupt-ai-{agentId}` |
| fallback text input | `input-fallback-text-{agentId}` |
| citation/evidence card | `citation-card-{agentId}-{sourceId}` |
| scan button | `btn-scan-{purpose}` |
| upload button | `btn-upload-{purpose}` |
| location permission | `permission-location-{purpose}` |
| microphone permission | `permission-microphone-{purpose}` |
| subscribe message permission | `permission-subscribe-{purpose}` |
| privacy consent | `consent-{purpose}` |

Rules:

- Mobile and desktop variants must preserve story IDs and business action names.
- Mobile-only controls still need `data-action`.
- Critical mobile elements must include `data-mobile="true"`.
- Permission gates must include `data-permission`.
- Weak-network retry targets must include `data-retry-for`.

Example:

```html
<button
  data-testid="btn-sticky-submit-driver-quiz"
  data-action="submit-driver-quiz"
  data-mobile="true"
  data-requires-network="true"
>
  提交考试
</button>
```

## Mini-Program Authorization

PRD must declare authorization and privacy boundaries:

| Capability | Required Contract |
|---|---|
| phone/login | auth provider, binding rule, fallback |
| subscription message | template id, trigger, user opt-in, frequency cap |
| location | purpose, precision, retention, fallback |
| microphone / audio recording | purpose, recording boundary, retention, fallback to text input |
| speech recognition / TTS | provider, latency target, transcript policy, failure fallback |
| avatar/video streaming | provider, rendering fallback, bandwidth policy, accessibility fallback |
| camera/scan | purpose, upload policy, failure path |
| file/media upload | size, type, compression, retry |
| behavior profile | consent, data minimization, usage boundary |

Forbidden:

- building sensitive user profile without consent;
- using training/risk profile for punishment unless an explicit human-approved business process exists;
- sending non-urgent messages while user is driving or in a safety-critical work state;
- hiding why a recommendation was generated.

## Video Learning Pattern

Required states:

```text
not_started -> in_progress -> completed -> quiz_pending -> passed | failed -> followup_monitoring
```

Required behavior:

- video has title, duration, risk/topic tag, reason for recommendation;
- video supports resume from last progress;
- completion threshold is declared, e.g. watched >= 90%;
- user can see why the video was recommended;
- quiz is unlocked only after completion threshold unless business allows pre-test;
- failed quiz creates retry/remedial path, not punishment;
- learning record writes audit and trace.

Required testids:

```text
video-player-{contentId}
video-reason-{contentId}
video-progress-{contentId}
btn-resume-video-{contentId}
quiz-{quizId}
btn-submit-quiz-{quizId}
quiz-result-{quizId}
```

## AI Digital Human / Conversational Tutor Pattern

Use this section when the mobile product contains AI 数字人、语音助教、AI 学习助教、AI 客服数字人、avatar tutor, voice tutor, or real-time conversational coaching.

Required conversation states:

```text
idle -> permission_check -> listening -> understanding -> responding -> awaiting_user
     -> completed | low_confidence | interrupted | fallback_text | human_handoff | failed
```

Required behavior:

- the user can see whether the AI is listening, thinking, speaking, interrupted, or failed;
- microphone permission is requested only when needed and has text-input fallback;
- the transcript is visible or retrievable when the business requires learning/audit trace;
- AI answers must show citation/evidence when using enterprise knowledge, regulation, courseware, or assessment data;
- low-confidence or out-of-scope questions must enter `low_confidence` with safe fallback, not fabricated answers;
- the user can interrupt a long AI response;
- avatar/rendering failure falls back to audio-only or text-only without losing the session;
- session memory boundary is declared: what is remembered, for how long, and whether the user can clear it;
- if the user may be driving or operating equipment, voice/quiz prompts must obey the non-interruption policy.

Latency and media contract:

| Item | Required Contract |
|---|---|
| STT latency | target and timeout; fallback after timeout |
| LLM response latency | target and loading state |
| TTS latency | target and fallback to text |
| avatar render latency | target and fallback to audio/text |
| interruption | expected stop time after user interrupt |
| bandwidth downgrade | avatar -> audio-only -> text-only |

Required testids:

```text
ai-avatar-{agentId}
ai-avatar-status-{agentId}
permission-microphone-{purpose}
voice-input-{agentId}
transcript-{sessionId}
btn-interrupt-ai-{agentId}
input-fallback-text-{agentId}
citation-card-{agentId}-{sourceId}
```

## Quiz / Exam Pattern

Required:

- question count, pass threshold, time limit if any;
- retry policy;
- anti-cheat requirement if business critical;
- explanation after answer if learning-oriented;
- result state and next action.

States:

```text
not_started -> answering -> submitted -> passed | failed | expired
```

Weak-network rule:

- save local draft for answers when possible;
- on submit failure, show retry and keep answer state;
- do not duplicate exam records; use idempotency key.

## Weak Network and Offline

Every mobile workflow must define:

| Case | Required UX |
|---|---|
| initial load slow | skeleton + timeout state |
| API failure | retry button + preserved user input |
| submit failure | keep draft + idempotent retry |
| video unavailable | fallback content or retry |
| STT/TTS failure | fallback to text input/output |
| avatar stream failure | downgrade to audio-only or text-only |
| conversation timeout | preserve transcript + retry last turn |
| offline | show cached list/detail when allowed |
| duplicate tap | disable button + idempotency |

No mobile flow is accepted if a network failure can silently lose user input.

## Required Mobile Artifact Schemas

Use these schemas for Stage 4.5 deliverables. QA may reject mobile delivery if these files are missing or use incompatible columns.

### `mobile-role-path-matrix.md`

| Story ID | Role | Platform | Entry | Core Steps | State Before | State After | Permission Gate | Weak-Network Behavior | Non-Interruption Rule | Exit/Next Action | Prototype Testids |
|---|---|---|---|---|---|---|---|---|---|---|---|

Minimum rules:
- Include one row per mobile role path, not one row per page.
- `Core Steps` must be executable in the prototype or explicitly marked future scope.
- `Prototype Testids` must include page root, entry control, primary action, and result state.

### `permission-gates.md`

| Capability | Trigger | User Prompt | Required Consent | Data Scope | Retention | Fallback If Denied | Audit/Testid |
|---|---|---|---|---|---|---|---|

Minimum rules:
- Include login, phone binding, subscription message, location, camera/upload, behavior profile, and sensitive records when applicable.
- A permission cannot be required silently; denied permission must have a fallback path.
- Sensitive capability rows must declare retention and data scope.

### `weak-network-matrix.md`

| Flow | Network Case | Preserved Data | UI State | Retry/Resume Action | Idempotency Key | Failure Boundary | Testid |
|---|---|---|---|---|---|---|---|

Minimum rules:
- Cover initial load, API failure, submit failure, offline state, duplicate tap, and media unavailable when relevant.
- Every submit flow must state preserved data and idempotency key.
- No row may end with only "show toast"; it must preserve, retry, resume, or explicitly discard with user confirmation.

## Safety / Non-Interruption Gate

For driver, operator, medical, field, or safety-related users:

```yaml
non_interruption_policy:
  active_work_signals: [driving, operating, in_task, high_risk_context]
  forbidden:
    - learning_push
    - quiz_prompt
    - non_urgent_modal
  allowed:
    - passive badge
    - urgent safety alert if legally/business required
  delayed_until:
    - rest_detected
    - user_opens_app
    - task_end
```

## Mobile Acceptance Checklist

- [ ] Mobile surface and platform declared.
- [ ] Mobile role path matrix exists.
- [ ] Bottom navigation / entry / exit path defined.
- [ ] Touch targets are large enough and primary action is reachable.
- [ ] Safe-area and sticky action behavior defined.
- [ ] Soft keyboard does not hide required inputs/actions.
- [ ] Weak-network and offline states preserve user input.
- [ ] Permission/consent gates are explicit and testable.
- [ ] Subscription messages include opt-in and frequency cap.
- [ ] Video/quiz flows have states, progress, retry, result, and audit.
- [ ] AI digital human / conversational tutor flows define microphone permission, transcript, latency, interruption, fallback, evidence/citation, and memory boundary where relevant.
- [ ] Safety/non-interruption policy exists where relevant.
- [ ] Mobile `data-testid` naming is applied.
