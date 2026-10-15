---
name: rutter
description: >
  Scaffold a project's AI-agent context system by reading the repo (or, if empty, a short intake): a root AGENTS.md, thin per-tool adapters (CLAUDE.md, GEMINI.md, Cursor, Copilot, Windsurf, Cline, Aider) pointing back to it, plus .agent/docs/, .agent/features/ and .agent/skills/. Works task by task: each document is proposed first and the user can proceed, adjust, or skip. Migrates existing hand-written docs without losing content. Re-runs update only content between rutter:begin/end markers. Use for "set up AGENTS.md", "scaffold agent docs", "add a CLAUDE.md/GEMINI.md/Cursor/Copilot adapter", "run Rutter" or "re-run Rutter". Works for any stack.
---

# Rutter

Generates a standard `AGENTS.md` + `.agent/docs/` + `.agent/features/` + `.agent/skills/`
documentation system, retargeted at whatever project this is run against, plus thin per-tool
adapter files that redirect tool-specific entry points (`CLAUDE.md`, `GEMINI.md`,
`.cursor/rules/project.mdc`, `.github/copilot-instructions.md`, `.windsurfrules`, `.clinerules`,
`.aider.conventions.md`) back to `AGENTS.md`. This is
**not** a find-and-replace template engine — the skill reads the target repo's actual manifests,
source tree, and code (or, if there's no code yet, asks a short intake instead — see step 1), and
writes what it actually finds. Only the parts of `AGENTS.md` that are process rules (how the
feature/task-file/skill system works) are copied verbatim; everything else is authored fresh from
what's really in the repo. Adapters carry zero project-specific content by design — each is a 3-5
line pointer to `AGENTS.md`, so there is nothing in them that can ever drift out of sync.

*(To audit an already-scaffolded repo for drift, broken markers, dead links, or budget bloat, see `rutter-doctor/SKILL.md`.)*

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
  markers were deliberately removed). **Stop** — do not overwrite it silently. Tell the user it
  already exists and offer four options, recommending the first:
  1. **Migrate (non-destructive, recommended)** — copy it to `AGENTS.old.md` (never delete it),
     treat its content as discovery input (see "Existing docs as input" in step 3a), then write a
     fresh marker-wrapped `AGENTS.md` that carries forward every rule, gotcha and convention it
     contained, restructured into Rutter's sections. Nothing may be dropped: anything that fits no
     section goes to a `.agent/docs/` file or the relevant `FEATURE.md`, and the Final report lists
     where each part of the old file went.
  2. **Regenerate** — rewrite the file from the template, carrying the old rules forward as in
     Migrate. Regenerate still copies the old file to `AGENTS.old.md` first; Rutter never discards
     a hand-written `AGENTS.md` without a backup. The difference from Migrate is only that the old
     file is replaced in place and its structure is not preserved.
  3. **Hand-edit** — leave the file as is and edit specific sections the user names.
  4. **Stop here** — end the run without writing anything. Always offer this; it is a valid
     answer, not an error. Report that nothing was changed.
  Only continue past this step automatically when no `AGENTS.md` exists yet or it already carries
  Rutter's own markers.

Apply the same three-way check independently to each adapter path (`CLAUDE.md`, `GEMINI.md`,
`.cursor/rules/project.mdc`, `.github/copilot-instructions.md`, `.windsurfrules`, `.clinerules`,
`.aider.conventions.md`) and each file under `.agent/docs/`
— each is checked on its own, so a markerless hand-written `GEMINI.md` doesn't block updating a
Rutter-managed `CLAUDE.md`, and vice versa. A markerless adapter or doc file is left untouched with
no prompt (unlike `AGENTS.md`, these are low-stakes enough not to interrupt the run for) — note
what was left untouched, and why, in the final summary.

**Match file and folder names case-insensitively** in every existence check above and below
(default macOS and Windows disks are case-insensitive anyway). An existing `.agent/docs/architecture.md`
*is* `ARCHITECTURE.md`: treat it as that doc's existing markerless file, so it is left untouched, and
never create a differently-cased twin. Wherever `AGENTS.md` links or lists that doc, use the file's
real on-disk name. List each such match in the Final report ("`architecture.md` covers
`ARCHITECTURE.md`"). An existing doc with no Rutter counterpart (a `prd.md`, a `conventions.md`) is
likewise left untouched; it is read as discovery input and may be listed in the `.agent/docs/` tree
with a one-line purpose.

`.agent/features/` and `.agent/skills/` are never marker-wrapped and never regenerated wholesale —
check whether they already have real content (not just this skill's own scaffolding from a prior
partial run). If either has files, treat that content as existing work: never delete or overwrite a
file that already exists there — in step 6, only add files that are genuinely missing, and mention
what you left untouched in the final summary.

### Ignore Rutter itself

When Rutter is dropped into the repo (e.g. `<repo>/rutter/`, `<repo>/rutter-doctor/`) it is a tool
being run *on* the project, not part of it. Throughout every step — mode detection, platform
detection, discovery, feature breakdown, Package Structure, Tech Stack, Key Shared Utilities, line
counts — **exclude** these paths: `rutter/`, `rutter-doctor/`, `rutter.zip`, `.claude/skills/rutter*`,
and any `AGENTS.old.md` backup this run created (read it for migration, but don't document it as
source). Never list them in the docs, never treat their `SKILL.md`/templates as project docs, and
never count their files as a signal that the project is "existing" or what language it uses. In the
Final report, if a drop-in `rutter/` folder is present in the repo root, remind the user it is safe
to delete or move out now that the run is finished — but never remove it yourself.

### 1. Detect mode: existing project or greenfield

Silent and automatic — never ask the user which mode applies. Check the target repo for real
signals of existing work: source files beyond a bare scaffold (entry points, multiple modules, a
test suite), a dependency manifest that actually lists dependencies, substantive hand-written docs,
git history. **No single signal is required** — a repo with no git history, or with no manifest
because it uses only a language's standard library, is still existing if its source tree is real.
Two outcomes:

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

Adapters are thin pointer files at each tool's required path that redirect that tool's entry point
back to `AGENTS.md`. Three groups:

**1. Core — always created** (cheap pointers, and these are the most common agent CLIs):

| Adapter | Path | Notes |
|---|---|---|
| Claude Code | `CLAUDE.md` | Claude Code does not read `AGENTS.md` on its own when a `CLAUDE.md` exists, so this pointer is required. |
| Gemini CLI + Antigravity | `GEMINI.md` | Gemini CLI reads `GEMINI.md`. Google Antigravity reads both `GEMINI.md` and `AGENTS.md`, with `GEMINI.md` taking precedence on conflict, so one `GEMINI.md` pointer covers both and stops it overriding `AGENTS.md` with stale rules. |

**2. Read `AGENTS.md` natively — no file is created.** Codex CLI (its primary config file),
Antigravity (v1.20.3+), and other tools that follow the AGENTS.md convention (e.g. OpenCode, Amp,
Zed) read the root `AGENTS.md` directly, so a pointer would only add a second file to maintain.
List these in Task 2's proposal and the Final report as "covered natively by `AGENTS.md`", so the
user can see Codex etc. were considered and not forgotten. Do not claim a tool reads `AGENTS.md`
unless it is named here or the user says so.

**3. Optional — created on evidence, or when the user picks them at Task 2:**

| Adapter | Path | Evidence that it is in use |
|---|---|---|
| Cursor | `.cursor/rules/project.mdc` | A `.cursor/` directory (rules, settings, etc.). |
| GitHub Copilot | `.github/copilot-instructions.md` | An existing `.github/copilot-instructions.md`, or `github.copilot.*` keys in `.vscode/settings.json`. |
| Windsurf | `.windsurfrules` | A `.windsurf/` or `.codeium/` directory. |
| Roo Code / Cline | `.clinerules` | An existing `.clinerules` file or `.roomodes` file. |
| Aider | `.aider.conventions.md` | An existing `.aider*` config or conventions file. |

Group 1 is decided automatically here (still skipped per file if step 0 found a markerless file of
that name). Group 3 is where the user decides: Task 2 **always** lists every group 3 adapter as an
explicit checklist — pre-ticked where evidence was found, unticked otherwise — and asks which to
include. A plain "proceed" means "group 1 plus the pre-ticked ones". This replaces silently
creating nothing for a fresh project, and also stops a repo with one tool's fingerprint from
quietly excluding the others the user may also use.

**Do not create `.agent/rules/`.** Antigravity treats that folder as workspace rules; Rutter's
`.agent/` only holds `docs/`, `features/` and `skills/`, so there is no collision, and keeping it that
way avoids Antigravity loading Rutter's docs as active rules.

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
| `pyproject.toml`, `uv.lock`, `poetry.lock`, `Pipfile`, `requirements.txt`, or `setup.py` at repo root | Python | `templates/platform-packs/python.md` |
| `go.mod` at repo root | Go | `templates/platform-packs/go.md` |
| `Cargo.toml` at repo root | Rust | `templates/platform-packs/rust.md` |
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
repo — you may load more than one pack. In this case, apply the signal table above to each
top-level subdirectory that looks like an independent project root (i.e. treat `<subdir>/` as if it
were repo root for matching purposes) — one level deep is enough for the common monorepo shape
(`web/`, `api/`, `apps/<name>/`, etc.); don't recurse further hunting for manifests nested deeper
than that.

**No manifest, or more than one language in the same root.** Some real projects have no manifest
for their main language (a standard-library-only Python or Go program, a shell-driven build) and
some mix languages in one root (e.g. a Python backend serving a TypeScript frontend, with only a
tooling `package.json`). Don't fall to `generic.md` just because the table's manifest file is
missing: detect the language from source files and entry points (`*.py` with a `__main__`/server
entry, `*.go`, `*.rs`, `*.ts`), and when two languages each have real source, load **both** packs
and describe each layer separately in Package Structure and Tech Stack. A `package.json` that only
lists build tooling (a compiler, a bundler) is a tooling note, not a framework signal. Record
"standard library only" as a Tech Stack fact when that's what the imports show, instead of leaving
the row empty. Also read non-manifest build/run files (shell scripts, Makefiles, CI configs) for the
Build config line and run/test commands.

Read the matched pack file now — it's a checklist of what to look for in that ecosystem and the
vocabulary to describe it with, not text to copy in. The actual content you write always comes
from what you find in the real repo.

Then actually read the target repo (open and read real source files directly, and search across
the codebase for patterns — not a manifest-only skim), using the pack's
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
- **Existing docs as input.** Read every substantive hand-written doc: `README.md`, `DESIGN.md`,
  `PLUGINS.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, `docs/`, ADRs, an existing `AGENTS.md`/
  `CLAUDE.md`. Their content is not discarded: build a short **migration ledger** (source file →
  where its content will live: a section of `AGENTS.md`, a `.agent/docs/` file, a feature's
  `FEATURE.md`/`references/`). Rules, gotchas and decisions recorded there are carried forward
  verbatim or lightly condensed, never dropped. The ledger is proposed in Task 1 and the originals
  are left in place (the user decides what to do with them; never delete them).
- **Feature breakdown (existing mode).** Identify the product's real features from the code, not
  from guesswork: directories or modules that own a distinct capability, plugin/route/screen
  groupings, and the headings in existing docs. Aim for features a maintainer would name in a
  sentence ("Read AGENTS, {feature} and fix X") — typically 3-10, each owning identifiable files.
  **Boundary rule:** a feature is one *capability* a maintainer would name ("services", "agents",
  "project discovery", "app shell"), not one technology layer. Never create features named for a
  layer or a catch-all (`core-backend`, `frontend`, `utils`, `misc`) — if a draft feature needs "and
  also" to describe it, split it by capability. Keep a capability's backend and frontend halves
  together in one feature (a Python route and the TypeScript screen that calls it are one
  feature). Do not merge code from the core app with code from a plugin/extension just because the
  UI shows them together (a core README tab and a plugin's file explorer are two features). Where
  the repo has a plugin/module/package folder per capability, that folder is one feature named
  after it (`plugins/logs/` → `plugin-logs`). Check each file you assign: it must belong to
  exactly one feature, and every significant source file should belong to some feature. Cross-cutting concerns (shell/layout, config) can be one feature. Propose the list with a one-line
  scope and owning files per feature in Task 1, for the user to confirm or adjust. Never invent a
  feature with no code behind it.
- Any existing `.agent/features/` content (if the repo already has some) → seed the Task Files
  table and Feature Docs tree instead of leaving them empty. Don't invent features that don't
  exist.
- **Existing format owners.** If the repo already has a skill or doc that is the canonical format
  for creating `FEATURE.md`, `TASKS.md` or skills (for example `.agent/skills/feature-docs-format/`,
  whose description says "use whenever you create or edit a TASKS.md or FEATURE.md"), record its path
  and which of the three formats it owns. Step 6 then skips the matching creation guide(s) and points
  `AGENTS.md` at the existing file instead, so each format has exactly one home. Report each one in
  Task 1 ("`feature-docs-format` already owns the TASKS.md and FEATURE.md formats; I'll point
  `AGENTS.md` at it and skip those two guides").
- Any existing `.claude/skills/<name>/` folders (Claude Code's own skill format) → a cross-reference
  row in `.agent/skills/INDEX.md` pointing at `.claude/skills/<name>/SKILL.md`, per step 6 — not a
  copy of its content.

**Depth before writing a feature doc.** A `FEATURE.md` describes code, so before writing one,
open the feature's owning source files (read the class, function and route definitions, not just
grep results or file listings) and write Architecture, Package Structure and Known Gotchas from
what you read there. Existing hand-written docs (e.g. `DESIGN.md`) supplement this; they do not
replace it. If a feature is too large to read in full, read its entry points and public surface and
record what you did not open in a short `> Needs verification:` line inside that `FEATURE.md`
instead of presenting grep-level detail as fact. A feature doc far thinner than the code behind it
(a handful of generic lines for a multi-file module) is a sign the code was not read.

**Coverage pass.** After drafting the feature list, list every significant source file (exclude
build output, vendored code, lockfiles, tests and Rutter itself) and confirm each one is named in
some feature's Package Structure or in `AGENTS.md`. Assign any leftover file (shared types, theme
or config modules, small helpers) to the feature that uses it most, or to the app-shell/config
feature, instead of leaving it undocumented. When one large file legitimately holds code for
several features (a route table, a main UI file), list it under each feature that uses it and add
a one-line note saying which functions or sections belong to that feature.

**Doc-versus-code check.** While reading the code, compare it with the claims in existing docs and
`AGENTS.old.md`. Where they disagree (a rule stricter than the code, a statement the code no longer
supports), document what the code actually does, keep the original rule's wording where it is a
deliberate rule, and list each disagreement in the Final report under "Docs that disagree with the
code", so the user can fix whichever side is wrong. Never silently pick one.

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

`OVERVIEW.md` and `ARCHITECTURE.md` are always created, and so are the three creation guides
(`FEATURE-CREATION.md`, `TASK-CREATION.md`, `SKILL-CREATION.md` — verbatim standard docs written in
Task 2, not selected here; a guide is skipped when step 3a found an existing owner of that format). For each of the rest, create it only on
real evidence found in step 3 — never on platform alone. In greenfield mode, an intake answer
counts as evidence the same way a code finding does in existing mode (e.g. "it'll have user
accounts" is evidence for `SECURITY.md`); most rows will have no evidence yet and stay unselected,
and `ARCHITECTURE.md` describes the planned shape from the intake rather than an as-built one.

| Doc | Create when |
|---|---|
| `SETUP.md` | A real install/run path exists (lockfile, build scripts, env config template) |
| `TESTING.md` | A test suite/framework is present |
| `SECURITY.md` | Auth/session handling or sensitive-data handling is present (or stated in intake) |
| `DECISIONS.md` | Existing ADRs/changelog rationale to migrate in (including decision or "why" text inside hand-written docs like `DESIGN.md`), a genuinely non-obvious choice actually found in the codebase worth recording now, or — greenfield only — a real choice Rutter itself made during intake because the user explicitly delegated it (e.g. "you decide the stack"); same evidence bar as the rest of this table otherwise, no exceptions |
| `UI.md` | A UI layer with its own styling conventions: a design system, a component library, or a shared theme (CSS variables, design tokens, a theming module) that new UI must follow. A theme file or stylesheet of variables counts even without a formal design system. |
| `API.md` | A REST/GraphQL/RPC surface exists (or stated as planned in intake) |
| `FLOWS.md` | An end-user UI with **three or more distinct screens, views or tabs** that a user moves between (apps — not pure libraries/CLIs/backends, and not a single-page tool). Fewer than three: fold the journey into `OVERVIEW.md` instead. Apply this test the same way every run. |
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
   stamp skipped automatically. **Task 1 on a re-run** (which should start by reading `.agent/.rutter-state.json`, see "Source
   fingerprint" in step 7, and listing exactly which source files were added, removed or changed
   since the last run — never conclude "nothing changed" from file times or from skimming)
   doesn't diff a file — it has none — instead
   its proposal leads with what's changed in the repo since the last run (new dependencies, new
   folders, a stack migration) rather than re-narrating everything as if seen for the first time;
   that's what makes the diffs in the tasks after it meaningful instead of redundant.
2. **Wait for the response.** The user answers one of:
   - **Proceed** — write exactly what was proposed, following the content and write rules in
     step 6.
   - **Adjust** — the user gives a correction or addition; fold it in, then write. No need to
     re-propose unless the adjustment changes what a *later* task will say (say so if it does).
   - **Proceed all** — the user may say this at any task: proceed with this and every remaining
     task using the proposals as drafted, still stopping for any task whose proposal contains an
     open question (e.g. Task 2's adapter question) and always producing the Final report.
   - **Skip** — write nothing for this task. Note it as skipped (and why, if given) in the final
     summary. Not offered on Tasks 1 or 2 — see the note below the table.
3. **Report** — "Done — created \<files\>." (or "Updated \<files\>." on a re-run, or "Skipped, per
   you.") — then immediately propose the next task. Don't wait to be asked.

| Task | Proposes |
|---|---|
| 1. Discovery / Intake | The detected mode (step 1) plus its findings: existing → detected stack, layout, commands to confirm or correct; greenfield → the intake questions (step 3b). This task's answers become the grounding for every task after it. |
| 2. `AGENTS.md` + adapters + creation guides | A two-line summary of what `AGENTS.md` will document, which adapters (step 2) will be created alongside it, and that the three standard creation guides (`FEATURE-CREATION.md`, `TASK-CREATION.md`, `SKILL-CREATION.md` in `.agent/docs/`) will be written verbatim from templates (minus any whose format an existing skill or doc already owns, per step 3a, which `AGENTS.md` will point at instead). Written together since adapters are trivial pointers and the guides are verbatim standard text — neither has unique content of its own. The proposal always (a) names the core adapters (`CLAUDE.md`, `GEMINI.md`), (b) states which tools are covered natively by `AGENTS.md` (Codex CLI, Antigravity, etc.), and (c) lists the optional adapters (Cursor/Copilot/Windsurf/Roo-Cline/Aider) as a checklist, pre-ticked where step 2 found evidence, and asks which to include — a plain "proceed" means core plus the pre-ticked ones. |
| 3…N. One task per selected `.agent/docs/` file | In this fixed order: `OVERVIEW.md`, `ARCHITECTURE.md`, then any of `SETUP/TESTING/SECURITY/DECISIONS/UI/API/FLOWS/DEPLOYMENT.md` selected in step 4. Each proposal is a two-line summary of what that specific doc will say — not the whole set at once. |
| N+1. `.agent/features/` scaffold | Existing: the confirmed feature breakdown from step 3a (and any pre-existing `.agent/features/` content) — one line per feature: slug, scope, owning files. Greenfield: the initial feature slice(s) worked out in step 3b — name each in one line. |
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

**Claim sweep (every re-run task for a doc or feature).** A doc can be wrong without any name or
file being missing. For each existing doc or feature this task covers, extract its **concrete
claims** — numbers and units (timeouts, limits, sizes, counts, ports), default values, flag and
environment-variable names, route paths, file paths, version requirements — and check each against
the code that owns it (open the source file; a grep that the name exists is not enough). Always do
this for every file the state-file diff lists as changed, and for the claims in the feature that owns
it; for unchanged files a sample is acceptable if stated. Report each mismatch in the task as the
old line, the new line and the evidence (file and line), and apply it only on approval. A task may
only report "no changes" if the sweep was done, and must say how many claims were checked.

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
  substituted (`Claude Code`, `Gemini CLI`, `Cursor`, `GitHub Copilot`, `Windsurf`, `Roo Code`,
  `Aider`) — Task 2. Same marker rule as `AGENTS.md`: wrap on create, replace only between markers on
  a re-run, skip untouched if step 0 found it markerless. `.cursor/rules/project.mdc` needs Cursor's
  MDC frontmatter prepended before the (markered) template body, or Cursor won't load it as an
  active rule:
  ```
  ---
  description: Project context pointer
  alwaysApply: true
  ---
  ```
- The three creation guides — `.agent/docs/FEATURE-CREATION.md`, `TASK-CREATION.md` and
  `SKILL-CREATION.md` — Task 2, from `templates/docs/FEATURE-CREATION.template.md`,
  `TASK-CREATION.template.md` and `SKILL-CREATION.template.md`. They are standard text: copy them
  verbatim with only the leading template comment removed; there is nothing to fill in. Same marker
  rule as every `.agent/docs/` file: wrap on create, replace only between markers on a re-run (so
  improvements to the standard reach existing repos), skip untouched if markerless. They are not
  selectable in step 4 and have no Skip of their own; drop one only if the user asks at Task 2.
  **Exception: an existing format owner (step 3a).** For each format that already has an owner, do
  not write that guide. In `AGENTS.md`, replace every `.agent/docs/<GUIDE>.md` reference for it (the
  pointer line, the "Creating a Feature / Reference / Task / Skill" table row and the App-Wide Docs
  tree line) with the owner's real path, and drop the guide's tree line. The owner's path is the only
  place the format lives. Never copy or edit the owner's content. If the owner's format visibly differs
  from the Rutter templates (other task-ID style, extra header lines), leave it as is; existing
  feature folders follow their own format.
- `.agent/docs/` — each doc from its template in `templates/docs/`, one per its own task — Tasks
  3…N. Same marker rule: wrap on create, replace only between markers on a re-run, skip untouched
  if markerless.
- `.agent/features/` — Task N+1. Never marker-wrapped; these are living, hand-maintained documents,
  not regenerated content (see why at the end of this bullet). Existing mode: one
  `.agent/features/<slug>/FEATURE.md` per feature confirmed in Task 1/N+1, written from the real code
  and the migrated doc content (Architecture in One Paragraph, Package Structure from actual files,
  Known Gotchas and Golden Rules carried over from existing docs and visible code constraints;
  long supporting material goes to `references/`). Do **not** create a `TASKS.md` for these unless
  the user names real open work or the repo has a TODO/roadmap to seed it from — a feature doc
  without a task file is normal. Do not touch feature folders that already exist.
  Greenfield mode: one `.agent/features/<slug>/` per feature worked out in step 3b, each with a
  `FEATURE.md` (per `templates/docs/FEATURE-CREATION.template.md`) and a `TASKS.md` (per
  `templates/docs/TASK-CREATION.template.md`) seeded with a first phase of tasks inferred from the
  idea — no separate greenfield template is needed, greenfield reuses the same formats existing-mode
  features use once they get a task file. On a re-run, never regenerate or overwrite a feature folder that already exists — a
  feature's `FEATURE.md`/`TASKS.md` accumulate hand edits (Known Gotchas, task checkmarks) over
  time, which is exactly why they're excluded from the marker system.
  **Stale lines on a re-run.** If the re-run finds a specific line in an existing `FEATURE.md` that
  the code or the repo now contradicts (a deleted folder it still mentions, a renamed file, a route
  that moved), propose that single-line fix in the feature task (the old line, the new line, and why)
  and apply it only if the user approves. If the user declines or skips, list the stale line in the
  Final report instead. Never rewrite sections of a feature doc, and never touch its task checkmarks.
  A line inside Known Gotchas or Golden Rules may be corrected or removed only when the code or repo
  verifiably contradicts it (name the evidence), the proposal says it touches one of those
  protected sections, and the user approves it. Never add new gotchas or rules, reword lines that
  are still true, or weaken a Golden Rule on Rutter's own judgement.
  A newly detected capability with no feature folder gets a new one; an existing feature is never
  recreated.
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

**Source fingerprint.** On every run (fresh or re-run, after the user's approvals), write
`.agent/.rutter-state.json`: `{"rutter": 1, "updated": "<date>", "files": {"<repo-relative path>":
"<first 12 hex chars of the file's SHA-256>", ...}}` covering every significant source file (the same
set the coverage pass uses, including docs such as `DESIGN.md`, excluding `rutter/`,
`rutter-doctor/`, build output and vendored code). If no hashing tool is available, record size and
modification time instead and say so. It is a plain JSON file, not marker-wrapped and not listed in
`AGENTS.md`; overwrite it each run. On the next re-run Task 1 reads it and reports the added,
removed and changed files exactly. **Parse it as JSON** (e.g. Python's `json` module or `jq`), never
by grepping or counting lines/colons in the raw text — the file has top-level keys (`rutter`,
`updated`) alongside `files`, so a text-based count silently miscounts the file total and, in a worse
case, could miscount the added/removed diff itself. Any count Task 1 states (files fingerprinted,
files changed) must come from that parsed structure, not an estimate corrected later in the Final
report. If the file is missing (first re-run after an older Rutter), say that no comparison is
possible, treat every file as possibly changed, and run the claim sweep over all docs.

**First, reconcile `AGENTS.md`.** Its App-Wide Docs table/tree, Task Files table, and Feature Docs
tree were drafted provisionally at Task 2 (step 6), before Tasks 3…N+2 were resolved. Now that they
have been, re-check each entry against what actually exists on disk: drop any row/link for a doc,
feature, or skill that was ultimately skipped, and add any that a Task 1 adjustment or an Adjust
response elsewhere surfaced late. Apply this as a normal marker-scoped update — same mechanism as
a re-run (step 6) — replacing only the affected lines between `AGENTS.md`'s markers. This is what
keeps a run where, say, `SECURITY.md` got skipped at Task 5 from leaving `AGENTS.md` pointing at a
file that doesn't exist.

**Then report.** State plainly which sources were read in full, which were only sampled (grep
checks, file listings, a doc skimmed rather than read), and which were not opened, and tell the
user which docs to skim before relying on them (typically API/route tables and per-feature
details). Then the migration ledger (each source doc → where its content now lives, and
that the originals were left untouched), then what was created or updated, every conditional doc that was skipped and why (e.g.
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
  sections marked `[FILL: ...]`. Process rules only: the `FEATURE.md`/`TASKS.md`/`SKILL.md` format
  specs live in the creation guides below, and `AGENTS.md` just points at them.
- `templates/docs/*.template.md` — one template per `.agent/docs/` file (13 total; `OVERVIEW`,
  `ARCHITECTURE` and the three `*-CREATION` guides are always used). The guides hold the
  `FEATURE.md`, `TASKS.md` and `SKILL.md` format specs, used whenever a feature, task file or skill
  gets added later — including greenfield feature seeding in step 6.
- `templates/platform-packs/{android,ios,react,flutter,python,go,rust,generic}.md` — per-stack
  checklists of what to look for and how to describe it; not fill-in text.
- `templates/ADAPTER.template.md` — shared body for all tool adapters; `[FILL: ToolName]`
  substituted per file.
- `templates/SKILLS_INDEX.template.md` — the `.agent/skills/INDEX.md` scaffold.
