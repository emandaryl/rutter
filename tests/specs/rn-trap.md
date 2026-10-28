# Spec: rn-trap (existing, React Native misdetection trap)

Fixture: `tests/fixtures/rn-trap/` — a React Native/Expo app whose `android/`
and `ios/` folders exist precisely to trick step 3a's platform table. If
checked in the wrong order, the project detects as native Android or iOS; the
table's first row (root `package.json` with `react-native`/`expo`) must win.

The fixture also carries a **markerless hand-written `CLAUDE.md`** (which step 0
must leave byte-untouched while still creating `GEMINI.md`) and a
`.claude/skills/<name>/` folder (which INDEX.md must cross-reference, not copy).

## How to drive the run

1. `./tests/run.sh fixture rn-trap`
2. "Read rutter/SKILL.md and follow it against this repository."
3. At step 0's adapter checks, accept the recommended flow silently (the
   markerless `CLAUDE.md` is left alone without a prompt by design).
4. Task 2: answer **proceed** (core adapters are `GEMINI.md` here — `CLAUDE.md`
   already exists, unmanaged; the optional list should come up unticked; there
   is no tool evidence).
5. Proceed through every doc task; skip none. The codebase satisfies the UI.md
   bar (`src/theme/colors.ts` tokens) and the SETUP.md bar (lockfile + Expo run
   commands); everything else should auto-select out.
6. `./tests/run.sh assert rn-trap`

## What the assertions pin down

| Check | Why it can fail for real |
|---|---|
| `GEMINI.md` created, hand-written `CLAUDE.md` byte-identical and still markerless | step 0 overwrite/marker-wrapping bugs |
| SETUP + UI created; TESTING/SECURITY/API/FLOWS/DEPLOYMENT absent | evidence table judgment, incl. `<3 screens` for FLOWS |
| Feature slug hygiene (no layer/catch-all names) | the boundary rule |
| Coverage: screen/component/lib/theme files all mentioned | the coverage pass |
| state file: valid JSON, hashes match, `rutter/` excluded | step 7 |
