# AGENTS.md — [FILL: ProjectName]

## Master Context for AI Coding Agents

> Read this file at the start of every session.
> For feature-specific work, also load the relevant feature doc from `.agent/features/` — see the bottom of this file.
> For a known recurring procedure, check `.agent/skills/INDEX.md` first — see "Skills" below.

---
<!--
STANDARD vs PROJECT-SPECIFIC — read this before filling the file in, then delete this comment block.

STANDARD sections (marked "[STANDARD]" below) are copied verbatim, project-name-substituted only.
Do not shorten, reword, or make them conditional — they are the process rules that make the rest
of this doc system work, independent of what kind of project this is.

[FILL: ...] markers are replaced with real content read from the actual target repo — manifests,
source tree, actual classes found. Never leave a [FILL: ...] token in the final file. If something
genuinely cannot be determined from the repo (no README to draft a product description from, a
convention that's tribal knowledge no file reveals), replace it with a single line:
`TODO(you): <what's missing>` — never invent content and never ship a bracketed placeholder.

Sections marked "(if applicable)" are only included when the target repo actually shows evidence
for them (a detected DB/ORM, a detected logging wrapper, etc.) — delete the whole section header
plus body if there's no evidence, rather than leaving it empty.
-->

## What [FILL: ProjectName] Is

[FILL: 1–2 sentence description of what the product/project does — draft from README.md if one
exists and is substantive; otherwise `TODO(you): add a 1-2 sentence product description`.]

---

## Tech Stack

| Layer | Technology |
|---|---|
[FILL: table rows built from the target repo's actual manifest/lockfile — language, UI framework,
architecture/DI framework, async model, local DB, networking, analytics/crash reporting, etc.
Only include rows for things actually present, in the `| Layer | Technology |` shape shown above.]

**Build config:** [FILL: one-liner — min/target platform versions, language version, build tool.]

---

## Package Structure

Root package/directory: `[FILL: e.g. io.example.app, or src/, or lib/]`

```
[FILL: top 2-3 levels of the real source tree, one line per folder with a short "← purpose"
annotation. Don't enumerate every file — folders and their responsibility only.]
```

---

## Architecture Pattern

[FILL: one paragraph describing the actual shape of the codebase — the main layers/classes and how
data flows between them, read from real code (entry points, state containers, how UI subscribes to
state). Add a short arrow diagram if the codebase shows clear layering (e.g.
`View → ViewModel → Repository → API`). Don't guess a textbook pattern name (MVVM/MVC/etc.) unless
the code actually matches it — describe what's really there.]

---

## Data Layer Conventions <!-- (if applicable — only if a DB/ORM was found in dependencies) -->

[FILL: how the codebase actually reads/writes its local or primary data store — instantiation
pattern, whether objects are passed by reference or copied, where DB-access classes live.]

---

## Key Shared Utilities

| Class / Module | Role |
|---|---|
[FILL: real singleton/manager/provider/client classes found in the codebase, with a role
description read from what the class actually does — not guessed from its name. Whenever one of
these is the established way to do something (a shared component library, a shared
request-execution helper, a canonical constants module), note that here AND add the matching
"check before creating a new one" line in Coding Conventions below — see the note on that rule at
the end of this section.]

---

## Logging <!-- (if applicable — only if a house logging wrapper actually exists) -->

[FILL: the project's logging convention — the wrapper class/function to use, what NOT to call
directly (e.g. raw `console.log`/`print`/`android.util.Log`), and what the wrapper routes to
(file, remote service, crash reporter) if that's discoverable.]

---

## Coding Conventions

[FILL: real, observed conventions only — write one short subsection per convention actually found,
in this repo's style (a one-line rule, a code snippet if it clarifies, a short "why"). Candidates
to actively look for, each only if there's real evidence:
- **Migration-in-progress rule** — if two languages/frameworks visibly coexist (e.g. JS files
  alongside TS, class components alongside hooks, Java alongside Kotlin), state the incremental
  conversion rule: convert as you touch, never mass-convert.
- **Null-safety / defensive-access pattern** — if the codebase has a recurring pattern for guarding
  against a nullable/untyped boundary (legacy models, external API responses).
- **Preferred pattern for a recurring task type** — e.g. how new API endpoints get added, with a
  ✅/❌ snippet, if the codebase shows a clear preferred way that supersedes an older one.
- **Framework preview/story mandate** — if the codebase already has UI previews/stories in use
  (Compose `@Preview`, SwiftUI `#Preview`, Storybook, Flutter golden tests), document the
  convention and whether it's treated as mandatory.
- **i18n / string-constants convention** — if user-facing strings already route through a house
  system (provider class, translation JSON, generated string resources) rather than being
  hardcoded, document that path and the "never hardcode a user-facing string" rule.
- **"Check before creating" rule(s)** — one line per shared utility from the Key Shared Utilities
  table above that exists specifically to prevent duplicate parallel implementations (a component
  library, a shared request-execution helper, a canonical constants/config module): "before writing
  a new X, check `<location>` first."
- **Near-duplicate systems warning** — if the codebase has two similarly-named or similarly-shaped
  systems that do genuinely different things (e.g. two different AI/LLM integrations, two caching
  layers), call this out explicitly as its own short warning so they don't get conflated.]

### Shared abstractions vs. duplication — the parallel-safety rule [STANDARD]

> **Rule: duplicate on the second occurrence, extract on the third.** Don't pull a shared
> helper/base class out of another feature's existing code just because a new feature needs the
> same boilerplate (a status-mapping function, a parsing routine, etc.).

- Two copies of the same small helper (~20–50 lines) is an acceptable, often preferable, cost.
  Extracting a shared class from a single prior example means guessing at the right shape from one
  data point — and it forces a touch (even just a `// TODO` comment) into a file that belongs to a
  different, possibly in-progress feature.
- **Why this matters more here than in most codebases:** features are built by parallel agent
  sessions, one per `.agent/features/<feature>/TASKS.md` (see "To run features in parallel" below).
  A shared abstraction spanning two feature packages creates a file both sessions need to touch —
  the first thing that breaks the "sessions don't conflict" guarantee the task-file structure is
  built around.
- A feature's tasks should only ever create or edit files under its own feature package (plus
  genuinely shared, already-established infrastructure everyone already depends on — those are fine
  to *read*, just don't refactor them mid-feature). If implementing a task would require editing
  another feature's files to extract something reusable, duplicate the boilerplate into the new
  feature instead and defer the extraction.
- Once a third feature needs the same boilerplate, that's the right time to extract — by then there
  are three real call sites to generalize from, and the extraction can be its own scoped task that
  doesn't block any single feature's session.

---

## Domain Concepts (quick reference)

[FILL: the core vocabulary of the domain — the nouns a new agent needs to know, read from real
model/entity names in the codebase (e.g. `Order → LineItem → Product` for a commerce app, or
`Board → List → Card` for a kanban app). Keep it to the handful of concepts that show up
everywhere, not an exhaustive glossary.]

---

## Task Files — Feature-Specific Work Tracking [STANDARD]

### TASKS.md Format

When creating a `.agent/features/<name>/TASKS.md`, follow this format strictly — structure,
headings, and status marks exactly as below. Only the title, the project-specific rules in the
instructions block, and the phase/task/prompt content are filled in per feature. The instructions
block must always include, at minimum, rules forbidding hardcoded strings/integers and any
project-specific logging bypass (see "Logging" above), plus any additional constraints specific to
that feature. The first phase (`Phase 0`) is conventionally reserved for manual/human setup work
(creating packages, baseline scaffolding) that an agent should not attempt itself. A manual-only
task still gets the full `Task {N.M}` block and checklist, but its **Agent prompt** line is a fixed
marker instead of an actual prompt — `**Agent prompt:** Manual step — not for an agent.` — rather
than improvising a "don't do this" instruction each time one comes up.

```markdown
# TASKS.md — {Title}

> **Instructions for agents:**
> - Read `AGENTS.md` and `.agent/features/{name}/FEATURE.md` before starting any task.
> - Work on ONE task at a time. Do not start the next task until the current one is marked `[x]`.
> - When a task is complete, mark it `[x]` and add a brief completion note.
> - Never skip a task. Each task builds on the ones before it.
> - If a task is blocked, mark it `[!]` and add a `> BLOCKED:` note explaining why.
> - Request human review before marking any task complete.
> - **{project-specific rule}.**
> - **{project-specific rule}.**

---

## Status Legend

| Mark | Meaning |
|---|---|
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Complete — reviewed and approved |
| `[!]` | Blocked — see note below task |

---

## Phase {N} — {Phase Name}

> **Goal:** {what this phase achieves}

### Task {N.M} — {Task Name}
- [ ] {checklist item}
- [ ] {checklist item}

> Completed: {brief note on what was done, added once the task is marked `[x]`}

**Agent prompt:**
> "{self-contained prompt: what to read, what to build/change, any constraints, 'Stop and request review.'}"

---
```

Each feature has its own task file at `.agent/features/<feature-name>/TASKS.md`. New rows are added
to the table below as features are created — see "Creating a Feature / Reference / Task" at the
bottom of this file.

| Feature | Task file |
|---|---|
<!-- [FILL: one row per feature that already exists in the repo, if any were found — otherwise
leave the table with just the header, ready for the first feature. Do not invent features. -->

**To work on a feature:** load `AGENTS.md` + the feature's `FEATURE.md` + its `TASKS.md`.
**To run features in parallel:** open separate sessions, each loading a different feature's files
— task files are scoped so sessions don't conflict. Keep it that way: a feature's tasks should only
create/edit files inside its own package/module. Don't write a task that extracts a shared helper
out of another feature's existing files, even for obviously-duplicated boilerplate — see "Shared
abstractions vs. duplication" above. That's the one thing that turns two parallel sessions into a
merge conflict.

---

## App-Wide Docs [STANDARD — table rows are conditional on what was actually created]

Engineering reference docs for the whole project. Read these when you need deeper context beyond
what AGENTS.md provides.

```
.agent/docs/
├── OVERVIEW.md      ← what the project is, scope, feature map
├── ARCHITECTURE.md  ← deeper technical flow than the summary above
<!-- [FILL: add one line per conditional doc that was actually created — SETUP.md, TESTING.md,
SECURITY.md, DECISIONS.md, UI.md, API.md, FLOWS.md, DEPLOYMENT.md — each with a short "← purpose"
note. Omit any that weren't created; never list a doc that doesn't exist on disk. -->
```

---

## Feature Docs — Feature-Specific Context [STANDARD]

When working on a specific feature, load its feature doc before writing code. Feature docs are the
authoritative agent-facing reference — more accurate and up to date than `.agent/docs/`.

> **Path note:** feature docs live at `.agent/features/<slug>/FEATURE.md`. Whether referred to as
> "feature/", "features/", singular or plural, with or without the `.agent/` prefix, or by just the
> feature name — this table is the source of truth for the real path. Resolve here first rather
> than trusting the literal path as typed.

### Resolving a shorthand feature instruction

A request will often arrive as shorthand, not a full path — all of these must resolve the same way:

- `"Read AGENTS and feature/{name}, then {description}"`
- `"Read AGENTS and {name}, then {description}"`
- `"Read AGENTS.md and .agent/features/{slug}/FEATURE.md, then {description}"`

**Resolution algorithm** — do this before reading anything else about the feature:
1. Match `{name}` against the tree in this section (and the Task Files table above), tolerating
   case differences and a `feature`/`features`/`.agent/` prefix either present or absent.
2. If there's no exact match, try again ignoring a common project-name prefix on the slug (e.g. a
   slug like `<project>-voice-coach` should still match a request for just `"voice-coach"`).
3. If more than one feature plausibly matches, or nothing matches, **ask which feature is meant**
   rather than guessing — silently picking the wrong feature wastes the whole point of scoping
   context per feature.
4. Once resolved, load in this order: `FEATURE.md` always; `TASKS.md` if it exists **and**
   `{description}` reads as continuing tracked work (follow its next unchecked task); the specific
   `references/<TOPIC>.md` file(s) `FEATURE.md` links to for the area `{description}` touches —
   not the whole `references/` folder indiscriminately.
5. A `{description}` that's an ad hoc bug fix or small modification, not tied to any open
   `TASKS.md` phase, doesn't need a task file created for it — just fix it directly against the
   context `FEATURE.md` (and any linked reference) provides. If the fix surfaces a non-obvious
   constraint, add it to that feature's `FEATURE.md` "Known Gotchas" section before finishing,
   the same as you would after retiring a `TASKS.md` — that section accumulates from both paths,
   not just completed task files.

A feature may also have a `.agent/features/<name>/TASKS.md` — a phased, checkbox-driven task list
for an active multi-step piece of work in that feature area. If one exists and the request is
continuing that work, read it and follow its own instructions header; work through it one task at
a time and don't skip ahead. Not every feature needs one — only add `TASKS.md` when there's real,
in-progress multi-step work to track, and remove or archive it once the work is done and the
feature's own "Known Gotchas"/"Architecture in One Paragraph" sections have been updated to
reflect the new state.

```
.agent/features/
<!-- [FILL: one entry per feature that already exists in the repo (if any were found during setup),
each with its FEATURE.md / TASKS.md / references/ children — mirror the tree style used in this
repo's own AGENTS.md. Leave empty (just the bare .agent/features/ line) if no features exist yet. -->
```

### FEATURE.md Format

When creating a new `.agent/features/<name>/FEATURE.md`, follow this shape. The frontmatter and
first three body sections are required; add whichever deeper sections the feature needs (State
Design, Data Flows, Screens, Side Effects, etc.) between "Package Structure" and "Known Gotchas".

```markdown
---
name: {feature-slug}
description: >
  {One paragraph, plain prose: what this feature is and what it covers. No "Trigger on: ..."
  keyword list — just describe the scope clearly enough that a reader can tell if this is the
  right doc for their task.}
---

# {Feature Title}

## What This Feature Covers

{What the feature is, what it replaces if this is a migration, and what it explicitly does NOT
cover — link to sibling feature docs for adjacent scope instead of duplicating it.}

## Architecture in One Paragraph

{The shape of the feature in a few sentences: the main classes/screens and how data flows between
them. Enough for a reader to orient before going deeper.}

## Package Structure

{File tree or table of the feature's classes/files and each one's responsibility.}

{...deeper sections as needed...}

## Known Gotchas

{Non-obvious constraints, past bugs and their root cause, workarounds, "don't do X because Y"
rules specific to this feature. Living section — update it any time work in this feature surfaces
something non-obvious, whether that's a TASKS.md phase being completed and retired, or a one-off
bug fix / ad hoc change done straight against this FEATURE.md with no task file involved. Gotchas
belong here permanently, not just in a task's completion note or a commit message.}

## Golden Rules

{Short numbered list of hard constraints for this feature — the "never do X" / "always do Y"
rules a future agent must not violate.}
```

**Prompting patterns** (all equivalent — see "Resolving a shorthand feature instruction" above):
- `"Read AGENTS.md and .agent/features/{slug}/FEATURE.md, then implement [task]."`
- `"Read AGENTS and feature/{feature_name} and [bug/implementation description]."`
- `"Read AGENTS and {feature_name} and [bug/implementation description]."`

New feature docs will be added as more features are built out. If no feature doc exists for the
area you're working on, check `.agent/docs/` for engineering reference docs.

---

## Skills — Tool-Agnostic Reusable Procedures [STANDARD]

`.agent/skills/` holds reusable, multi-step procedures any tool or agent can follow — written in
plain, tool-agnostic language (no assumptions about slash commands, a particular subagent system,
or any single vendor's tool surface). Where `.agent/features/` captures context about *what the
project is*, `.agent/skills/` captures *how to correctly do a specific recurring task* — a release
process, a codegen step, a data-migration script, an onboarding checklist.

Check `.agent/skills/INDEX.md` before starting any task that looks like a known recurring
procedure — it's a one-line-per-skill lookup, faster than opening every skill folder to find the
right one. A row may point at a skill living outside `.agent/skills/` — e.g. a Claude-Code-specific
skill at `.claude/skills/<name>/SKILL.md` — rather than duplicating it here; the index is the single
lookup table regardless of where each skill's real content lives.

```
.agent/skills/
├── INDEX.md                     ← one line per skill: name, when to use it
└── <skill-name>/
    ├── SKILL.md                 ← instructions, written in tool-agnostic language
    ├── references/              ← optional supporting docs (protocol detail, worked examples)
    └── scripts/                 ← optional automation — see the no-script fallback rule below
```

### SKILL.md format

```markdown
---
name: {skill-slug}
description: {one line — what this does and when to use it; becomes the INDEX.md row}
---

# {Skill Title}

## When to Use This

{The trigger conditions — what request or situation should make an agent load this skill.}

## Steps

{Numbered, tool-agnostic instructions describing the procedure itself, not one tool's specific
syntax for it — "run this project's lint command" rather than a command tied to one particular
CLI or vendor.}

## Known Gotchas

{Non-obvious failure modes or edge cases this procedure has hit before.}
```

### The no-script fallback rule

If a skill's `scripts/` folder contains an automation script, `SKILL.md`'s "Steps" section must
also spell out the manual equivalent — a numbered fallback, not just a bare "run
`scripts/foo.sh`" line. Not every environment an agent runs in can execute a local script
(sandboxing, a missing runtime, a different OS); the manual fallback is what keeps the skill
usable everywhere the script isn't. Don't create `scripts/` preemptively — add it only once a
real automatable step exists, the same evidence bar `references/` gets in Feature Docs above.

---

## Creating a Feature / Reference / Task / Skill [STANDARD]

Four related but distinct things get added to this doc system over time — use the right one:

1. **New feature** → create `.agent/features/<slug>/`, write `FEATURE.md` following the
   "FEATURE.md Format" above, then add it to the tree in "Feature Docs" above and add its row to
   the Task Files table if it also gets a `TASKS.md`.
2. **New reference** → when a feature's supplementary material (protocol/domain detail, deep
   architecture for one sub-system, a debrief/postmortem) would bloat `FEATURE.md` past being
   scannable, split it into `.agent/features/<slug>/references/<TOPIC>.md` — one self-contained
   topic per file, written so it can be loaded on its own — and link it from the relevant
   `FEATURE.md` section instead of inlining the material. Don't create a `references/` folder
   preemptively; add it the first time a feature actually needs one.
3. **New task file** → only when there's real, in-progress multi-step work to track for that
   feature (not one automatically for every feature) — create `TASKS.md` following the "TASKS.md
   Format" above. Once the work is done, fold any permanent gotchas into the feature's `FEATURE.md`
   "Known Gotchas" section, then archive or remove the task file.
4. **New skill** → when a recurring, multi-step *procedure* (not project context — that's a
   feature) needs to be captured so any tool or agent can follow it correctly — create
   `.agent/skills/<slug>/`, write `SKILL.md` following the "SKILL.md format" above, and add its
   row to `.agent/skills/INDEX.md`. Add `references/` or `scripts/` only once real supporting
   material or an actual automatable step exists — and if `scripts/` gets added, `SKILL.md` must
   include the manual no-script fallback described above.
