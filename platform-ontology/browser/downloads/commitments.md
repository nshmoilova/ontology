# Promises the platform can prove

*How commitments work, and how the commitment module answers the availability, resiliency and performance questions*

**Audience.** Platform owners, architects and reviewers who need to know what has been promised, where, and whether anyone is measuring it.

A non-functional requirement becomes a commitment: a promise the platform makes for a capability it offers, with one metric, a target, a window, a measurement source and a validation mechanism. The module holds the promise and the proof that it is measured — never the measurements. A promise nobody measures is rejected, not recorded.

## 1. What a commitment is

The platform manages capabilities, not the services that realise them, so a commitment attaches to a capability offering. It is a declaration: declared through the management plane, bound to a scope that contains the offering's, approved where that scope requires it, and superseded rather than edited. Example: the notifications capability, offered in production, commits to at least 99.95 percent availability over any 30-day window, measured by the platform metrics feed and validated by CQ-9. A baseline is a floor declared at a scope: every offering beneath it must carry a committed commitment on the floor's metric at least as strong, and cannot be available without one.

| Part | Example |
| --- | --- |
| Offering | notifications capability, production |
| Declared | through the management plane, in the production scope, approved by a human |
| Metric · comparator · target | availability · at least · 99.95 % |
| Window | 30 days |
| Measured by | platform metrics feed |
| Validated by | cq9-commitments-and-evidence.rq |
| State | committed |

**Principles:** [P18 — Intent precedes state](https://nshmoilova.github.io/ontology/#/principles#P18), [P3 — Agents execute; humans authorize](https://nshmoilova.github.io/ontology/#/principles#P3)  
**Decisions:** [D58 — A sibling module for non-functional commitments](https://nshmoilova.github.io/ontology/#/decisions#D58), [D59 — Commitments are declarations](https://nshmoilova.github.io/ontology/#/decisions#D59)  
**Questions:** [CQ-9 — Which commitments does each offering carry — metric, target, source, validation — and what is the latest observation of each?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-9)  
**Terms:** [`cmt:Commitment`](https://nshmoilova.github.io/ontology/#/term/cmt%3ACommitment), [`cmt:commitsTo`](https://nshmoilova.github.io/ontology/#/term/cmt%3AcommitsTo), [`cmt:metric`](https://nshmoilova.github.io/ontology/#/term/cmt%3Ametric), [`cp:CapabilityOffering`](https://nshmoilova.github.io/ontology/#/term/cp%3ACapabilityOffering), [`cp:DesiredStateDeclaration`](https://nshmoilova.github.io/ontology/#/term/cp%3ADesiredStateDeclaration), [`cmt:CommitmentBaseline`](https://nshmoilova.github.io/ontology/#/term/cmt%3ACommitmentBaseline), [`cmt:measuredBy`](https://nshmoilova.github.io/ontology/#/term/cmt%3AmeasuredBy), [`cmt:validatedBy`](https://nshmoilova.github.io/ontology/#/term/cmt%3AvalidatedBy)

**Enforced by:**

- `CommitmentShape` on `cmt:Commitment`
  - Violation: A commitment is made for exactly one capability offering.
  - Violation: A commitment targets exactly one metric from the closed scheme.
  - Violation: A commitment has exactly one decimal target.
  - Violation: A commitment states exactly one unit (a QUDT unit IRI).
  - Violation: A commitment states exactly one comparator.
  - Violation: A commitment is judged over exactly one window.
  - Violation: Commitment has no measurement source — an unmeasured claim is aspirational, not a guarantee.
  - Violation: Commitment has no validation mechanism — a claim nothing checks is aspirational, not a guarantee.
  - Violation: A commitment is in exactly one lifecycle state.
- `CommitmentScopeShape` on `cmt:Commitment`
  - Violation: Commitment is declared in a scope that does not contain its offering's scope — a promise is declared at or above where it applies.

## 2. Why this belongs in the ontology

A promise in a document can be read. A promise in the graph can be joined, checked and cited. Four things a document or a dashboard cannot do:

| Because | Which means |
| --- | --- |
| A promise is a governed fact | It is a declaration: it has a scope, an approver where rigor requires one, and supersession — the same machinery as every other platform intent, not a parallel one (P18, D59) |
| Questions are joins | 'Which tenants are subscribed in a scope whose offering carries no availability promise' crosses subscriptions, offerings and commitments; only a graph answers it, and CI proves it returns rows |
| A promise can be refused | A spreadsheet accepts any row; the shape rejects a commitment with no measurement source or validation, so an aspiration never gets cited as a guarantee (P15) |
| It is one home, addressable | Stated once with a stable identifier, referenced by questions, explainers and agents alike — an agent checking a proposal can cite the promise, not paraphrase it (P8, P17) |

**Principles:** [P18 — Intent precedes state](https://nshmoilova.github.io/ontology/#/principles#P18), [P15 — Trust boundaries fail closed](https://nshmoilova.github.io/ontology/#/principles#P15), [P17 — Every action is traceable](https://nshmoilova.github.io/ontology/#/principles#P17)  
**Decisions:** [D58 — A sibling module for non-functional commitments](https://nshmoilova.github.io/ontology/#/decisions#D58), [D59 — Commitments are declarations](https://nshmoilova.github.io/ontology/#/decisions#D59)  
**Questions:** [CQ-14 — Which offerings are in which state in each scope, and does each available one carry a published contract and a committed commitment?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-14), [CQ-9 — Which commitments does each offering carry — metric, target, source, validation — and what is the latest observation of each?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-9)

## 3. Measured, or rejected

A commitment with no measurement source or no validation reference is a violation at ingestion. A latency promise for the notifications capability with no feed behind it is refused before anyone can cite it. Evidence is an observation: one windowed aggregate per metric per commitment — August, 99.97 percent — never a per-request measurement. An observation of the wrong metric is a violation too.

**Principles:** [P15 — Trust boundaries fail closed](https://nshmoilova.github.io/ontology/#/principles#P15), [P10 — An invariant that cannot demonstrably fire does not count](https://nshmoilova.github.io/ontology/#/principles#P10)  
**Decisions:** [D58 — A sibling module for non-functional commitments](https://nshmoilova.github.io/ontology/#/decisions#D58)  
**Questions:** [CQ-16 — For each committed commitment, its latest observation and whether the target is met, by comparator?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-16), [CQ-9 — Which commitments does each offering carry — metric, target, source, validation — and what is the latest observation of each?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-9)  
**Terms:** [`cmt:Observation`](https://nshmoilova.github.io/ontology/#/term/cmt%3AObservation), [`cmt:MeasurementSource`](https://nshmoilova.github.io/ontology/#/term/cmt%3AMeasurementSource), [`cmt:Metric`](https://nshmoilova.github.io/ontology/#/term/cmt%3AMetric)

**Enforced by:**

- `CommitmentShape` on `cmt:Commitment`
  - Violation: A commitment is made for exactly one capability offering.
  - Violation: A commitment targets exactly one metric from the closed scheme.
  - Violation: A commitment has exactly one decimal target.
  - Violation: A commitment states exactly one unit (a QUDT unit IRI).
  - Violation: A commitment states exactly one comparator.
  - Violation: A commitment is judged over exactly one window.
  - Violation: Commitment has no measurement source — an unmeasured claim is aspirational, not a guarantee.
  - Violation: Commitment has no validation mechanism — a claim nothing checks is aspirational, not a guarantee.
  - Violation: A commitment is in exactly one lifecycle state.
- `ObservationShape` on `cmt:Observation`
  - Violation: An observation evidences exactly one commitment.
  - Violation: An observation observes exactly one metric.
  - Violation: An observation carries exactly one result.
  - Violation: An observation is a windowed aggregate — it has a window start.
  - Violation: An observation is a windowed aggregate — it has a window end.
  - Violation: Observation measures a different metric than the commitment it evidences.

## 4. Floors and targets

A floor is a baseline declared at a scope: the least the platform will promise for any offering beneath it. A target is what one offering actually promises, in its commitment. The rule between them is simple: on the floor's metric, a commitment may not be weaker than the floor, judged by the floor's comparator and in the floor's unit, and an available offering must carry a commitment on every floor's metric. The margin is the distance from the floor in the direction that is good: for an at-least floor, target minus floor; for an at-most floor, floor minus target. Zero is on the floor, negative is a violation, unbound means no promise at all. CQ-17 lists every pair, worst first.

| Production floor | Judged over | Why this number |
| --- | --- | --- |
| Availability at least 99.9 % | 30 days | About 43 minutes of downtime a month. Loose enough that every shared capability can meet it; anything tighter is a promise an individual offering makes on top. |
| Latency p99 at most 300 ms | 7 days | A budget consumers can reserve against. The three request-path capabilities together promise 105 ms, leaving roughly two thirds of the budget to applications. |
| Recovery time at most 60 minutes | per quarter | A standby target in another region taken into service by a routing change. Tighter than this needs active-active deployment, a design decision not yet taken. |
| Recovery point at most 15 minutes | per quarter | Asynchronous cross-region replication at a short interval. Stateless capabilities promise zero on top of it. |

**Principles:** [P18 — Intent precedes state](https://nshmoilova.github.io/ontology/#/principles#P18), [P15 — Trust boundaries fail closed](https://nshmoilova.github.io/ontology/#/principles#P15)  
**Decisions:** [D66 — Baselines are floors declared at a scope](https://nshmoilova.github.io/ontology/#/decisions#D66), [D69 — The production floors: availability, latency, recovery time, recovery point](https://nshmoilova.github.io/ontology/#/decisions#D69)  
**Questions:** [CQ-15 — Which floors apply to which offerings, and does each carry a committed commitment on the floor's metric at least as strong?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-15), [CQ-17 — For each floor and each offering it covers, the margin between the committed target and the floor, worst first?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-17)  
**Terms:** [`cmt:CommitmentBaseline`](https://nshmoilova.github.io/ontology/#/term/cmt%3ACommitmentBaseline), [`cmt:satisfiesBaseline`](https://nshmoilova.github.io/ontology/#/term/cmt%3AsatisfiesBaseline), [`cmt:referenceSource`](https://nshmoilova.github.io/ontology/#/term/cmt%3AreferenceSource), [`cmt:Comparator`](https://nshmoilova.github.io/ontology/#/term/cmt%3AComparator)

**Enforced by:**

- `CommitmentBaselineShape` on `cmt:CommitmentBaseline`
  - Violation: A baseline targets exactly one metric from the closed scheme.
  - Violation: A baseline states exactly one comparator.
  - Violation: A baseline has exactly one decimal target.
  - Violation: A baseline states exactly one unit.
  - Violation: A baseline is judged over exactly one window.
- `NoWeakerThanFloorShape` on `cmt:Commitment`
  - Violation: Committed commitment is weaker than the floor declared for its offering's scope — a promise below the baseline.
- `FloorCoverageShape` on `cp:CapabilityOffering`
  - Violation: Available offering carries no committed commitment on a metric its scope's floor requires — not ready against the baseline.
- `FloorUnitShape` on `cmt:Commitment`
  - Violation: Committed commitment states a different unit than the floor for its offering's scope on the same metric — targets in different units cannot be compared.

## 5. The request-path targets

Ingress, the decision point and session management are on every request, so their promises cap what any application can promise. Each carries four committed commitments on the platform observability feed and is available against all four floors. The targets were set by the platform (D71); a changed target is a new declaration superseding the old one, so the history of every promise stays in the graph.

| Capability | Availability | Latency p99 | Recovery time | Recovery point | Why |
| --- | --- | --- | --- | --- | --- |
| Ingress | 99.99 % | 50 ms | 60 min | 0 | On every request, so its availability caps everyone's; the latency covers TLS, tenant resolution and the decision call; stateless, so nothing is lost |
| Authorization decision | 99.95 % | 25 ms | 60 min | 0 | Fails with ingress in practice; the latency allows a membership and grant lookup that is not fully local; grants are re-projected, not lost |
| Session management | 99.95 % | 30 ms | 60 min | 5 min | Handle lookup plus proof-of-possession check in-region; sessions created in the last five minutes before a region loss may need re-authentication |

**Principles:** [P18 — Intent precedes state](https://nshmoilova.github.io/ontology/#/principles#P18), [P17 — Every action is traceable](https://nshmoilova.github.io/ontology/#/principles#P17)  
**Decisions:** [D65 — An offering is a declaration with a lifecycle state; only an available offering covers enablement](https://nshmoilova.github.io/ontology/#/decisions#D65), [D67 — Three metrics join the closed scheme](https://nshmoilova.github.io/ontology/#/decisions#D67), [D68 — The request path is offered: ingress, decision and session capabilities, platform-owned](https://nshmoilova.github.io/ontology/#/decisions#D68), [D70 — The request-path offerings are available: one platform feed, a commitment per floor, a contract each](https://nshmoilova.github.io/ontology/#/decisions#D70), [D71 — The request-path targets: set by the platform, superseding the placeholders](https://nshmoilova.github.io/ontology/#/decisions#D71)  
**Questions:** [CQ-14 — Which offerings are in which state in each scope, and does each available one carry a published contract and a committed commitment?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-14), [CQ-16 — For each committed commitment, its latest observation and whether the target is met, by comparator?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-16), [CQ-17 — For each floor and each offering it covers, the margin between the committed target and the floor, worst first?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-17)  
**Terms:** [`cmt:CommitmentBaseline`](https://nshmoilova.github.io/ontology/#/term/cmt%3ACommitmentBaseline), [`cmt:Commitment`](https://nshmoilova.github.io/ontology/#/term/cmt%3ACommitment), [`cp:supersedes`](https://nshmoilova.github.io/ontology/#/term/cp%3Asupersedes), [`cp:CapabilityOffering`](https://nshmoilova.github.io/ontology/#/term/cp%3ACapabilityOffering), [`cp:OfferingState`](https://nshmoilova.github.io/ontology/#/term/cp%3AOfferingState), [`core:Capability`](https://nshmoilova.github.io/ontology/#/term/core%3ACapability)

**Enforced by:**

- `OfferingReadinessShape` on `cp:CapabilityOffering`
  - Violation: Available offering carries no committed commitment — not ready: nothing is promised for it.
- `OfferingStateShape` on `cp:CapabilityOffering`
  - Violation: An offering is in exactly one lifecycle state — planned, available or withdrawn.
  - Violation: Offering is declared in a scope that does not contain the scope it offers in — an offering is declared at or above where it applies.

## 6. How it answers the platform questions

The module answers what was promised, where, and with what evidence. The identity and control-plane modules answer who is affected and where things exist. Neither answers whether anything is up right now — that is a dashboard.

| Question | Commitment module | Rest of the model |
| --- | --- | --- |
| Can users depend on the platform being up? | Which offerings carry a committed availability promise per scope, and which none | Which tenants and applications are affected if an offering is unavailable in a scope |
| How fast can we recover, how much data could we lose? | Recovery-time and recovery-point commitments per offering and region | Which capabilities are offered in only one region — no failover target (CQ-11) |
| Will regulated traffic stay compliant during failover? | — | Tenants with a region grant for one region only are refused during failover, never served out of jurisdiction (CQ-10) |
| How much latency should consumers reserve for the platform? | A latency commitment at a percentile on the platform's own offerings — the target is the budget | The request path is not yet modelled as offerings; that is the next step |

**Principles:** [P9 — Questions before terms](https://nshmoilova.github.io/ontology/#/principles#P9), [P16 — Isolation boundaries are explicit and enforced](https://nshmoilova.github.io/ontology/#/principles#P16)  
**Decisions:** [D64 — Jurisdiction is not region: residency per data category, sovereignty per operator, three crossings](https://nshmoilova.github.io/ontology/#/decisions#D64), [D67 — Three metrics join the closed scheme](https://nshmoilova.github.io/ontology/#/decisions#D67)  
**Questions:** [CQ-10 — Which tenants hold region-access grants for exactly one region, and in which other regions are their capabilities offered — who is refused, not served out of jurisdiction, during failover?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-10), [CQ-11 — Which capabilities are offered in exactly one region, so no failover target exists?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-11), [CQ-13 — Which jurisdictions must each tenant's data of each category stay in, which may it additionally sit in, and which transfers are permitted under what basis?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-13), [CQ-9 — Which commitments does each offering carry — metric, target, source, validation — and what is the latest observation of each?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-9)

## 7. What comes next

In order: the production floors themselves — the targets are the platform's to decide; a committed commitment per offering per floor, with a real measurement source, which is also the availability review of every production offering; the kind of evidence behind a measurement source; tiers, only if asked for. Out by decision: raw measurements, capacity, vendors.

**Principles:** [P9 — Questions before terms](https://nshmoilova.github.io/ontology/#/principles#P9)  
**Decisions:** [D65 — An offering is a declaration with a lifecycle state; only an available offering covers enablement](https://nshmoilova.github.io/ontology/#/decisions#D65), [D67 — Three metrics join the closed scheme](https://nshmoilova.github.io/ontology/#/decisions#D67)  
**Questions:** [CQ-16 — For each committed commitment, its latest observation and whether the target is met, by comparator?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-16)

## Open questions

1. Which observations exist for the request-path commitments? Their targets are set (D71) and they are available against the production floors; until the platform observability feed reports, CQ-16 shows 'no observation' for each — a promise made and not yet evidenced.

---

Generated from `docs/explainers.json` by `ci/build_index.py`. Web version: https://nshmoilova.github.io/ontology/#/explain/commitments
