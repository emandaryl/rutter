# Rutter — Start Here

Rutter generates the agent-facing doc set for a project — `AGENTS.md`, thin per-tool adapters,
`.agent/docs/`, `.agent/features/`, `.agent/skills/` — task by task, with you approving every step.

This file is for you, the human who just unzipped this folder. The actual instructions an agent
follows live in `SKILL.md` — you don't need to read that one yourself, just point an agent at it.

## Pick your path

### Claude Code — install once, use everywhere

Unzip this folder into your skills directory:

```
# global — every project
~/.claude/skills/rutter/

# or per-project
<repo>/.claude/skills/rutter/
```

From then on, Rutter triggers itself whenever you ask for agent docs in any repo you open — no
invocation sentence needed.

### Any other tool — Cursor, Copilot, Gemini CLI, Windsurf, Aider, etc.

Unzip this folder straight into the repo you want documented:

```
<repo>/rutter/
```

Then paste this into your assistant:

```
Read rutter/SKILL.md and follow it against this repository.
```

Delete the `rutter/` folder afterward, or keep it around for re-runs later.

**Which should you pick?** If you live in Claude Code, install the skill — it stays out of your
repos entirely. The drop-in folder is for everything else.

## What happens next

Once invoked, Rutter detects on its own whether the repo already has code (existing mode — it
reads and documents what's there) or is empty (greenfield mode — a short intake instead). Either
way, it works one document at a time: propose what it's about to write, you answer **proceed**,
**adjust**, or **skip**, then it writes exactly that and moves to the next one. Nothing is written
without that check-in first.

Run it again later — after a stack change, a new dependency, a new convention — and it updates only
the content it originally wrote, leaving anything you've hand-edited alone.

## Effortless maintenance afterward

Once generated, your codebase becomes dramatically easier to maintain with AI agents. You don't have to re-explain the architecture or paste dozens of lines of context. Just command any agent:

```
"Read AGENTS, {feature} and fix {issue}"
"Read AGENTS, {feature} and work on {task}"
```

For example:
- `"Read AGENTS, auth and fix the session expiration issue"`
- `"Read AGENTS, checkout and work on refund support"`

The agent follows `AGENTS.md` to resolve the feature, inspects its `FEATURE.md` and Known Gotchas, respects boundaries, and updates documentation as it finishes.

## Auditing and health checks

To check an already-scaffolded repo for drift, dead links, broken markers, ungrounded gaps, or context bloat, see `rutter-doctor/START-HERE.md` or invoke:

```
Read rutter-doctor/SKILL.md and follow it against this repository.
```
