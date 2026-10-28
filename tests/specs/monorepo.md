# Spec: monorepo (existing, migration path)

Fixture: `tests/fixtures/monorepo/` — a web/ + api/ split (React + FastAPI)
with a **pre-existing, markerless, hand-written `AGENTS.md`**. Step 0 must stop
and offer four options; the driver picks **Migrate**. The assertions then check
the strongest guarantees Rutter makes: nothing from the old file is lost, the
original is kept intact as `AGENTS.old.md`, and the new docs stand on their own
(no leaning on the README for coverage).

## How to drive the run

1. `./tests/run.sh fixture monorepo`
2. "Read rutter/SKILL.md and follow it against this repository."
3. Step 0 will stop on the hand-written `AGENTS.md` — choose **Migrate** (the
   recommended first option).
4. Task 2: **proceed** (CLAUDE.md + GEMINI.md; nothing optional has evidence).
5. Proceed through every task; skip none. With both packs loaded, the
   conditional set should be: SETUP, TESTING, API, UI.
6. `./tests/run.sh assert monorepo`

## What the assertions pin down

| Check | Why it can fail for real |
|---|---|
| `AGENTS.old.md` exists and contains the original rules | Migrate must back up before replacing |
| Each of the four rule substrings appears in *generated* docs only | the "nothing may be dropped" ledger guarantee |
| Both layers documented (`web/`, `api/` in AGENTS.md) | the two-pack rule for mixed-language roots |
| SETUP/TESTING/API/UI present; SECURITY/FLOWS/DEPLOYMENT absent | evidence bars incl. no-auth and 2-screens |
| Coverage of significant files in *generated* docs | proof the feature docs were written from code |
| state file valid + consistent | step 7 |
