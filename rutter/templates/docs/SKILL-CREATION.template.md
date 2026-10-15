<!-- Always created, in Task 2, alongside AGENTS.md. Standard process doc: copy it verbatim — it carries no project-specific content, so there is nothing to fill in. Wrapped in rutter markers on write like every .agent/docs/ file. Delete this comment when done. -->

# Creating a Skill

How to capture a recurring, multi-step *procedure* — not project context, that's a feature — so any tool or agent can follow it correctly: a release process, a codegen step, a data-migration script, an onboarding checklist. Follow the format below exactly.

## Steps

1. Create `.agent/skills/<slug>/` and write its `SKILL.md` in the format below.
2. Add its row to `.agent/skills/INDEX.md`: one line, what it does and when to load it. A skill that has to live elsewhere to work (e.g. a Claude Code skill at `.claude/skills/<name>/SKILL.md`) gets a row pointing there instead of a copy.
3. Add `references/` or `scripts/` only once real supporting material or an actual automatable step exists — never preemptively. If you add `scripts/`, follow the no-script fallback rule below.

## Folder layout

```
.agent/skills/
├── INDEX.md                     ← one line per skill: name, when to use it
└── <skill-name>/
    ├── SKILL.md                 ← instructions, written in tool-agnostic language
    ├── references/              ← optional supporting docs (protocol detail, worked examples)
    └── scripts/                 ← optional automation — see the no-script fallback rule below
```

## SKILL.md format

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

## The no-script fallback rule

If a skill's `scripts/` folder contains an automation script, `SKILL.md`'s "Steps" section must
also spell out the manual equivalent — a numbered fallback, not just a bare "run
`scripts/foo.sh`" line. Not every environment an agent runs in can execute a local script
(sandboxing, a missing runtime, a different OS); the manual fallback is what keeps the skill
usable everywhere the script isn't. Don't create `scripts/` preemptively — add it only once a
real automatable step exists, the same evidence bar `references/` gets in Feature Docs above.
