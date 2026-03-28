# 🎬 Movie Recommender

A personal movie recommendation web app built around my Letterboxd watch history. Every shuffle picks 6 films I haven't seen yet, personalised to my taste — with an AI-generated blurb explaining exactly why I'd like each one.

---

## What it does

- Reads my Letterboxd export (ratings, watchlist, watch history) to build a taste profile
- Pulls discovery candidates from TMDB's top-rated and genre-popular lists
- Scores and picks 6 unwatched films with diversity enforcement (genre variety, era mix, watchlist + discovery balance)
- Generates personalised "why you'd like it" blurbs via Groq AI
- Remembers the last 5 shuffles so films don't repeat

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 18 · Vite · plain CSS |
| Backend | Python · Flask |
| AI blurbs | Groq API (`llama-3.1-8b-instant`) |
| Movie data | TMDB API |
| Hosting | Vercel (frontend) · Render (backend) |

## Design

Deep Space aesthetic — near-black background with ambient purple/blue blob animations, liquid glass cards with `backdrop-filter: blur`, and a 3D card-flip shuffle animation.

---

## Running locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- [TMDB API read access token](https://developer.themoviedb.org/docs/getting-started)
- [Groq API key](https://console.groq.com) (free)

### Setup

```bash
# 1. Clone
git clone https://github.com/HafsahNasir/movie-recommender.git
cd movie-recommender

# 2. Add your Letterboxd CSV export to /data/
#    Export from: Letterboxd → Settings → Import & Export
#    You need: ratings.csv, watchlist.csv, watched.csv

# 3. Create .env in the project root
cp .env.example .env
# Fill in TMDB_READ_ACCESS_TOKEN and GROQ_API_KEY
```

```bash
# Terminal 1 — backend
cd backend
pip install -r requirements.txt
python app.py

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Or use the launch script:
```bash
./start.sh
```

Open **http://localhost:5173**

### Environment variables

```
TMDB_READ_ACCESS_TOKEN=...
GROQ_API_KEY=...
```

---

## Deploying your own version

1. Fork this repo and add your own Letterboxd CSVs to `/data/`
2. Deploy backend to [Render](https://render.com) — `render.yaml` is included
3. Deploy frontend to [Vercel](https://vercel.com) — set root directory to `frontend`
4. Set env vars on both platforms
5. Add `VITE_API_URL=https://your-render-url.onrender.com` to Vercel

---

## Project structure

```
movie_recommender/
├── backend/
│   ├── app.py                  # Flask API (/api/recommend, /api/stats)
│   ├── letterboxd_parser.py    # reads Letterboxd CSV exports
│   ├── letterboxd_scraper.py   # TMDB-based discovery candidates
│   ├── taste_profile.py        # builds weighted taste profile from watch history
│   ├── recommender.py          # scores candidates, enforces diversity, picks 6
│   ├── tmdb_client.py          # TMDB metadata fetching with disk cache
│   ├── gemini_client.py        # Groq API blurb generation
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── index.css
│       └── components/
│           ├── HeroCard.jsx
│           ├── MovieCard.jsx
│           └── ShuffleButton.jsx
├── data/                       # Letterboxd CSV exports
├── render.yaml                 # Render deployment config
└── start.sh                    # local launch script
```
