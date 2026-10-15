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
1. For each target file, find the **marker lines**: lines that consist of nothing but
   `<!-- rutter:begin -->` or `<!-- rutter:end -->` (ignoring surrounding whitespace) and that are
   not inside a fenced code block.
2. Verify:
   - Exactly one begin-marker line and exactly one end-marker line exist.
   - The begin marker comes before the end marker.
   - There is managed content between them.
3. Content **outside** the markers (above the begin line or below the end line) is the user's own
   hand-written notes. It is expected and allowed: never flag it, and never require the markers to
   be the first or last line of the file. Rutter's own re-run logic replaces only what is between
   the markers.
4. If a marker is missing, duplicated, out of order, or the block is empty, flag `✗ Fail` with the
   file and what was found. Otherwise report `✓ Pass`.

> **Why whole-line marker matching:** a raw `grep -c` counts prose that merely mentions the marker
> syntax (e.g. in a "Coding Conventions" note), giving false failures. Matching only whole-line
> markers outside code fences ignores such mentions, and not caring about the file's first and last
> lines lets users keep their own notes around the managed block.

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
   Also ignore paths that only appear in `[STANDARD]` sections or fenced code blocks as generic
   examples or placeholders (e.g. `.agent/skills/<skill-name>/SKILL.md`, `TASKS-v{N}.md`); resolve
   only paths that name a real file the project is meant to have.
2. Resolve relative paths relative to the file containing the reference (or repo root for root docs).
3. Check whether the target file or directory exists on disk, comparing names case-insensitively (a
   tree entry `ARCHITECTURE.md` resolves to an on-disk `architecture.md`). A case-only difference is
   `✓ Pass`, optionally noted; it is not a missing file.
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
   **Ignore text that Rutter copies verbatim.** The `.agent/docs/*-CREATION.md` guides are standard text throughout, so skip them entirely; and `AGENTS.md` contains `[STANDARD]` sections (Task
   Files, Feature Docs, Skills, Creating-a-Feature, and the shared-abstractions rule) whose text
   legitimately mentions `TODO(you)` and `[FILL:` as instructions, usually inside code fences. Skip
   any hit that is (a) inside a fenced code block, (b) inside a `[STANDARD]` section, or (c) a
   backticked mention (`` `TODO(you)` ``) rather than a line that starts a gap. A real gap is a
   line in a project-specific section of the form `TODO(you): <explanation>`, or an unreplaced
   `[FILL: ...]` token outside any code fence. If unsure, report the hit as "likely a mention,
   not a gap" instead of counting it.
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
4. **TASKS.md structure:**
   - For every `.agent/features/<slug>/TASKS.md` (not files under `archive/`), verify it has a
     `> **Instructions for agents:**` block, a `## Status Legend` section, and at least one `## Phase`
     heading containing a `### Task` heading. A missing piece is `✗ Fail`, naming the file and what is
     missing. The format lives in `.agent/docs/TASK-CREATION.md`. **If that guide does not exist** because
     the repo has another canonical format owner (the `AGENTS.md` pointer names a skill or doc
     elsewhere), check against that owner's format instead where it states required headings, and
     downgrade every miss to `⚠ Warn`: the structure belongs to the owner, not to Rutter.
   - Items from the newer format that older task files may predate are `⚠ Warn`, never `✗ Fail`: no
     `## Open Questions` section, or a phase with no `### Phase {N} Code Review` checklist.
5. If nothing is flagged, report `✓ Pass`.

---

## Check 5: Context Budget

`AGENTS.md` is designed as a harbor chart, not an encyclopedia. Its budget applies to the
project-specific sections only — roughly ~150–200 lines — per `AGENTS.template.md`'s own "Context
Budget" note. The mandatory `[STANDARD]` process sections (Task Files, Feature Docs, Skills,
Creating-a-Feature) are fixed, copied-verbatim overhead of roughly 170 lines and are expected on every file regardless of project size — they are not what this check is watching for. A typical, healthy `AGENTS.md` therefore lands around 250–350 lines total; that is normal, not bloat. (A repo scaffolded before the creation guides existed still carries the format specs inline and lands around 450–550 lines; it will warn here until Rutter is re-run, which moves those specs out to `.agent/docs/*-CREATION.md`.)

### Procedure
1. Count the total lines in `AGENTS.md`.
2. Evaluation:
   - `<= 400 lines`: `✓ Pass` (project-specific content is within the expected budget).
   - `401–500 lines`: `⚠ Warn` — report the line count and suggest moving detailed architecture or
     feature-specific notes into `.agent/docs/` or `.agent/features/`.
   - `> 500 lines`: `⚠ Warn` — same as above, worded more strongly (the project-specific portion
     is now well over budget, not just near it).
3. **Severity note:** Context budget is an architectural guideline, not a syntax error. It is
   always reported as `⚠ Warn`, never `✗ Fail`.

---

## Check 6: Migration Fidelity

Only runs when `AGENTS.old.md` exists in the repo root (Rutter's backup of a hand-written
`AGENTS.md` it migrated). If it does not exist, skip this check and print `- Check 6: skipped (no
AGENTS.old.md)`. Migration must not lose rules, so this check compares the old file to the new docs.

### Procedure
1. Read `AGENTS.old.md` and list its discrete rules: bullets, numbered items, "never/always/must"
   sentences, commands, paths, and gotchas. Ignore headings and filler.
2. For each rule, search the new `AGENTS.md`, `.agent/docs/*.md` and `.agent/features/**/*.md` for
   the same meaning (exact wording is not required; a rule that was condensed or moved counts as
   kept). Match on specific terms (file names, commands, flags), not just topic.
3. Report `✓ Pass` if every rule is found. Otherwise report `⚠ Warn` with the count, and list each
   rule not found with its line number in `AGENTS.old.md`, so the user can restore it or confirm it
   was dropped on purpose. This is a warning, not a failure: Doctor cannot judge intent.
4. Also report the total: "N of M rules found".

---

## Check 7: Feature Boundaries & Coverage

Check 4 verifies that feature docs exist and have headers. This check asks whether the features are
*good*: split by capability, covering the code, and written from the code. Always a `⚠ Warn`,
never a `✗ Fail`, because it is a judgement about quality.

### Procedure
1. **Layer or catch-all slugs.** Flag any `.agent/features/<slug>/` whose slug is named for a
   technology layer or a catch-all: `core`, `core-*`, `backend`, `frontend`, `*-backend`,
   `*-frontend`, `server`, `client`, `utils`, `common`, `shared`, `misc`, `other`. Report it as "named
   for a layer, not a capability — split by capability". Plugin/module slugs that mirror a folder
   (`plugin-logs`) are fine.
2. **Coverage.** List the repo's significant source files (exclude `node_modules`, `vendor/`,
   build output such as `dist/` and `build/`, lockfiles, tests, `rutter/`, `rutter-doctor/`, and
   generated files, `tsconfig*.json` and hash files such as `.source-hash`). For each, check whether its path or filename appears in some `FEATURE.md`
   (Package Structure) or in `AGENTS.md`. Report the files mentioned nowhere, grouped by folder.
   If more than ~15% of significant files are unmentioned, say so plainly.
3. **Overlap.** Treat brace lists such as `frontend/src/{main,api,theme}.ts` as naming each
   expanded path (`main.ts`, `api.ts`, `theme.ts`) when checking coverage and overlap. Match files by their **full repo-relative path** (`plugins/logs/backend.py`), never
   by bare filename: many plugins legitimately share names like `backend.py`, `frontend.ts`,
   `plugin.json` and `style.css`, and a bare-name match is a false positive. Flag a path claimed in
   the Package Structure of three or more features. Then classify it:
   - **Shared file with ownership notes (info, not a defect):** every feature that claims the file
     also names the specific functions, handlers, classes or sections it uses from it (e.g. "route
     handlers `r_add`, `r_dismiss`" or "the Registry class"). Size does not matter: a 150-line
     config module and a 700-line UI file are both fine if the notes are there. Report it as `ℹ`
     and do not count it toward the warning.
   - **Possible boundary problem (warn):** at least one claiming feature lists the file with no
     specifics (a bare file name or a vague "uses config.py"), so the split cannot be checked, or a
     small single-purpose file is claimed by three or more features. Advise adding the function or
     section names to those features, or reconsidering the boundary.
4. **Thin docs.** For each `FEATURE.md`, compare its size to the code it owns. Flag one whose body
   (excluding frontmatter and blank lines) is under ~20 lines while its owning files total over
   ~400 lines, and any feature with no `> Needs verification:` note whose Package Structure lists
   only file names with no responsibility text.
5. Report `✓ Pass` if nothing is flagged; otherwise `⚠ Warn` listing each flagged slug or file and
   the reason.

---

## Check 8: Source Fingerprint (Staleness)

Rutter records a fingerprint of the source tree in `.agent/.rutter-state.json` at the end of each
run. This check tells you whether the code has changed since, i.e. whether the docs may be stale.
Always `⚠ Warn` at worst, never `✗ Fail`.

### Procedure
1. If `.agent/.rutter-state.json` is missing, report `⚠ Warn: no fingerprint (run Rutter once to
   record one)` and stop.
2. Recompute the same short hashes (first 12 hex chars of SHA-256; or size and modification time if
   that is what the file recorded) for the files it lists, and also find significant source files
   that are not in it. Do not modify the state file.
3. Report `✓ Pass` if nothing changed. Otherwise `⚠ Warn` listing changed, added and removed files
   (group by folder if more than ~15) and advise: "docs may be stale for these files; re-run
   Rutter".

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
⚠ Check 5: Context Budget (612 lines — well over the ~400 line budget)
  - Suggestion: offload detailed sub-system diagrams into .agent/docs/
⚠ Check 6: Migration Fidelity (10 of 11 rules found)
  - AGENTS.old.md:17: "never add a default launcher" not found in the new docs
⚠ Check 7: Feature Boundaries & Coverage
  - .agent/features/core-backend/: named for a layer, not a capability
  - backend/ports.py, backend/external.py: not mentioned in any FEATURE.md

Overall: 2 checks passed · 2 warnings · 2 failures
```

**This block illustrates the report's format only** — indentation, grouping, the final tally line.
Every check's own symbol (`✓`/`⚠`/`✗`) must come from applying that check's procedure to what you
actually found, never copied from this example. In particular: a `401+`-line `AGENTS.md` (shown above) does warrant `⚠` on Check 5, but a file at or under 400 lines is `✓ Pass`, full stop — don't
print `⚠` and then explain in prose that it's really a pass. Likewise Check 6 is `✓ Pass` the moment
every rule is found (this example's "10 of 11" is a warn only because one rule is genuinely
missing) — "N of N found" is always `✓`, never a hedged `⚠` with a note that it doesn't really
count.

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
