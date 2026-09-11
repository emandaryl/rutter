---
name: rutter-doctor
description: >
  Audit and health-check an already-scaffolded AI-agent context system (AGENTS.md, adapters,
  .agent/docs/, .agent/features/, .agent/skills/) for drift, broken markers, dead references,
  ungrounded gaps, missing feature sections, orphaned feature folders, and context budget bloat.
  Reports findings without modifying files. Use when the user asks to "run rutter doctor",
  "audit AGENTS.md", "check for doc drift", "verify rutter markers", "is my AGENTS.md stale",
  or health-check agent docs in an existing repo.
---

# Rutter Doctor

A read-only diagnostic skill that audits an existing `AGENTS.md` context system for drift, rot, and
structural breaks.

While `rutter/SKILL.md` step 7 self-reconciles links immediately following a scaffold run, **Doctor's
job is catching drift that accumulates afterward** — as features get added or deleted by hand, files
move, markers get accidentally edited, and context files grow over time.

## Core Invariants

1. **Doctor reports; it never writes.** Doctor never silently repairs a broken marker, deletes a
   stale task file, or modifies documentation. Silently mutating context violates Rutter's core
   guarantee that the user remains at the helm. All repairs must be explicit follow-up actions
   approved by the user.
2. **Tool-agnostic execution.** Every check has a clear, manual grep/read-based procedure that works
   identically across any coding assistant (Claude Code, Cursor, Copilot, Gemini CLI, Windsurf,
   Roo/Cline, Aider) without requiring local scripts or executables.
3. **Severity tiers:**
   - `✓` **Pass** — Check fully satisfied; no issues found.
   - `⚠` **Warn** — Soft drift or non-breaking item: ungrounded `TODO(you)` gaps, context budget
     exceeding ~150–200 lines (soft guideline, never `✗`), or minor formatting irregularities.
   - `✗` **Fail** — Structural break: broken or missing `<!-- rutter:begin -->` / `<!-- rutter:end -->`
     markers, dead links or references to non-existent files, missing required sections in a
     `FEATURE.md`, orphaned feature folders lacking `FEATURE.md`, or invalid archive filenames.

---

## Check 1: Marker Integrity

Managed markers (`<!-- rutter:begin -->` and `<!-- rutter:end -->`) allow Rutter to re-run safely
without overwriting manual edits outside the managed blocks. This check verifies that every managed
file preserves intact markers.

### Files to check
- `AGENTS.md`
- Any present adapter file in the repo root:
  - `CLAUDE.md`
  - `GEMINI.md`
  - `.cursor/rules/project.mdc`
  - `.github/copilot-instructions.md`
  - `.windsurfrules`
  - `.clinerules`
  - `.aider.conventions.md`
- All files in `.agent/docs/*.md`

> **Note on adapters:** Repos typically configure a subset of the supported adapters. Doctor only
> checks the adapter files that actually exist on disk. Missing adapter files are normal and
> are **not** a finding.

### Procedure
1. For each target file, check position, not occurrence count: read the file's first non-blank
   line and last non-blank line.
2. Verify:
   - The first non-blank line is exactly `<!-- rutter:begin -->`.
   - The last non-blank line is exactly `<!-- rutter:end -->`.
3. If either boundary line doesn't match exactly, flag as `✗ Fail` with the specific file path and
   what was found instead. If both boundaries match, report `✓ Pass`.

> **Why position, not a raw count:** A naive `grep -c` for the marker strings anywhere in the file
> produces false failures — prose that mentions the marker syntax itself (e.g. explaining the
> managed-content convention in a "Coding Conventions" note) would count as an extra occurrence
> even though the file's actual managed boundaries are perfectly intact. Checking the literal
> first/last line is what the marker system actually depends on (see `rutter/SKILL.md`'s wrap/re-run
> logic), and it isn't fooled by an incidental mention mid-file.

---

## Check 2: Reference and Link Verification

A common drift mode is deleting or moving a file (such as a retired feature or refactored reference
doc) while stale pointers survive in `AGENTS.md`, `.agent/docs/`, or feature specs. This check
validates all referenced file paths.

### Scopes to extract references from
1. **`AGENTS.md` Task Files table:** Extract backtick-quoted file paths in table cells:
   `| <feature> | `<path>` | ... |`
2. **`AGENTS.md` Directory Tree code blocks:**
   - Lines in the `.agent/docs/` tree (e.g. `├── ARCHITECTURE.md`) → check `.agent/docs/<file>`.
   - Lines in the `.agent/features/` tree (e.g. `├── <slug>/` and child `FEATURE.md` / `TASKS.md` /
     `references/<file>`).
3. **Prose Markdown links:** All `[text](path)` links in:
   - `AGENTS.md`
   - All `.agent/docs/*.md`
   - All `.agent/features/<slug>/FEATURE.md`
   - All `.agent/features/<slug>/references/*.md`
4. **Skills Index:** All skill paths referenced in `.agent/skills/INDEX.md` (pointing to
   `.agent/skills/<name>/SKILL.md` or `.claude/skills/<name>/SKILL.md`).

### Procedure
1. Extract all target paths from the scopes above. Ignore external URLs (`http://`, `https://`,
   `mailto:`).
2. Resolve relative paths relative to the file containing the reference (or repo root for root docs).
3. Check whether the target file or directory exists on disk.
4. If any path does not exist, flag as `✗ Fail` listing the referring file, line number (if
   available), and the missing target path. If all references resolve, report `✓ Pass`.

---

## Check 3: Gap Audit

Rutter marks unknown facts as `TODO(you): <explanation>` rather than guessing. If a project was
scaffolded from a template, unreplaced `[FILL: ...]` tokens may also remain. This check audits
remaining gaps so the user knows what needs human attention.

### Procedure
1. Grep across `AGENTS.md`, all present adapter files, and the entire `.agent/` directory for:
   - `TODO(you):`
   - `[FILL:`
2. Tally total occurrences and group findings by file and line number.
3. If findings > 0: report `⚠ Warn` listing the count and specific locations. (This is a warning
   because ungrounded gaps do not break tooling, but need human answers.)
4. If 0 gaps found: report `✓ Pass`.

---

## Check 4: Living-Doc Health & Orphan Detection

The `.agent/features/` directory is the authoritative source of truth for feature-scoped agent work.
This check verifies feature completeness, orphan directories, and valid archiving.

### Procedure
1. **Orphaned Feature Folders:**
   - List only the immediate (direct-child) subdirectories of `.agent/features/` — each one is a
     feature slug, e.g. `.agent/features/<slug>/`. Do not recurse into a slug's own `references/` or
     `archive/` subfolders; those never contain a `FEATURE.md` and are normal, expected structure,
     not features in their own right.
   - Check if each feature slug directory contains a `FEATURE.md`.
   - If a feature slug directory exists without a `FEATURE.md`, flag as
     `✗ Fail: Orphaned feature folder without FEATURE.md`.
2. **Required Feature Sections:**
   - For every `.agent/features/<slug>/FEATURE.md`, verify the presence of all 4 required headers:
     - `## What This Feature Covers`
     - `## Architecture in One Paragraph`
     - `## Package Structure`
     - `## Known Gotchas`
   - If any required header is missing, flag as `✗ Fail` specifying which header is missing from
     which feature.
3. **Archive Naming Convention:**
   - For any files inside `.agent/features/<slug>/archive/`, verify they match one of the two
     canonical archive formats specified in `AGENTS.template.md`:
     - Version pattern: `TASKS-v*.md` (e.g. `TASKS-v1.0.md`)
     - Date pattern: `TASKS-YYYY-MM*.md` (e.g. `TASKS-2026-09.md`)
   - Any file in `archive/` not matching either pattern is flagged as `✗ Fail: Invalid archive filename`.
4. If all checks pass, report `✓ Pass`.

---

## Check 5: Context Budget

`AGENTS.md` is designed as a harbor chart, not an encyclopedia. Its budget applies to the
project-specific sections only — roughly ~150–200 lines — per `AGENTS.template.md`'s own "Context
Budget" note. The mandatory `[STANDARD]` process sections (Task Files, Feature Docs, Skills,
Creating-a-Feature) are fixed, copied-verbatim overhead of roughly 300 lines and are expected on
every file regardless of project size — they are not what this check is watching for. A typical,
healthy `AGENTS.md` therefore lands around 450–550 lines total; that is normal, not bloat.

### Procedure
1. Count the total lines in `AGENTS.md`.
2. Evaluation:
   - `<= 500 lines`: `✓ Pass` (project-specific content is within the expected budget).
   - `501–650 lines`: `⚠ Warn` — report the line count and suggest moving detailed architecture or
     feature-specific notes into `.agent/docs/` or `.agent/features/`.
   - `> 650 lines`: `⚠ Warn` — same as above, worded more strongly (the project-specific portion
     is now well over budget, not just near it).
3. **Severity note:** Context budget is an architectural guideline, not a syntax error. It is
   always reported as `⚠ Warn`, never `✗ Fail`.

---

## Output Report

At the conclusion of the audit, display a concise findings summary followed by actionable next steps.

### Example Report Output

```
=== RUTTER DOCTOR FINDINGS ===

✓ Check 1: Marker Integrity (9 files checked: AGENTS.md, CLAUDE.md, .cursor/rules/project.mdc, 6 docs)
✗ Check 2: Reference & Link Verification
  - AGENTS.md:244: Table references .agent/features/billing/TASKS.md (file not found)
  - .agent/docs/ARCHITECTURE.md:14: Link to .agent/docs/OLD_API.md (file not found)
⚠ Check 3: Gap Audit (2 items pending)
  - .agent/docs/ARCHITECTURE.md:42: TODO(you): specify staging cluster topology
  - AGENTS.md:88: [FILL: deployment target]
✗ Check 4: Living-Doc Health
  - .agent/features/auth/FEATURE.md: missing "## Known Gotchas"
  - .agent/features/temp-export/: orphaned feature folder (missing FEATURE.md)
  - .agent/features/auth/archive/notes.md: non-standard archive name (expected TASKS-v{N}.md or TASKS-YYYY-MM.md)
⚠ Check 5: Context Budget (218 lines — exceeds ~150–200 line target)
  - Suggestion: offload detailed sub-system diagrams into .agent/docs/

Overall: 2 checks passed · 2 warnings · 2 failures
```

---

## Actionable Remediation (Human-at-the-Helm)

Doctor does not edit files automatically. To resolve findings, guide your assistant using Rutter's
standard shorthand commands:

- **To fix dead feature references or missing gotchas:**
  ```
  Read AGENTS, {feature} and fix {issue}
  ```
  *Example:* `"Read AGENTS, auth and add Known Gotchas section for token refreshes"`

- **To refresh or re-scaffold drifted managed sections:**
  ```
  Read rutter/SKILL.md and follow it against this repository.
  ```

- **To resolve ungrounded gaps:**
  Search for `TODO(you)` across the repository and replace them with confirmed facts.
