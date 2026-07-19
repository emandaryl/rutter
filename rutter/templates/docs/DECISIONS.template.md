# Decisions

<!-- Conditional — same evidence bar as every other conditional doc: only created because the repo
already has recorded decisions (existing ADRs, a CHANGELOG with rationale) to migrate in, because
the skill found a genuinely non-obvious choice in the codebase worth recording now, or — greenfield
only — because the skill itself made a real choice during intake that the user explicitly
delegated (e.g. "you decide the stack"). If none of those apply, don't create this file — an empty
log with no real entry isn't evidence, it's a placeholder, and this doc system doesn't ship
placeholders. Delete this comment when done. -->

A running log of non-obvious architectural or technical decisions — why something was built the
way it was, not just what was built. Add a new entry any time a decision is made that a future
agent (or teammate) would otherwise have to re-derive or might accidentally undo.

## Format

Each entry:

```markdown
## [FILL: short title] — [FILL: date]

**Decision:** [FILL: what was decided]

**Why:** [FILL: the reasoning — constraints, alternatives considered, tradeoffs accepted]

**Status:** [FILL: active | superseded by <link>]
```

---

[FILL: at least one real entry, following the format above — migrated from an existing
ADR/CHANGELOG rationale, a genuinely non-obvious existing choice found in the codebase during
setup (e.g. an unusual dependency choice, a deliberate deviation from a framework's default
pattern), or — greenfield only — a choice the skill itself made during intake because the user
explicitly delegated it (e.g. a stack pick), with the reasoning behind it. This file is only
created when at least one such entry exists — see the evidence bar in the comment above.]
