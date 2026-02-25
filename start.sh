#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting PocketBase..."
cd "$SCRIPT_DIR/backend" && ./pocketbase serve --http=127.0.0.1:8090 --origins='*' &
PB_PID=$!

echo "Starting lyrics server..."
"$SCRIPT_DIR/lyrics_server/venv/bin/python" "$SCRIPT_DIR/lyrics_server/webserver.py" &
LYRICS_PID=$!

echo "Starting frontend..."
cd "$SCRIPT_DIR/frontend" && npm run dev

# Cleanup background processes on exit
trap "kill $PB_PID $LYRICS_PID 2>/dev/null" EXIT
