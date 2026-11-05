#!/usr/bin/env python3
"""Build a hand-crafted mock scaffold of the `empty` fixture — a stand-in for
what a Rutter run against tests/fixtures/empty/ should produce. Used by
tests/run.sh check-harness to exercise the assertion layer itself (both the
pass case and a deliberately-broken negative case), without needing a real
agent run.

This is a test double, not generated output: it must stay in sync with
tests/specs/empty.json and the guide templates.
"""

import hashlib
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def wrap(body):
    return "<!-- rutter:begin -->\n" + body.strip() + "\n<!-- rutter:end -->\n"


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def build(work):
    shutil.rmtree(work, ignore_errors=True)
    docs = os.path.join(work, ".agent", "docs")
    cli = os.path.join(work, ".agent", "features", "cli")

    write(os.path.join(work, "README.md"),
          open(os.path.join(ROOT, "tests", "fixtures", "empty", "README.md")).read())

    # guides: verbatim template body between markers (leading comment removed)
    for guide in ("FEATURE-CREATION", "TASK-CREATION", "SKILL-CREATION"):
        tpl = open(os.path.join(ROOT, "rutter", "templates", "docs",
                                f"{guide}.template.md")).read()
        body = tpl.split("-->", 1)[1].strip()
        write(os.path.join(docs, f"{guide}.md"), wrap(body))

    # state file, parsed and hash-consistent
    readme = os.path.join(work, "README.md")
    sha = hashlib.sha256(open(readme, "rb").read()).hexdigest()[:12]
    write(os.path.join(work, ".agent", ".rutter-state.json"),
          json.dumps({"rutter": 1, "updated": "2026-10-28",
                      "files": {"README.md": sha}}, indent=1) + "\n")

    # adapters
    for tool, name in (("Claude Code", "CLAUDE.md"), ("Gemini CLI", "GEMINI.md")):
        write(os.path.join(work, name), wrap(
            f"# {tool} Instructions\n\n"
            "Read `AGENTS.md` at the repo root before doing anything else — it is the source\n"
            "of truth for this project. This file is intentionally just a pointer."))

    # Claude Code sub-agents: verbatim templates (frontmatter, then marker-wrapped body)
    for agent in ("explorer", "doc-updater", "test-runner", "task-tracker", "committer", "code-reviewer"):
        tpl = open(os.path.join(ROOT, "rutter", "templates", "claude-agents",
                                f"{agent}.template.md")).read()
        write(os.path.join(work, ".claude", "agents", f"{agent}.md"), tpl)

    # Codex sub-agents (optional group): verbatim TOML templates
    for agent in ("repo_explorer", "test_runner", "doc_updater"):
        tpl = open(os.path.join(ROOT, "rutter", "templates", "codex-agents",
                                f"{agent}.template.toml")).read()
        write(os.path.join(work, ".codex", "agents", f"{agent}.toml"), tpl)

    os.makedirs(os.path.join(work, ".claude", "hooks"), exist_ok=True)
    for hk in ("agent-bash-guard.sh", "agent-bash-guard.py"):
        shutil.copy(os.path.join(ROOT, "rutter", "templates", "claude-hooks", hk),
                    os.path.join(work, ".claude", "hooks", hk))

    # AGENTS.md — markers first and last; only links that will exist
    write(os.path.join(work, "AGENTS.md"), wrap("\n".join([
        "# AGENTS.md — Brew log",
        "",
        "## What Brew Log Is",
        "",
        "A command-line tool for tracking coffee-brew settings: beans, grind, ratio,",
        "time, tasting notes.",
        "",
        "## App-Wide Docs [STANDARD]",
        "",
        "```",
        ".agent/docs/",
        "├── OVERVIEW.md          ← what the project is, scope, feature map",
        "├── ARCHITECTURE.md      ← deeper technical flow than the summary above",
        "├── FEATURE-CREATION.md  ← how to add a feature or a references/ file",
        "├── TASK-CREATION.md     ← how to write a TASKS.md",
        "└── SKILL-CREATION.md    ← how to add a skill",
        "```",
        "",
        "## Task Files — Feature-Specific Work Tracking [STANDARD]",
        "",
        "| Feature | Task file |",
        "|---|---|",
        "| cli | `.agent/features/cli/TASKS.md` |",
        "",
        "## Feature Docs — Feature-Specific Context [STANDARD]",
        "",
        "```",
        ".agent/features/",
        "└── cli/",
        "    ├── FEATURE.md",
        "    └── TASKS.md",
        "```",
        "",
        "## Skills",
        "",
        "Check `.agent/skills/INDEX.md` first.",
        "",
        "## Creating a Feature / Reference / Task / Skill",
        "",
        "| To add… | Read first |",
        "|---|---|",
        "| A new feature | `.agent/docs/FEATURE-CREATION.md` |",
        "| A TASKS.md | `.agent/docs/TASK-CREATION.md` |",
        "",
        "## Delegation & Token Efficiency [STANDARD]",
        "",
        "Hand broad searches to the `explorer` agent and post-task doc updates to `doc-updater`.",
        "",
        "## After Every Task: Keep the Docs Current [STANDARD]",
        "",
        "Update the matching FEATURE.md and any touched `.agent/docs/` file in the same change.",
    ])))

    write(os.path.join(docs, "OVERVIEW.md"), wrap("\n".join([
        "# OVERVIEW.md — Brew log",
        "",
        "A command-line tool for tracking coffee-brew settings: beans, grind, ratio,",
        "time, tasting notes.",
    ])))

    # one deliberate TODO(you): the stack was left open at intake, so this is
    # the allowed, canonical TODO — not invented content
    write(os.path.join(docs, "ARCHITECTURE.md"), wrap("\n".join([
        "# ARCHITECTURE.md — Brew log",
        "",
        "Single-binary CLI, stdlib-first.",
        "",
        "TODO(you): stack decision pending — recorded as an open slot, not invented.",
    ])))

    write(os.path.join(cli, "FEATURE.md"), "\n".join([
        "## What This Feature Covers",
        "The record/query CLI (list, add, query brews).",
        "",
        "## Architecture in One Paragraph",
        "Stdlib-first single binary: commands parse args, read the brew file, print.",
        "",
        "## Package Structure",
        "(laid out once first code exists)",
        "",
        "## Known Gotchas",
        "(none yet)",
    ]))

    write(os.path.join(cli, "TASKS.md"), "\n".join([
        "# TASKS.md — cli",
        "",
        "> **Instructions for agents:**",
        "> - Read `AGENTS.md` and `.agent/features/cli/FEATURE.md` first.",
        "",
        "## Status Legend",
        "",
        "| Mark | Meaning |",
        "|---|---|",
        "| `[ ]` | Not started |",
        "",
        "## Phase 1 — boot",
        "",
        "> **Goal:** runtime decided and hello-world standing",
        "",
        "### Task 1.1 — pick the runtime",
        "- [ ] decide runtime",
    ]))

    write(os.path.join(work, ".agent", "skills", "INDEX.md"),
          "| Skill | Path |\n|---|---|\n")

    return work


def break_spec(work, which):
    """Introduce one canonical defect for the negative case."""
    if which == "token":
        p = os.path.join(work, ".agent", "docs", "OVERVIEW.md")
        txt = open(p).read().replace("# OVERVIEW.md", "[FILL: Oops]\n# OVERVIEW.md", 1)
        open(p, "w").write(txt)
    elif which == "dangling":
        p = os.path.join(work, "AGENTS.md")
        txt = open(p).read().replace(
            "└── SKILL-CREATION.md", "├── SKILL-CREATION.md\n└── TESTING.md", 1)
        open(p, "w").write(txt)
    elif which == "tasks":
        p = os.path.join(work, ".agent", "features", "cli", "TASKS.md")
        txt = open(p).read().replace("## Status Legend", "## Legend", 1)
        open(p, "w").write(txt)
    elif which == "hash":
        p = os.path.join(work, ".agent", ".rutter-state.json")
        data = json.load(open(p))
        data["files"]["README.md"] = "000000000000"
        open(p, "w").write(json.dumps(data))
    elif which == "adapter":
        # a tool with no evidence got an adapter that the spec doesn't expect
        write(os.path.join(work, ".windsurfrules"),
              wrap("# Windsurf Instructions\n\nRead `AGENTS.md` first."))
    else:
        raise SystemExit(f"unknown break: {which}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: build_mock_scaffold.py <workdir> [break:{'token,dangling,tasks,hash,adapter'}]")
        sys.exit(2)
    work = build(sys.argv[1])
    if len(sys.argv) > 2:
        break_spec(work, sys.argv[2])
    print(work)
