# Retrieval is not reasoning

*Why RAG hits a wall, and how ontologies, knowledge graphs, and context graphs let AI operate over meaning instead of text.*

**Audience.** Anyone building or governing systems that must reason reliably over enterprise documents, not just retrieve them.

A retrieval system gives an LLM relevant passages. A reasoning system gives it the enterprise's meaning. The gap between the two is where architecture becomes load-bearing: an ontology that fixes what terms denote, a knowledge graph that records facts in that grammar, and a context graph that assembles the neighborhood one question needs. This explainer walks the problem, the three-layer solution, and how the pieces work together.

## 1. Retrieval sounds like reasoning, and isn't

A language model can quote documents back faithfully. It can retrieve passages from thousands of files and cite them. Yet it can still draw a fundamentally wrong conclusion because the documents disagree on what their own terms mean, and nothing in the retrieval path resolves that ambiguity.

A simple case: suppose an LLM reads four sentences about "client", each true:

```
The client sends requests through the web application.
Client configuration belongs to the customer tenant.
The OAuth client is registered with the identity provider.
Client access is restricted by region.
```

Retrieval returns all four, correctly — they all discuss "client". But which client is meant in each sentence? Is access restricted by region for the web client, the OAuth client, or the business client? A retrieval system returns text chunks; it does not resolve what "client" denotes. The LLM has to guess, using statistical association from training data. Where the enterprise's documentation is internally inconsistent — and it usually is — that guess can be confidently wrong.

## 2. Shallow RAG: proximity without meaning

Traditional retrieval-augmented generation works by proximity: embed a question, search for nearby text chunks, hand those chunks to a language model. The fundamental unit is text, and text chunks sit near each other because of keyword overlap, not because they describe related semantic entities.

## 3. Three layers: ontology, graph, context

An ontology is not a glossary. It defines which kinds of things exist, which relations between them are legal, and which combinations are structurally impossible. Before any fact is written into a knowledge graph, the ontology closes off the interpretations that would lead to silent contradictions.

A knowledge graph is not a document store. It records facts as typed nodes and named edges: if the ontology says an Application can be owned by a Tenant, the graph records that specific applications own specific tenants, and the ontology prevents anything else from being asserted under the name "owns".

A context graph is neither of those. It is the slice of the graph one question needs, assembled on demand or in advance. It answers: which facts matter for this particular decision?

## 4. The example: typed concepts stop silent errors

Suppose an enterprise calls three unrelated things "client". The ontology names them separately: a device class (web, mobile, api); an OAuth client registration (the credentialed identity a session manager uses); and a business client (the customer a principal acts for, which cannot itself authenticate).

A graph built on those definitions cannot silently collapse them into one. An LLM reasoning over the graph cannot infer "a business client authenticated" because the ontology forbids it — not as a warning, but as a type error. A statement like "Client X obtained a token" resolves unambiguously: Client X must be an OAuth registration, because business clients cannot authenticate. That certainty is not an opinion; it is a structural fact of the ontology.

**Principles:** [P5 — An identifier resolves to an entity; it does not substitute for one](https://nshmoilova.github.io/ontology/#/principles#P5), [P6 — OWL for semantics, SHACL for contracts](https://nshmoilova.github.io/ontology/#/principles#P6)  
**Terms:** [`core:BusinessClient`](https://nshmoilova.github.io/ontology/#/term/core%3ABusinessClient), [`authn:OAuthClientRegistration`](https://nshmoilova.github.io/ontology/#/term/authn%3AOAuthClientRegistration), [`session:DeviceClass`](https://nshmoilova.github.io/ontology/#/term/session%3ADeviceClass)

## 5. Contradictions become a query, not an opinion

Once an ontology is fixed, checking whether two facts contradict each other stops being something an LLM reasons about in prose and becomes a yes-or-no query over the graph.

For example: "A capability depends on itself through a chain of other capabilities" is not a style issue or a code smell. It is a structural violation of a constraint the ontology defined in advance — a capability's dependencies must form a directed acyclic graph. The same applies to hundreds of other rules: a principal approving their own action, a data plane in a jurisdiction the residency permits nowhere, an entitlement dimension evaluated at the platform layer that the ontology reserved for applications alone.

None of these are patterns an LLM learned to recognize. Each is a violation of the grammar itself.

**Principles:** [P6 — OWL for semantics, SHACL for contracts](https://nshmoilova.github.io/ontology/#/principles#P6), [P10 — An invariant that cannot demonstrably fire does not count](https://nshmoilova.github.io/ontology/#/principles#P10)

## 6. Hybrid: vector search + graph search

This does not mean abandoning retrieval. Vector search answers one question well: "What documents discuss this topic?" Graph search answers a different question: "What entities and relationships are involved?" The two complement each other.

A complete reasoning system retrieves both evidence (via vector search) and structure (via graph traversal), assembles the context the question needs, and hands it to the language model for interpretation, planning, and explanation. The LLM is not the knowledge base — it is the reasoning and communication layer over a knowledge base that already enforces consistency.

**Principles:** [P13 — Decisions are policy-based and externalized](https://nshmoilova.github.io/ontology/#/principles#P13)

## 7. From one question to a reasoning platform

Enterprise AI maturity progresses through five levels:

**Level 1: LLM alone** — Powerful but probabilistic, with no grounding in organizational truth.

**Level 2: RAG** — Documents retrieved by proximity, giving some context but no semantic structure.

**Level 3: Graph RAG** — Entities and relationships are known, but the vocabulary is fluid or learned from data.

**Level 4: Ontology-driven Graph RAG** — Fixed vocabulary, fixed rules, deterministic validation at the semantic layer. The LLM reasons inside a constrained world.

**Level 5: Agentic reasoning** — The system plans queries, discovers entities, validates constraints, acts on decisions, and updates institutional memory continuously.

Moving through these levels is not about building a bigger model or retrieving more documents. It is about making the enterprise's meaning explicit and machine-checkable.

**Questions:** [CQ-7 — Does this subject's tenant have the right to enter this application through this platform-controlled endpoint and deployment scope?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-7)

## 8. Accuracy at each level

Concrete research on accuracy gains as you move through the maturity levels: Text-to-SQL with a language model alone achieves 16 percent baseline accuracy on complex database questions. Adding knowledge graph retrieval jumps to 54 percent. Adding ontology-governed reasoning — where the system validates answers against fixed semantic constraints — reaches 80 percent.

That progression is not about having a better model. At each level, the same underlying LLM is constrained differently. The model is more useful when it operates inside a semantic cage.

## 9. What to do now

Identify the decision that would create the most value if an AI agent could execute it reliably at scale. That decision is your starting point. Name the entities, relationships, and rules that govern it. This is your first ontology scope.

Build a pilot for that decision that stands on its own as a foundation you will extend. Connect it to GenAI for fluency and keep the knowledge graph in the loop for grounding and traceability.

Measure three things:

- Accuracy against authoritative sources.
- Provenance completeness: can you trace every answer to its origin?
- Cycle time improvement.

Engagement metrics tell you people are using the system. These metrics tell you whether they should trust it.

Design the pilot so the semantic foundation compounds. Every entity you encode creates relationship opportunities. Every rule you formalize becomes a constraint an agent can consult at runtime.

## 10. Further reading

- On this site: [The shape of institutional memory](https://nshmoilova.github.io/ontology/#/explain/institutional-memory), [Request path boundaries](https://nshmoilova.github.io/ontology/#/explain/evaluation-layers), [Competency questions](https://nshmoilova.github.io/ontology/#/questions).
- Patrick Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks, 2020. [Paper](https://arxiv.org/abs/2005.11401)
- Darren Edge et al., From Local to Global: A Graph RAG Approach to Query-Focused Summarization, Microsoft Research, 2024. [Paper](https://arxiv.org/abs/2404.16130)
- Frédéric Verhelst, The Ontology Imperative, Substack essays (accuracy progression from [Own the ontology, or rent your future](https://theontologyimperative.substack.com/p/own-the-ontology-or-rent-your-future)):
  - [Start here: The Ontology Imperative](https://theontologyimperative.substack.com/p/start-here-the-ontology-imperative)
  - [Own the ontology, or rent your future](https://theontologyimperative.substack.com/p/own-the-ontology-or-rent-your-future)
  - [Knowledge graph competitive landscape](https://theontologyimperative.substack.com/p/1a-knowledge-graph-competitive-landscape-ontology-imperative)
  - [The hidden governance crisis](https://theontologyimperative.substack.com/p/the-hidden-governance-crisis-what)
  - [The stakes and the false solutions](https://theontologyimperative.substack.com/p/the-stakes-and-the-false-solutions)
  - [The missing contract: Why most boards cannot govern what they cannot define](https://theontologyimperative.substack.com/p/the-missing-contract-why-most-boards)

## Open questions

1. At what scale does hand-authored vocabulary become unmaintainable, and how do you know when to switch to learned embeddings over fixed types?

---

Generated from `docs/explainers.json` by `ci/build_index.py`. Web version: https://nshmoilova.github.io/ontology/#/explain/retrieval-to-reasoning
