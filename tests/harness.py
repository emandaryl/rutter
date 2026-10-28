#!/usr/bin/env python3
"""Rutter test harness.

Two layers, both standard library only (no dependencies, no build step):

  harness.py self              — static consistency checks on THIS repo: the grep
                                 rituals CONTRIBUTING.md used to do by hand, as
                                 executable assertions.
  harness.py assert DIR        — post-run assertions on a scaffolded fixture copy:
                                 markers, leaked template tokens, adapter set,
                                 links, feature docs, migration fidelity, the
                                 source-fingerprint file. Reads the matching
                                 spec from tests/specs/<name>.json.

  run.sh orchestrates both plus the fixture workflow.
"""

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "rutter", "templates")
WORKDIR = ""  # set by assert_repo; rel() reports paths inside it relative to it

FAILS = []
WARNS = []


def fail(msg):
    FAILS.append(msg)


def warn(msg):
    WARNS.append(msg)


def rel(path):
    # paths inside an asserted workdir read better relative to that workdir
    global WORKDIR
    if WORKDIR and path.startswith(WORKDIR):
        return os.path.relpath(path, WORKDIR)
    return os.path.relpath(path, ROOT)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# --------------------------------------------------------------------------
# helpers shared by both layers
# --------------------------------------------------------------------------

def marker_positions(path):
    """Return (begin_lines, end_lines) of whole-line rutter markers, ignoring
    occurrences inside fenced code blocks."""
    begins, ends, in_fence = [], [], False
    for i, line in enumerate(read(path).splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped == "<!-- rutter:begin -->":
            begins.append(i)
        elif stripped == "<!-- rutter:end -->":
            ends.append(i)
    return begins, ends


def check_marker_pair(path, strict_first_last=False):
    name = rel(path)
    if not os.path.exists(path):
        fail(f"{name}: missing")
        return None
    begins, ends = marker_positions(path)
    if len(begins) != 1 or len(ends) != 1:
        fail(f"{name}: expected exactly one marker pair, found "
             f"{len(begins)} begin / {len(ends)} end")
        return None
    if begins[0] >= ends[0]:
        fail(f"{name}: begin marker not before end marker")
        return None
    lines = read(path).splitlines()
    if ends[0] - begins[0] < 2:
        fail(f"{name}: empty managed block")
    if strict_first_last:
        if begins[0] != 1:
            fail(f"{name}: begin marker is not the first line (line {begins[0]})")
        if ends[0] != len(lines):
            fail(f"{name}: end marker is not the last line (line {ends[0]} of {len(lines)})")
    return (begins[0], ends[0])


def marker_body(path):
    """Content between the marker pair, or None if the pair isn't sane."""
    begins, ends = marker_positions(path)
    if len(begins) != 1 or len(ends) != 1 or begins[0] >= ends[0]:
        return None
    return "\n".join(read(path).splitlines()[begins[0]: ends[0] - 1])


# --------------------------------------------------------------------------
# layer 1: self-checks on this repo
# --------------------------------------------------------------------------

def self_check():
    skill = read(os.path.join(ROOT, "rutter", "SKILL.md"))
    headings = set(re.findall(r"^#{3,4} (\d+[ab]?)\.\s", skill, re.M))

    # 1. frontmatter name matches directory
    for d in ("rutter", "rutter-doctor"):
        text = read(os.path.join(ROOT, d, "SKILL.md"))
        m = re.search(r"^name:\s*(\S+)", text, re.M)
        if not m or m.group(1) != d:
            fail(f"{d}/SKILL.md: frontmatter name ({m.group(1) if m else 'missing'}) "
                 f"does not match directory name '{d}'")

    # 2. step headings exist and every "step N" reference resolves
    expected_steps = {"0", "1", "2", "3", "3a", "3b", "4", "5", "6", "7"}
    missing = expected_steps - headings
    if missing:
        fail(f"rutter/SKILL.md: missing step headings: {sorted(missing)}")
    for ref in re.findall(r"[Ss]tep[s]? (\d+[ab]?)\b", skill):
        if ref not in headings:
            fail(f"rutter/SKILL.md: references 'step {ref}' but no '### {ref}.' heading exists")

    # 3. step references in templates also resolve against rutter/SKILL.md
    for base, _, names in os.walk(TEMPLATES):
        for name in names:
            if not name.endswith(".md"):
                continue
            p = os.path.join(base, name)
            for ref in re.findall(r"SKILL\.md step (\d+[ab]?)\b", read(p)):
                if ref not in headings:
                    fail(f"{rel(p)}: references 'SKILL.md step {ref}' which does not resolve")

    # 4. "N total" doc count in the References section matches templates/docs
    docs_dir = os.path.join(TEMPLATES, "docs")
    n_docs = len([n for n in os.listdir(docs_dir) if n.endswith(".template.md")])
    for t in re.findall(r"(\d+) total\b", skill):
        if int(t) != n_docs:
            fail(f"rutter/SKILL.md References says '{t} total' but rutter/templates/docs "
                 f"has {n_docs} templates")

    # 5. platform pack names in References match the template pack files
    packs_dir = os.path.join(TEMPLATES, "platform-packs")
    actual_packs = {n[:-3] for n in os.listdir(packs_dir) if n.endswith(".md")}
    for group in re.findall(r"platform-packs/\{([^}]+)\}\.md", skill):
        named = {n.strip() for n in group.split(",")}
        if named != actual_packs:
            fail(f"rutter/SKILL.md References names platform packs {sorted(named)} "
                 f"but rutter/templates/platform-packs holds {sorted(actual_packs)}")

    # 6. every *.template.md referenced in SKILL.md exists
    template_files = []
    for base, _, names in os.walk(TEMPLATES):
        template_files += [os.path.join(base, n) for n in names if n.endswith(".md")]
    for name in re.findall(r"([\w-]+\.template\.md)", skill):
        if not any(os.path.exists(os.path.join(os.path.dirname(f), name)) or f.endswith("/" + name)
                   for f in template_files):
            fail(f"rutter/SKILL.md references template '{name}' which does not exist")

    # 7. adapter paths consistent across SKILL.md, Doctor, CONTRIBUTING, ADAPTER template
    adapter_paths = ["CLAUDE.md", "GEMINI.md", ".cursor/rules/project.mdc",
                     ".github/copilot-instructions.md", ".windsurfrules",
                     ".clinerules", ".aider.conventions.md"]
    homes = {
        "rutter/SKILL.md step 0 list": skill,
        "rutter-doctor/SKILL.md Check 1": read(os.path.join(ROOT, "rutter-doctor", "SKILL.md")),
        "CONTRIBUTING.md format table": read(os.path.join(ROOT, "CONTRIBUTING.md")),
        "rutter/templates/ADAPTER.template.md": read(os.path.join(TEMPLATES, "ADAPTER.template.md")),
    }
    for home, text in homes.items():
        for p in adapter_paths:
            if p not in text:
                fail(f"{home}: adapter path '{p}' missing (every adapter home must list "
                     f"all paths — legacy files are still marker-checked)")

    # 8. step 4 evidence table rows all have a template
    for doc in re.findall(r"^\| `([A-Z]+\.md)` \|", skill, re.M):
        if not os.path.exists(os.path.join(docs_dir, doc.replace(".md", ".template.md"))):
            fail(f"rutter/SKILL.md step 4 evidence table lists '{doc}' but "
                 f"rutter/templates/docs/{doc.replace('.md', '.template.md')} is missing")

    # 9. Doctor's format expectations match the actual templates
    doctor = read(os.path.join(ROOT, "rutter-doctor", "SKILL.md"))
    feat_tpl = read(os.path.join(docs_dir, "FEATURE-CREATION.template.md"))
    for header in re.findall(r"- `## ([^`]+)`", doctor):
        if header not in feat_tpl:
            fail(f"rutter-doctor/SKILL.md requires FEATURE.md header '{header}' but "
                 f"FEATURE-CREATION.template.md has no such heading")
    task_tpl = read(os.path.join(docs_dir, "TASK-CREATION.template.md"))
    for token in ("> **Instructions for agents:**", "## Status Legend", "## Phase", "### Task"):
        if token not in doctor:
            fail(f"rutter-doctor/SKILL.md check 4 expects marker '{token}' preserved; "
                 f"was the check rewritten?")
        if token not in task_tpl:
            fail(f"rutter-doctor/SKILL.md and TASK-CREATION.template.md disagree: "
                 f"'{token}' is missing from the template")
    if "TASKS-v{N}.md" not in read(os.path.join(TEMPLATES, "AGENTS.template.md")) or "TASKS-v" not in doctor:
        fail("archive naming convention (TASKS-v{N}.md) is out of sync between "
             "AGENTS.template.md and rutter-doctor/SKILL.md")

    # 10. in-page and cross-page anchors on both HTML pages resolve
    for page in ("rutter-landing.html", "rutter-howto.html"):
        p = os.path.join(ROOT, page)
        html = read(p)
        ids = set(re.findall(r'id="([^"]+)"', html))
        for href in re.findall(r'href="#([^"]+)"', html):
            if href not in ids:
                fail(f"{page}: in-page anchor '#{href}' has no matching id")
        for target, anchor in re.findall(
                r'href="((?:rutter-landing|rutter-howto)\.html)#([^"]+)"', html):
            if target == page:
                continue
            other = read(os.path.join(ROOT, target))
            if anchor not in set(re.findall(r'id="([^"]+)"', other)):
                fail(f"{page}: cross-page anchor '{target}#{anchor}' has no matching id")

    print(f"self-check: {n_docs} doc templates, headings {sorted(headings)}, "
          f"packs {sorted(actual_packs)}")


# --------------------------------------------------------------------------
# layer 2: post-run assertions on a scaffolded fixture
# --------------------------------------------------------------------------

CODE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".swift", ".kt",
             ".m", ".mm", ".java", ".rb", ".css", ".scss", ".gradle", ".kts",
             ".xml", ".plist", ".sh"}
SKIP_DIRS = {"node_modules", "vendor", "dist", "build", ".git", ".agent",
             "rutter", "rutter-doctor", "ios", "android", "tests", "__tests__"}
SKIP_FILES = {"package-lock.json", "package.json", "pyproject.toml",
              "pnpm-lock.yaml", "uv.lock"}
FORBIDDEN_SLUGS_EXACT = {"core", "backend", "frontend", "server", "client",
                         "utils", "common", "shared", "misc", "other"}
FEATURE_HEADERS = ("## What This Feature Covers", "## Architecture in One Paragraph",
                   "## Package Structure", "## Known Gotchas")


def assert_repo(workdir):
    global WORKDIR
    workdir = os.path.normpath(os.path.abspath(workdir))
    WORKDIR = workdir
    spec_path = os.path.join(ROOT, "tests", "specs",
                             f"{os.path.basename(workdir)}.json")
    if not os.path.exists(spec_path):
        fail(f"no spec file tests/specs/{os.path.basename(workdir)}.json for workdir "
             f"'{os.path.basename(workdir)}' (fixtures are asserted from a copy named "
             f"after the fixture — see tests/run.sh)")
        return
    spec = json.loads(read(spec_path))

    agents = os.path.join(workdir, "AGENTS.md")
    docs_dir = os.path.join(workdir, ".agent", "docs")
    features_dir = os.path.join(workdir, ".agent", "features")
    skills_dir = os.path.join(workdir, ".agent", "skills")

    # --- the skill drop-ins: per SKILL.md ("Ignore Rutter itself") the run must
    # leave rutter/ in place and remind the user about it; warn, don't fail.
    for drop in ("rutter", "rutter-doctor"):
        if os.path.exists(os.path.join(workdir, drop)):
            warn(f"'{drop}/' is still present — expected: skill says never remove the drop-in "
                 f"itself, only remind the user it is safe to delete now")

    # --- AGENTS.md: exists, marker-wrapped; fresh-run markers are first/last lines
    check_marker_pair(agents, strict_first_last=True)

    # --- no unresolved template tokens anywhere; TODO(you) tallied against spec
    todo_files = []
    # marker-wrapped verbatim template copies (standard process docs copied straight
    # from templates, e.g. .agent/docs/TASK-CREATION.md) carry template-sanctioned
    # text only — a "TODO(you)" inside one is sample format text, never an agent
    # leaving an unresolved placeholder, so exempt them from the scan
    guide_tpl = {}
    for guide in ("FEATURE-CREATION", "TASK-CREATION", "SKILL-CREATION"):
        tpl = os.path.join(TEMPLATES, "docs", f"{guide}.template.md")
        if os.path.exists(tpl):
            guide_tpl[guide] = read(tpl).split("-->", 1)[1].strip()
    def is_verbatim_guide(path):
        begins, ends = marker_positions(path)
        if len(begins) != 1 or len(ends) != 1 or begins[0] >= ends[0]:
            return False
        lines = read(path).splitlines()
        # begins/ends are 1-based line numbers; content sits between them (exclusive)
        body = "\n".join(lines[begins[0] : ends[0] - 1]).strip()
        return any(body == tpl for tpl in guide_tpl.values())
    for base, name in md_walk(workdir):
        p = os.path.join(base, name)
        text = read(p)
        if "[FILL:" in text:
            fail(f"{rel(p)}: unresolved [FILL: ...] token leaked into output")
        inside = False
        for line in text.splitlines():
            if line.strip().startswith("```"):
                inside = not inside
                continue
            if not inside and "TODO(you):" in line:
                if is_verbatim_guide(p):
                    continue
                todo_files.append(rel(p))
    if todo_files and spec.get("todo_policy", "none") != "any":
        fail(f"TODO(you): left behind in {sorted(set(todo_files))} — spec allows none; "
             f"every fixture fact was written down for the run to find grounded")

    # --- adapter set exactly as specified
    for adb in spec["adapters_expected"]:
        p = os.path.join(workdir, adb)
        if not os.path.exists(p):
            fail(f"adapter '{adb}' expected but missing")
            continue
        check_marker_pair(p, strict_first_last=True)
    created = spec.get("adapters_may_exist", [])
    untouched = list(spec.get("untouched_exact", {}).keys())
    for adb in (["CLAUDE.md", "GEMINI.md", ".cursor/rules/project.mdc",
                 ".github/copilot-instructions.md", ".windsurfrules",
                 ".clinerules", ".aider.conventions.md"]):
        p = os.path.join(workdir, adb)
        if os.path.exists(p) and adb not in spec["adapters_expected"] + created + untouched:
            fail(f"adapter '{adb}' exists but spec expects it not to be created")

    # --- pre-existing markerless files must be byte-untouched
    for adb, sha in spec.get("untouched_exact", {}).items():
        p = os.path.join(workdir, adb)
        if not os.path.exists(p):
            fail(f"pre-existing file '{adb}' expected untouched but is missing")
            continue
        text = read(p)
        if "rutter:begin" in text or "rutter:end" in text:
            fail(f"pre-existing markerless file '{adb}' was marker-wrapped — overwrite happened")
        got = hashlib.sha256(text.encode()).hexdigest()[:12]
        if got != sha:
            fail(f"pre-existing file '{adb}' was modified (hash {got}, expected {sha})")

    # --- .agent/docs selection matches the evidence bars as recorded in the spec
    if (spec.get("docs_expected") or spec.get("docs_absent") or spec.get("docs_optional")) \
            and not os.path.isdir(docs_dir):
        fail(".agent/docs/ directory missing entirely")
        on_disk = []
    else:
        on_disk = sorted(n for n in os.listdir(docs_dir) if n.endswith(".md")) \
            if os.path.isdir(docs_dir) else []
    expected = spec.get("docs_expected", [])
    absent = spec.get("docs_absent", [])
    optional = spec.get("docs_optional", [])
    for name in expected:
        if name not in on_disk:
            fail(f".agent/docs: '{name}' expected but missing")
    for name in absent:
        if name in on_disk:
            fail(f".agent/docs: '{name}' exists but spec expects it absent (created without evidence?)")
    for name in on_disk:
        if name not in expected + optional and not name.endswith("-CREATION.md"):
            fail(f".agent/docs: unexpected file '{name}' (not in spec's expected/optional list)")
        if not name.endswith("-CREATION.md"):
            check_marker_pair(os.path.join(docs_dir, name), strict_first_last=True)
    guides_check(docs_dir)

    # --- features
    slugs = []
    if os.path.isdir(features_dir):
        slugs = sorted(d for d in os.listdir(features_dir)
                       if os.path.isdir(os.path.join(features_dir, d))
                       and not d.startswith("."))
    lo = spec.get("features", {}).get("min", 0)
    hi = spec.get("features", {}).get("max", 99)
    if not (lo <= len(slugs) <= hi):
        fail(f".agent/features: {len(slugs)} feature folders, spec allows {lo}–{hi}")
    for slug in slugs:
        if slug in FORBIDDEN_SLUGS_EXACT or re.fullmatch(r"(core-.*)|(.*-(backend|frontend))", slug):
            warn(f"feature slug '{slug}/' is named for a layer, not a capability — "
                 f"split by capability (plugin/module slugs mirroring a folder are fine)")
        feat = os.path.join(features_dir, slug, "FEATURE.md")
        if not os.path.exists(feat):
            fail(f".agent/features/{slug}/: orphaned folder without FEATURE.md")
            continue
        text = read(feat)
        for header in FEATURE_HEADERS:
            if header not in text:
                fail(f".agent/features/{slug}/FEATURE.md: missing required header '{header}'")
        tasks = os.path.join(features_dir, slug, "TASKS.md")
        if spec.get("features", {}).get("tasks", False) and not os.path.exists(tasks):
            fail(f".agent/features/{slug}/TASKS.md: expected in this mode but missing")
        if os.path.exists(tasks):
            ttext = read(tasks)
            for token in ("> **Instructions for agents:**", "## Status Legend", "## Phase"):
                if token not in ttext:
                    fail(f".agent/features/{slug}/TASKS.md: missing '{token}' "
                         f"(read TASK-CREATION.md and follow its format exactly)")

    # --- skills index (and cross-reference of fixture's .claude skills, if any)
    idx = os.path.join(skills_dir, "INDEX.md")
    if not os.path.exists(idx):
        fail(".agent/skills/INDEX.md missing")
    else:
        idx_text = read(idx)
        claude_dir = os.path.join(workdir, ".claude", "skills")
        if os.path.isdir(claude_dir):
            for name in os.listdir(claude_dir):
                if os.path.exists(os.path.join(claude_dir, name, "SKILL.md")) and name not in idx_text:
                    fail(f".agent/skills/INDEX.md: missing cross-reference row for "
                         f".claude/skills/{name}/ (cross-referenced, never duplicated)")

    # --- links in AGENTS.md resolve on disk (case-insensitive)
    if os.path.exists(agents):
        check_agents_links(workdir, agents)
        agents_text = read(agents)
        for needle in spec.get("must_mention", []):
            if needle not in agents_text:
                fail(f"AGENTS.md does not mention '{needle}' (spec says it is real)")

    # --- migration fidelity
    mig = spec.get("migration")
    if mig:
        old = os.path.join(workdir, "AGENTS.old.md")
        if not os.path.exists(old):
            fail("migration spec expects AGENTS.old.md (the backup); it was not created")
        else:
            oldtext = read(old)
            for rule in mig.get("rules", []):
                if rule not in oldtext:
                    warn(f"AGENTS.old.md backup is missing original rule substring: {rule}")
        generated = generated_corpus(workdir)
        for rule in mig.get("carried_forward", []):
            if rule.lower() not in generated.lower():
                fail(f"migration fidelity: rule substring '{rule}' not found in any generated "
                     f"doc — carrying rules forward is the whole point of Migrate")

    # --- coverage: significant source files must be mentioned somewhere
    if spec.get("coverage", True):
        cov = coverage_pass(workdir)
        if cov["missing"]:
            if cov["pct"] > 15:
                fail(f"coverage: {cov['pct']}% of significant source files are mentioned "
                     f"nowhere: {cov['missing']}")
            else:
                warn(f"coverage: {cov['pct']}% unmentioned (within 15% tolerance): {cov['missing']}")

    # --- source fingerprint state file
    state = os.path.join(workdir, ".agent", ".rutter-state.json")
    if not os.path.exists(state):
        fail(".agent/.rutter-state.json missing (step 7 must write it on every run)")
    else:
        try:
            data = json.loads(read(state))
        except json.JSONDecodeError as exc:
            fail(f".agent/.rutter-state.json is not valid JSON: {exc} (parse it as JSON, "
                 f"never by grepping the raw text)")
            data = None
        if data:
            if data.get("rutter") != 1:
                fail(".agent/.rutter-state.json: 'rutter' key must be 1")
            if not data.get("updated"):
                fail(".agent/.rutter-state.json: missing 'updated' date")
            files = data.get("files", {})
            if not files:
                fail(".agent/.rutter-state.json: 'files' fingerprint map is empty")
            for path, digest in files.items():
                if path.startswith(("rutter/", "rutter-doctor/")):
                    fail(f".agent/.rutter-state.json: fingerprints '{path}' — the skill's "
                         f"own folder must be excluded")
                abspath = os.path.join(workdir, path)
                if not os.path.exists(abspath):
                    fail(f".agent/.rutter-state.json: fingerprints non-existent file '{path}'")
                    continue
                got = hashlib.sha256(read(abspath).encode()).hexdigest()[:12]
                if got != digest:
                    fail(f".agent/.rutter-state.json: hash mismatch for '{path}' "
                         f"(recorded {digest}, actual {got} — stale fingerprint?)")

    if WARNS:
        print("warns:")
        for w in WARNS:
            print(f"  ⚠ {w}")


def md_walk(workdir):
    """All .md files under workdir excluding the skill drop-ins and noise —
    the skill-folders-cleanup assertion carries that signal on its own."""
    for base, dirs, names in os.walk(workdir):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git", "rutter", "rutter-doctor"}]
        for name in names:
            if name.endswith(".md"):
                yield base, name


def guides_check(docs_dir):
    troot = os.path.join(TEMPLATES, "docs")
    for guide in ("FEATURE-CREATION", "TASK-CREATION", "SKILL-CREATION"):
        gen = os.path.join(docs_dir, f"{guide}.md")
        tpl = os.path.join(troot, f"{guide}.template.md")
        if not os.path.exists(gen) or not os.path.exists(tpl):
            fail(f".agent/docs/{guide}.md or its template is missing")
            continue
        tpl_text = read(tpl)
        body = tpl_text.split("-->", 1)[1].strip() if tpl_text.startswith("<!--") else tpl_text.strip()
        got = marker_body(gen)
        if got is None:
            fail(f".agent/docs/{guide}.md: no usable marker block")
            continue
        if got.strip() != body:
            fail(f".agent/docs/{guide}.md: not verbatim from {guide}.template.md "
                 f"(guides are standard text — no project-specific edits allowed)")


def check_agents_links(workdir, agents):
    """Resolve paths mentioned in AGENTS.md against the filesystem, case-insensitively."""
    text = read(agents)
    mentioned = set()

    for m in re.findall(r"`(\.agent/[^`\s]+)`", text):
        mentioned.add(m.strip())

    # fenced trees: parse entries with the fence's section as the base dir
    inside = False
    current = None          # ".agent/docs" or ".agent/features"
    parent = None           # last <slug>/ line inside a feature tree
    for line in text.splitlines():
        if line.strip().startswith("```"):
            inside = not inside
            if not inside:
                current = parent = None
            continue
        if not inside:
            low = line.lower()
            if "app-wide docs" in low or "task files" in low:
                current = ".agent/docs" if "app-wide" in low else None
            elif "feature docs" in low:
                current = ".agent/features"
            continue
        if ".agent/" in line:  # the tree's root line, not an entry
            current = ".agent/docs" if ".agent/docs/" in line else ".agent/features"
            continue
        if current == ".agent/docs":
            for m in re.findall(r"[├└|]\s*─+\s*([\w.\-]+\.md)", line):
                mentioned.add(f".agent/docs/{m}")
        elif current == ".agent/features":
            slug_m = re.search(r"[├└]\s*─+\s*([\w.\-]+)/\s*$", line.rstrip())
            if slug_m:
                parent = slug_m.group(1)
                continue
            file_m = re.search(r"[├└]\s*─+\s*([\w.\-]+\.md)", line)
            if file_m and parent:
                mentioned.add(f".agent/features/{parent}/{file_m.group(1)}")
            sub_m = re.search(r"([\w.\-]+)/\s*$", line.rstrip())
            if sub_m and sub_m.group(1) != parent and not sub_m.group(1).endswith(".md"):
                mentioned.add(f".agent/features/{parent}/{sub_m.group(1)}")

    def resolve(path):
        if path.endswith("/"):
            return os.path.isdir(os.path.join(workdir, path.rstrip("/")))
        dirp, base = os.path.split(path)
        entries = os.listdir(os.path.join(workdir, dirp or "."))
        return any(e.lower() == base.lower() for e in entries)

    for path in sorted(mentioned):
        if any(ch in path for ch in "{}<>*… "):
            continue  # template placeholders, truncations, multi-entries
        try:
            ok = resolve(path)
        except FileNotFoundError:
            ok = False
        if not ok:
            fail(f"AGENTS.md references '{path}' which does not exist on disk "
                 f"(a skipped doc/feature must not leave a dangling link)")


def generated_corpus(workdir):
    """Generated doc text only: AGENTS.md + everything under .agent/**.md.
    Pre-existing hand-written docs (README, AGENTS.old.md, .claude skills) are
    deliberately excluded — migration fidelity and coverage are judged against
    what Rutter's output itself says."""
    parts = []
    agents = os.path.join(workdir, "AGENTS.md")
    if os.path.exists(agents):
        parts.append(read(agents))
    agent_dir = os.path.join(workdir, ".agent")
    for base, dirs, names in os.walk(agent_dir):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git"}]
        for name in names:
            if name.endswith(".md"):
                try:
                    parts.append(read(os.path.join(base, name)))
                except OSError:
                    pass
    return "\n".join(parts)


def coverage_pass(workdir):
    files = []
    for base, dirs, names in os.walk(workdir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in names:
            stem, ext = os.path.splitext(name)
            if ext not in CODE_EXTS or name in SKIP_FILES or stem.startswith("."):
                continue
            files.append(os.path.relpath(os.path.join(base, name), workdir))
    corpus = generated_corpus(workdir).lower()
    missing = [f for f in files
               if f.lower() not in corpus
               and os.path.basename(f).lower() not in corpus]
    pct = round(100 * len(missing) / len(files)) if files else 0
    return {"pct": pct, "missing": missing, "total": len(files)}


# --------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("self", "assert") \
            or (sys.argv[1] == "assert" and len(sys.argv) != 3):
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "self":
        self_check()
    else:
        assert_repo(sys.argv[2])
    if FAILS:
        print("FAIL:")
        for f in FAILS:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("all assertions passed")
