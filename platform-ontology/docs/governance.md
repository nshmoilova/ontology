# Ontology Governance

## Versioning
- Semantic versioning per module, recorded in `owl:versionInfo` and `owl:versionIRI`.
- MAJOR: term removal or semantics change; MINOR: new terms; PATCH: annotations/docs.
- Terms are never deleted within a major version: mark `owl:deprecated true`,
  annotate the replacement with `dct:isReplacedBy`, and keep shapes tolerant of
  the deprecated form for one MINOR cycle.

## Term lifecycle
Every class/property carries `vs:term_status`: `draft` → `testing` → `stable`
→ `deprecated`. Promotion to `stable` requires: a competency question that
exercises the term, a SHACL shape governing its use, positive and negative
test instances, and steward sign-off.

## Definition style

A `skos:definition` states **what the term denotes** — enough that a reader
can correctly classify an instance — and nothing else. One or two sentences;
if it runs past about forty words it is almost certainly carrying content
that belongs elsewhere.

Everything else has a home, and duplicating it into the definition means the
browser shows the same argument twice on one page:

| Content | Belongs in |
|---|---|
| Why it is modelled this way; rejected alternatives | `docs/decisions.json` |
| What is enforced, and what violates | the shape's `sh:message` |
| Contrast with a sibling term | `owl:disjointWith`, plus `skos:editorialNote` if the reason matters |
| Examples | `skos:example` |
| Version history, migrations | the module's `dct:description` |
| Known gaps, open questions | `docs/competency-questions.md` |

A clause that constrains what can be an instance is definitional and stays,
even when it reads like rationale — "a business client is not itself
authenticable" is an example.

## Principles

`docs/principles.json` holds the rules the ontology obeys, each stated
exactly once. A **decision** picks among alternatives at one point; a
**principle** constrains every future pick. Decisions list the principles
they apply; shapes are listed by the principles they enforce; the browser
joins them so "which invariants realise this principle" is answerable.

A candidate is promoted only if it passes all four fitness criteria:

| Criterion | Meaning |
|---|---|
| Generative | It has produced more than one decision or invariant. A rule applied once is a decision. |
| Testable | It can be phrased as a question a new proposal is checked against. |
| A commitment, not a choice | It constrains all future selections rather than making one. |
| Enforced or enforceable | An invariant, build check or CI gate realises it, or it is a stated review-time test. |

Candidates that fail are recorded under `evaluatedNotPrinciples` with the
reason, so the evaluation is not repeated. Decisions promoted to principles
keep their retired ids (D38, D39, D40, D42 → P6, P7, P3, P8); ids are never
reused.

State a principle in this file and reference it everywhere else. A principle
restated in a definition, a README and an explainer is three versions waiting
to disagree — which is the observation that created this layer.

## Change control
- All changes via PR; CI (`ci/validate.py`) is a required check.
- Changes to `authz` and `control-plane` modules additionally require review
  by the platform security architecture group — these modules define what the
  firm's audit answers are built on.
- Every merged change to `stable` terms references a change ticket.

## Division of labour
- **OWL (TBox)** defines meaning and licenses inference. Keep `rdfs:domain`
  and `rdfs:range` off shared properties; typing is enforced in SHACL.
- **SHACL** is the data contract. `sh:Violation` = reject at ingestion;
  `sh:Warning` = admit but route to stewardship queue.
- **Profile**: OWL 2 QL is the target (virtual-graph/query-rewriting over
  relational IAM sources). CI should gain a ROBOT profile check before any
  reasoning-dependent consumer goes live.

## Identifier strategy
- Humans: firm directory identifier (`dir:...`) as `core:identifier`.
- Workloads: SPIFFE ID as `core:identifier`.
- Ontology terms: `https://w3id.org/examplebank/platform/<module>#Term`
  (swap in the firm's registered base IRI before first release).
