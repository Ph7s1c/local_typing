# local_typing

Local-only version of MelodyType — a browser typing game synced to YouTube lyrics.

No auth, no analytics, no cloud. Everything runs on localhost.

## Project Structure

```
local_typing/
├── frontend/           # Vue.js app (Vite)
├── backend/            # PocketBase Go source (build binary here)
├── lyrics_server/      # Python FastAPI lyrics fetcher
├── pb_schema.json      # PocketBase collections schema for import
├── start.sh            # One-command startup for all three services
└── README.md
```

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Go | 1.21+ | https://go.dev/dl/ |
| Node.js | 18+ | https://nodejs.org/ |
| Python | 3.10–3.12 | https://www.python.org/ (avoid 3.13+ — some deps lack wheels) |
| YouTube Data API v3 key | — | https://console.cloud.google.com/ |

---

## First-Time Setup

### 1. Build PocketBase

```bash
cd backend
go build -o pocketbase .
```

This produces a `pocketbase` binary inside `backend/`. Only needs to be done once.

### 2. Initialize PocketBase and import the schema

Start PocketBase to trigger the first-run setup:

```bash
cd backend
./pocketbase serve
```

Visit **http://127.0.0.1:8090/_/** in your browser and create an admin account.

Then import the collections schema:

1. Go to **Settings → Import collections**
2. Paste the entire contents of `pb_schema.json`
3. Click **Review → Confirm**

This creates the `song_uploads` and `unlabeled_songs` collections with open (unauthenticated) rules suitable for local use.

Stop PocketBase with `Ctrl+C` — `start.sh` will manage it going forward.

### 3. Set up the Python lyrics server

Use Python 3.10–3.12 (not 3.13+):

```bash
cd lyrics_server
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the env file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your YouTube Data API v3 key:

```
PB_URL=http://127.0.0.1:8090
YOUTUBE_API_KEY=your_key_here
```

To get a free API key: [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services → Enable APIs** → search **YouTube Data API v3** → **Create credentials → API key**.

### 4. Set up the frontend

```bash
cd frontend
npm install
cp .env.example .env.local
```

The default values in `.env.local` point to localhost and work as-is:

```
VITE_PB_URL=http://127.0.0.1:8090
VITE_LYRICS_API_URL=http://127.0.0.1:8000
```

---

## Running

```bash
./start.sh
```

This starts all three services:

| Service | URL |
|---------|-----|
| Frontend (Vite) | http://localhost:5173 |
| Lyrics server (FastAPI) | http://127.0.0.1:8000 |
| PocketBase | http://127.0.0.1:8090 |

To stop everything: `Ctrl+C`.

---

## Usage

- **Home** — Paste a YouTube URL (or 11-character video ID) to fetch synced lyrics and start playing immediately
- **Upload** — Paste a YouTube URL to open the lyric timing editor; sync and save songs to your local library
- **Browse** — View all locally saved songs and replay any of them

Game results (WPM, accuracy, characters typed) are saved to `localStorage` after each completed game.

---

## Stopping detached processes

If services get detached (e.g. after a failed start), kill them by port:

```bash
lsof -ti :8090 | xargs kill -9   # PocketBase
lsof -ti :8000 | xargs kill -9   # lyrics server
lsof -ti :5173 | xargs kill -9   # frontend
```
