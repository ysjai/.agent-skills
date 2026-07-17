#!/usr/bin/env bash
# Stop the brainstorm server and clean up
# Usage: stop-server.sh <session_dir>
#
# Sends an authenticated stop request. Only deletes session directory if it's
# under /tmp (ephemeral). Persistent directories (.brainstorm/) are
# kept so mockups can be reviewed later.

SESSION_DIR="$1"

if [[ -z "$SESSION_DIR" ]]; then
  echo '{"error": "Usage: stop-server.sh <session_dir>"}'
  exit 1
fi

SESSION_DIR=$(node -e 'process.stdout.write(require("path").resolve(process.argv[1]))' "$SESSION_DIR" 2>/dev/null)
if [[ -z "$SESSION_DIR" ]]; then
  echo '{"status": "failed", "error": "invalid session directory"}'
  exit 1
fi

if [[ ! -e "$SESSION_DIR" ]]; then
  echo '{"status": "not_running"}'
  exit 0
fi

if [[ ! -f "${SESSION_DIR}/.brainstorm-session" ]]; then
  echo '{"status": "failed", "error": "directory is not a brainstorm session"}'
  exit 1
fi

STATE_DIR="${SESSION_DIR}/state"
PID_FILE="${STATE_DIR}/server.pid"
INFO_FILE="${STATE_DIR}/server-info"

pid=""
if [[ -f "$INFO_FILE" ]]; then
  info_pid=$(node -e '
    const fs = require("fs");
    const info = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
    if (Number.isInteger(info.pid) && info.pid > 0) process.stdout.write(String(info.pid));
  ' "$INFO_FILE" 2>/dev/null || true)
  if [[ "$info_pid" =~ ^[0-9]+$ ]]; then
    pid="$info_pid"
  fi
fi

if [[ -z "$pid" && -f "$PID_FILE" ]]; then
  candidate_pid=$(cat "$PID_FILE")
  if [[ "$candidate_pid" =~ ^[0-9]+$ ]]; then
    pid="$candidate_pid"
  fi
fi

stop_requested="false"
if [[ -f "$INFO_FILE" ]]; then
  if node -e '
    const fs = require("fs");
    const http = require("http");
    const path = require("path");
    const info = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
    if (!info.stop_token) process.exit(1);
    const expectedStateDir = path.resolve(process.argv[2], "state");
    if (path.resolve(info.state_dir) !== expectedStateDir) process.exit(1);
    const host = info.host === "0.0.0.0" ? "127.0.0.1" : info.host;
    const req = http.request({
      host, port: info.port, path: "/__stop", method: "POST",
      headers: { "x-brainstorm-stop-token": info.stop_token }
    }, (res) => {
      res.resume();
      res.on("end", () => process.exit(res.statusCode === 202 ? 0 : 1));
    });
    req.setTimeout(1000, () => req.destroy());
    req.on("error", () => process.exit(1));
    req.end();
  ' "$INFO_FILE" "$SESSION_DIR"; then
    stop_requested="true"
  fi
fi

if [[ "$stop_requested" == "true" && -n "$pid" ]]; then
  for i in {1..30}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      break
    fi
    sleep 0.1
  done
fi

if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
  echo '{"status": "failed", "error": "server identity or shutdown could not be confirmed; process was not signaled"}'
  exit 1
fi

if [[ -d "$STATE_DIR" ]]; then
  rm -f "$PID_FILE" "${STATE_DIR}/server.log" "$INFO_FILE" \
    "${STATE_DIR}/events" "${STATE_DIR}/server-stopped"
  rmdir "$STATE_DIR" 2>/dev/null || true
fi

SESSION_PARENT=$(dirname "$SESSION_DIR")
SESSION_NAME=$(basename "$SESSION_DIR")
if [[ "$SESSION_PARENT" == "/tmp" && "$SESSION_NAME" =~ ^brainstorm-[A-Za-z0-9._-]+$ ]]; then
  rm -rf -- "$SESSION_DIR"
fi

if [[ "$stop_requested" == "true" ]]; then
  echo '{"status": "stopped"}'
else
  echo '{"status": "not_running"}'
fi
