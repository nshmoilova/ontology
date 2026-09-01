# Platform Ontology — v0.x (pre-release)

Modular RDF/OWL ontology + SHACL constraints for a financial-services
application platform: **authentication (journeys, subject identifiers),
sessions, ingress, ABAC-first authorization (entitlements, actions,
admission), and a two-tier control plane (management vs. capability,
subscriptions, offerings, applications, portals)**.

Module versions: `core 0.2.0 · authn 0.2.0 · session 0.2.0 · authz 0.2.0 ·
ingress 0.1.0 · control-plane 0.3.0`. All terms are `vs:term_status "draft"`.
The design rationale lives in the Ontology Decision Register (shared
artifact); questions come before terms — see `docs/competency-questions.md`.

## Layout

```
ontology/          TBox modules (OWL 2 QL target), one file per domain
  core.ttl           principals, tenants, capabilities, applications,
                     authorized parties (azp), delivery channels, XACML roles
  authn.ttl          credentials, events, journeys, AALs, subject identifiers
  session.ttl        sessions (journey-established), tokens (aud + azp)
  ingress.ttl        gateways, listeners, routes (domain/path → tenant), upstreams
  authz.ttl          policies, attributes, entitlement grants, actions,
                     decisions incl. ingress admission (AuthZEN-aligned)
  control-plane.ttl  scope tree, declarations, subscriptions, offerings,
                     requirements, enablement, portals, mutations
shapes/            SHACL shapes graphs, mirroring the module structure
data/test/         positive.ttl (must conform) / negative.ttl (must fail)
queries/competency/  formalized competency questions (CQ-1..6) as SPARQL
browser/           the ontology browser app (GitHub Pages); data/index.json
                   is generated, never hand-edited
ci/                validate.py — parse, SHACL, negative-case, CQ gates
                   build_index.py — Turtle → the browser's search index
docs/              competency register (6 formal + large graded backlog),
                   decisions.json (the recorded "why"), governance policy
```

## Browsing it

The **ontology browser** publishes to GitHub Pages from `browser/`: search
across terms, constraints, decisions and questions; browse by module; and
read, on every term page, the recorded reasoning for why that term exists
and which alternatives were rejected. It is generated from the Turtle by
`ci/build_index.py`, and CI fails if the committed index is stale — so the
browser cannot drift from the ontology. See `browser/README.md`.

Module import chain: `control-plane → authz → authn → core`, with
`session → authn` and `ingress → core`. Cross-domain joins live in `core`.

## Design decisions baked in

1. **OWL for semantics, SHACL for contracts.** No `rdfs:domain`/`range` on
   shared properties; typing and cardinality live in shapes.
2. **States, levels, and vocabularies are individuals** in closed SKOS
   schemes: session/subscription states, outcomes, methods, AALs (ranked),
   entitlement dimensions, actions, channels, subject-identifier formats.
   Closed schemes make "platform-owned vocabulary" machine-checkable.
3. **Governance defines, enforcement checks.** The management control plane
   declares scoped, immutable, human-approved desired state; capability
   control planes actuate it (sole-writer); entitlement grants are machine-
   generated projections distributed to ingress — the token is evidence,
   the grant is authority.
4. **"Agents execute, humans authorize"** — policy changes, declarations in
   rigor-requiring scopes, and subscription activations all require a human
   approval; SHACL-enforced.
5. **Events are PROV activities** (`core:PlatformEvent ⊑ prov:Activity`).

## Validation

```bash
pip install -r ci/requirements.txt
python3 ci/validate.py
```

Four gates (also in `.github/workflows/validate.yml`): all Turtle parses;
positive data conforms; **29 named invariants demonstrably fire** on the
negative corpus (assurance chain, locality, sole-writer, enablement gate,
offering coverage, azp binding, subject-identifier collisions, action
vocabulary closure, portal coherence, …); all competency queries execute.

## Before first internal release

- Replace `w3id.org/examplebank` with the firm's registered base IRI.
- Add a ROBOT OWL 2 QL profile check and reasoner coherence gate to CI.
- Wire WIDOCO doc generation; publish per-module HTML docs.
- Close the remaining standards gaps (credential lifecycle + state-change
  events for CAEP, token lineage/revocation, amr/acr mappings).
- Security-architecture review is required for `authz`, `session`, and
  `control-plane` changes.
