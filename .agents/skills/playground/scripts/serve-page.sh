#!/usr/bin/env bash
set -euo pipefail

usage() {
	cat >&2 <<'USAGE'
Usage: serve-page.sh [--open|--no-open] [html-file]
       serve-page.sh --stop

Serve an HTML artifact from the current Git repository on 127.0.0.1.
The file defaults to index.html and must stay inside the repository.
The browser remains closed unless --open or PLAYGROUND_OPEN=1 is set.
USAGE
}

OPEN_BROWSER="${PLAYGROUND_OPEN:-0}"
STOP_SERVER=0
REQUESTED_FILE=""

while [[ $# -gt 0 ]]; do
	case "$1" in
	--open)
		OPEN_BROWSER=1
		;;
	--no-open)
		OPEN_BROWSER=0
		;;
	--stop)
		STOP_SERVER=1
		;;
	-h | --help)
		usage
		exit 0
		;;
	-*)
		printf 'playground: unknown option: %s\n' "$1" >&2
		usage
		exit 2
		;;
	*)
		if [[ -n "$REQUESTED_FILE" ]]; then
			usage
			exit 2
		fi
		REQUESTED_FILE="$1"
		;;
	esac
	shift
done

if [[ $STOP_SERVER -eq 1 && -n "$REQUESTED_FILE" ]]; then
	usage
	exit 2
fi

if git_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
	ROOT_DIR="$(cd "$git_root" && pwd -P)"
else
	ROOT_DIR="$(pwd -P)"
fi

root_key="$(printf '%s' "$ROOT_DIR" | cksum | awk '{print $1}')"
STATE_DIR="${TMPDIR:-/tmp}/code-research-playground/$root_key"
PID_FILE="$STATE_DIR/pid"
PORT_FILE="$STATE_DIR/port"
ROOT_FILE="$STATE_DIR/root"
NONCE_FILE="$STATE_DIR/nonce"
LOG_FILE="$STATE_DIR/server.log"
mkdir -p "$STATE_DIR"

state_server_is_alive() {
	[[ -s "$PID_FILE" && -s "$PORT_FILE" && -s "$ROOT_FILE" && -s "$NONCE_FILE" ]] || return 1
	[[ "$(cat "$ROOT_FILE")" == "$ROOT_DIR" ]] || return 1
	pid="$(cat "$PID_FILE")"
	port="$(cat "$PORT_FILE")"
	nonce="$(cat "$NONCE_FILE")"
	kill -0 "$pid" >/dev/null 2>&1 || return 1
	response="$(curl -fsS --max-time 1 "http://127.0.0.1:$port/.playground-health/$nonce" 2>/dev/null)" || return 1
	[[ "$response" == "$nonce" ]]
}

remove_state() {
	rm -f "$PID_FILE" "$PORT_FILE" "$ROOT_FILE" "$NONCE_FILE" "$LOG_FILE"
	rmdir "$STATE_DIR" >/dev/null 2>&1 || true
}

stop_server() {
	if state_server_is_alive; then
		pid="$(cat "$PID_FILE")"
		kill "$pid" >/dev/null 2>&1 || true
		for _ in {1..30}; do
			kill -0 "$pid" >/dev/null 2>&1 || break
			sleep 0.1
		done
	fi
	remove_state
}

if [[ $STOP_SERVER -eq 1 ]]; then
	stop_server
	printf 'playground: preview server stopped\n'
	exit 0
fi

REQUESTED_FILE="${REQUESTED_FILE:-index.html}"
if [[ "$REQUESTED_FILE" = /* ]]; then
	candidate="$REQUESTED_FILE"
else
	candidate="$ROOT_DIR/$REQUESTED_FILE"
fi

if [[ ! -f "$candidate" ]]; then
	printf 'playground: page not found: %s\n' "$candidate" >&2
	exit 1
fi

HTML_FILE="$(realpath "$candidate")"
case "$HTML_FILE" in
"$ROOT_DIR"/*) ;;
*)
	printf 'playground: refusing to serve a file outside %s\n' "$ROOT_DIR" >&2
	exit 1
	;;
esac

case "$HTML_FILE" in
*.html | *.htm) ;;
*)
	printf 'playground: expected an HTML file: %s\n' "$HTML_FILE" >&2
	exit 1
	;;
esac

if ! command -v uv >/dev/null 2>&1; then
	printf 'playground: uv is required to run the local preview server\n' >&2
	exit 1
fi

server_is_alive() {
	state_server_is_alive
}

start_server() {
	stop_server
	mkdir -p "$STATE_DIR"
	: >"$LOG_FILE"
	nonce="$(printf '%s:%s:%s:%s' "$ROOT_DIR" "$$" "$RANDOM" "$(date +%s%N)" | cksum | awk '{print $1}')"
	printf '%s\n' "$nonce" >"$NONCE_FILE"

	uv run --no-project python - "$ROOT_DIR" "$PORT_FILE" "$nonce" <<'PY' >>"$LOG_FILE" 2>&1 &
import functools
import http.server
import os
import pathlib
import socketserver
import stat
import sys
import typing
from urllib.parse import unquote, urlsplit

root: pathlib.Path = pathlib.Path(sys.argv[1]).resolve()
port_file: pathlib.Path = pathlib.Path(sys.argv[2])
nonce: str = sys.argv[3]
health_path: str = f"/.playground-health/{nonce}"
open_flags: int = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
root_fd: int = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)


class SafeHandler(http.server.SimpleHTTPRequestHandler):
    def request_path(self) -> str:
        return unquote(urlsplit(self.path).path)

    def request_parts(self) -> list[str]:
        parts = [
            part
            for part in pathlib.PurePosixPath(self.request_path()).parts
            if part not in {"/", "."}
        ]
        if not parts:
            return ["index.html"]
        if ".." in parts or any(
            part == ".git" or part.startswith(".env") for part in parts
        ):
            raise ValueError("blocked preview path")
        return parts

    def open_request_file(self) -> tuple[typing.BinaryIO, os.stat_result, str]:
        parts = self.request_parts()
        current_fd = os.dup(root_fd)
        try:
            for part in parts:
                next_fd = os.open(part, open_flags, dir_fd=current_fd)
                os.close(current_fd)
                current_fd = next_fd

            file_stat = os.fstat(current_fd)
            display_path = "/".join(parts)
            if stat.S_ISDIR(file_stat.st_mode):
                next_fd = os.open("index.html", open_flags, dir_fd=current_fd)
                os.close(current_fd)
                current_fd = next_fd
                file_stat = os.fstat(current_fd)
                display_path = f"{display_path}/index.html"

            if not stat.S_ISREG(file_stat.st_mode):
                raise OSError("preview target is not a regular file")

            return os.fdopen(current_fd, "rb"), file_stat, display_path
        except (OSError, ValueError):
            os.close(current_fd)
            raise

    def send_head(self) -> typing.BinaryIO | None:
        try:
            file_object, file_stat, display_path = self.open_request_file()
        except (OSError, ValueError):
            self.send_error(404)
            return None

        try:
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(display_path))
            self.send_header("Content-Length", str(file_stat.st_size))
            self.send_header(
                "Last-Modified", self.date_time_string(file_stat.st_mtime)
            )
            self.end_headers()
        except (OSError, ValueError):
            file_object.close()
            raise
        return file_object

    def send_health(self, include_body: bool) -> None:
        body = nonce.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def do_GET(self) -> None:
        if self.request_path() == health_path:
            self.send_health(include_body=True)
            return
        super().do_GET()

    def do_HEAD(self) -> None:
        if self.request_path() == health_path:
            self.send_health(include_body=False)
            return
        super().do_HEAD()

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


handler = functools.partial(SafeHandler, directory=str(root))


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


try:
    with ThreadingServer(("127.0.0.1", 0), handler) as server:
        host = server.server_address[0]
        port = server.server_address[1]
        port_file.write_text(str(port), encoding="utf-8")
        sys.stdout.write(f"playground serving {root} at http://{host}:{port}/\n")
        sys.stdout.flush()
        server.serve_forever()
finally:
    os.close(root_fd)
PY
	pid=$!
	printf '%s\n' "$pid" >"$PID_FILE"
	printf '%s\n' "$ROOT_DIR" >"$ROOT_FILE"

	for _ in {1..50}; do
		if [[ -s "$PORT_FILE" ]] && state_server_is_alive; then
			return 0
		fi
		sleep 0.1
	done

	kill "$pid" >/dev/null 2>&1 || true
	printf 'playground: preview server failed to start; log follows:\n' >&2
	sed 's/^/  /' "$LOG_FILE" >&2 || true
	remove_state
	exit 1
}

if ! server_is_alive; then
	start_server
fi

SERVER_PORT="$(cat "$PORT_FILE")"
RELATIVE_PATH="${HTML_FILE#"$ROOT_DIR"/}"
URL_PATH="$(
	uv run --no-project python - "$RELATIVE_PATH" <<'PY'
import sys
from urllib.parse import quote

sys.stdout.write("/" + quote(sys.argv[1]) + "\n")
PY
)"
URL="http://127.0.0.1:${SERVER_PORT}${URL_PATH}"

if [[ "$OPEN_BROWSER" == "1" ]]; then
	if command -v open >/dev/null 2>&1; then
		open "$URL" >/dev/null 2>&1 || true
	elif command -v xdg-open >/dev/null 2>&1; then
		xdg-open "$URL" >/dev/null 2>&1 || true
	fi
fi

printf '%s\n' "$URL"
