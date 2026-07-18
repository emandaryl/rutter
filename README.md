# Rutter

Sailing directions for AI coding agents — a skill that scaffolds the agent-facing doc set for a
project (`AGENTS.md`, thin per-tool adapters, `.agent/docs/`, `.agent/features/`,
`.agent/skills/`), task by task, with the user approving every step.

> Keel sails for you. Rutter keeps you at the helm.

## What's in this folder

| Path | What it is |
|---|---|
| `rutter/` | The actual skill. `SKILL.md` is what an agent reads and executes; `START-HERE.md` is the human-facing quickstart; `templates/` holds every file template the skill fills in with real, project-specific content. |
| `rutter.zip` | The packaged skill — unzip into `~/.claude/skills/rutter/` (Claude Code) or `<repo>/rutter/` (any other tool). See `rutter/START-HERE.md` for both install paths. |
| `rutter-landing.html` | The marketing/landing page. |
| `rutter-howto.html` | The walkthrough page (linked from the landing page) — a worked example on an existing repo, the greenfield path, and an FAQ. |

## What Rutter does

Given a repo, Rutter detects on its own whether there's already code (**existing mode** — it
reads and documents what's actually there) or the folder is empty (**greenfield mode** — a short
intake stands in for discovery). Either way, it works one document at a time: propose what it's
about to write, the user answers **proceed**, **adjust**, or **skip**, then it writes exactly that
and moves to the next task. Nothing is written without that check-in first.

Every generated file (`AGENTS.md`, each adapter, each `.agent/docs/` file) is wrapped in
`<!-- rutter:begin --> … <!-- rutter:end -->` markers, so re-running Rutter later — after a stack
change, a new dependency, a new convention — updates only the content it originally wrote and
leaves anything hand-edited outside those markers untouched.

Full behavior spec: [`rutter/SKILL.md`](rutter/SKILL.md).

## Using it

- **Live in Claude Code?** Unzip `rutter.zip` into `~/.claude/skills/rutter/` (global) or
  `<repo>/.claude/skills/rutter/` (per-project). It triggers itself from then on — no invocation
  sentence needed.
- **Any other tool** (Cursor, Copilot, Gemini CLI, Windsurf, Aider, …): unzip `rutter.zip` into the
  repo you want documented as `<repo>/rutter/`, then paste into your assistant:
  ```
  Read rutter/SKILL.md and follow it against this repository.
  ```

## Regenerating the zip

After editing anything under `rutter/`, rebuild the archive from this directory:

```bash
find rutter -name ".DS_Store" -delete
zip -r rutter.zip rutter -x "*.DS_Store" "*.git*"
```

The `-x "*.git*"` exclusion matters if a `.git/` ever ends up inside `rutter/` — it shouldn't ship
in the distributed skill.
