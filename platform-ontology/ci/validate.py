#!/usr/bin/env python3
"""CI validation for the platform ontology.

Gates:
  1. All Turtle files parse.
  2. Positive test data conforms to all SHACL shapes (warnings allowed,
     violations fail the build).
  3. Negative test data produces the expected violations — every
     constraint must demonstrably fire.
  4. Every competency question query executes and (where expected)
     returns rows against the positive dataset.

Run from the repository root:  python3 ci/validate.py
"""
import sys
from pathlib import Path

from rdflib import Graph
from pyshacl import validate

ROOT = Path(__file__).resolve().parent.parent
SH = "http://www.w3.org/ns/shacl#"

def load(dir_name: str) -> Graph:
    g = Graph()
    for f in sorted((ROOT / dir_name).glob("*.ttl")):
        g.parse(f, format="turtle")
        print(f"  parsed {f.relative_to(ROOT)}")
    return g

def run_shacl(data: Graph, shapes: Graph, ont: Graph):
    # Merge the TBox (class hierarchy, vocabulary individuals, assurance
    # ranks) into the data graph explicitly so sh:class checks and
    # SHACL-SPARQL constraints can see it, then apply RDFS inference.
    merged = Graph()
    for g in (ont, data):
        for t in g:
            merged.add(t)
    conforms, report_graph, report_text = validate(
        data_graph=merged,
        shacl_graph=shapes,
        inference="rdfs",
        advanced=True,
        allow_warnings=True,
    )
    return conforms, report_graph, report_text

def main() -> int:
    failures = 0

    print("== 1. Parsing ontology modules ==")
    ont = load("ontology")
    print("== Parsing shapes ==")
    shapes = load("shapes")

    print("\n== 2. Positive data must conform ==")
    pos = Graph().parse(ROOT / "data/test/positive.ttl", format="turtle")
    conforms, _, text = run_shacl(pos, shapes, ont)
    if conforms:
        print("  PASS: positive dataset conforms (no violations)")
    else:
        print("  FAIL: positive dataset has violations:\n" + text)
        failures += 1

    print("\n== 3. Negative data must trip expected constraints ==")
    neg = Graph().parse(ROOT / "data/test/negative.ttl", format="turtle")
    conforms, report, text = run_shacl(neg, shapes, ont)
    if conforms:
        print("  FAIL: negative dataset unexpectedly conforms")
        failures += 1
    else:
        messages = "\n".join(
            str(o) for o in report.objects(None, None) if "must" in str(o) or "—" in str(o)
        )
        expected_fragments = [
            "exactly one authentication journey execution",
            "must originate from a successful authentication",
            "exactly one policy enforcement point",
            "below the policy's required AAL",
            "agents execute, humans authorize",
            "authoritative issuer",
            "orphan write",
            "sole-writer invariant",
            "governance is separated from actuation",
            "self-governance loop",
            "outside the declaration's scope",
            "its scope requires human approval",
            "circular capability dependency",
            "exceeds its owner's active subscriptions",
            "derivation link to its governing source",
            "subscription activation lacks approval",
            "lacks an active subscription for its hard dependency",
            "hard dependency lacks a covering offering",
            "no offering covers",
            "issued to exactly one authorized party",
            "bound to exactly one delivery channel",
            "subject-identifier collision",
            "must evaluate exactly one action",
            "outside the platform-owned action vocabulary",
            "arrive via exactly one channel",
            "at least one entitlement grant",
            "fronted by a party owned by a different tenant",
            "application owned by another tenant",
            "not covered by any offering",
            "same domain and path to different tenants",
            "no route-binding declaration behind it",
            "binds a tenant but declares no hostname",
            "not sender-constrained",
            "resolve to exactly one session",
            "sender constraining must not be lost",
            "key confusion",
        ]
        for frag in expected_fragments:
            if frag in text:
                print(f"  PASS: fired -> ...{frag}...")
            else:
                print(f"  FAIL: expected violation did not fire -> {frag}")
                failures += 1

    print("\n== 4. Competency question suite ==")
    kb = Graph()
    for t in (ont, pos):
        for triple in t:
            kb.add(triple)
    expect_rows = {  # queries that must return >=1 row on seed data
        "cq2-routes-and-peps.rq", "cq3-policy-change-approvers.rq",
        "cq4-attribute-provenance.rq", "cq5-permits-with-assurance-chain.rq",
        "cq6-workload-principals.rq",
    }
    for qf in sorted((ROOT / "queries/competency").glob("*.rq")):
        try:
            rows = list(kb.query(qf.read_text()))
            n = len(rows)
            if qf.name in expect_rows and n == 0:
                print(f"  FAIL: {qf.name} returned 0 rows (expected >=1)")
                failures += 1
            else:
                print(f"  PASS: {qf.name} -> {n} row(s)")
        except Exception as e:
            print(f"  FAIL: {qf.name} did not execute: {e}")
            failures += 1

    print(f"\n{'BUILD FAILED' if failures else 'BUILD PASSED'} ({failures} failure(s))")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
