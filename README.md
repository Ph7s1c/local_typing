# local_typing

Local typing game synced to YouTube lyrics. No auth, no cloud.

## Prerequisites

- Go 1.21+
- Node.js 18+
- Python 3.10–3.12
- YouTube Data API v3 key ([get one here](https://console.cloud.google.com/))

## Setup

```bash
# 1. Build PocketBase
cd backend && go build -o pocketbase .

# 2. Frontend dependencies
cd ../frontend && npm install && cp .env.example .env.local

# 3. Python venv
cd ../lyrics_server && python3.12 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cp .env.example .env  # then add your YOUTUBE_API_KEY
```

**PocketBase schema (one-time):** run `./backend/pocketbase serve`, visit http://127.0.0.1:8090/_, create an admin account, then import `pb_schema.json` via Settings → Import collections. Stop it when done.

## Run

```bash
./start.sh
```

Open http://localhost:5173.
