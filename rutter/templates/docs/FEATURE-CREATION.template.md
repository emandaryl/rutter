<!-- Always created, in Task 2, alongside AGENTS.md. Standard process doc: copy it verbatim — it carries no project-specific content, so there is nothing to fill in. Wrapped in rutter markers on write like every .agent/docs/ file. Delete this comment when done. -->

# Creating a Feature

How to add a feature doc, and a `references/` file when a feature outgrows one file. Follow it exactly — don't write a `FEATURE.md` from memory.

## Steps

1. Create `.agent/features/<slug>/`.
2. Write `.agent/features/<slug>/FEATURE.md` in the format below.
3. Add the feature to the `.agent/features/` tree in `AGENTS.md` ("Feature Docs").
4. Only if there is real, in-progress multi-step work to track, also add a `TASKS.md` — follow `.agent/docs/TASK-CREATION.md` — and add its row to the Task Files table in `AGENTS.md`. Not every feature gets one.

## FEATURE.md format

The frontmatter and the first three body sections are required; add whichever deeper sections the feature needs (State Design, Data Flows, Screens, Side Effects, etc.) between "Package Structure" and "Known Gotchas".

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

{File tree or table of the feature's classes/files and each one's responsibility. Living section,
same as Known Gotchas below — update it as part of finishing any task that adds, moves, or removes
a file, not just once at the start.}

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

## Adding a reference

When a feature's supplementary material (protocol/domain detail, deep architecture for one sub-system, a debrief/postmortem) would bloat `FEATURE.md` past being scannable, split it into `.agent/features/<slug>/references/<TOPIC>.md` — one self-contained topic per file, written so it can be loaded on its own — and link it from the relevant `FEATURE.md` section instead of inlining the material. Don't create a `references/` folder preemptively; add it the first time a feature actually needs one.
