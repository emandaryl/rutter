# rutter-managed: copied verbatim by Rutter to .claude/hooks/agent-bash-guard.py.
# Do not hand-edit; re-run Rutter to update. (A copy without this line is treated as hand-written
# and left alone.)
#
# PreToolUse hook logic for Claude Code sub-agents that have the Bash tool. Reads the hook JSON on
# stdin and allows (exit 0) or blocks (exit 2) the command. Run via agent-bash-guard.sh:
#   sh agent-bash-guard.sh <profile>
#   review  read-only git only (code-reviewer, doc-updater)
#   commit  review + `git add <paths>` and `git commit` (committer); no -A, amend, --no-verify
#   runner  any command except a deny-list of destructive ones and git writes (test-runner).
#           The deny-list catches mistakes; it is NOT a sandbox (a test script can run anything).
#           With .claude/hooks/agent-bash-allow.txt present, only listed prefixes run.
# Any internal error also exits 2: Claude Code treats other non-zero exits as non-blocking.
import json, os, re, shlex, sys

PROFILE = sys.argv[1] if len(sys.argv) > 1 else ""
READ_SUBS = {"diff", "log", "status", "show", "rev-parse", "blame", "ls-files",
             "merge-base", "rev-list", "shortlog", "diff-tree"}
COMMIT_SUBS = READ_SUBS | {"add", "commit"}
RUNNER_BAN = {"rm", "sudo", "su", "doas", "curl", "wget", "dd", "mkfs", "chmod", "chown",
              "kill", "killall", "pkill", "shutdown", "reboot", "ssh", "scp", "eval", "env", "xargs", "command", "builtin", "nohup", "-delete",
              "mv", "cp", "tee", "ln", "truncate", "rsync", "awk", "gawk", "mawk",
              "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprintf", "-fls"}
GIT_WRITE = {"push", "commit", "add", "reset", "clean", "checkout", "switch", "restore",
             "rebase", "merge", "stash", "cherry-pick", "revert", "tag", "branch", "pull",
             "fetch", "rm", "mv", "apply", "am", "config", "remote", "gc", "prune",
             "worktree", "submodule", "init", "clone", "update-ref", "filter-branch"}
CMD_BAN = {"source", ".", "exec", "install"}  # banned only as the command name: `ruff check .`,
# `docker compose exec`, `bundle exec` and `npm install` are fine
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish"}
INLINE = {"python": "c", "node": "ep", "nodejs": "ep", "perl": "eE", "ruby": "e", "php": "r",
          "lua": "e"}
INLINE_LONG = {"node": ("--eval", "--print"), "nodejs": ("--eval", "--print")}
SECRET_NAMES = re.compile(r"(^|/)(\.env($|\.)|id_[a-z0-9]+$|.*\.(pem|key|p12|pfx|keystore)$|"
                          r"\.npmrc$|\.netrc$|credentials(\.|$)|.*secrets?\.[a-z]+$)", re.I)
# VAR=value prefixes are allowed (DEBUG=1, PYTHONPATH=src, DATABASE_URL=...) except names that make
# a program load or run other code, or change which shell/tool runs.
UNSAFE_ENV = re.compile(r"^(LD_|DYLD_|GIT_|BASH|ENV$|PATH$|IFS$|SHELL$|PROMPT_COMMAND$|HOME$|"
                        r"PYTHONSTARTUP$|PYTHONHOME$|PERL5LIB$|RUBYLIB$|EDITOR$|VISUAL$|PAGER$|"
                        r"NPM_CONFIG_|.*_OPTIONS$|.*_OPTS$|.*OPT$)", re.I)
SCRIPT_EXT = (".py", ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl", ".php", ".lua")
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
        if is_opt(a, "--ext-diff", 5):
            deny("--ext-diff runs an external program and is not allowed")
    if sub == "add":
        for a in args:
            short = a.startswith("-") and not a.startswith("--")
            if a == "--":
                continue
            if (short and set(a[1:]) & set("Aufpie")) or is_opt(a, "--all") \
                    or is_opt(a, "--update") or is_opt(a, "--force") \
                    or is_opt(a, "--patch") or is_opt(a, "--interactive") \
                    or is_opt(a, "--edit") \
                    or a.startswith("--pathspec"):
                deny("%s is not allowed; stage specific files by path" % a)
            if not (short or a.startswith("--")) and SECRET_NAMES.search(a):
                deny("%r looks like a secret or credential file; do not stage it" % a)
            if short or a.startswith("--"):
                continue
            if a in {".", "./", "..", "*"} or a.startswith((":", "/", "../")) \
                    or "/../" in a or a.endswith("/") or any(c in a for c in "*?[") \
                    or os.path.isdir(os.path.join(cwd, a)):
                deny("stage specific files by path, not %r (directories, globs, pathspec "
                     "magic and paths outside the repo are blocked)" % a)
    if sub == "commit":
        pending = None  # option waiting for its value in the next argument
        for a in args:
            if pending is not None:
                check_commit_value(pending, a)
                pending = None
                continue
            if any(is_opt(a, n, 3) for n in ("--amend", "--no-verify", "--all")):
                deny("%s is not allowed" % a)
            if a.startswith("--"):
                name, eq, val = a.partition("=")
                if is_opt(name, "--template") or is_opt(name, "--author"):
                    deny("%s is not allowed" % name)
                if name in COMMIT_VALUE_LONG:
                    if eq:
                        check_commit_value(name, val)
                    else:
                        pending = name
            elif a.startswith("-") and len(a) > 1:
                for j, ch in enumerate(a[1:], 1):
                    if ch in COMMIT_VALUE_SHORT:
                        if ch == "t":
                            deny("-t (template) is not allowed")
                        if j == len(a) - 1:
                            pending = "-" + ch
                        else:
                            check_commit_value("-" + ch, a[j + 1:])
                        break
                    if ch in "an":
                        deny("%s (amend/-a/-n style flags) is not allowed" % a)


def check_commit_value(opt, val):
    if opt in ("-F", "--file") and (val.startswith(("/", "~", "-")) or ".." in val.split("/")):
        deny("%s must name a file inside the repo, not %r" % (opt, val))


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
            if UNSAFE_ENV.match(seg[0].split("=", 1)[0]):
                deny("setting %s is not allowed (it changes what code runs); other VAR=value "
                     "prefixes are fine" % seg[0].split("=", 1)[0])
            seg = seg[1:]
        if not seg:
            continue
        base = os.path.basename(seg[0])
        if seg[0] in CMD_BAN:
            deny("'%s' is not allowed as a command" % seg[0])
        if seg[0].startswith("$"):
            deny("a variable cannot be used as the command name")
        for k, tok in enumerate(seg):
            tb = os.path.basename(tok)
            if tb in SHELLS:
                deny("shells are not allowed for the test-runner agent (run the documented "
                     "command directly)")
            interp = re.sub(r"[\d.]+$", "", tb)
            letters = INLINE.get(interp)
            if letters:
                # interpreter flags end at the script or `-m module`; later flags are the script's
                opts = []
                for a in seg[k + 1:]:
                    if a == "-m" or a == "--" or a.endswith(SCRIPT_EXT):
                        break
                    opts.append(a)
                if any(a.startswith("-") and not a.startswith("--") and set(a[1:]) & set(letters)
                       for a in opts):
                    deny("inline code (%s -%s) is not allowed" % (tb, letters))
                if any(a.split("=", 1)[0] in INLINE_LONG.get(interp, ()) for a in opts):
                    deny("inline code (%s --eval/--print) is not allowed" % tb)
            if tb == "sed" and any(a == "--in-place" or a.startswith("--in-place=")
                                   or (a.startswith("-") and not a.startswith("--")
                                       and "i" in a) for a in seg[k + 1:]):
                deny("sed -i edits files and is not allowed")
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
