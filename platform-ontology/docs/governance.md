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

**Levels** are defined by what a principle constrains, and the enforcement
mechanism follows: *platform* principles constrain the platform's behaviour
and are enforced by shapes over platform data; *modelling* principles
constrain the form of the ontology and are enforced by OWL axioms and build
checks; *method* principles constrain how this layer is worked and are
enforced by CI gates and review-time tests.

**Scope** records how a principle actually holds: `contract` (shapes),
`ci` (a build or validation gate), `runtime-asserted` (the runtime half is
claimed, not observable in the graph), `review-time` (a stated test only).
A principle whose scope is only runtime-asserted or review-time fails
criterion four and is not promoted; the build reports one that already
holds that way as weakly held.

**Status** is computed: a principle is *confirmed* once a decision records
it in `motivatedBy` — made because of the principle, not merely consistent
with it — and *provisional* until then. Archaeology (attributing earlier
decisions) is legitimate evidence for promotion; a forward decision is what
confirms.

**Exceptions** are structured: clause, gap, the backlog section that holds
the work, an owner role, and the date opened. The build fails on a pointer
to a section that does not exist. An exception is not a waiver; it is a
debt with an address.

**Collisions** between principles are not ordered in advance. A decision
that resolves one records `resolves: {between, yielded}` and cites both;
the recorded resolutions are the precedence that actually holds.

Candidates that fail are recorded under `evaluatedNotPrinciples` with the
reason, so the evaluation is not repeated; a demoted principle joins the
same list. Decisions promoted to principles keep their retired ids
(D38, D39, D40, D42 → P6, P7, P3, P8); ids are never reused (P11 retired).

Changes to `docs/principles.json` require review by the platform security
architecture group, as the authz and control-plane modules do: a principle
changes every future decision. `.github/CODEOWNERS` requests that review;
the file, not a repository setting, carries the rule.

State a principle in this file and reference it everywhere else. A principle
restated in a definition, a README and an explainer is three versions waiting
to disagree.

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
