#!/usr/bin/env python3
"""Build the ontology browser's search index from the repository sources.

Everything the browser shows is derived here — modules, terms, vocabularies,
SHACL constraints, the relationship graph, competency questions, and the
design decisions behind each term. Nothing in the app is hand-maintained,
so the browser cannot drift from the ontology.

Run from the repository root:  python3 ci/build_index.py
Writes: browser/data/index.json
"""
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, RDF, RDFS, OWL, Literal, URIRef
from rdflib.namespace import SKOS, DCTERMS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "browser" / "data" / "index.json"

BASE = "https://w3id.org/examplebank/platform/"
SH = "http://www.w3.org/ns/shacl#"
VS = URIRef("http://www.w3.org/2003/06/sw-vocab-status/ns#term_status")

MODULE_ORDER = ["core", "authn", "session", "ingress", "authz", "control-plane", "commitment"]
MODULE_PREFIX = {"control-plane": "cp", "commitment": "cmt"}
MODULE_BLURB = {
    "core": "Upper module: principals, tenancy, capabilities, applications, "
            "authorized parties, delivery channels and the XACML roles.",
    "authn": "Credentials, identity providers, assurance levels, authentication "
             "journeys and issuer-scoped subject identifiers.",
    "session": "Sessions established by journey executions, step-up elevations, "
               "and tokens carrying both ends of their journey.",
    "ingress": "Network entry: gateways, listeners, routes, TLS termination and "
               "upstream services — deliberately implementation-independent.",
    "authz": "ABAC-first authorization plus the platform-owned coarse-grained "
             "layer: dimensions, grants, actions and admission decisions.",
    "control-plane": "Two-tier planes, the scope tree, and the chain from "
                     "subscriptions and offerings to declarations and mutations.",
    "commitment": "Non-functional commitments on offerings — metric, target, window, measurement source, validation — and the windowed observations that evidence them. A sibling module; nothing imports it.",
}


def module_of(iri: str):
    """Map a term IRI to its module name, or None if foreign."""
    if not iri.startswith(BASE):
        return None
    rest = iri[len(BASE):]
    name = rest.split("#")[0].split("/")[0]
    return name if name in MODULE_ORDER else None


def local_name(iri: str) -> str:
    return iri.split("#")[-1].split("/")[-1]


def curie(iri: str) -> str:
    mod = module_of(iri)
    if mod:
        prefix = MODULE_PREFIX.get(mod, mod)
        return f"{prefix}:{local_name(iri)}"
    for ns, pfx in (
        (str(SKOS), "skos"), (str(RDFS), "rdfs"), (str(OWL), "owl"),
        (str(DCTERMS), "dct"), ("http://www.w3.org/ns/prov#", "prov"), ("http://www.w3.org/ns/sosa/", "sosa"), ("http://qudt.org/vocab/unit/", "unit"), ("http://qudt.org/schema/qudt/", "qudt"),
        ("http://www.w3.org/2001/XMLSchema#", "xsd"), (SH, "sh"),
    ):
        if iri.startswith(ns):
            return f"{pfx}:{local_name(iri)}"
    return iri


def lit(g, subj, pred):
    v = g.value(subj, pred)
    return str(v) if v is not None else None


def lits(g, subj, pred):
    return sorted(str(o) for o in g.objects(subj, pred))


def load_ontology() -> Graph:
    g = Graph()
    for f in sorted((ROOT / "ontology").glob("*.ttl")):
        g.parse(f, format="turtle")
    return g


def load_shapes() -> Graph:
    g = Graph()
    for f in sorted((ROOT / "shapes").glob("*.ttl")):
        g.parse(f, format="turtle")
    return g


def collect_modules(g: Graph):
    mods = []
    for s in g.subjects(RDF.type, OWL.Ontology):
        iri = str(s)
        name = iri[len(BASE):].strip("/") if iri.startswith(BASE) else iri
        if name not in MODULE_ORDER:
            continue
        mods.append({
            "name": name,
            "iri": iri,
            "prefix": MODULE_PREFIX.get(name, name),
            "title": lit(g, s, DCTERMS.title) or name,
            "version": lit(g, s, OWL.versionInfo) or "",
            "description": lit(g, s, DCTERMS.description) or "",
            "blurb": MODULE_BLURB.get(name, ""),
            "imports": sorted(
                m for m in (module_of(str(o)) for o in g.objects(s, OWL.imports)) if m
            ),
        })
    mods.sort(key=lambda m: MODULE_ORDER.index(m["name"]))
    return mods


def collect_terms(g: Graph):
    """Classes and properties, with their annotations and hierarchy."""
    terms = {}
    kinds = [
        (OWL.Class, "class"),
        (OWL.ObjectProperty, "objectProperty"),
        (OWL.DatatypeProperty, "datatypeProperty"),
    ]
    for rdf_type, kind in kinds:
        for s in g.subjects(RDF.type, rdf_type):
            iri = str(s)
            mod = module_of(iri)
            if mod is None:
                continue
            terms[iri] = {
                "iri": iri,
                "name": local_name(iri),
                "curie": curie(iri),
                "kind": kind,
                "module": mod,
                "label": lit(g, s, SKOS.prefLabel),
                "definition": lit(g, s, SKOS.definition),
                "editorialNote": lit(g, s, SKOS.editorialNote),
                "altLabels": lits(g, s, SKOS.altLabel),
                "conformsTo": sorted(str(o) for o in g.objects(s, DCTERMS.conformsTo)),
                "status": lit(g, s, VS) or "draft",
                "subClassOf": [
                    curie(str(o)) for o in g.objects(s, RDFS.subClassOf)
                    if isinstance(o, URIRef)
                ],
                "subPropertyOf": [
                    curie(str(o)) for o in g.objects(s, RDFS.subPropertyOf)
                    if isinstance(o, URIRef)
                ],
                "disjointWith": [
                    curie(str(o)) for o in g.objects(s, OWL.disjointWith)
                    if isinstance(o, URIRef)
                ],
                "subClasses": [],
                "shapes": [],
                "constraints": [],
                "outgoing": [],
                "incoming": [],
                "usedBy": [],
                "vocabulary": [],
                "decisions": [],
                "principles": [],
            }
    # invert the class hierarchy
    by_curie = {t["curie"]: t for t in terms.values()}
    for t in terms.values():
        for parent in t["subClassOf"]:
            if parent in by_curie:
                by_curie[parent]["subClasses"].append(t["curie"])
    for t in terms.values():
        t["subClasses"].sort()
    return terms


def collect_vocabularies(g: Graph, terms):
    """SKOS concept schemes and their members, attached to their class."""
    schemes = []
    for s in g.subjects(RDF.type, SKOS.ConceptScheme):
        members = []
        for m in g.subjects(SKOS.inScheme, s):
            member_types = [
                str(o) for o in g.objects(m, RDF.type) if str(o) != str(SKOS.Concept)
            ]
            members.append({
                "iri": str(m),
                "curie": curie(str(m)),
                "label": lit(g, m, SKOS.prefLabel) or local_name(str(m)),
                "notation": lit(g, m, SKOS.notation),
                "definition": lit(g, m, SKOS.definition),
                "note": lit(g, m, SKOS.editorialNote),
                "rank": lit(g, m, URIRef(BASE + "authn#assuranceRank")),
                "types": [curie(t) for t in member_types],
            })
        members.sort(key=lambda x: (x["rank"] or "", x["label"]))
        scheme = {
            "iri": str(s),
            "curie": curie(str(s)),
            "title": lit(g, s, DCTERMS.title) or local_name(str(s)),
            "note": lit(g, s, SKOS.editorialNote),
            "module": module_of(str(s)),
            "members": members,
        }
        schemes.append(scheme)
        # attach members to the class they instantiate
        for m in members:
            for tc in m["types"]:
                for t in terms.values():
                    if t["curie"] == tc:
                        t["vocabulary"].append(m)
    schemes.sort(key=lambda s: (MODULE_ORDER.index(s["module"]) if s["module"] else 99, s["title"]))
    return schemes


def _constraint_from_property_shape(g: Graph, ps):
    """Read one sh:property blank node into a plain dict."""
    def v(p):
        o = g.value(ps, URIRef(SH + p))
        if o is None:
            return None
        return str(o) if not isinstance(o, Literal) else o.toPython()

    in_list = []
    in_node = g.value(ps, URIRef(SH + "in"))
    if in_node is not None:
        from rdflib.collection import Collection
        in_list = [str(x) for x in Collection(g, in_node)]

    path = g.value(ps, URIRef(SH + "path"))
    return {
        "kind": "property",
        "path": curie(str(path)) if path is not None else None,
        "pathIri": str(path) if path is not None else None,
        "minCount": v("minCount"),
        "maxCount": v("maxCount"),
        "class": curie(v("class")) if v("class") else None,
        "classIri": v("class"),
        "datatype": curie(v("datatype")) if v("datatype") else None,
        "in": in_list,
        "minInclusive": v("minInclusive"),
        "maxInclusive": v("maxInclusive"),
        "severity": local_name(v("severity") or "") or "Violation",
        "message": v("message"),
    }


def collect_shapes(g_shapes: Graph, terms):
    """Node shapes with their property and SPARQL constraints."""
    shapes = []
    for s in g_shapes.subjects(RDF.type, URIRef(SH + "NodeShape")):
        target = g_shapes.value(s, URIRef(SH + "targetClass"))
        target_iri = str(target) if target is not None else None
        constraints = []
        for ps in g_shapes.objects(s, URIRef(SH + "property")):
            constraints.append(_constraint_from_property_shape(g_shapes, ps))
        for sp in g_shapes.objects(s, URIRef(SH + "sparql")):
            constraints.append({
                "kind": "sparql",
                "severity": local_name(str(g_shapes.value(sp, URIRef(SH + "severity")) or "")) or "Violation",
                "message": str(g_shapes.value(sp, URIRef(SH + "message")) or ""),
                "select": str(g_shapes.value(sp, URIRef(SH + "select")) or "").strip(),
            })
        shape = {
            "iri": str(s),
            "name": local_name(str(s)),
            "targetClass": curie(target_iri) if target_iri else None,
            "targetClassIri": target_iri,
            "module": module_of(target_iri) if target_iri else None,
            "constraints": constraints,
            "violations": sum(1 for c in constraints if c["severity"] == "Violation"),
            "warnings": sum(1 for c in constraints if c["severity"] == "Warning"),
        }
        shapes.append(shape)
        if target_iri and target_iri in terms:
            terms[target_iri]["shapes"].append(shape["name"])
            terms[target_iri]["constraints"].extend(constraints)
    shapes.sort(key=lambda s: (s["module"] or "zz", s["name"]))
    return shapes


def build_relationships(shapes, terms):
    """Typed edges, derived from SHACL: targetClass --path--> sh:class.

    The OWL deliberately carries no domain/range on shared properties, so
    SHACL is the only place typed relationships are actually stated.
    """
    edges = []
    seen = set()
    by_curie = {t["curie"]: t for t in terms.values()}
    for sh in shapes:
        src = sh["targetClass"]
        if not src:
            continue
        for c in sh["constraints"]:
            if c["kind"] != "property" or not c.get("class") or not c.get("path"):
                continue
            key = (src, c["path"], c["class"])
            if key in seen:
                continue
            seen.add(key)
            card = ""
            if c.get("minCount") is not None and c.get("maxCount") is not None:
                card = f"{c['minCount']}..{c['maxCount']}"
            elif c.get("minCount") is not None:
                card = f"{c['minCount']}..*"
            elif c.get("maxCount") is not None:
                card = f"0..{c['maxCount']}"
            edge = {
                "from": src, "property": c["path"], "to": c["class"],
                "cardinality": card, "severity": c["severity"],
            }
            edges.append(edge)
            if src in by_curie:
                by_curie[src]["outgoing"].append(edge)
            if c["class"] in by_curie:
                by_curie[c["class"]]["incoming"].append(edge)
            if c["path"] in by_curie:
                by_curie[c["path"]]["usedBy"].append(edge)
    edges.sort(key=lambda e: (e["from"], e["property"]))
    return edges


def load_decisions(terms):
    path = ROOT / "docs" / "decisions.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    decisions = data.get("decisions", [])
    by_name = defaultdict(list)
    for t in terms.values():
        by_name[t["name"]].append(t)
    for d in decisions:
        d.setdefault("invariant", False)
        d.setdefault("rejected", [])
        resolved = []
        for name in d.get("terms", []):
            for t in by_name.get(name, []):
                resolved.append(t["curie"])
                t["decisions"].append(d["id"])
        d["termCuries"] = sorted(set(resolved))
        missing = [n for n in d.get("terms", []) if n not in by_name]
        if missing:
            problem(f"{d['id']} references unknown terms: {', '.join(missing)}")
    return decisions


PROBLEMS: list[str] = []


def problem(msg: str) -> None:
    """A dangling reference is a failure, not a warning (P15 — fail closed)."""
    PROBLEMS.append(msg)
    print(f"  FAIL: {msg}")


STANDARD_MENTION = re.compile(r"RFC ?\d{4}|NIST SP ?800-63|XACML|AuthZEN|SPIFFE|DPoP|OpenID Connect|\bOIDC\b|\bOAuth\b|\bPROV-O\b", re.I)


def check_standards(terms, decisions):
    """P8: a definition that names a specification adopts it — the term must say so
    machine-readably (dct:conformsTo); a recorded deviation must name the standard
    and its justification."""
    for t in terms.values():
        if STANDARD_MENTION.search(t.get("definition") or "") and not t["conformsTo"]:
            problem(f"{t['curie']} names a specification in its definition but declares no dct:conformsTo")
    for d in decisions:
        dev = d.get("deviatesFrom")
        if dev is not None and not (dev.get("standard") and dev.get("justification")):
            problem(f"{d['id']} records a deviation without both 'standard' and 'justification'")
    standards = {}
    for t in terms.values():
        for u in t["conformsTo"]:
            standards.setdefault(u, []).append(t["curie"])
    return [{"url": u, "terms": sorted(v)} for u, v in sorted(standards.items())]


g_shared = None


def load_principles(terms, shapes, decisions):
    """The principles layer: stated once, joined to the terms they cover, the
    shapes that enforce them and the decisions that apply them."""
    path = ROOT / "docs" / "principles.json"
    if not path.exists():
        return [], []
    data = json.loads(path.read_text())
    principles = data.get("principles", [])
    by_name = defaultdict(list)
    for t in terms.values():
        by_name[t["name"]].append(t)
    known_shapes = {s["name"]: s for s in shapes}
    known_decisions = {d["id"]: d for d in decisions}
    for pr in principles:
        pr.setdefault("enforcedBy", []); pr.setdefault("appliedIn", []); pr.setdefault("terms", [])
        resolved = []
        for name in pr["terms"]:
            for t in by_name.get(name, []):
                resolved.append(t["curie"])
                if pr["id"] not in t["principles"]:
                    t["principles"].append(pr["id"])
        pr["termCuries"] = sorted(set(resolved))
        missing = [n for n in pr["terms"] if n not in by_name]
        if missing:
            problem(f"{pr['id']} references unknown terms: {', '.join(missing)}")
        bad = [s for s in pr["enforcedBy"] if s not in known_shapes]
        if bad:
            problem(f"{pr['id']} references unknown shapes: {', '.join(bad)}")
        for s in pr["enforcedBy"]:
            if s in known_shapes:
                known_shapes[s].setdefault("principles", []).append(pr["id"])
        bad = [d for d in pr["appliedIn"] if d not in known_decisions]
        if bad:
            problem(f"{pr['id']} references unknown decisions: {', '.join(bad)}")
        for did in pr["appliedIn"]:
            if did in known_decisions:
                ps = known_decisions[did].setdefault("principles", [])
                if pr["id"] not in ps:
                    ps.append(pr["id"])
    # a decision may also declare principles it applies that the principle did not list
    known_p = {pr["id"] for pr in principles}
    for d in decisions:
        bad = [x for x in d.get("principles", []) if x not in known_p]
        if bad:
            problem(f"{d['id']} applies unknown principles: {', '.join(bad)}")
    # scope, exceptions, motivation, collisions (grilling round, 2026-09-02)
    SCOPES = {"contract", "ci", "runtime-asserted", "review-time"}
    headings = set(re.findall(r"^### (.+?)(?: \(.*)?$", (ROOT / "docs" / "competency-questions.md").read_text(), re.M))
    motivated = {}
    for d in decisions:
        for x in d.get("motivatedBy", []):
            if x not in known_p:
                problem(f"{d['id']} is motivated by unknown principle {x}")
            motivated.setdefault(x, []).append(d["id"])
        r = d.get("resolves")
        if r is not None:
            ok = isinstance(r.get("between"), list) and len(r["between"]) == 2 and all(x in known_p for x in r["between"]) and r.get("yielded") in r["between"]
            if not ok:
                problem(f"{d['id']} records a collision resolution that is not two known principles plus which yielded")
    for pr in principles:
        sc = pr.get("scope")
        if not isinstance(sc, list) or not sc or not set(sc) <= SCOPES:
            problem(f"{pr['id']} has no valid scope (subset of {sorted(SCOPES)})")
        elif set(sc) <= {"runtime-asserted", "review-time"}:
            pr["weaklyHeld"] = True
            print(f"  note: {pr['id']} is held only by {', '.join(sc)} — fails criterion four for a new promotion")
        for ex in pr.get("exceptions", []):
            if not all(ex.get(k) for k in ("clause", "gap", "backlog", "owner", "since")):
                problem(f"{pr['id']} has an exception missing clause/gap/backlog/owner/since")
            elif ex["backlog"] not in headings:
                problem(f"{pr['id']} exception points at backlog section '{ex['backlog']}', which does not exist")
        pr["motivatedBy"] = motivated.get(pr["id"], [])
        pr["status"] = "confirmed" if pr["motivatedBy"] else "provisional"
    if dr_gate := [str(s) for s in set(g_shared.subjects(RDFS.domain, None)) | set(g_shared.subjects(RDFS.range, None))]:
        problem(f"P6: properties declare rdfs:domain/range — typing belongs in SHACL: {', '.join(sorted(dr_gate)[:5])}")
    print(f"  {sum(1 for p in principles if p['status']=='confirmed')} principles confirmed, "
          f"{sum(1 for p in principles if p['status']=='provisional')} provisional, "
          f"{sum(len(p.get('exceptions', [])) for p in principles)} open exception(s)")
    return principles, data.get("evaluatedNotPrinciples", [])


def load_explainers(terms, shapes):
    """Guided walkthroughs, with diagrams inlined and references verified."""
    path = ROOT / "docs" / "explainers.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    explainers = data.get("explainers", [])
    known_terms = {t["curie"] for t in terms.values()}
    known_shapes = {s["name"] for s in shapes}
    pfile = ROOT / "docs" / "principles.json"
    known_principles = {p["id"] for p in json.loads(pfile.read_text()).get("principles", [])} if pfile.exists() else set()
    for ex in explainers:
        for step in ex.get("steps", []):
            diagram = step.get("diagram")
            if diagram:
                svg = ROOT / "docs" / "diagrams" / diagram
                if svg.exists():
                    step["svg"] = svg.read_text().strip()
                else:
                    problem(f"{ex['id']} references missing diagram {diagram}")
                    step["svg"] = None
            for key, known, kind in (("terms", known_terms, "term"),
                                     ("shapes", known_shapes, "shape"),
                                     ("principles", known_principles, "principle")):
                missing = [x for x in step.get(key, []) if x not in known]
                if missing:
                    problem(f"{ex['id']} references unknown {kind}s: "
                          f"{', '.join(missing)}")
        ex["stepCount"] = len(ex.get("steps", []))
    return explainers


def load_competency_questions():
    """Formal CQs from the table + their SPARQL; backlog grouped by heading."""
    path = ROOT / "docs" / "competency-questions.md"
    formal, backlog = [], []
    if not path.exists():
        return formal, backlog
    text = path.read_text()
    for m in re.finditer(r"^\|\s*(CQ-\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|", text, re.M):
        cq_id, question, query, modules = (x.strip() for x in m.groups())
        query = query.strip("`")
        qpath = ROOT / "queries" / "competency" / query
        formal.append({
            "id": cq_id,
            "question": question,
            "query": query,
            "sparql": qpath.read_text().strip() if qpath.exists() else None,
            "modules": [x.strip() for x in modules.split(",")],
        })
    section = "General"
    in_backlog = False
    for line in text.splitlines():
        if line.startswith("## Backlog"):
            in_backlog = True
            continue
        if not in_backlog:
            continue
        if line.startswith("### "):
            section = line[4:].strip()
            continue
        if line.startswith("- "):
            backlog.append({"section": section, "question": line[2:].strip()})
        elif backlog and line.startswith("  ") and line.strip():
            backlog[-1]["question"] += " " + line.strip()
    for b in backlog:
        q = re.sub(r"\s+", " ", b["question"]).strip()
        b["expectedEmpty"] = "expected empty" in q.lower()
        # strip markdown emphasis, keeping the parenthetical note readable
        q = re.sub(r"\*+([^*]+)\*+", r"\1", q)
        mk = re.search(r"\s*\[realised: ([^\]]+)\]", q)
        b["realizedBy"] = [s.strip() for s in mk.group(1).split(",")] if mk else []
        if mk:
            q = q[:mk.start()] + q[mk.end():]
        b["question"] = re.sub(r"`([^`]+)`", r"\1", q).strip()
    return formal, backlog


def source_digest() -> str:
    """Stable digest over everything the index is derived from."""
    h = hashlib.sha256()
    for rel in ("ontology", "shapes", "queries/competency", "docs/diagrams"):
        for f in sorted((ROOT / rel).glob("*")):
            if f.is_file():
                h.update(f.name.encode())
                h.update(f.read_bytes())
    for rel in ("docs/decisions.json", "docs/principles.json", "docs/explainers.json",
                "docs/competency-questions.md"):
        f = ROOT / rel
        if f.exists():
            h.update(f.read_bytes())
    return h.hexdigest()[:12]


def stamp_asset_versions() -> str:
    """Content-hash app.js and styles.css into index.html.

    GitHub Pages serves everything with `max-age=600` and no revalidation,
    so without this a deploy is invisible to anyone who loaded the page in
    the previous ten minutes. A content hash in the query string makes each
    build a new URL, which no cache can serve staler than the build itself.
    """
    browser = ROOT / "browser"
    html_path = browser / "index.html"
    if not html_path.exists():
        return ""
    html = html_path.read_text()
    digests = []
    for asset in ("app.js", "styles.css"):
        path = browser / asset
        if not path.exists():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:10]
        digests.append(digest)
        # match the asset with or without an existing ?v= stamp
        html = re.sub(
            rf'(["\'])({re.escape(asset)})(\?v=[0-9a-f]+)?\1',
            rf'\g<1>{asset}?v={digest}\g<1>',
            html,
        )
    html_path.write_text(html)
    return hashlib.sha256("".join(digests).encode()).hexdigest()[:10]


def main() -> int:
    print("== Building ontology browser index ==")
    g = load_ontology()
    gs = load_shapes()
    print(f"  ontology triples: {len(g)}   shape triples: {len(gs)}")

    modules = collect_modules(g)
    terms = collect_terms(g)
    schemes = collect_vocabularies(g, terms)
    shapes = collect_shapes(gs, terms)
    edges = build_relationships(shapes, terms)
    decisions = load_decisions(terms)
    global g_shared
    g_shared = g
    standards = check_standards(terms, decisions)
    principles, not_principles = load_principles(terms, shapes, decisions)
    explainers = load_explainers(terms, shapes)
    formal, backlog = load_competency_questions()
    shape_names = {s["name"] for s in shapes}
    for bq in backlog:
        for s in bq["realizedBy"]:
            if s not in shape_names:
                problem(f"backlog question marked realised by unknown shape {s}: {bq['question'][:60]}")
    print(f"  {sum(1 for bq in backlog if bq['realizedBy'])} backlog questions realised by invariants, "
          f"{sum(1 for bq in backlog if not bq['realizedBy'])} open")

    term_list = sorted(
        terms.values(),
        key=lambda t: (MODULE_ORDER.index(t["module"]), t["kind"], t["name"]),
    )
    counts = defaultdict(int)
    for t in term_list:
        counts[t["kind"]] += 1

    index = {
        "generated": True,
        # Digest of the sources, not a wall-clock time: the build must be
        # reproducible or CI's staleness check would fail on every run.
        "sourceDigest": source_digest(),
        "stats": {
            "modules": len(modules),
            "classes": counts["class"],
            "objectProperties": counts["objectProperty"],
            "datatypeProperties": counts["datatypeProperty"],
            "shapes": len(shapes),
            "violations": sum(s["violations"] for s in shapes),
            "warnings": sum(s["warnings"] for s in shapes),
            "vocabularies": len(schemes),
            "relationships": len(edges),
            "decisions": len(decisions),
            "principles": len(principles),
            "standards": len(standards),
            "realisedBacklog": sum(1 for bq in backlog if bq["realizedBy"]),
            "provisionalPrinciples": sum(1 for p in principles if p.get("status") == "provisional"),
            "explainers": len(explainers),
            "formalCQs": len(formal),
            "backlogCQs": len(backlog),
        },
        "modules": modules,
        "terms": term_list,
        "vocabularies": schemes,
        "shapes": shapes,
        "relationships": edges,
        "decisions": decisions,
        "principles": principles,
        "standards": standards,
        "evaluatedNotPrinciples": not_principles,
        "explainers": explainers,
        "competencyQuestions": {"formal": formal, "backlog": backlog},
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if PROBLEMS:
        print(f"\nBUILD FAILED ({len(PROBLEMS)} unresolved reference(s)); index not written")
        return 1
    OUT.write_text(json.dumps(index, indent=1, sort_keys=False))
    stamp = stamp_asset_versions()
    if stamp:
        print(f"  stamped app.js / styles.css with content hashes ({stamp})")
    s = index["stats"]
    print(f"  {s['modules']} modules · {s['classes']} classes · "
          f"{s['objectProperties']}+{s['datatypeProperties']} properties")
    print(f"  {s['shapes']} shapes · {s['relationships']} relationships · "
          f"{s['decisions']} decisions · {s['principles']} principles · "
          f"{s['formalCQs']}+{s['backlogCQs']} questions")
    undocumented = [t["curie"] for t in term_list if not t["decisions"] and not t["principles"]]
    if undocumented:
        print(f"  note: {len(undocumented)} terms have no recorded decision "
              f"(shown as 'no recorded rationale' in the browser)")
    print(f"  {sum(len(x['terms']) for x in standards)} terms conform to {len(standards)} specifications")
    print(f"  wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
