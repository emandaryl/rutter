---
name: rutter
description: >
  Scaffold a new or existing project's AI-agent context system — a root AGENTS.md, thin per-tool
  adapters (CLAUDE.md, GEMINI.md, .cursor/rules/project.mdc, .github/copilot-instructions.md)
  that point back to it, plus .agent/docs/, .agent/features/, and .agent/skills/ — by actually
  reading the target repo (or, on an empty folder, running a short intake) and writing real,
  project-specific content, not by asking the user to fill in a template. Works task by task: each
  document is proposed before it's written, and the user can proceed, adjust, or skip at every
  step. Re-runs on an already-scaffolded repo update only the managed content it originally wrote
  (guarded by rutter:begin/end markers), leaving anything the user added outside those markers
  untouched. Use when the user wants to "set up AGENTS.md", "scaffold agent docs", "add a
  CLAUDE.md/GEMINI.md/Cursor rules/Copilot instructions adapter", "run Rutter on this repo",
  "re-run Rutter", or start a project that needs agent-facing documentation. Works for any stack —
  Android, iOS, React/React Native/Next.js, Flutter, or anything else via a generic fallback.
---

# Rutter

Generates a standard `AGENTS.md` + `.agent/docs/` + `.agent/features/` + `.agent/skills/`
documentation system, retargeted at whatever project this is run against, plus thin per-tool
adapter files that redirect tool-specific entry points (`CLAUDE.md`, `GEMINI.md`,
`.cursor/rules/project.mdc`, `.github/copilot-instructions.md`) back to `AGENTS.md`. This is
**not** a find-and-replace template engine — the skill reads the target repo's actual manifests,
source tree, and code (or, if there's no code yet, asks a short intake instead — see step 1), and
writes what it actually finds. Only the parts of `AGENTS.md` that are process rules (how the
feature/task-file/skill system works) are copied verbatim; everything else is authored fresh from
what's really in the repo. Adapters carry zero project-specific content by design — each is a 3-5
line pointer to `AGENTS.md`, so there is nothing in them that can ever drift out of sync.

**The user stays at the helm throughout.** Nothing is written speculatively: every document is
proposed — a short summary of exactly what it will say — *before* it's created, one task at a
time, and the user answers **proceed**, **adjust**, or **skip** at each one. See step 5.

**Managed markers make re-runs safe.** Every file Rutter generates — `AGENTS.md`, each adapter,
each `.agent/docs/` file — is wrapped in a pair of HTML-comment markers:

```
<!-- rutter:begin -->
...generated content...
<!-- rutter:end -->
```

On a later run against the same repo, only the content *between* those markers is ever replaced;
anything the user adds above the opening marker or below the closing one is permanently theirs and
is never read as a signal or touched. This applies only to the files above — `.agent/features/`
and `.agent/skills/` content is living, hand-maintained work by design and is never regenerated
wholesale (see step 6). See step 0 for exactly how a re-run is detected.

## When to use

- User asks to set up agent-facing docs, an `AGENTS.md`, or "the same doc system as \<other
  project\>" for a repo that doesn't have one yet.
- User is starting a brand-new project — even an empty folder — and wants agent context
  scaffolding in place from day one. Detection (step 1) is automatic: the user never has to say
  which mode applies.
- User wants to re-run Rutter after the project has changed (new dependencies, a stack migration,
  new conventions) to bring the doc set back up to date. This is a normal, non-destructive use —
  step 0 detects it automatically via the markers above and updates only what it originally wrote.
- Do **not** use this to edit an *existing, markerless* `AGENTS.md` in place — a hand-written file
  Rutter didn't generate. Tell the user and ask whether they want it fully regenerated (destructive)
  or want specific sections hand-edited instead. See step 0 for the distinction.

## Steps

### 0. Check for an existing setup

Before touching anything, check the target repo root for an existing `AGENTS.md`. Three outcomes:

- **Doesn't exist** — fresh run. Continue to step 1 normally.
- **Exists and contains the `<!-- rutter:begin -->` / `<!-- rutter:end -->` marker pair** —
  **re-run mode**. This is Rutter's own prior output. Don't stop or ask permission — continue to
  step 1 as normal; the task loop in step 5 will propose fresh content for each managed file and
  update only what's between its markers when approved. Content the user added outside the markers
  in any of these files is left exactly as-is, untouched by discovery, drafting, or writing.
- **Exists without the marker pair** — a hand-written `AGENTS.md` Rutter didn't generate (or the
  markers were deliberately removed). **Stop** — do not regenerate or overwrite it. Tell the user
  it already exists and ask whether they want it fully regenerated (destructive — confirm
  explicitly before proceeding, and note this replaces the whole file, not just a managed section)
  or want you to hand-edit specific sections instead. Only continue past this step automatically
  when no `AGENTS.md` exists yet or it already carries Rutter's own markers.

Apply the same three-way check independently to each adapter path (`CLAUDE.md`, `GEMINI.md`,
`.cursor/rules/project.mdc`, `.github/copilot-instructions.md`) and each file under `.agent/docs/`
— each is checked on its own, so a markerless hand-written `GEMINI.md` doesn't block updating a
Rutter-managed `CLAUDE.md`, and vice versa. A markerless adapter or doc file is left untouched with
no prompt (unlike `AGENTS.md`, these are low-stakes enough not to interrupt the run for) — note
what was left untouched, and why, in the final summary.

`.agent/features/` and `.agent/skills/` are never marker-wrapped and never regenerated wholesale —
check whether they already have real content (not just this skill's own scaffolding from a prior
partial run). If either has files, treat that content as existing work: never delete or overwrite a
file that already exists there — in step 6, only add files that are genuinely missing, and mention
what you left untouched in the final summary.

### 1. Detect mode: existing project or greenfield

Silent and automatic — never ask the user which mode applies. Check the target repo for real
signals of existing work: a dependency manifest that actually lists dependencies, source files
beyond a bare scaffold, more than a trivial git history. Two outcomes:

- **Existing mode** — there's a real codebase. Detection and discovery read it (step 3a) and every
  doc describes what's actually there.
- **Greenfield mode** — the folder is empty, or has nothing beyond a README/LICENSE/`.gitignore`.
  Discovery becomes a short intake conversation instead of a code scan (step 3b), and the docs
  describe the idea the user states, not code that doesn't exist yet.

If it's ambiguous (e.g. a scaffold with a manifest but no real dependencies yet), don't guess —
treat it as greenfield and let the intake questions confirm or correct it.

**State the detected mode in Task 1's proposal** (step 5) — "this looks like an existing X app" or
"this folder looks empty — I'll run a short intake" — so a wrong guess is corrected before a single
file exists, rather than discovered after docs are already written from the wrong premise.

### 2. Detect which agent-tool adapters to create

Adapters are thin pointer files at each tool's required path — `CLAUDE.md`, `GEMINI.md`,
`.cursor/rules/project.mdc`, `.github/copilot-instructions.md` — that redirect that tool's entry
point back to `AGENTS.md`. Create one only where there's real evidence that tool is actually in
use in this repo, with one exception:

| Adapter | Path | Evidence required |
|---|---|---|
| Claude Code | `CLAUDE.md` | Always — this skill itself runs inside Claude Code, which is evidence enough on its own. Still skipped if step 0 found an existing `CLAUDE.md`. |
| Gemini CLI | `GEMINI.md` | A `.gemini/` directory, or `gemini-cli`/`@google/gemini-cli` listed as a dependency in a manifest. |
| Cursor | `.cursor/rules/project.mdc` | A `.cursor/` directory already present (rules, settings, etc.). |
| GitHub Copilot | `.github/copilot-instructions.md` | An existing `.github/copilot-instructions.md`, or Copilot config in `.vscode/settings.json` (`github.copilot.*` keys). |

This decision is made automatically here, the same as step 4's conditional-docs table — it isn't
itself a checkpoint. If **none** of the three non-Claude-Code signals turn up anywhere in the repo
— including the normal case for a greenfield folder, which by definition has no tool fingerprints
yet — don't guess, and don't silently create zero either: flag this explicitly for Task 2 to ask
about (step 5). Silently creating zero adapters would defeat the "scaffold agent context from day
one" use case for a fresh project, so Task 2's proposal must include an explicit question — which
of Gemini/Cursor/Copilot, if any — rather than treating a plain "proceed" as an answer. The moment
at least one real signal is found anywhere, skip the question: only create adapters for the tools
with actual evidence (plus Claude Code, always), and Task 2 just proposes them normally like
everything else.

### 3. Discovery or intake

Which branch runs depends on the mode detected in step 1.

#### 3a. Existing mode — read the repo

First, detect the platform. Check the target repo root for, **in this order** (order matters — see
the React Native note below):

| Signal | Platform | Pack |
|---|---|---|
| `package.json` at repo root with `react-native` (or `expo`) in deps | React (React Native) | `templates/platform-packs/react.md` |
| `build.gradle(.kts)` + `AndroidManifest.xml` **at repo root** (not nested inside an `android/` subfolder that sits alongside a root `package.json`) | Android | `templates/platform-packs/android.md` |
| `*.xcodeproj` / `*.xcworkspace` / `Package.swift` / `Podfile` **at repo root** (not nested inside an `ios/` subfolder that sits alongside a root `package.json`) | iOS | `templates/platform-packs/ios.md` |
| `pubspec.yaml` with a `flutter` dependency | Flutter | `templates/platform-packs/flutter.md` |
| `package.json` with `react`/`next` in deps (no `react-native`) | React | `templates/platform-packs/react.md` |
| None of the above | — | `templates/platform-packs/generic.md` |

**Why the order matters:** a React Native project has its own `android/build.gradle` +
`AndroidManifest.xml` and `ios/*.xcodeproj` — the generated native shells RN itself creates. Those
would match the Android/iOS rows if checked first, misdetecting an RN project as a native Android
or iOS app. Checking root `package.json` for `react-native`/`expo` first avoids that. Once React
Native is detected, treat `android/` and `ios/` as generated build output, not separate platforms
to document — the `react.md` pack covers what to look for in each if anything there is genuinely
hand-maintained (e.g. native modules).

If multiple *genuine* platforms are present in different subdirectories (a real monorepo — e.g. a
Flutter app next to an unrelated Node backend, not an RN project's own generated shells), note each
subproject separately later in Package Structure rather than picking one platform for the whole
repo — you may load more than one pack.

Read the matched pack file now — it's a checklist of what to look for in that ecosystem and the
vocabulary to describe it with, not text to copy in. The actual content you write always comes
from what you find in the real repo.

Then actually read the target repo (Read/Grep/Glob — not a manifest-only skim), using the pack's
checklist as a guide:

- Manifests/lockfiles → Tech Stack table + Build config line.
- Top 2-3 levels of the primary source tree → Package Structure, annotated one line per folder.
- Entry points, state containers, how the UI layer subscribes to state → Architecture Pattern
  paragraph (and a short diagram if the layering is clear).
- Any DB/ORM found in dependencies → Data Layer Conventions (skip the section if none).
- Real singleton/manager/provider/client classes → Key Shared Utilities table, with roles read
  from what the class actually does, not guessed from its name.
- A house logging wrapper if one exists → Logging section (skip if the codebase just uses raw
  print/console/log calls with nothing wrapping them).
- Real observed conventions → Coding Conventions. Actively check for: an in-progress
  language/framework migration, a null-safety/defensive-access pattern at external boundaries, a
  preferred pattern for a recurring task type, a UI preview/story mandate already in use, an i18n/
  string-constants system, and — importantly — any shared utility from the Key Shared Utilities
  table that exists specifically to prevent duplicate implementations (a component library, a
  shared request-execution helper, a canonical constants module): each of those gets a matching
  "check before creating a new one" line here. If two similarly-shaped systems exist that do
  genuinely different things, add an explicit warning not to conflate them.
- Core model/entity/schema definitions → Domain Concepts, limited to the handful of nouns that
  show up everywhere, not an exhaustive glossary.
- README.md, if present and substantive → draft the "What \<ProjectName\> Is" paragraph from it.
- Any existing `.agent/features/` content (if the repo already has some) → seed the Task Files
  table and Feature Docs tree instead of leaving them empty. Don't invent features that don't
  exist.
- Any existing `.claude/skills/<name>/` folders (Claude Code's own skill format) → a cross-reference
  row in `.agent/skills/INDEX.md` pointing at `.claude/skills/<name>/SKILL.md`, per step 6 — not a
  copy of its content.

Everything found here is what gets *proposed* — not written — in Task 1 of the loop (step 5).

#### 3b. Greenfield mode — run a short intake

No code exists to scan, so ask instead. Keep it short — a handful of questions, not a
questionnaire; a five-minute passage doesn't survive a long interrogation:

1. **What are you building?** — one or two sentences: the product/tool and its core purpose.
2. **Who's it for?**
3. **Any stack or architecture preference** — or should that be left open (recorded as
   `TODO(you)`, for the user or a builder tool to decide later)?
4. *(optional)* Any known constraints worth recording now — compliance, a must-integrate-with-X,
   a timeline.

If the user names a concrete stack in question 3, load the matching platform pack from the table
in step 3a for vocabulary/formatting purposes, even though there's no code yet to check against
it. If they name more than one component (e.g. a React frontend plus a separate backend), load one
pack per named component, the same as the real-monorepo case in step 3a. Otherwise use
`templates/platform-packs/generic.md`.

If an answer is thin or the user doesn't have one yet, mark the corresponding slot `TODO(you)` in
the eventual doc rather than pressing for more — same rule as step 6.

From the answers, work out a small initial slice of features the idea implies (typically 1-4).
This isn't written yet — it's proposed as part of the features task in the loop (step 5). Never
invent feature scope beyond what the user actually described; if it's genuinely unclear how to
slice the idea into features, ask instead of guessing. A small idea can be one feature covering the
whole MVP.

### 4. Decide which conditional `.agent/docs/` files apply

`OVERVIEW.md` and `ARCHITECTURE.md` are always created. For each of the rest, create it only on
real evidence found in step 3 — never on platform alone. In greenfield mode, an intake answer
counts as evidence the same way a code finding does in existing mode (e.g. "it'll have user
accounts" is evidence for `SECURITY.md`); most rows will have no evidence yet and stay unselected,
and `ARCHITECTURE.md` describes the planned shape from the intake rather than an as-built one.

| Doc | Create when |
|---|---|
| `SETUP.md` | A real install/run path exists (lockfile, build scripts, env config template) |
| `TESTING.md` | A test suite/framework is present |
| `SECURITY.md` | Auth/session handling or sensitive-data handling is present (or stated in intake) |
| `DECISIONS.md` | Existing ADRs/changelog rationale to migrate in, a genuinely non-obvious choice actually found in the codebase worth recording now, or — greenfield only — a real choice Rutter itself made during intake because the user explicitly delegated it (e.g. "you decide the stack"); same evidence bar as the rest of this table otherwise, no exceptions |
| `UI.md` | A UI/design-system layer exists |
| `API.md` | A REST/GraphQL/RPC surface exists (or stated as planned in intake) |
| `FLOWS.md` | An end-user journey exists (apps — not pure libraries/CLIs/backends with no UI) |
| `DEPLOYMENT.md` | CI/CD or release config exists |

This decision is made automatically here; it isn't itself a checkpoint. What gets confirmed with
the user is each individual doc, one at a time, in the task loop below.

### 5. Run the task loop

From here on, nothing is written without a checkpoint immediately before it. Work through the
tasks in the table below **in order, one at a time**:

1. **Propose** — post a short (1-3 line) summary of exactly what this task will create or contain,
   grounded only in what step 3 (discovery or intake) already confirmed. Nothing is written yet.
   **On a re-run, Tasks 2 through N+2** (step 0 found the task's target file already carrying
   Rutter's markers) diff the freshly drafted content against what's currently between the markers
   and propose the *change*, not the whole document — "no changes to `ARCHITECTURE.md`" if nothing
   moved, or a short description of what's different (e.g. "Tech Stack: adding Redis, detected in
   `package.json`") if something did. A no-change task still goes through the same
   proceed/adjust/skip checkpoint — it's usually a one-word "proceed" from the user, not a rubber
   stamp skipped automatically. **Task 1 on a re-run** doesn't diff a file — it has none — instead
   its proposal leads with what's changed in the repo since the last run (new dependencies, new
   folders, a stack migration) rather than re-narrating everything as if seen for the first time;
   that's what makes the diffs in the tasks after it meaningful instead of redundant.
2. **Wait for the response.** The user answers one of:
   - **Proceed** — write exactly what was proposed, following the content and write rules in
     step 6.
   - **Adjust** — the user gives a correction or addition; fold it in, then write. No need to
     re-propose unless the adjustment changes what a *later* task will say (say so if it does).
   - **Skip** — write nothing for this task. Note it as skipped (and why, if given) in the final
     summary. Not offered on Tasks 1 or 2 — see the note below the table.
3. **Report** — "Done — created \<files\>." (or "Updated \<files\>." on a re-run, or "Skipped, per
   you.") — then immediately propose the next task. Don't wait to be asked.

| Task | Proposes |
|---|---|
| 1. Discovery / Intake | The detected mode (step 1) plus its findings: existing → detected stack, layout, commands to confirm or correct; greenfield → the intake questions (step 3b). This task's answers become the grounding for every task after it. |
| 2. `AGENTS.md` + adapters | A two-line summary of what `AGENTS.md` will document, and which adapters (step 2) will be created alongside it. Written together since adapters are trivial pointers with no unique content of their own. If step 2 found zero non-Claude-Code signals, this proposal also asks explicitly which of Gemini/Cursor/Copilot to include, if any — a plain "proceed" isn't an answer to that part. |
| 3…N. One task per selected `.agent/docs/` file | In this fixed order: `OVERVIEW.md`, `ARCHITECTURE.md`, then any of `SETUP/TESTING/SECURITY/DECISIONS/UI/API/FLOWS/DEPLOYMENT.md` selected in step 4. Each proposal is a two-line summary of what that specific doc will say — not the whole set at once. |
| N+1. `.agent/features/` scaffold | Existing: which pre-existing features (if any, found in step 3a) will be seeded into the index, or confirmation it starts empty. Greenfield: the initial feature slice(s) worked out in step 3b — name each in one line. |
| N+2. `.agent/skills/` scaffold | Confirms `INDEX.md` will be created (header row only, unless step 3a turned up something worth seeding). |
| Final. Verification | Not a proceed/adjust/skip checkpoint — a report. First reconciles `AGENTS.md`'s provisional tables against what Tasks 2…N+2 actually produced (step 7), then summarizes everything created, updated, and skipped. |

Skip is a first-class answer at every task from 3…N onward. It isn't offered on Tasks 1 or 2:
Task 1 doesn't write anything — it's confirming the facts every later task is grounded in, so
there's nothing to skip, only proceed or adjust — and Task 2 creates `AGENTS.md`, the file every
doc task's proposal and every adapter points back to. Skipping it would leave the rest of the run
with no coherent anchor. If the user genuinely doesn't want `AGENTS.md`, that's a reason to stop
the whole run at Task 2, not a reason to keep going without it.

A skipped doc, feature scaffold, or skills scaffold (Tasks 3…N+2) is simply omitted — never
substituted with a guess, and never silently retried later in the same run. Individual adapters
don't get their own Skip either — they're bundled into Task 2 and excluded via step 2's automatic
evidence check or an Adjust response there ("skip Gemini, I don't use it"), not via a separate
Skip on a non-existent adapter task.

### 6. Content and write rules (apply during Execute)

These are the rules for *what* to write once a task in step 5 is approved (proceed or adjust) —
not a separate phase, just how "write exactly what was proposed" is carried out for each task.

**Drafting `AGENTS.md`:** start from `templates/AGENTS.template.md`. Sections marked `[STANDARD]`
in that file are copied verbatim with only the project name substituted — do not shorten, reword,
or make them conditional. Every `[FILL: ...]` marker gets replaced with real content confirmed in
step 3 (adjusted per any Task 1 corrections).

Three parts of `AGENTS.md` describe files that Tasks 3…N+2 haven't been confirmed yet when Task 2
runs — the App-Wide Docs pointer table/tree, the Task Files table, and the Feature Docs tree. Draft
all three at Task 2 from step 4's selections and step 3's findings as a **provisional best guess**
— never link to a file step 4 didn't select, but accept that a doc selected here may still be
skipped later. Don't treat this draft as final: the Final task (step 7) reconciles all three
against what was actually created and corrects `AGENTS.md` in place before reporting, so a skip in
Task 5 or Task N+1 never leaves a dangling link.

**Flagging gaps:** if the product one-liner can't be drafted from a README or intake answer, or a
`[FILL: ...]` slot has no real findings to report, replace it with a single
`TODO(you): <what's missing>` line. Never leave a `[FILL: ...]` token in the written file, and
never invent content to fill a gap.

**Writing files:** per step 0, never overwrite a markerless file that already exists in the target
repo — only create what's genuinely missing or update what's genuinely marker-managed, and only
for tasks the user approved.

- `AGENTS.md` at the target repo root — Task 2. Fresh run: create it wrapped in
  `<!-- rutter:begin -->` / `<!-- rutter:end -->` as its first and last lines (step 0 guaranteed
  none existed, or none without markers). Re-run: replace only the content between the existing
  markers with the freshly drafted version; leave anything outside them exactly as written.
- Each adapter selected in step 2, from `templates/ADAPTER.template.md` with `[FILL: ToolName]`
  substituted (`Claude Code`, `Gemini CLI`, `Cursor`, `GitHub Copilot`) — Task 2. Same marker rule
  as `AGENTS.md`: wrap on create, replace only between markers on a re-run, skip untouched if step 0
  found it markerless. `.cursor/rules/project.mdc` needs Cursor's MDC frontmatter prepended before
  the (markered) template body, or Cursor won't load it as an active rule:
  ```
  ---
  description: Project context pointer
  alwaysApply: true
  ---
  ```
- `.agent/docs/` — each doc from its template in `templates/docs/`, one per its own task — Tasks
  3…N. Same marker rule: wrap on create, replace only between markers on a re-run, skip untouched
  if markerless.
- `.agent/features/` — Task N+1. Never marker-wrapped; these are living, hand-maintained documents,
  not regenerated content (see why at the end of this bullet). Existing mode: created empty unless
  step 3a found existing features to seed.
  Greenfield mode: one `.agent/features/<slug>/` per feature worked out in step 3b, each with a
  `FEATURE.md` (per the "FEATURE.md Format" in `AGENTS.template.md`) and a `TASKS.md` (per the
  "TASKS.md Format" in the same file) seeded with a first phase of tasks inferred from the idea —
  no new template is needed for this, greenfield reuses the same formats existing-mode features use
  once they get a task file. On a re-run, never touch a feature folder that already exists — a
  feature's `FEATURE.md`/`TASKS.md` accumulate hand edits (Known Gotchas, task checkmarks) over
  time, which is exactly why they're excluded from the marker system.
- `.agent/skills/INDEX.md` — Task N+2, from `templates/SKILLS_INDEX.template.md`, scaffolded with
  just the header row unless step 3a turned up existing tool-agnostic skill content worth seeding
  (rare — don't go looking for it, only seed if it fell out naturally while reading the repo).
  Also never marker-wrapped, for the same living-document reason as `.agent/features/` — rows get
  added over time as real skills are created. If step 3a found an existing `.claude/skills/<name>/`
  (Claude Code's own skill format), add a row here pointing at
  `.claude/skills/<name>/SKILL.md` rather than duplicating its content into `.agent/skills/` —
  `.claude/skills/` is where Claude Code needs the real file to trigger it, so the index
  cross-references it instead of copying it, the same one-canonical-home rule the adapters use for
  `CLAUDE.md`/`GEMINI.md`. Delete the template's own scaffolding comment when writing the file,
  same as every other template. Don't create any `.agent/skills/<name>/` subfolder speculatively;
  those get added later per "Creating a Feature / Reference / Task / Skill" in `AGENTS.md`.

### 7. Final task: verification and summary

The last row of the task loop, run automatically once every other task has been proceeded, adjusted,
or skipped — no checkpoint of its own, just two automatic actions:

**First, reconcile `AGENTS.md`.** Its App-Wide Docs table/tree, Task Files table, and Feature Docs
tree were drafted provisionally at Task 2 (step 6), before Tasks 3…N+2 were resolved. Now that they
have been, re-check each entry against what actually exists on disk: drop any row/link for a doc,
feature, or skill that was ultimately skipped, and add any that a Task 1 adjustment or an Adjust
response elsewhere surfaced late. Apply this as a normal marker-scoped update — same mechanism as
a re-run (step 6) — replacing only the affected lines between `AGENTS.md`'s markers. This is what
keeps a run where, say, `SECURITY.md` got skipped at Task 5 from leaving `AGENTS.md` pointing at a
file that doesn't exist.

**Then report.** What was created or updated, every conditional doc that was skipped and why (e.g.
"no `API.md` — no route/schema definitions found"), every adapter that was skipped and why (no
evidence found, or the user opted out when asked in Task 2), any existing file left untouched per
step 0, and every `TODO(you):` left behind so nothing silently ships incomplete.

**On a re-run only:** also check whether any previously-created `.agent/docs/` file no longer
matches its evidence bar in step 4 (e.g. `TESTING.md` exists but the test suite it was based on is
gone). A doc in this state was never one of this run's Tasks 3…N — step 4 didn't select it — so the
reconcile step above already dropped its row from `AGENTS.md`'s pointer table along with any
genuinely-skipped doc. The file itself is different: never delete it automatically, only the link
to it. Flag it in the summary instead ("`TESTING.md` may be stale — no test suite detected this
run, and its `AGENTS.md` link was removed; delete the file by hand if that's correct") and let the
user decide.

## References

- `templates/AGENTS.template.md` — the root doc: standard sections verbatim, project-specific
  sections marked `[FILL: ...]`. Includes the `FEATURE.md`/`TASKS.md`/`SKILL.md` format specs used
  whenever a feature, task file, or skill gets added later — including during greenfield feature
  seeding in step 6, which reuses these same formats rather than a separate greenfield template.
- `templates/docs/*.template.md` — one stub template per `.agent/docs/` file (10 total; first two
  always used).
- `templates/platform-packs/{android,ios,react,flutter,generic}.md` — per-stack checklists of what
  to look for and how to describe it; not fill-in text.
- `templates/ADAPTER.template.md` — shared body for all four tool adapters; `[FILL: ToolName]`
  substituted per file.
- `templates/SKILLS_INDEX.template.md` — the `.agent/skills/INDEX.md` scaffold.
