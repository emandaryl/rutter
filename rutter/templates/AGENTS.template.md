# AGENTS.md — [FILL: ProjectName]

## Master Context for AI Coding Agents

> Read this file at the start of every session.
> For feature-specific work, also load the relevant feature doc from `.agent/features/` — see the bottom of this file.
> For a known recurring procedure, check `.agent/skills/INDEX.md` first — see "Skills" below.
>
> **Context Budget:** keep the project-specific sections concise (~150–200 lines combined); long-form material belongs in `.agent/docs/` or feature references, linked by explicit path.

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

[FILL: 1–2 sentences — what it does, who uses it, platforms. Draft from README. If unknown: `TODO(you): product description`.]

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
  Branch isolation already has to absorb the shared-file collisions that doc-currency updates can
  cause on `AGENTS.md`/`.agent/docs/` — a shared *code* abstraction spanning two feature packages
  would pile an avoidable code-level collision on top of that, for no real benefit this early.
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

[FILL: core domain nouns the agent needs, read from real model/entity names — handful only, not an exhaustive glossary.]

---

## App-Wide Docs [STANDARD — table rows are conditional on what was actually created]

Engineering reference docs for the whole project. Read these when you need deeper context beyond
what AGENTS.md provides. The three `*-CREATION.md` guides are process docs, not project docs — read
the matching one before creating a feature, `TASKS.md` or skill.

```
.agent/docs/
├── OVERVIEW.md          ← what the project is, scope, feature map
├── ARCHITECTURE.md      ← deeper technical flow than the summary above
├── FEATURE-CREATION.md  ← how to add a feature or a references/ file
├── TASK-CREATION.md     ← how to write a TASKS.md
├── SKILL-CREATION.md    ← how to add a skill
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

A request like `"Read AGENTS, {name} and fix {issue}"` must resolve to `.agent/features/<slug>/FEATURE.md`.
**Resolution algorithm:**
1. Match `{name}` against the Feature Docs tree below, tolerating case and `feature`/`features`/`.agent/` prefixes.
2. If ambiguous or no match, **ask which feature** — never guess.
3. Ad hoc bug fix or small change: no task file needed; work from `FEATURE.md`, and if it surfaces a non-obvious constraint, add it to that feature's Known Gotchas before finishing.
4. Load `FEATURE.md` always; `TASKS.md` only if continuing tracked work; the specific `references/<TOPIC>.md` files linked from `FEATURE.md` — not the whole folder.

A feature may also have a `.agent/features/<name>/TASKS.md` — a phased, checkbox-driven task list
for an active multi-step piece of work in that feature area. If one exists and the request is
continuing that work, read it and follow its own instructions header; work through it one task at
a time and don't skip ahead. Not every feature needs one — only add `TASKS.md` when there's real, in-progress multi-step work to
track, and remove or archive it once the work is done and the feature's own "Known
Gotchas"/"Architecture in One Paragraph" sections have been updated to reflect the new state. When
archiving, move it to `.agent/features/<slug>/archive/TASKS-v{N}.md` (e.g. `TASKS-v1.0.md` or
`TASKS-2026-09.md`) so active context remains lean while preserving a permanent audit trail.

```
.agent/features/
<!-- [FILL: one entry per feature that already exists in the repo (if any were found during setup),
each with its FEATURE.md / TASKS.md / references/ children (e.g.
├── <feature-slug>/
│   ├── FEATURE.md
│   ├── TASKS.md
│   └── references/
). Leave empty (just the bare .agent/features/ line) if no features exist yet. -->
```

### FEATURE.md Format

**Before creating a new `FEATURE.md` or a `references/<TOPIC>.md` file, read `.agent/docs/FEATURE-CREATION.md` and follow its format exactly — do not write one from memory.**

If no feature doc exists for the area you're working on, check `.agent/docs/` for engineering reference docs.

---

## Task Files — Feature-Specific Work Tracking [STANDARD]

### TASKS.md Format

**Before creating or restructuring any `TASKS.md`, read `.agent/docs/TASK-CREATION.md` and follow its format exactly — do not write one from memory.**

**Managed content.** Anything between the rutter begin and end marker comments in `AGENTS.md`, the adapters and `.agent/docs/` files is managed: a task-completing agent may update it directly (the doc-currency rule in every `TASKS.md`). Anything outside the markers is a human's own notes — never touch it.

Each feature has its own task file at `.agent/features/<feature-name>/TASKS.md`. New rows are added
to the table below as features are created — see "Creating a Feature / Reference / Task" at the
bottom of this file.

| Feature | Task file |
|---|---|
<!-- [FILL: one row per feature that already exists in the repo, if any were found — otherwise
leave the table with just the header, ready for the first feature. Do not invent features. -->

**To work on a feature:** load `AGENTS.md` + the feature's `FEATURE.md` + its `TASKS.md`.
**To run features in parallel:** give each session its own git branch or worktree — never run two
feature sessions directly against the same uncommitted working tree. Task files are scoped so
sessions shouldn't need to touch the same *code*, but the doc-currency rule in each `TASKS.md` (keeping
`AGENTS.md`/`.agent/docs/` updated as tasks complete) means two sessions genuinely can end up
editing the same shared file. With separate branches, that's safe: it surfaces as a normal git
merge, auto-resolved if the edits don't overlap, a visible conflict for a human to resolve if they
do. Without separate branches, it's not a conflict at all — it's a silent overwrite. Whichever
session writes `AGENTS.md` second wins, and the first session's update just vanishes with no
warning. Keep code isolation too, on top of branch isolation: a feature's tasks should only
create/edit files inside its own package/module. Don't write a task that extracts a shared helper
out of another feature's existing files, even for obviously-duplicated boilerplate — see "Shared
abstractions vs. duplication" above. Branch isolation protects shared docs; package isolation
protects code — a parallel run needs both.

---

## Skills — Tool-Agnostic Reusable Procedures [STANDARD]

`.agent/skills/` holds reusable multi-step procedures any tool can follow, in tool-agnostic language. Before starting a task that looks like a known recurring procedure, check `.agent/skills/INDEX.md` — a one-line-per-skill lookup. A row may point at a skill living outside `.agent/skills/` (e.g. `.claude/skills/<name>/SKILL.md`); the index is the single lookup table either way.

**Before creating a skill, read `.agent/docs/SKILL-CREATION.md` and follow its format exactly.**

---

## Delegation & Token Efficiency [STANDARD]

Keep the main session's context small and the bill low. Delegate only when the input is large and the answer is small (many files to search, a long log to read); each delegation has a fixed cost (the agent starts cold and re-reads this file), so a small job is cheaper inline. Use a cheap model for the delegated job where the tool allows it.

- **Broad search** ("where is X", "what touches Y", sweeps across many files) → a *search* agent; ask for a short answer with `path:line` references, not file contents.
- **Noisy output** (full test runs, build logs, migrations, any long output) → a *test runner* agent, which runs a documented command and returns only the failures and the fix-relevant lines.
- **Post-task doc updates** → after a change touching several files, a *doc updater* agent applies the mechanical "After Every Task" edits (file lists, commands, endpoints) from a one-paragraph summary of the change. For a one- or two-file change, edit the docs inline. You still write Known Gotchas, Architecture changes and `DECISIONS.md` entries yourself; the agent only flags them.
- **Commits, review and task status** (Claude Code only) → a *committer* commits only when the user asked and never pushes; a *code reviewer* reviews the diff read-only, before a PR or when asked, not after every edit; a *task tracker* records `[x]` / `[~]` / `[!]` in `TASKS.md` after the user approves (it refuses `[x]` without the approval quoted). You still decide whether a task is done.
- **Push, PRs and debugging stay with you.** Push or open a PR only when the user asks, from the main session. Root-cause debugging needs the context you hold: use the search agent to locate code and the test runner to reproduce, then reason inline.
- **Do it yourself** when the target file is already known, the edit is small, the output will be short anyway, or the task needs the context you already hold.

| Job | Claude Code (`.claude/agents/`) | Codex (`.codex/agents/`) |
|---|---|---|
| Search | `explorer` | `repo_explorer` |
| Test runner | `test-runner` | `test_runner` |
| Doc updater | `doc-updater` | `doc_updater` |
| Commit / review / task status | `committer`, `code-reviewer`, `task-tracker` | none |

Claude Code agents with Bash run behind a guard hook in `.claude/hooks/`, a safety net and not a sandbox. If it blocks a command, rerun it as one plain command or do that step yourself. Codex agents have no guard, only their instructions; they inherit the session model unless `default_subagent_model` is set under `[agents]` in `config.toml`, and Codex spawns them only when asked, so ask by name. In any other tool, use its own sub-agent feature for the same jobs, or work inline with short outputs.

When delegating, state the exact question and the output you want (length, format). Read targeted line ranges instead of whole files, and do not paste large outputs back into the conversation.

---

## Creating a Feature / Reference / Task / Skill [STANDARD]

<!-- Delete this comment when done. If step 3a found an existing owner of a format, replace that row's `.agent/docs/<GUIDE>.md` path (here and in the pointer lines above) with the owner's real path; see SKILL.md step 6. -->

Read the matching guide before creating anything — never write these from memory:

| To add… | Read first |
|---|---|
| A new feature, or a `references/<TOPIC>.md` file | `.agent/docs/FEATURE-CREATION.md` |
| A `TASKS.md` (only for real multi-step work) | `.agent/docs/TASK-CREATION.md` |
| A skill | `.agent/docs/SKILL-CREATION.md` |

After adding a feature, add it to the tree in "Feature Docs" and, if it has a `TASKS.md`, to the Task Files table. When a feature's work is done, fold permanent gotchas into its `FEATURE.md` "Known Gotchas" and archive the `TASKS.md` as described in "Feature Docs" above.

---

## After Every Task: Keep the Docs Current [STANDARD]

When you finish any task, in the same change as the code:

1. Update the matching `.agent/features/<slug>/FEATURE.md`: Package Structure for any file added, moved or removed; Known Gotchas for anything non-obvious you hit; the Architecture paragraph if the shape changed.
2. Update any `.agent/docs/` file the change touches: `API.md` (endpoints, models), `UI.md` (tokens, components), `SETUP.md` (commands, ports, prerequisites), `ARCHITECTURE.md` (data flows), `DECISIONS.md` (a new non-obvious decision, with the why). Only files that exist.
3. Update the project plan (e.g. `docs/PLAN.md`) if one exists and scope, phase order or a decision changed, and the root `README.md` if run steps changed.
4. If a doc line is now wrong, fix the line. Do not leave stale text for later.

Do not re-run Rutter to do this; edit the docs directly and keep changes small.
