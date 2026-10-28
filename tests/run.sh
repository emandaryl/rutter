#!/bin/sh
# Rutter test harness runner. Usage:
#
#   tests/run.sh self             — static consistency checks on this repo
#   tests/run.sh fixture <name>   — copy a fixture to $TMPDIR/rutter-work/<name>,
#                                   drop rutter/ in, print the drive instructions
#   tests/run.sh assert <workdir> — post-run assertions on a scaffolded copy
#   tests/run.sh assert <name>    — shorthand for $TMPDIR/rutter-work/<name>
#
# `self` needs nothing but python3. `fixture`/`assert` support the two-step
# fixture flow: a human (or agent) drives the actual Rutter run, the harness
# then asserts on what was produced.

set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
HARNESS="$ROOT/tests/harness.py"
SPEC="$ROOT/tests/specs"
FIXTURES="$ROOT/tests/fixtures"

usage() {
    sed -n '2,12p' "$0"
    exit 2
}

resolve_target() {
    if [ -d "$1" ]; then
        echo "$1"
    elif [ -d "${TMPDIR:-/tmp}/rutter-work/$1" ]; then
        echo "${TMPDIR:-/tmp}/rutter-work/$1"
    else
        echo "no workdir '$1' under \${TMPDIR}/rutter-work and not an existing directory" >&2
        exit 2
    fi
}

case "${1:-}" in
self)
    python3 "$HARNESS" self
    ;;
check-harness)
    # Exercise the assertion layer itself: a mock scaffold of the `empty`
    # fixture must pass; each deliberately-broken variant must fail. Each
    # variant gets a fresh directory (never rmtree-and-reuse) so the run is
    # not sensitive to filesystem caching behavior.
    MOCKS="$ROOT/tests/mocks"
    MBASE="${TMPDIR:-/tmp}/rutter-mock"
    rm -rf "$MBASE"
    pass_dir="$MBASE/empty"
    python3 "$MOCKS/build_mock_scaffold.py" "$pass_dir" >/dev/null
    if python3 "$HARNESS" assert "$pass_dir" >/dev/null 2>&1; then
        echo "check-harness: pass case ok"
    else
        echo "check-harness: FAIL — the unbroken mock does not pass; harness bug" >&2
        python3 "$HARNESS" assert "$pass_dir" || true
        exit 1
    fi
    for broken in token dangling tasks hash adapter; do
        broken_dir="$MBASE/break-$broken/empty"
        python3 "$MOCKS/build_mock_scaffold.py" "$broken_dir" "$broken" >/dev/null
        if python3 "$HARNESS" assert "$broken_dir" >/dev/null 2>&1; then
            echo "check-harness: FAIL — broken case '$broken' was not detected" >&2
            exit 1
        fi
        echo "check-harness: break '$broken' correctly detected"
    done
    ;;
fixture)
    [ -n "${2:-}" ] || usage
    [ -d "$FIXTURES/$2" ] || { echo "no fixture named '$2' (have: $(ls "$FIXTURES"))" >&2; exit 2; }
    WORK="${TMPDIR:-/tmp}/rutter-work/$2"
    rm -rf "$WORK"
    mkdir -p "$WORK"
    cp -R "$FIXTURES/$2/." "$WORK/"
    cp -R "$ROOT/rutter" "$WORK/rutter"
    echo "workdir: $WORK"
    echo
    echo "drive instructions:"
    while IFS= read -r line; do echo "  $line"; done < "$SPEC/$2.md"
    echo
    echo "when the run has finished, assert the scaffold:"
    echo "  tests/run.sh assert $2"
    ;;
assert)
    [ -n "${2:-}" ] || usage
    TARGET=$(resolve_target "$2") || exit 2
    python3 "$HARNESS" assert "$TARGET"
    ;;
*)
    usage
    ;;
esac
