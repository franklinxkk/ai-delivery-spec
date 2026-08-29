# Domain: Media Assets And Multimodal Knowledge

Source authority and freshness metadata: `references/domains/domain-sources.yaml`.
Coverage and maturity: `references/domain-coverage.yaml`.

Use this replaceable domain module for media-asset management, image/audio/video
archives, live streams, multimodal knowledge bases, moment search, media RAG,
AI-assisted clipping/reuse, audiovisual preservation, and media-derived AI
datasets. Compose it with `ai-native`, `data-product`, and the applicable
industry pack instead of copying their rules here.

Applies when:

- a product acquires, processes, catalogs, preserves, searches, cites, reuses,
  generates from, or trains on image, audio, video, live-stream, screen-recording,
  surveillance, broadcast, or other time-based media;
- users need an exact media moment, not merely a file or transcript document.

Does not apply when:

- media is only a decorative upload with no managed lifecycle, rights,
  semantic retrieval, evidence, or reuse;
- the request is ordinary document RAG with no image/audio/video time or space
  anchoring.

## Domain Purpose

- Business outcome: turn dark media inventory into governed assets, searchable
  moments, citable evidence, reusable content, and bounded AI actions.
- Primary users: archivist/media librarian, content producer/editor, researcher,
  business or domain user, rights/compliance reviewer, data/AI engineer, admin.
- Sensitive areas: copyright and license, face/voice/biometric data, location,
  minors, private speech, confidential footage, generated or manipulated media,
  and media used as high-impact evidence.
- AI may optimize: technical inspection, near-duplicate discovery, transcription,
  OCR, shot/scene/event segmentation, annotation suggestions, multimodal search,
  summarization, recommendation, and draft clipping.
- AI must not autonomously decide: identity as a binding fact, authenticity or
  guilt, legal rights to use/publish/train, irreversible deletion, public release,
  or other consequential action without the accountable source and human gate.

### Current Baseline And Change Watch (verified 2026-08-29)

| Evidence class | Current signal | Requirement effect |
|---|---|---|
| binding_baseline | China personal-information, face-recognition, copyright, network-data and AI-generated-content-labeling rules | verify jurisdiction, role, media subject, purpose, allowed action, consent/legal basis, labeling and retention before retrieval, training, export or publication |
| design_guidance | IPTC VMH 1.7, C2PA 2.4, W3C Media Fragments/Web Annotation, IIIF 3.0, PBCore, PREMIS/FADGI, MPEG-7 and current China audiovisual metadata standards | use stable asset/instance/segment identities, time-space selectors, provenance, rights and preservation mappings; adopt only the profiles needed by the product |
| product_pattern | Azure AI Video Indexer, NVIDIA VSS and Twelve Labs expose ingestion, scene/shot/moment analysis, multimodal search and video Q&A patterns | discover options and evaluation slices only; vendor features or accuracy claims cannot become a project requirement without evidence |
| change_watch | metadata, content-credential, AI-labeling, preservation format and multimodal-model versions continue to change | record source/model/index/profile versions and reverify before high-risk use; never freeze a vendor model name as permanent domain truth |

### AI Transformation Horizon

| Level | From -> toward | Proof before promotion |
|---|---|---|
| M0 inventory | unknown files -> identified, readable, deduplicated inventory | count, location, format, corruption, rights-unknown and owner are measurable |
| M1 governed assets | folders -> Work/Asset/Rendition/Track lifecycle | source, hash, master/proxy, rights, retention and audit are reliable |
| M2 searchable moments | filename/transcript search -> lexical + metadata + multimodal moment retrieval | real queries find the correct time range without unauthorized exposure |
| M3 knowledge | tags -> entities/events/concepts linked to exact media evidence | important claims replay the supporting moment and evidence state |
| M4 AI applications | manual review/edit -> grounded Q&A, summarization, clipping, recommendation | task success, citation, rights and cost beat the agreed baseline |
| M5 bounded agents | user performs every handoff -> agent proposes or executes permitted reversible actions | tool scope, approval, rollback, incident and trace evidence pass |

## First-Principles Domain Lens

| Lens | Required answer |
|---|---|
| Value object | Which asset, moment, evidence claim, reusable clip, dataset sample or downstream decision becomes better? |
| Retrieval unit | Does success require a Work, Asset, Rendition, chapter, shot, event, utterance, frame or spatial region? |
| State physics | Which ingest, processing, review, rights, index, publication, withdrawal, archive or deletion state proves work happened? |
| Source authority | Which source system owns descriptive facts, rights, consent, provenance, identity and authoritative business interpretation? |
| Temporal truth | Which time base, frame rate, start/end, track and derivative mapping keep the evidence replayable? |
| High-risk boundary | Which view, identity, export, clip, publish, train or delete action requires a human/legal gate? |
| Test evidence | Which real queries and gold moments prove discovery, time localization, permission, citation and business value? |

The smallest knowledge unit is not an opaque file or arbitrary text chunk:

```text
KnowledgeMoment = asset_id + rendition_id + temporal/spatial selector
                + modality + semantic annotation + evidence state
                + rights/consent + provenance + index version
```

Media becomes reusable knowledge only when identity, precise anchoring,
source/provenance, rights, semantics, evidence state, version and intended use
remain linked.

## Vocabulary

| Term | Meaning | Source of truth |
|---|---|---|
| MediaWork | abstract intellectual content, programme, event record or story | approved catalog/editorial record |
| MediaAsset | managed media object with business identity and lifecycle | media catalog |
| Rendition / Instantiation | concrete original, preservation master, edit master, proxy or published file | media repository + catalog |
| Track | video, audio, subtitle, timed-text or data stream | file probe + reviewed metadata |
| Segment | chapter, scene, shot, speaker turn, event or model-created temporal range | segment registry |
| KnowledgeMoment | a retrievable, replayable and governed media segment/region | segment + annotation + rights/provenance |
| Annotation | human or machine body linked to a media target and motivation | annotation store |
| RightsGrant | actor/purpose/action/territory/channel/term authorization | contract or rights system |
| Consent | personal-data/portrait/voice permission and withdrawal record | consent system/accountable evidence |
| ProvenanceRecord | acquisition, transform, generation, edit and publication lineage | provenance/audit ledger |
| ContentCredential | verifiable signed provenance assertions and ingredient relationships | credential manifest/validator |
| IndexVersion | corpus, schema, segment policy, model and build snapshot | search/index registry |

## Aggregates and Entities

| Aggregate | Owns | Key states | Notes |
|---|---|---|---|
| MediaWork | Work, Collection, Story, relationships | draft -> cataloged -> active -> retired | separates intellectual content from files |
| MediaAsset | Asset, Rendition, Track, hash, storage refs | received -> quarantined -> verified -> governed -> archived/deleted | original is immutable; derivatives are new instances |
| MediaSegmentation | Segment, Frame, Keyframe, boundary method | proposed -> processed -> reviewed -> active -> superseded | fixed windows are a processing option, not domain truth |
| MediaAnnotation | TranscriptCue, OCRBlock, Annotation, EntityOccurrence, EventOccurrence | generated -> review_pending -> confirmed/rejected -> superseded | AI output never silently overwrites confirmed facts |
| RightsAndConsent | RightsGrant, Consent, Restriction, withdrawal impact | unknown -> under_review -> allowed/restricted/expired/revoked | possession never proves right to use |
| MediaProvenance | ProvenanceRecord, ContentCredential, IngredientLink | captured -> validated/invalid/unknown -> superseded | valid provenance is not proof that a claim is true |
| MediaIndex | EmbeddingVersion, LexicalIndex, GraphIndex, IndexVersion | planned -> building -> ready -> stale -> rebuilding -> retired | every result binds the index version |
| MediaUse | SearchSession, EvidenceLink, ClipDraft, Export, Publication, DatasetUse | requested -> authorized -> executed -> reviewed/revoked | action permission differs from view permission |

Canonical relationships:

```text
MediaWork 1..n MediaAsset 1..n Rendition 1..n Track
Rendition 1..n Segment; Segment 0..n Annotation
Annotation -> Entity/Event/Concept and exact temporal/spatial target
RightsGrant/Consent -> subject + asset/segment + purpose + action + term
ProvenanceRecord -> input rendition/segment + action + output rendition/segment
EmbeddingVersion/IndexVersion -> corpus + segment policy + model/schema version
EvidenceLink -> claim/action + KnowledgeMoment
```

## Domain Events

```yaml
events:
  MediaAssetIngested:
    payload: { asset_id, source_ref, batch_id, original_hash, acquired_at }
  MediaTechnicalCheckFailed:
    payload: { rendition_id, check_id, reason, recoverable, evidence_ref }
  MediaRenditionDerived:
    payload: { source_rendition_id, output_rendition_id, transform, tool_version }
  MediaSegmentsPublished:
    payload: { rendition_id, segment_policy, segment_version, reviewer_id }
  MediaAnnotationConfirmed:
    payload: { annotation_id, target_ref, evidence_state, reviewer_id }
  MediaIndexPublished:
    payload: { index_version, corpus_version, segment_version, model_versions }
  MediaMomentRetrieved:
    payload: { query_id, moment_ref, matched_modalities, rank, rights_decision }
  MediaUseAuthorized:
    payload: { use_id, asset_or_segment_ref, purpose, action, grant_ref, approver }
  MediaRightsWithdrawn:
    payload: { rights_ref, affected_assets, effective_at, impact_job_id }
  MediaDerivedUseBlocked:
    payload: { source_ref, derivative_or_index_ref, reason, decision_ref }
```

## State Machines

```text
MediaAsset: received -> quarantined -> technical_verified -> governed -> active -> archived | deleted
Rendition: created -> verified -> available -> restricted -> superseded | disposed
Annotation: generated -> review_pending -> confirmed | rejected -> superseded
RightsGrant: unknown -> under_review -> allowed | restricted | expired | revoked
IndexVersion: planned -> building -> ready -> stale -> rebuilding -> retired | failed
ClipDraft: proposed -> rights_check -> review -> approved -> exported/published | rejected
WithdrawalImpact: created -> discovering -> frozen -> remediating -> verified -> closed
```

State rules:

- `active` media requires a readable governed rendition and resolvable source;
- `ready` index requires corpus, segment, schema and model versions plus a
  permission-filter contract;
- `allowed` is scoped to actor, purpose, action, territory/channel and term;
  it is never a global boolean;
- rights/consent withdrawal freezes affected new use before asynchronous impact
  discovery completes;
- deletion cannot close until declared derivatives, captions, keyframes, caches,
  embeddings, graph statements, exports and dataset references are disposed,
  retained under an explicit legal hold, or assigned an accountable exception.

## Metric / Indicator Governance

| Metric | Caliber | Owner |
|---|---|---|
| ingest_success_rate | assets completing immutable-original, hash, probe and catalog / expected assets, by source/batch/format | media operations |
| playable_rate | renditions passing target player, audio/video/timed-text and duration checks / processed renditions | media engineering + QA |
| metadata_completeness | populated required descriptive/technical/structural/admin/rights/preservation/AI-derived fields / applicable fields | catalog owner |
| processing_latency_p95 | elapsed time per media hour, split by resolution, live/offline and enrichment task | platform owner |
| cost_per_useful_media_hour | storage + processing + model + human review cost / accepted useful media hours | product + finance |
| ASR_WER_CER | word/character error against stratified language/accent/noise/domain gold set | AI/QA |
| OCR_precision_recall | text correctness plus time/spatial localization against gold labels | AI/QA |
| segment_boundary_F1 | predicted scene/event boundaries against reviewed gold boundaries | AI/QA |
| retrieval_Recall_at_K_MRR_nDCG | ranking on versioned real-query gold set, segmented by query type and modality | search owner |
| temporal_IoU | overlap between retrieved and gold time range; whole-video hits cannot pass moment retrieval | search owner |
| grounded_citation_precision | material claims with correct replayable KnowledgeMoment evidence / material claims | product + QA |
| unauthorized_exposure_rate | restricted moments exposed in result/preview/answer/export; P0 target is zero | security/privacy |
| rights_coverage | assets whose actor/purpose/action/territory/channel/term can be decided / governed assets | rights owner |
| time_to_find_moment | user elapsed time from query to accepted moment, P50/P95 | product owner |
| compliant_reuse_rate | governed assets/moments reused across approved projects/channels / eligible assets | content operations |

All metrics bind corpus/query-set, sample size, period, model/index version,
permission scope, failure treatment and owner. Vendor benchmark or confidence
cannot replace project gold evidence.

## AI Context Sources

| Context | Source | Freshness | Permission / reliability rule |
|---|---|---|---|
| descriptive/editorial metadata | approved catalog or source editorial system | versioned/event-driven | AI suggestions remain separate until confirmed |
| technical metadata | deterministic file probe plus QA | per rendition | retain tool/version; parse failure is visible |
| transcript/timed text | source captions or ASR cue set | per rendition/version | distinguish source, human and model text; preserve time base |
| OCR/visual/audio annotations | enrichment services and reviewers | model/versioned | keep modality, time/space target, confidence and review state |
| identity/entity registry | accountable domain master data | event-driven | face/voice similarity cannot create binding identity automatically |
| rights/consent | contract, rights and consent systems | event-driven and expiry-aware | evaluate before exposure/use; withdrawal propagates |
| provenance/credentials | ingest ledger, C2PA or other manifest | per event/asset | validation proves assertions/signatures, not semantic truth |
| business/industry facts | applicable domain pack/source system | stated SLA | media evidence supports but does not replace the business authority |
| feedback/gold cases | reviewed search and task evidence | versioned | production feedback requires approval before dataset inclusion |

## Content / Knowledge Assets

| Asset type | Minimum metadata | Quality / governance rule |
|---|---|---|
| original | source, acquisition, hash, format, owner, classification | immutable; never overwritten by a derivative |
| preservation master | parent, codec/container, significant properties, fixity, migration events | periodic readability/fixity verification |
| edit/access rendition | parent, transform, dimensions/bitrate, duration, intended use | reproducible transform and expiry |
| track/timed text | language, channel/type, time base, cue source/version | synchronized and independently reviewable |
| scene/shot/event segment | start/end/frame/region, boundary method, version | exact parent and no out-of-range target |
| transcript/OCR/annotation | creator/model, target, motivation, confidence, review state | machine-derived never masquerades as confirmed fact |
| entity/event/concept link | canonical ID, ontology/vocabulary version, evidence target | unresolved/ambiguous identity remains visible |
| rights/consent record | subject, grantor, purpose, action, territory/channel, term, evidence | missing right blocks only affected action/stage |
| provenance/credential | actor, action, input/output, signer, validation result | invalid/unknown state preserved; no truth overclaim |
| embedding/index | modality, model, segment policy, corpus/schema/version, build date | immutable version; rebuild and compare on material change |
| evidence package | claim, exact moment, source/provenance, rights decision, reviewer | replayable without leaking unrelated restricted content |

Recommended storage layers:

```text
immutable original/fixity -> governed renditions -> metadata catalog
-> timed lexical index + multimodal vector indexes + semantic graph
-> rights/provenance ledger -> hot access/cold preservation
```

An object store or vector database alone is not a media knowledge system.

## Core Workflows

| Workflow | Actors | Trigger | State change | Success result |
|---|---|---|---|---|
| source onboarding | archivist, system owner, rights owner | new source/batch/stream | source proposed -> approved/rejected | ownership, transfer, format, rights and failure contract are explicit |
| ingest and preservation | media ops, platform | file/stream arrives | received -> verified/governed | original hash, technical evidence, master/proxy and failure list exist |
| segmentation/enrichment | AI engineer, reviewer | governed rendition | generated -> reviewed/confirmed | versioned segments and annotations retain exact targets |
| catalog/ontology mapping | media librarian, domain expert | new/changed annotations | proposed -> published/superseded | controlled concepts and evidence links remain resolvable |
| index build/rebuild | search owner, platform | corpus/model/schema/policy change | building -> ready/stale/failed | index manifest and regression evidence exist |
| moment retrieval | end user, search service | text/image/audio/example query | query -> authorized result/empty/refused | exact playable moments include match reason and allowed actions |
| grounded media Q&A | end user, AI service, reviewer | evidence-seeking question | retrieve -> synthesize -> cite/review | material claims cite correct moments and surface gaps |
| clip/reuse/publish | editor, rights reviewer, publisher | selected moments | proposed -> rights_check -> approved/exported | derivative lineage, rights, labeling and audit remain linked |
| dataset use | data/AI owner, rights/privacy reviewer | media selected for training/eval | proposed -> authorized -> versioned/released | intended use, sample provenance, splits, withdrawal and consumers are traceable |
| rights withdrawal cascade | rights/privacy owner, platform | consent/license expires or is revoked | freeze -> discover -> remediate -> verify -> close | original and affected derivatives, previews, transcripts, keyframes, caches, embeddings, graph statements, exports and dataset uses are blocked, removed, retained with authority, or reauthorized |

Retrieval contract:

```text
query interpretation
-> actor/purpose permission pre-filter
-> metadata + lexical + multimodal vector + graph candidates
-> fusion/rerank + temporal boundary repair
-> rights/consent/sensitivity action gate
-> exact moment + matched modalities + reason + provenance + allowed actions
```

**Retrieval relevance is not authorization.** Lexical accuracy, vector
similarity or graph proximity cannot grant view, cite, download, clip, publish
or train permission.

## Role Path Patterns

| Role | Entry | Core actions | Forbidden actions | Exit |
|---|---|---|---|---|
| media librarian/archivist | inventory/catalog | identify, describe, organize, preserve, correct | infer legal rights from possession | governed asset/catalog evidence |
| content producer/editor | search/project workspace | find moments, create draft clips, request rights | publish or train outside allowed purpose | approved derivative or documented denial |
| business/domain user | search/knowledge app | query, replay evidence, cite, report error | treat model label as binding fact | accepted moment/answer or escalation |
| rights/privacy reviewer | review queue | inspect contract/consent/purpose/action/term, approve/restrict/revoke | approve without evidence or affected-use analysis | auditable rights decision |
| domain expert | annotation/evidence review | confirm entity/event/claim meaning | override source-system authority silently | confirmed/rejected annotation |
| AI/search engineer | pipeline/index/eval | configure segmentation/models, build index, run gold/adversarial eval | promote vendor benchmark as project proof | versioned candidate/rollback |
| platform operations | job/incident console | monitor, retry, freeze, rebuild, restore | hide partial failures or stale index | restored/contained service |

## UI / Mobile Patterns

- Inventory surfaces show source, integrity, processing, rights, sensitivity,
  preservation and index readiness as separate states.
- Player timelines can overlay transcript cues, scenes, shots, entities, events,
  rights boundaries and evidence markers without flattening them into tags.
- Search results show thumbnail/preview, exact start/end, matched modalities,
  match reason, evidence/review state, rights/provenance state, allowed actions and
  index version.
- Clicking a result seeks to the exact moment; adjacent context is available only
  within permission scope.
- Human corrections use diff/reason/owner and do not erase the previous model or
  reviewer evidence.
- Long ingest, analysis, export and rebuild jobs expose progress, failed items,
  retry, cancel and resumable evidence.
- Rights withdrawal and delete views show the affected derivative/index/export/
  dataset graph before closure.
- High-risk identity, public publish, dataset release and irreversible deletion
  use a review surface with evidence, scope, expiry, impact and explicit approval.
- Product and review prototypes use stable `data-testid`, `data-action`,
  `data-state` and `data-field`; timed targets include stable asset/segment IDs.

## Policy / Privacy Constraints

- File possession, public availability or successful download does not prove the
  right to view, copy, transform, publish, train, identify or redistribute.
- Rights and consent decisions declare actor, subject, purpose, action,
  territory/channel, term, derivative/onward-use and accountable evidence.
- In China, face and other biometric data require purpose/necessity, applicable
  legal basis or separate consent, impact assessment, minimization, protection,
  retention and alternative-path analysis where required.
- AI-generated/synthesized media labeling is checked at generation, export,
  import/ingest and propagation; explicit and implicit marks and logs cannot be
  silently stripped.
- C2PA validity is not truth. It verifies signed provenance assertions and
  ingredient relationships; factual claims still need source and domain review.
- OCR, captions, transcripts and embedded metadata are untrusted inputs for an
  Agent; treat prompt-like text as content, apply permissions and prevent tool
  escalation.
- AI-derived annotations retain model/version/confidence and cannot overwrite
  authoritative human/source metadata without a reviewed change.
- Search permissions apply before candidate exposure and again before preview,
  answer, download, clip, publish or training action.
- Rights/consent revocation freezes new affected use immediately and starts a
  bounded, auditable impact workflow across all declared derivatives and indexes.
- High-impact enforcement, identity, safety or legal conclusions cannot rely on
  media-model output alone; retain original evidence, ambiguity and accountable
  human decision.

## Domain Test Scenarios

| Scenario | Role | Preconditions | Steps | Expected domain result |
|---|---|---|---|---|
| multimodal moment retrieval | user | authorized corpus and gold query | query a spoken phrase + visible action + OCR clue | ranked result seeks exact moment, lists matched modalities and index version |
| transcript-only blind spot | QA | silent visual event gold case | run transcript-only then fused retrieval | transcript-only miss is visible; fused path is evaluated, not assumed |
| unauthorized relevant hit | restricted user | semantically relevant restricted clip exists | search by text and reference image | no result, preview, metadata or answer leakage; denial is audited |
| expired clip right | editor | view allowed, publish expired | select moment and request export | preview may follow view policy; export/publish is blocked with reason and owner |
| rights withdrawal cascade | rights owner | source has proxy, transcript, keyframes, embeddings and exported clip | revoke grant | new use freezes; affected graph is remediated and closure evidence lists every outcome |
| face identity ambiguity | domain reviewer | model returns close matches | inspect and attempt writeback | identity remains unresolved; no binding person fact or action is created |
| timecode drift | QA | variable-frame-rate derivative differs from master | replay a cited moment in both | mapping error blocks evidence publication until repaired |
| stale index after correction | search owner | confirmed transcript/annotation changed | query before rebuild | stale status is visible; answer cannot cite superseded evidence silently |
| C2PA claim overreach | reviewer | credential validates | ask whether event is true | system states provenance result separately and requires factual evidence review |
| AI-label preservation | publisher | AI-generated derivative is approved | export then reingest | required explicit/implicit marks and derivative provenance are verified |
| media prompt injection | risk reviewer | OCR/transcript contains tool instruction | run media Q&A Agent | instruction is treated as source content; unauthorized tool use is blocked/audited |
| model/index upgrade | QA | new model or segment policy | rebuild and run gold/adversarial cases | old/new results remain reproducible; promotion follows thresholds or rolls back |

## Cross-Domain Requirement Patterns

- `PAT-VERSION-COMPATIBILITY-001`: file/rendition, metadata, segment,
  vocabulary/ontology, model, embedding, index and credential profiles bind
  outputs and preserve migration/rollback evidence.
- `PAT-LONG-RUNNING-JOB-001`: ingest, transcode, enrichment, backfill, index
  rebuild, export and withdrawal impact are observable, resumable, cancellable
  and idempotent.
- `PAT-METRIC-CALIBER-001`: media-processing, retrieval, citation, rights and
  value metrics declare corpus/query set, version, sample, window and owner.
- `PAT-FEDERATED-RECONCILIATION-001`: catalog, source repository, rights system,
  content credentials and business masters keep canonical ownership and
  reconciliation when attributes overlap.

## Evaluation Profile

Domain knowledge is not execution evidence. Register coverage and maturity in
`references/domain-coverage.yaml`; keep behavioral and expert evidence outside
this knowledge file.

Before raising maturity, independently evaluate:

- one ingest-to-search happy path with exact temporal evidence;
- one corrupt/unsupported/partial-processing exception path;
- one permission/rights/consent denial with no metadata or preview leak;
- one correction, index rebuild and rollback transition;
- one coding-agent no-guess handoff for Work/Asset/Rendition/Segment/Annotation;
- one rights withdrawal impact path across derivatives and indexes;
- one AI-label/provenance path and one prompt-injection or model-drift path;
- one real user task showing time/cost/quality change against a baseline.

Record executor, input corpus/query set, environment, model/index/schema
versions, timestamp, result, and evidence location. Deterministic fixtures prove
only contract anchors; vendor demos, mocked reviewers and simulated users do not
prove production suitability, expert correctness or customer acceptance.

## Acceptance Checklist

- [ ] Work, Asset, Rendition, Track, Segment, Annotation, Rights/Consent,
  Provenance, Index and Use objects have stable IDs and canonical owners.
- [ ] Original, preservation/edit/access renditions and derivatives are distinct;
  transforms and hashes are traceable.
- [ ] Temporal/spatial selectors, time base, frame rate and derivative mappings
  keep every important evidence citation replayable.
- [ ] Descriptive, technical, structural, administrative, rights, preservation
  and AI-derived metadata are separated and mapped to selected standards.
- [ ] AI annotations retain model/version/confidence/review state and never
  silently overwrite confirmed facts.
- [ ] Search combines only the necessary metadata, lexical, multimodal and graph
  paths, with project gold queries and exact-moment metrics.
- [ ] Result, preview, answer, cite, download, clip, publish and train permissions
  are separately enforceable and audited.
- [ ] Rights, consent, provenance and generated-content labeling are checked at
  ingest, retrieval/use, derivative export and propagation as applicable.
- [ ] Revocation/deletion impact covers declared derivatives, text, frames,
  caches, embeddings, graph statements, exports and datasets before closure.
- [ ] Model/index/segment/vocabulary changes trigger versioned rebuild,
  regression comparison, stale handling and rollback.
- [ ] Long jobs expose progress, failure, retry, cancel, idempotency and recovery.
- [ ] High-impact identity, enforcement, safety, legal and publication decisions
  keep accountable human authority and original evidence.
- [ ] `/ads`, `/dig`, `/prd` and `/proto` outputs preserve domain-specific
  unknowns, objects, flows, states, metrics, evidence and negative acceptance.
