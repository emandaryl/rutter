# Spec: empty (greenfield)

Fixture: `tests/fixtures/empty/` — a folder with only an idea. Asserts the
greenfield path: intake becomes short, features get seeded with TASKS.md files,
everything conditional stays out for lack of evidence, and undecided facts are
marked `TODO(you)` rather than invented.

## How to drive the run

1. `./tests/run.sh fixture empty` — copies the fixture to `$TMPDIR/rutter-work/empty/`
   and drops `rutter/` in for the invoke sentence.
2. Point the agent at the copy: "Read rutter/SKILL.md and follow it against this repository."
3. Give exactly these intake answers (they keep the spec deterministic):
   - **What are you building?** "A command-line tool for tracking coffee-brew
     settings: beans, grind, ratio, time, tasting notes."
   - **Who is it for?** "Just me, on my laptop."
   - **Stack preference?** "Leave it open for now."  ← this is what makes the
     TODO(you) allowance load-bearing and DECISIONS.md evidence absent.
   - **Constraints?** "None yet."
4. Answer **proceed** (never *proceed all* — this spec wants the checkpoint
   behavior itself exercised) to Tasks 1, 2, then **skip nothing**, answer
   *proceed* for OVERVIEW and ARCHITECTURE, the feature scaffold, and the
   skills scaffold, then let the Final task run.
5. `./tests/run.sh assert empty`

## What the assertions pin down

| Check | Why it can fail for real |
|---|---|
| Adapters: exactly `CLAUDE.md` + `GEMINI.md` | greenfield with no tool fingerprints — Task 2 must not tick extras |
| Only OVERVIEW + ARCHITECTURE + the three guides | all eight conditional docs lack greenfield evidence with these intake answers |
| 1–4 seeded features, each with `TASKS.md` | greenfield features get task files by design |
| `TODO(you)` allowed anywhere | stack was deliberately left undecided — inventing it is the failure |
| state file valid + self-consistent | step 7 must parse-safe JSON, exclude `rutter/` |
