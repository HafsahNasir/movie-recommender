# Movie Recommender — Design Spec
*2026-03-28*

## Overview

A local web app that recommends 6 unwatched films to hafsahnasir, personalised to her Letterboxd taste profile. Recommendations come from a mix of her watchlist and popular Letterboxd lists. Each film comes with a short description and a Gemini-generated "why you'd like it" blurb. She can shuffle to get a new set at any time.

---

## Data Sources

### Letterboxd (personal data)
- **CSV export** — user drops files from Letterboxd's data export into `/data/`:
  - `ratings.csv` — all watched films with star ratings
  - `watchlist.csv` — saved watchlist
  - `watched.csv` — full watch history (no ratings)
- **Scraping** — on first run each session, the app scrapes a fixed set of popular Letterboxd lists to source discovery candidates:
  - Letterboxd Official Top 250 Narrative Feature Films
  - Top 250 by decade (60s–2010s)
  - Top genre lists: horror, sci-fi, drama
- Scraped data is cached in memory for the session; CSVs are read once at startup.
- Letterboxd username: `hafsahnasir`

### TMDB
- Used for: movie posters, runtime, cast, genre tags, overview text, star rating
- API Read Access Token stored in `.env`

### Gemini
- Used for: personalised "why you'd like it" blurb per film (one API call per shuffle, batched)
- Input: compact taste summary (top genres, top directors, example high-rated films) + the 6 candidate films
- API key stored in `.env`

---

## Recommendation Engine

**Algorithm: Taste Matching + Diversity Enforcement**

1. **Taste profile** — built from `ratings.csv`:
   - Genre weights (genres appearing in 4★+ films score higher) — genres fetched from TMDB per film
   - Director affinity (directors of 4★+ films) — director fetched from TMDB per film
   - Actor affinity (top-billed cast of 4★+ films) — cast fetched from TMDB per film
   - Era preference (decade distribution of 4★+ films)
   - Note: building the taste profile requires TMDB lookups for each rated film; results are cached to disk to avoid repeat calls

2. **Candidate pool** — all films the user has not watched, drawn from:
   - Watchlist entries
   - Popular Letterboxd list films

3. **Scoring** — each candidate gets a score based on overlap with taste profile (genre match, director match, actor match, era match).

4. **Diversity enforcement** — the final 6 picks must:
   - Include at least 2 watchlist films and at least 2 discovery films (from lists)
   - Span at least 3 different genres
   - Not all be from the same era
   - Prefer at least 1 pre-2000 film when candidates exist (soft constraint, skipped if pool is too small)

5. **Gemini blurb generation** — after picking 6, one Gemini call generates a personalised sentence for each, referencing specific films the user has liked.

---

## UI Design

### Theme
- **Deep Space** — near-black base (`#07071a`) with deep purple/blue ambient glow blobs
- **Liquid glass cards** — `backdrop-filter: blur(20px)`, semi-transparent backgrounds, subtle borders
- Animated background: 3 soft blobs drift slowly using CSS `animation`

### Layout: Hero + Row
- **Header** — avatar, "What to Watch", username, stats (films watched, watchlist count)
- **Hero card** — featured film shown large (poster left, details right):
  - Source tag ("From your watchlist" or "Letterboxd Top 250")
  - Title, year, director, runtime, TMDB rating
  - Short film description
  - "Why you'd like it" blurb (Gemini-generated)
  - Genre chips
- **Row of 5** — smaller cards below hero, each showing:
  - Poster (from TMDB)
  - Title, year, director
  - Short reason (abbreviated Gemini blurb)
- **Shuffle button** — centred below the row, glassy pill button with purple glow

### Shuffle Animation: Card Flip
- On shuffle click, each card flips 180° on the Y-axis in sequence (staggered, ~120ms delay between cards)
- While flipped, the backend call fires; new data slots in on the back face
- Cards un-flip to reveal new recommendations
- Loading indicator shown if the backend takes >1.5s

### Interactions
- Hover: cards lift slightly (`translateY(-3px)`) with a shadow glow
- Click a small card: it becomes the hero (swap animation)
- No filters, no settings — fully automatic

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.11+ · Flask |
| Frontend | React 18 · Vite |
| Styling | Plain CSS (no framework) |
| Scraping | `requests` + `BeautifulSoup4` |
| HTTP client | `axios` (frontend) |
| API comms | REST — single `/api/recommend` endpoint |

---

## File Structure

```
movie_recommender/
├── backend/
│   ├── app.py                  # Flask server, /api/recommend endpoint
│   ├── letterboxd_parser.py    # reads CSV exports
│   ├── letterboxd_scraper.py   # scrapes popular lists (cached per session)
│   ├── taste_profile.py        # builds weighted taste profile from ratings
│   ├── recommender.py          # scores candidates, enforces diversity, picks 6
│   ├── tmdb_client.py          # TMDB metadata + poster fetching
│   ├── gemini_client.py        # Gemini blurb generation
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── main.jsx
│   │   └── components/
│   │       ├── HeroCard.jsx
│   │       ├── MovieCard.jsx
│   │       └── ShuffleButton.jsx
│   ├── package.json
│   └── vite.config.js          # proxy /api → localhost:5000
├── data/                       # user drops Letterboxd CSV exports here
│   └── .gitkeep
├── .env                        # API keys (gitignored)
├── .env.example                # template with key names, no values
└── .gitignore
```

---

## API

### `GET /api/recommend`
Returns 6 film recommendations.

**Response:**
```json
{
  "recommendations": [
    {
      "tmdb_id": 1018,
      "title": "Mulholland Drive",
      "year": 2001,
      "director": "David Lynch",
      "runtime": 147,
      "tmdb_rating": 4.4,
      "genres": ["Mystery", "Drama"],
      "poster_url": "https://image.tmdb.org/...",
      "overview": "An aspiring actress...",
      "why": "You tend to love slow-burn psychological films...",
      "source": "watchlist"
    }
  ],
  "taste_summary": "Loves slow-burn psychological films, arthouse, Wong Kar-wai, Lynch..."
}
```

The first item is the hero. `source` is either `"watchlist"` or `"discovered"`.

---

## Running the App

```bash
# 1. Add your Letterboxd CSV exports to /data/
# 2. Fill in .env (copy from .env.example)

# Terminal 1 — backend
cd backend
pip install -r requirements.txt
python app.py          # runs on http://localhost:5000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev            # runs on http://localhost:5173
```

Open **http://localhost:5173**.

---

## Environment Variables (`.env`)

```
TMDB_READ_ACCESS_TOKEN=...
GEMINI_API_KEY=...
```

---

## Verification

1. Drop a real Letterboxd CSV export into `/data/` and start both servers
2. Open the app — header should show real watch count from CSV
3. First load should return 6 recommendations with real TMDB posters
4. Click Shuffle — cards should flip, then reveal a new set of 6
5. "Why you'd like it" blurb should reference films you've actually rated highly
6. At least 2 of the 6 should be from the watchlist, at least 2 from discovered lists
7. Genres across the 6 should vary (not all the same genre)
