<!-- Always created, in Task 2, alongside AGENTS.md. Standard process doc: copy it verbatim — it carries no project-specific content, so there is nothing to fill in. Wrapped in rutter markers on write like every .agent/docs/ file. Delete this comment when done. -->

# Creating a TASKS.md

How to add a task file for a feature. Follow the format below exactly — structure, headings and status marks as shown. Don't write a `TASKS.md` from memory.

## When to create one

Only when there is real, in-progress multi-step work to track for that feature — not automatically for every feature. A feature doc without a task file is normal.

## Steps

1. Create `.agent/features/<name>/TASKS.md` in the format below. Only the title, the `{...}` slots in the instructions block, and the phase/task/prompt content change per feature. Fill every `{...}` slot with real content; if something can't be determined, write a single `TODO(you): <what's missing>` line instead — never leave a brace placeholder in the file.
2. The instructions block must always carry, at minimum: rules forbidding hardcoded strings/integers; any logging rule from the Logging section of `AGENTS.md`, if it has one; and the two standing doc-currency rules (updating stale content, recording real decisions in `DECISIONS.md`). Copy those two verbatim — neither is project-specific. Add any constraints specific to the feature on top.
3. Phase 0 is conventionally reserved for manual/human setup work (creating packages, baseline scaffolding) that an agent should not attempt itself. A manual-only task still gets the full `Task {N.M}` block and checklist, but its **Agent prompt** line is the fixed marker `**Agent prompt:** Manual step — not for an agent.` rather than an improvised "don't do this" instruction.
4. Add the file's row to the Task Files table in `AGENTS.md`.
5. When the work is done, retire the file as described in `AGENTS.md` under "Feature Docs": fold permanent gotchas into the feature's `FEATURE.md` first, then archive it.

## Format

```markdown
# TASKS.md — {Title}

> **Instructions for agents:**
> - Read `AGENTS.md` and `.agent/features/{name}/FEATURE.md` before starting any task.
> - **Reading order and precedence:** {files to read, in order, and which source wins if two of them disagree — e.g. a spec vs `FEATURE.md`}.
> - **Where to start:** {the first phase with unchecked tasks; name any earlier phases that are historical or superseded, e.g. "Phases 1–3 are done — start at Phase 4"}.
> - **Scope:** {where new files may go; which shared files may be touched additively only; non-goals}.
> - Work on ONE task at a time. Do not start the next task until the current one is marked `[x]`.
> - Before marking a task `[x]`, check whether its work makes anything in the root `AGENTS.md` or
>   `.agent/docs/` stale, or resolves a `TODO(you)` there — a new shared class for Key Shared
>   Utilities, a Package Structure line that's changed, an architecture detail that's now built
>   instead of planned. If so, update the specific section that changed, right now, as part of
>   finishing this task — don't defer it to a separate pass. Also update this feature's own
>   `FEATURE.md` Package Structure section the same way; it's a living section, same as Known
>   Gotchas.
> - If this task involved a real, non-obvious technical choice the plan didn't already specify (a
>   library picked, a pattern adopted, a tradeoff accepted), record it in
>   `.agent/docs/DECISIONS.md` as a short title, a **Decision:** line, a **Why:** line, and a
>   **Status: active** line. Create the file with a `# Decisions` heading if it doesn't exist yet
>   — don't skip the entry just because nothing warranted the file when the docs were first
>   generated. Same bar either way: genuinely non-obvious, not routine.
> - When a task is complete, mark it `[x]` and add a brief completion note — mention here if a
>   root doc got updated too, so there's a record of what changed and why.
> - Never skip a task. Each task builds on the ones before it.
> - Never delete or re-tick history. A phase that a later phase replaces stays in the file under a `> **Superseded by Phase {X} ({date}):** {why}` banner. Later fixes and reviews are appended as new phases, never edits to finished ones.
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

> Completed {date}. {what was done, plus the build/verify result — added once the task is marked `[x]`}

**Verify:** `{exact command}` *(optional)*

**Agent prompt:**
> "{self-contained prompt: what to read, what to build/change, any constraints, 'Stop and request review.'}"

---

### Phase {N} Code Review
- [ ] {build/test command passes}
- [ ] Only the intended files were touched
- [ ] {feature-specific invariant still holds}

---

## Open Questions (do not resolve unilaterally — {why})

1. {question that needs a human decision}
2. ~~{a resolved question}~~ **Resolved {date} (explicit user direction):** {the answer} — done in Phase {X}.
```

Repeat the Phase block, with its Code Review, for every phase. Open Questions always comes last.
