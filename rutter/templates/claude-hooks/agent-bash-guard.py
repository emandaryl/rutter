# rutter-managed: copied verbatim by Rutter to .claude/hooks/agent-bash-guard.py.
# Do not hand-edit; re-run Rutter to update. (A copy without this line is treated as hand-written
# and left alone.)
#
# PreToolUse hook logic for Claude Code sub-agents that have the Bash tool. Reads the hook JSON on
# stdin and allows (exit 0) or blocks (exit 2) the command. Run via agent-bash-guard.sh:
#   sh agent-bash-guard.sh <profile>
#   review  read-only git only (code-reviewer, doc-updater)
#   commit  review + `git add <paths>` and `git commit` (committer); no -A, amend, --no-verify
#   runner  any command except a deny-list of destructive ones and git writes (test-runner)
# Any internal error also exits 2: Claude Code treats other non-zero exits as non-blocking.
import json, os, re, shlex, sys

PROFILE = sys.argv[1] if len(sys.argv) > 1 else ""
READ_SUBS = {"diff", "log", "status", "show", "rev-parse", "blame", "ls-files",
             "merge-base", "rev-list", "shortlog", "diff-tree"}
COMMIT_SUBS = READ_SUBS | {"add", "commit"}
RUNNER_BAN = {"rm", "sudo", "su", "doas", "curl", "wget", "dd", "mkfs", "chmod", "chown",
              "kill", "killall", "pkill", "shutdown", "reboot", "ssh", "scp", "eval", "env", "xargs", "exec", "command", "builtin", "nohup", "-delete"}
GIT_WRITE = {"push", "commit", "add", "reset", "clean", "checkout", "switch", "restore",
             "rebase", "merge", "stash", "cherry-pick", "revert", "tag", "branch", "pull",
             "fetch", "rm", "mv", "apply", "am", "config", "remote", "gc", "prune",
             "worktree", "submodule", "init", "clone", "update-ref", "filter-branch"}
CMD_BAN = {"source", "."}  # banned only as the command name (`ruff check .` is fine)
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish"}
INLINE = {"python": "c", "node": "ep", "nodejs": "ep", "perl": "eE", "ruby": "e", "php": "r",
          "lua": "e"}
SAFE_ENV = {"CI", "FORCE_COLOR", "NO_COLOR", "TERM", "TZ", "LANG", "LC_ALL", "NODE_ENV"}
SEPARATORS = {"&&", ";", "||", "|"}
PUNCT = set("();<>|&")
COMMIT_VALUE_SHORT = set("mFCct")
COMMIT_VALUE_LONG = ("--message", "--file", "--reuse-message", "--reedit-message", "--author",
                     "--date", "--cleanup", "--template", "--trailer", "--fixup", "--squash")


def deny(msg):
    sys.stderr.write("agent-bash-guard (%s): %s\n" % (PROFILE, msg))
    sys.exit(2)


def is_opt(arg, name, minlen=4):
    """True if arg is name or an abbreviation git would accept (e.g. --no-ver)."""
    if not arg.startswith("--"):
        return False
    head = arg.split("=", 1)[0]
    return len(head) >= minlen and name.startswith(head)


def scan(cmd, ops=False, allow_var=False):
    """Quote-aware scan of the raw command for things the shell acts on but token inspection
    cannot see. Returns a message, or None. Always rejected outside single quotes: backticks and
    `$(`, `$'`, `${` (and any `$` unless allow_var). Rejected outside all quotes: raw newlines
    and, when ops is set, shell operators and braces (; & | < > ( ) { })."""
    sq = dq = esc = False
    for i, ch in enumerate(cmd):
        if esc:
            esc = False
            continue
        if ch == "\\" and not sq:
            esc = True
            continue
        if sq:
            sq = ch != "'"
            continue
        if ch == "'" and not dq:
            sq = True
            continue
        if ch == '"':
            dq = not dq
            continue
        if ch == "`":
            return "backticks are only allowed inside single quotes"
        if ch == "$" and (not allow_var or cmd[i + 1:i + 2] in ("(", "'", "{", '"')):
            return "$ expansion is only allowed inside single quotes"
        if not dq:
            if ch in "\r\n":
                return "raw newlines outside quotes are not allowed (use one command per call)"
            if ops and ch in ";&|<>(){}":
                return "shell operators (; & | < > ( ) { }) are not allowed; run one git command"
    return None


def tokens(cmd, punct):
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=punct)
    lex.whitespace_split = True
    lex.commenters = ""  # shlex would otherwise drop everything after a mid-word '#'
    return list(lex)


def check_git(toks, allowed, cwd):
    if len(toks) < 2 or toks[0] != "git":
        deny("only git commands are allowed for this agent")
    sub, args = toks[1], toks[2:]
    if sub.startswith("-"):
        deny("git global options before the subcommand are not allowed")
    if sub not in allowed:
        deny("git %s is not allowed for this agent" % sub)
    for a in args:
        if is_opt(a, "--output"):
            deny("--output writes files and is not allowed")
    if sub == "add":
        for a in args:
            short = a.startswith("-") and not a.startswith("--")
            if a == "--":
                continue
            if (short and set(a[1:]) & set("Auf")) or is_opt(a, "--all") \
                    or is_opt(a, "--update") or is_opt(a, "--force") \
                    or a.startswith("--pathspec"):
                deny("%s is not allowed; stage specific files by path" % a)
            if short or a.startswith("--"):
                continue
            if a in {".", "./", "..", "*"} or a.startswith((":", "/", "../")) \
                    or "/../" in a or a.endswith("/") or any(c in a for c in "*?[") \
                    or os.path.isdir(os.path.join(cwd, a)):
                deny("stage specific files by path, not %r (directories, globs, pathspec "
                     "magic and paths outside the repo are blocked)" % a)
    if sub == "commit":
        skip = False
        for a in args:
            if skip:
                skip = False
                continue
            if any(is_opt(a, n, 3) for n in ("--amend", "--no-verify", "--all")):
                deny("%s is not allowed" % a)
            if a.startswith("--"):
                skip = a in COMMIT_VALUE_LONG
            elif a.startswith("-") and len(a) > 1:
                for j, ch in enumerate(a[1:], 1):
                    if ch in COMMIT_VALUE_SHORT:
                        skip = j == len(a) - 1
                        break
                    if ch in "an":
                        deny("%s (amend/-a/-n style flags) is not allowed" % a)


def strip_redirects(toks):
    """Drop harmless redirects: 2>&1, >&2, >/dev/null, 2>/dev/null, >>/dev/null."""
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        n1 = toks[i + 1] if i + 1 < len(toks) else ""
        n2 = toks[i + 2] if i + 2 < len(toks) else ""
        if re.fullmatch(r"\d+", t) and n1 == ">&" and re.fullmatch(r"\d+|-", n2):
            i += 3
        elif t == ">&" and re.fullmatch(r"\d+|-", n1):
            i += 2
        elif re.fullmatch(r"\d+", t) and n1 in (">", ">>") and n2 == "/dev/null":
            i += 3
        elif t in (">", ">>") and n1 == "/dev/null":
            i += 2
        else:
            out.append(t)
            i += 1
    return out


def load_allowlist():
    """Optional per-project allowlist for the runner profile: one command prefix per line
    (`npm test`, `pytest`), `#` comments. Absent file = deny-list mode only."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent-bash-allow.txt")
    if not os.path.isfile(path):
        return None
    rows = []
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if line:
            rows.append(line.split())
    return rows


def check_runner(cmd, rows):
    toks = strip_redirects(tokens(cmd, True))
    segs, cur = [], []
    for t in toks:
        if t in SEPARATORS:
            segs.append(cur)
            cur = []
        elif t and set(t) <= PUNCT:
            deny("redirects, background jobs and subshells are not allowed for the "
                 "test-runner agent (only 2>&1 and >/dev/null)")
        else:
            cur.append(t)
    segs.append(cur)
    for n, seg in enumerate(segs):
        while seg and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[0]):
            if seg[0].split("=", 1)[0] not in SAFE_ENV:
                deny("setting %s is not allowed (allowed: %s)"
                     % (seg[0].split("=", 1)[0], ", ".join(sorted(SAFE_ENV))))
            seg = seg[1:]
        if not seg:
            continue
        base = os.path.basename(seg[0])
        if seg[0] in CMD_BAN:
            deny("'%s' is not allowed as a command" % seg[0])
        if seg[0].startswith("$"):
            deny("a variable cannot be used as the command name")
        if base in SHELLS:
            if n > 0:
                deny("piping into a shell is not allowed")
            if any(a.startswith("-") and not a.startswith("--") and "c" in a for a in seg[1:]):
                deny("shell -c is not allowed")
        letters = INLINE.get(re.sub(r"[\d.]+$", "", base))
        if letters and any(a.startswith("-") and not a.startswith("--")
                           and set(a[1:]) & set(letters) for a in seg[1:]):
            deny("inline code (%s -%s) is not allowed" % (base, letters))
        if rows is not None and not any(seg[:len(r)] == r for r in rows):
            deny("'%s' is not in .claude/hooks/agent-bash-allow.txt; add its prefix there if it "
                 "is a safe test/lint/build command" % " ".join(seg[:3]))
    for i, t in enumerate(toks):
        base = os.path.basename(t)
        if base in RUNNER_BAN:
            deny("'%s' is not allowed for the test-runner agent" % t)
        if base == "git":
            nxt = toks[i + 1] if i + 1 < len(toks) else ""
            if nxt.startswith("-") or nxt in GIT_WRITE:
                deny("git %s is not allowed for the test-runner agent" % nxt)


def main():
    data = json.load(sys.stdin)
    if data.get("tool_name") is None:
        deny("hook input has no tool_name")
    if data.get("tool_name") != "Bash":
        return
    cmd = (data.get("tool_input") or {}).get("command")
    if not isinstance(cmd, str) or not cmd.strip():
        deny("no command to check")
    cwd = data.get("cwd") if isinstance(data.get("cwd"), str) else os.getcwd()
    if PROFILE in ("review", "commit"):
        msg = scan(cmd, ops=True)
        if msg:
            deny(msg + " (single-quote text that needs them; repeat -m for more lines)")
        check_git(tokens(cmd, False), READ_SUBS if PROFILE == "review" else COMMIT_SUBS, cwd)
    elif PROFILE == "runner":
        msg = scan(cmd, allow_var=True)
        if msg:
            deny(msg)
        check_runner(cmd, load_allowlist())
    else:
        deny("unknown guard profile %r" % PROFILE)


try:
    main()
except SystemExit:
    raise
except BaseException as exc:
    sys.stderr.write("agent-bash-guard: internal error (%s); blocking\n" % exc)
    sys.exit(2)
