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
              "kill", "killall", "pkill", "shutdown", "reboot", "ssh", "scp", "eval", "-delete"}
GIT_WRITE = {"push", "commit", "add", "reset", "clean", "checkout", "switch", "restore",
             "rebase", "merge", "stash", "cherry-pick", "revert", "tag", "branch", "pull",
             "fetch", "rm", "mv", "apply", "am", "config", "remote", "gc", "prune",
             "worktree", "submodule", "init", "clone", "update-ref", "filter-branch"}
PUNCT = set("();<>|&")


def deny(msg):
    sys.stderr.write("agent-bash-guard (%s): %s\n" % (PROFILE, msg))
    sys.exit(2)


def is_opt(arg, name, minlen=4):
    """True if arg is name or an abbreviation git would accept (e.g. --no-ver)."""
    if not arg.startswith("--"):
        return False
    head = arg.split("=", 1)[0]
    return len(head) >= minlen and name.startswith(head)


def hazard(cmd, allow_var=False, allow_newline=False):
    """Quote-aware scan. Returns a message if the shell would expand or split something that
    token inspection cannot see: a backtick or `$` outside single quotes (command or variable
    substitution; `$VAR` is fine when allow_var) or a newline outside any quotes."""
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
        elif ch == '"':
            dq = not dq
        elif ch == "`" or (ch == "$" and not (allow_var and cmd[i + 1:i + 2] != "(")):
            return "backticks and $ expansion are not allowed outside single quotes"
        elif ch in "\r\n" and not dq and not allow_newline:
            return "raw newlines outside quotes are not allowed"
    return None


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


def check_allowlist(cmd, rows):
    cmd = re.sub(r"\d*>&\d+|\d*>\s*/dev/null", " ", cmd)
    segs, cur = [], []
    for t in tokens(cmd):
        if t in ("&&", ";", "||", "|"):
            segs.append(cur)
            cur = []
        elif t and set(t) <= PUNCT:
            deny("redirects and subshells are not allowed for the test-runner agent")
        else:
            cur.append(t)
    segs.append(cur)
    for seg in segs:
        while seg and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[0]):
            seg = seg[1:]
        if not seg:
            continue
        if not any(seg[:len(r)] == r for r in rows):
            deny("'%s' is not in .claude/hooks/agent-bash-allow.txt; add its prefix there if it "
                 "is a safe test/lint/build command" % " ".join(seg[:3]))


def tokens(cmd):
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    return list(lex)


def check_git(toks, allowed):
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
            if a in {".", "./", "*", ":/", "-A", "--all", "-u", "--update"} \
                    or is_opt(a, "--all") or is_opt(a, "--update") \
                    or (a.startswith("-") and not a.startswith("--") and set(a[1:]) & set("Au")):
                deny("stage specific files by path, not %s" % a)
    if sub == "commit":
        for a in args:
            if any(is_opt(a, n, 3) for n in ("--amend", "--no-verify", "--all")):
                deny("%s is not allowed" % a)
            if a.startswith("-") and not a.startswith("--"):
                for ch in a[1:]:
                    if ch in "mFCc":
                        break
                    if ch in "an":
                        deny("%s (amend/-a/-n style flags) is not allowed" % a)


def main():
    data = json.load(sys.stdin)
    if data.get("tool_name") is None:
        deny("hook input has no tool_name")
    if data.get("tool_name") != "Bash":
        return
    cmd = (data.get("tool_input") or {}).get("command")
    if not isinstance(cmd, str) or not cmd.strip():
        deny("no command to check")
    if PROFILE in ("review", "commit"):
        msg = hazard(cmd)
        if msg:
            deny(msg + " (single-quote text that needs them; repeat -m for more lines)")
        toks = tokens(cmd)
        if any(t and set(t) <= PUNCT for t in toks):
            deny("shell operators (; & | < > ( )) are not allowed; run one git command")
        check_git(toks, READ_SUBS if PROFILE == "review" else COMMIT_SUBS)
    elif PROFILE == "runner":
        msg = hazard(cmd, allow_var=True, allow_newline=True)
        if msg:
            deny(msg)
        toks = tokens(cmd)
        rows = load_allowlist()
        if rows is not None:
            check_allowlist(cmd, rows)
        for t in toks:
            if t in RUNNER_BAN:
                deny("'%s' is not allowed for the test-runner agent" % t)
        for i, t in enumerate(toks):
            if t == "git":
                nxt = toks[i + 1] if i + 1 < len(toks) else ""
                if nxt.startswith("-") or nxt in GIT_WRITE:
                    deny("git %s is not allowed for the test-runner agent" % nxt)
        for i, t in enumerate(toks):
            if t in ("sh", "bash", "zsh") and "-c" in toks[i + 1:i + 3]:
                deny("nested shell -c is not allowed")
    else:
        deny("unknown guard profile %r" % PROFILE)


try:
    main()
except SystemExit:
    raise
except BaseException as exc:
    sys.stderr.write("agent-bash-guard: internal error (%s); blocking\n" % exc)
    sys.exit(2)
