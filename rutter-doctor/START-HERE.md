# Rutter Doctor — Start Here

Rutter Doctor audits an existing project's AI-agent context system (`AGENTS.md`, adapters,
`.agent/docs/`, `.agent/features/`, `.agent/skills/`) for drift, broken markers, dead links, and
budget bloat. It is read-only by default; ask it to fix and it will apply low-risk repairs after you
approve them (see "Fix Mode" below).

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

Doctor runs ten non-destructive checks against your documentation. The core ones:

1. **Marker integrity** — confirms managed markers (`<!-- rutter:begin/end -->`) are intact.
2. **Reference & link verification** — verifies every file path in tables, trees, and markdown links
   resolves to an actual file on disk.
3. **Gap audit** — tallies ungrounded `TODO(you)` items and template tokens.
4. **Living-doc health** — validates required feature sections, checks for orphaned feature folders,
   and verifies skill/archive conventions.
5. **Context budget** — warns if `AGENTS.md` is exceeding its line budget.
6. **Migration fidelity**, 7. **Feature boundaries**, 8. **Source fingerprint**, 9. **Standard sections**, 10. **Sub-agents** — catch lost content after a migration, mis-scoped feature docs, a stale scaffold, an `AGENTS.md` missing standard sections newer Rutter versions add, and missing or malformed `.claude/agents/` and `.codex/agents/` files.

By default Doctor **reports only and never writes**. When findings are reported, you remain at the
helm — resolve them using standard Rutter shorthand:

```
Read AGENTS, {feature} and fix {issue}
```

## Fix Mode

Say "run rutter doctor and fix it" and Doctor audits first, then sorts findings into three tiers:

- **A — mechanical** (e.g. a link whose file moved to exactly one new place, a missing required
  `FEATURE.md` header): shown as a diff, approved once as a batch.
- **B — needs your decision** (orphaned folders, ambiguous dead links, bad archive names): asked one
  at a time with concrete options.
- **C — never auto-fixed** (gaps, budget, staleness, missing sub-agents/hooks, unpaired markers):
  listed with the recommended next step, usually re-running Rutter.

Doctor edits narrowly, never invents facts, never commits, re-checks what it touched, and asks first
if the files have uncommitted changes. Review `git diff` afterwards.
