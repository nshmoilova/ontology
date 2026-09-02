# Ontology Browser

A dependency-free single-page app for browsing and searching the platform
ontology: modules, terms, SHACL constraints, relationships, competency
questions, and the recorded reasoning behind every term.

Published to GitHub Pages by `.github/workflows/pages.yml` on every push to
`main`.

## The point of it

Everything here is **generated from the Turtle sources** by
`ci/build_index.py`, which writes `browser/data/index.json`. Nothing in the
app is hand-maintained, so the browser cannot drift from the ontology CI
validates. The `ontology-ci` workflow rebuilds the index and fails if the
committed copy is stale.

The distinctive part is **"Why this exists"** on every term page. Term
definitions say *what* something means; they cannot say why the model is
shaped that way, which alternatives were considered, or which ones were
rejected and for what reason. That lives in `docs/decisions.json`, keyed to
terms by local name, and the build joins the two.

## Editing

| To change… | Edit… |
|---|---|
| a term, its definition or annotations | `ontology/*.ttl` |
| a constraint or its message | `shapes/*.ttl` |
| the reasoning shown under "Why this exists" | `docs/decisions.json` |
| a principle, its test, or what enforces it | `docs/principles.json` |
| a guided explainer / walkthrough | `docs/explainers.json` |
| an explainer diagram | `docs/diagrams/*.svg` |
| competency questions | `docs/competency-questions.md` |
| the app itself | `browser/index.html`, `app.js`, `styles.css` |

After editing any source, regenerate the index:

```bash
python3 ci/build_index.py
```

Commit `browser/data/index.json` along with your change — CI enforces that it
matches the sources.

## Guided explainers

`docs/explainers.json` holds walkthroughs for working sessions: a topic
explained end to end, assembling prose, a diagram, live term links, the
SHACL messages quoted verbatim, and the open questions worth arguing about.

Each step may carry `heading`, `body` (blank-line-separated paragraphs), a
`diagram` (a filename in `docs/diagrams/`), a `table`, `terms` (CURIEs) and
`shapes` (shape names). Terms and shapes are resolved at build time and the
build warns about any that do not exist, so an explainer cannot quietly
reference a term that has been renamed.

Diagrams are inlined into the index rather than linked, so they inherit the
page's theme — author them with `currentColor` and the `--m-*` / `--accent`
CSS variables rather than literal hex.

## Running locally

The app fetches `data/index.json`, so it needs to be served over HTTP rather
than opened as a `file://` URL:

```bash
python3 -m http.server --directory browser 8000
```

Then open <http://localhost:8000>.

## Keyboard

- `/` or `⌘K` / `Ctrl+K` — focus search
- `↑` `↓` — move through results, `Enter` — open, `Esc` — dismiss

## Adding a decision

A term with no recorded rationale renders a note saying so — deliberately, to
make the gap visible rather than invisible. To close one, add an entry to
`docs/decisions.json`:

```json
{
  "id": "D42",
  "title": "Short claim, stated as a decision",
  "area": "Foundations",
  "invariant": false,
  "reasoning": "Why this is the way it is, including the trade-off accepted.",
  "terms": ["LocalTermName", "anotherTerm"],
  "rejected": ["The alternative, and the specific reason it lost."]
}
```

`terms` uses local names (not CURIEs); the build resolves them and warns
about any that do not exist.
