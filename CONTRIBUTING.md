# Contributing to Rutter

Maintainer-facing doc — see `README.md` for the pitch. This covers the conventions, rules, and
formats that keep this repo consistent, for whoever (human or agent) edits it next.

## Layout, from a maintainer's angle

| Path | Nature |
|---|---|
| `rutter/SKILL.md` | The actual spec. An agent reads and executes this. **Source of truth.** |
| `rutter/templates/` | Every template `SKILL.md` fills in — the root doc, per-doc stubs, platform packs, adapters, skills index. |
| `rutter/START-HERE.md` | Human-facing quickstart, read by a person before any agent is invoked. Not read by the agent executing the skill. |
| `rutter-landing.html`, `rutter-howto.html` | Marketing/prose *description* of what the skill does. Not executable, not read by an agent running Rutter — for humans deciding whether to install it. |
| `README.md` | Project pitch for this repo. |
| `rutter.zip` | Personal, local-only convenience artifact. Gitignored, never committed, not documented in README. Rebuild with the command at the bottom of this file. |

## Format specs — where they live

Every doc type Rutter generates has an exact format spec, and every spec has exactly one home.
Duplicating any of them here (or anywhere else) would violate the same one-canonical-home rule the
*generated* docs themselves are built to follow — so if you need to check or change a format, edit
it at its source. Never copy one out "for convenience," even into this file.

| Format | Lives in |
|---|---|
| `AGENTS.md` itself — which sections are `[STANDARD]` (copied verbatim) vs `[FILL: ...]` (authored per-repo) | `rutter/templates/AGENTS.template.md` — the file *is* the spec |
| `TASKS.md` format — Phase/Task numbering (`Task {N.M}`), the `[ ]`/`[~]`/`[x]`/`[!]` status legend, the agent-prompt block | `AGENTS.template.md`, "TASKS.md Format" section |
| `FEATURE.md` format — frontmatter, required sections, "Known Gotchas" | `AGENTS.template.md`, "FEATURE.md Format" section |
| A nested `.agent/skills/<name>/SKILL.md` format (a *generated-repo's* skill file — not this project's own `SKILL.md`) | `AGENTS.template.md`, "SKILL.md format" section |
| Each `.agent/docs/<NAME>.md` file's own section structure | Its own `rutter/templates/docs/<NAME>.template.md` |
| Adapter file body (`CLAUDE.md`, `GEMINI.md`, `.cursor/rules/project.mdc`, `.github/copilot-instructions.md`) | `rutter/templates/ADAPTER.template.md` |
| `.agent/skills/INDEX.md` scaffold | `rutter/templates/SKILLS_INDEX.template.md` |
| Which conditional docs get created at all, and on what evidence | `rutter/SKILL.md` step 4's evidence table |

The Conventions section below covers *rules about* these formats (e.g. why task IDs look the way
they do); this table is for finding the formats themselves.

## Source of truth: `SKILL.md` wins

`rutter/SKILL.md` is the real behavior. `rutter-landing.html` and `rutter-howto.html` are prose
*describing* that behavior for humans. When the two disagree, treat the HTML as stale and edit it
to match `SKILL.md` — not the reverse. Before mechanically "fixing" a mismatch this way, check
which side is actually correct: the HTML isn't automatically wrong just because it's HTML, and
`SKILL.md` isn't automatically right just because it's the spec — a mismatch can mean either one
needs to change.

## Conventions and rules

- **`TODO(you): <what's missing>`**, not `TBD`, is the marker for anything ungrounded. It's
  unambiguous about *whose* job it is to fill the gap — `TBD` could be misread as "the agent will
  figure it out," which is exactly the invented-content failure mode the skill exists to avoid.
- **Task IDs are `Task {N.M}`** (phase.task, e.g. `Task 1.2`), never a flat `T2`. The phase grouping
  is structurally meaningful (see the `TASKS.md` format) — don't flatten it in copy or templates
  just because it reads shorter.
- **There is no "profile" concept** (minimal/standard/full). Doc selection is fully automatic,
  evidence-based (`SKILL.md` step 4), plus the user's per-task skip in the task loop. Skip already
  subsumes what a preset would do — don't reintroduce user-selectable presets.
- **`.claude/skills/<name>/` content is cross-referenced, never duplicated.** A real, functional
  Claude Code skill needs its actual file at that path to trigger — copying it into
  `.agent/skills/` would duplicate content and not even work for its original purpose. It gets one
  row in `.agent/skills/INDEX.md` pointing back at the original path instead.
- **Managed markers wrap the entire file**, not per-section. `<!-- rutter:begin -->` /
  `<!-- rutter:end -->` are the first and last lines of `AGENTS.md`, each adapter, and each
  `.agent/docs/` file. `.agent/features/` and `.agent/skills/` are *never* marker-wrapped — they're
  living, hand-edited documents (Known Gotchas, task checkmarks accumulate over time), not
  regenerated content. Don't extend the marker system to them.
- **Task 1 and Task 2 of the task loop are not skippable** (proceed/adjust only). Task 1
  (discovery/intake) writes nothing, so there's nothing to skip. Task 2 (`AGENTS.md` + adapters) is
  the anchor every later task's content links back into — skipping it would leave the rest of the
  run with no coherent target.
- **`AGENTS.md`'s cross-reference tables are provisional until the Final task.** The App-Wide Docs
  table/tree, Task Files table, and Feature Docs tree get drafted at Task 2 — before Tasks 3…N+2
  (the docs/features/skills tasks) are resolved — so the Final task (`SKILL.md` step 7) reconciles
  all three against what was actually created, using the same marker-scoped update mechanism as a
  re-run, before reporting. Preserve this two-pass reconcile if you restructure the task loop.
- **The skill's directory name and its `name:` frontmatter field must always match** (`rutter`,
  both places).
- **Templates must be self-contained.** If you see language like "the way this repo's own X
  section is written" in a template, rewrite it — Rutter ships no reference implementation of its
  own, so a template can't lean on "the way this repo does it."
- **Keel** is a sibling product referenced in the marketing copy (an autonomous, greenfield-only
  app builder, contrasted against Rutter's interactive, docs-only approach). Don't couple
  `SKILL.md`'s actual logic to Keel by name — the greenfield intake (step 3b) only vaguely says "a
  builder tool" when deferring a stack decision, on purpose.

## Common maintenance tasks

### Changing `SKILL.md`'s step order or numbering

`SKILL.md` is full of internal cross-references like "see step 6" — these are **not**
auto-updated, and this has been a real, recurring source of drift. After renumbering anything, run:

```bash
grep -rn "step [0-9]\|SKILL\.md step" rutter/SKILL.md rutter/templates/*.md rutter/templates/**/*.md
```

and manually verify every hit still points at the right content. `rutter/templates/ADAPTER.template.md`
and `rutter/templates/SKILLS_INDEX.template.md` both reference specific `SKILL.md` step numbers and
are easy to forget.

### Adding or removing a conditional `.agent/docs/` file

Touch all of these together, not just the template:

1. `rutter/templates/docs/<NAME>.template.md` — add or delete the stub.
2. `rutter/SKILL.md` step 4's evidence table — the "create when" row.
3. `rutter/SKILL.md`'s References section doc count (currently "10 total; first two always used").
4. `rutter-landing.html`'s `#standard` section, "The depth" manifest tree — illustrative, keep it
   loosely in sync (it shows 5 example doc names, not all of them).
5. The relevant platform pack(s)' "Conditional docs signals" bullet, if the new doc has
   stack-specific evidence worth calling out.

### Editing the HTML pages

Both files share a CSS specificity gotcha — watch for it if you add more top-level sections:

> An element with `class="wrap"` that also matches a bare element-type rule (e.g. a plain
> `section{padding:...}` selector) will have the type-selector's `padding` **silently overridden**
> by `.wrap`'s `padding:0 28px`, because a class selector always beats a type selector regardless
> of source order. The fix is `section.wrap{padding-top:...}` — a compound selector with the
> *longhand* property, so it wins on specificity without clobbering `.wrap`'s horizontal padding.
> Use the same pattern for any new bare-element rule on an element that also carries `.wrap`.

Also: keep in-page anchor links (`#standard`, `#passage`, `#outcomes`, `#name`, `#get`, etc.) in
sync with the actual section `id`s — nothing validates this automatically, and both files link to
each other's anchors too (`rutter-howto.html` links to `rutter-landing.html#standard`, etc.).

### Whenever `SKILL.md`'s behavior changes

Re-check both HTML pages for copy that now contradicts it — task loop mechanics, doc names,
terminology (`TODO(you)`, `Task {N.M}`), the managed-markers snippet, anything under "The passage"
or the FAQ. `SKILL.md` is the spec; the HTML is prose describing the spec, so it drifts the moment
the spec changes and nobody goes back to check.

## Repo notes

- The git repo root is this directory, not `rutter/` — cloning it puts the skill at `rutter/`
  inside the clone, not at the repo root. If you ever move `.git`, verify with `git status`/
  `git diff` that files show as renames, not delete+add — that's how you know history was
  preserved correctly.
- `rutter.zip` is gitignored and personal-only — it's not part of what this repo documents or
  distributes. To rebuild it for your own local testing:
  ```bash
  find rutter -name ".DS_Store" -delete
  zip -r rutter.zip rutter -x "*.DS_Store" "*.git*"
  ```
  The `-x "*.git*"` exclusion matters if a `.git/` ever ends up inside `rutter/` again — it must
  never ship inside the packaged skill.
- No CI, no build step, no package manifest — this is plain markdown plus two static HTML files.
  "Testing" a change means re-checking `SKILL.md` for internal consistency (see above) and,
  ideally, actually running it against a real repo end to end.
