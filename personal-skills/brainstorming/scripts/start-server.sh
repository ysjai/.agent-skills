#!/usr/bin/env bash
# Start the brainstorm server and output connection info
# Usage: start-server.sh [--project-dir <path>] [--foreground] [--background]
#
# Starts server on a random high port, outputs JSON with URL.
# Each session gets its own directory to avoid conflicts.
#
# Options:
#   --project-dir <path>  Store session files under <path>/.brainstorm/
#                         instead of /tmp. Files persist after server stops.
#   --host <bind-host>    Loopback host only (127.0.0.1 or localhost).
#   --url-host <host>     Loopback hostname shown in returned URL JSON.
#   --foreground          Run server in the current terminal (no backgrounding).
#   --background          Force background mode (overrides Codex auto-foreground).

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Parse arguments
PROJECT_DIR=""
FOREGROUND="false"
FORCE_BACKGROUND="false"
BIND_HOST="127.0.0.1"
URL_HOST=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir)
      if [[ $# -lt 2 || -z "$2" || "$2" == --* ]]; then
        echo '{"error": "--project-dir requires a path"}'
        exit 1
      fi
      PROJECT_DIR="$2"
      shift 2
      ;;
    --host)
      if [[ $# -lt 2 || -z "$2" || "$2" == --* ]]; then
        echo '{"error": "--host requires a value"}'
        exit 1
      fi
      BIND_HOST="$2"
      shift 2
      ;;
    --url-host)
      if [[ $# -lt 2 || -z "$2" || "$2" == --* ]]; then
        echo '{"error": "--url-host requires a value"}'
        exit 1
      fi
      URL_HOST="$2"
      shift 2
      ;;
    --foreground|--no-daemon)
      FOREGROUND="true"
      shift
      ;;
    --background|--daemon)
      FORCE_BACKGROUND="true"
      shift
      ;;
    *)
      echo "{\"error\": \"Unknown argument: $1\"}"
      exit 1
      ;;
  esac
done

if [[ "$BIND_HOST" != "127.0.0.1" && "$BIND_HOST" != "localhost" ]]; then
  echo '{"error": "brainstorm server only supports loopback; use port forwarding for remote access"}'
  exit 1
fi

if [[ -n "$URL_HOST" && "$URL_HOST" != "127.0.0.1" && "$URL_HOST" != "localhost" ]]; then
  echo '{"error": "--url-host must be 127.0.0.1 or localhost"}'
  exit 1
fi

if [[ -n "$PROJECT_DIR" && ! -d "$PROJECT_DIR" ]]; then
  echo '{"error": "--project-dir must reference an existing directory"}'
  exit 1
fi

if [[ -z "$URL_HOST" ]]; then
  if [[ "$BIND_HOST" == "127.0.0.1" || "$BIND_HOST" == "localhost" ]]; then
    URL_HOST="localhost"
  else
    URL_HOST="$BIND_HOST"
  fi
fi

if ! command -v node >/dev/null 2>&1; then
  echo '{"error": "node is required"}'
  exit 1
fi

STOP_TOKEN=$(node -e 'process.stdout.write(require("crypto").randomBytes(16).toString("hex"))')
if [[ -z "$STOP_TOKEN" ]]; then
  echo '{"error": "failed to generate stop token"}'
  exit 1
fi

# Some environments reap detached/background processes. Auto-foreground when detected.
if [[ -n "${CODEX_CI:-}" && "$FOREGROUND" != "true" && "$FORCE_BACKGROUND" != "true" ]]; then
  FOREGROUND="true"
fi

# Windows/Git Bash reaps nohup background processes. Auto-foreground when detected.
if [[ "$FOREGROUND" != "true" && "$FORCE_BACKGROUND" != "true" ]]; then
  case "${OSTYPE:-}" in
    msys*|cygwin*|mingw*) FOREGROUND="true" ;;
  esac
  if [[ -n "${MSYSTEM:-}" ]]; then
    FOREGROUND="true"
  fi
fi

# Generate unique session directory
SESSION_ID="$$-$(date +%s)"

if [[ -n "$PROJECT_DIR" ]]; then
  PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
  SESSION_DIR="${PROJECT_DIR}/.brainstorm/${SESSION_ID}"
else
  SESSION_DIR="/tmp/brainstorm-${SESSION_ID}"
fi

STATE_DIR="${SESSION_DIR}/state"
PID_FILE="${STATE_DIR}/server.pid"
LOG_FILE="${STATE_DIR}/server.log"

# Create the unique session directory atomically; never reuse a collision.
mkdir -p "$(dirname "$SESSION_DIR")"
if ! mkdir "$SESSION_DIR"; then
  echo '{"error": "session directory collision"}'
  exit 1
fi
mkdir "${SESSION_DIR}/content" "$STATE_DIR"
printf 'brainstorm-session\n' > "${SESSION_DIR}/.brainstorm-session"

cleanup_failed_start() {
  status=$?
  if [[ $status -ne 0 && -n "${SESSION_DIR:-}" && -f "${SESSION_DIR}/.brainstorm-session" ]]; then
    rm -rf -- "$SESSION_DIR"
  fi
}
trap cleanup_failed_start EXIT

# A fresh session directory must never contain an existing PID file.
if [[ -f "$PID_FILE" ]]; then
  echo '{"error": "session directory collision: existing server.pid"}'
  exit 1
fi

cd "$SCRIPT_DIR"

# Resolve the harness PID (grandparent of this script).
# $PPID is the ephemeral shell the harness spawned to run us — it dies
# when this script exits. The harness itself is $PPID's parent.
OWNER_PID="$(ps -o ppid= -p "$PPID" 2>/dev/null | tr -d ' ')"
if [[ -z "$OWNER_PID" || "$OWNER_PID" == "1" ]]; then
  OWNER_PID="$PPID"
fi

# Foreground mode for environments that reap detached/background processes.
if [[ "$FOREGROUND" == "true" ]]; then
  echo "$$" > "$PID_FILE"
  trap - EXIT
  exec env BRAINSTORM_DIR="$SESSION_DIR" BRAINSTORM_HOST="$BIND_HOST" BRAINSTORM_URL_HOST="$URL_HOST" BRAINSTORM_OWNER_PID="$OWNER_PID" BRAINSTORM_STOP_TOKEN="$STOP_TOKEN" node server.cjs
fi

# Start server, capturing output to log file
# Use nohup to survive shell exit; disown to remove from job table
nohup env BRAINSTORM_DIR="$SESSION_DIR" BRAINSTORM_HOST="$BIND_HOST" BRAINSTORM_URL_HOST="$URL_HOST" BRAINSTORM_OWNER_PID="$OWNER_PID" BRAINSTORM_STOP_TOKEN="$STOP_TOKEN" node server.cjs > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
disown "$SERVER_PID" 2>/dev/null
echo "$SERVER_PID" > "$PID_FILE"

# Wait for server-started message (check log file)
for i in {1..50}; do
  if grep -q "server-started" "$LOG_FILE" 2>/dev/null; then
    # Verify server is still alive after a short window (catches process reapers)
    alive="true"
    for _ in {1..20}; do
      if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        alive="false"
        break
      fi
      sleep 0.1
    done
    if [[ "$alive" != "true" ]]; then
      echo "{\"error\": \"Server started but was killed. Retry in a persistent terminal with: $SCRIPT_DIR/start-server.sh${PROJECT_DIR:+ --project-dir $PROJECT_DIR} --host $BIND_HOST --url-host $URL_HOST --foreground\"}"
      exit 1
    fi
    node -e '
      const fs = require("fs");
      const lines = fs.readFileSync(process.argv[1], "utf8").split("\n");
      const line = lines.find((item) => item.includes("server-started"));
      if (!line) process.exit(1);
      process.stdout.write(line + "\n");
    ' "$LOG_FILE"
    trap - EXIT
    exit 0
  fi
  sleep 0.1
done

# Timeout - server didn't start
echo '{"error": "Server failed to start within 5 seconds"}'
exit 1
