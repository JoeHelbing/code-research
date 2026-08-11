#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER="$SCRIPT_DIR/serve-page.sh"
TEST_ROOT="$(mktemp -d)"
OUTSIDE_FILE="$(dirname "$TEST_ROOT")/playground-outside-$$.html"
STALE_PID=""
RACE_PID=""

cleanup() {
	(
		cd "$TEST_ROOT"
		"$SERVER" --stop >/dev/null 2>&1 || true
	)
	if [[ -n "$RACE_PID" ]] && kill -0 "$RACE_PID" >/dev/null 2>&1; then
		kill "$RACE_PID" >/dev/null 2>&1 || true
		wait "$RACE_PID" 2>/dev/null || true
	fi
	if [[ -n "$STALE_PID" ]] && kill -0 "$STALE_PID" >/dev/null 2>&1; then
		kill "$STALE_PID" >/dev/null 2>&1 || true
		wait "$STALE_PID" 2>/dev/null || true
	fi
	rm -rf "$TEST_ROOT"
	rm -f "$OUTSIDE_FILE"
}
trap cleanup EXIT

fail() {
	printf 'FAIL: %s\n' "$1" >&2
	exit 1
}

mkdir -p "$TEST_ROOT/reports"
printf '<!doctype html><title>Root marker</title>\n' >"$TEST_ROOT/index.html"
printf '<!doctype html><title>Nested marker</title>\n' >"$TEST_ROOT/reports/demo page.html"
printf '<!doctype html><title>Outside marker</title>\n' >"$OUTSIDE_FILE"
printf '<!doctype html><title>Inside marker</title>\n' >"$TEST_ROOT/inside.html"
ln -s "$OUTSIDE_FILE" "$TEST_ROOT/leak.html"

cd "$TEST_ROOT"
root_key="$(printf '%s' "$TEST_ROOT" | cksum | awk '{print $1}')"
state_dir="${TMPDIR:-/tmp}/code-research-playground/$root_key"

root_url="$($SERVER index.html)"
[[ "$root_url" == http://127.0.0.1:*/* ]] || fail "server did not return a loopback URL"
curl -fsS "$root_url" | grep -Fq 'Root marker' || fail "root page was not served"

nested_url="$($SERVER 'reports/demo page.html')"
curl -fsS "$nested_url" | grep -Fq 'Nested marker' || fail "nested page with spaces was not served"

base_url="${root_url%/index.html}"
if curl -fsS "$base_url/leak.html" >/dev/null 2>&1; then
	fail "server followed a symlink outside the workspace"
fi

(
	for ((i = 0; i < 20000; i++)); do
		ln -sfn "$TEST_ROOT/inside.html" "$TEST_ROOT/race.html"
		ln -sfn "$OUTSIDE_FILE" "$TEST_ROOT/race.html"
	done
) &
RACE_PID=$!
for ((i = 0; i < 3000; i++)); do
	body="$(curl -sS --max-time 1 "$base_url/race.html" 2>/dev/null || true)"
	if [[ "$body" == *'Outside marker'* ]]; then
		fail "server exposed an outside file during a symlink swap"
	fi
done
wait "$RACE_PID" 2>/dev/null || true
RACE_PID=""

if "$SERVER" "$OUTSIDE_FILE" >/dev/null 2>&1; then
	fail "server accepted a file outside the workspace"
fi

$SERVER --stop >/dev/null
[[ ! -e "$state_dir" ]] || fail "server stop left temporary state behind"

mkdir -p "$TEST_ROOT/fake-bin"
printf '#!/usr/bin/env bash\nexit 42\n' >"$TEST_ROOT/fake-bin/uv"
chmod +x "$TEST_ROOT/fake-bin/uv"
if PATH="$TEST_ROOT/fake-bin:$PATH" "$SERVER" index.html >/dev/null 2>&1; then
	fail "server unexpectedly started with a failing uv launcher"
fi
[[ ! -e "$state_dir" ]] || fail "failed server start left temporary state behind"

mkdir -p "$state_dir"
sleep 30 &
STALE_PID=$!
printf '%s\n' "$STALE_PID" >"$state_dir/pid"
printf '%s\n' '9' >"$state_dir/port"
printf '%s\n' "$TEST_ROOT" >"$state_dir/root"
printf '%s\n' 'stale-nonce' >"$state_dir/nonce"

$SERVER --stop >/dev/null
kill -0 "$STALE_PID" >/dev/null 2>&1 || fail "server stop killed an unrelated stale PID"
kill "$STALE_PID" >/dev/null 2>&1 || true
wait "$STALE_PID" 2>/dev/null || true
STALE_PID=""

printf 'PASS: playground preview server\n'
