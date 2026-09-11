# Rutter Doctor — Start Here

Rutter Doctor audits an existing project's AI-agent context system (`AGENTS.md`, adapters,
`.agent/docs/`, `.agent/features/`, `.agent/skills/`) for drift, broken markers, dead links, and
budget bloat — completely read-only.

This file is for you, the human. The actual instructions an agent follows live in `SKILL.md` — point
an agent at it or install it into your skills directory.

## Pick your path

### Claude Code — install once, use everywhere

Copy this folder into your skills directory:

```
# global — every project
~/.claude/skills/rutter-doctor/

# or per-project
<repo>/.claude/skills/rutter-doctor/
```

From then on, Doctor triggers itself whenever you ask to "run rutter doctor", "audit AGENTS.md", or
"check for doc drift" — no invocation sentence needed.

### Any other tool — Cursor, Copilot, Gemini CLI, Windsurf, Roo/Cline, Aider, etc.

Copy this folder into the repo you want audited:

```
<repo>/rutter-doctor/
```

Then paste this into your assistant:

```
Read rutter-doctor/SKILL.md and follow it against this repository.
```

## What happens next

Doctor runs five non-destructive checks against your documentation:

1. **Marker integrity** — confirms managed markers (`<!-- rutter:begin/end -->`) are intact.
2. **Reference & link verification** — verifies every file path in tables, trees, and markdown links
   resolves to an actual file on disk.
3. **Gap audit** — tallies ungrounded `TODO(you)` items and template tokens.
4. **Living-doc health** — validates required feature sections, checks for orphaned feature folders,
   and verifies skill/archive conventions.
5. **Context budget** — warns if `AGENTS.md` is exceeding its ~150–200 line guideline.

Doctor **reports only and never writes**. When findings are reported, you remain at the helm —
resolve them using standard Rutter shorthand:

```
Read AGENTS, {feature} and fix {issue}
```
