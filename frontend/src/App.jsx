import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL ?? ''
import HeroCard from './components/HeroCard.jsx'
import MovieCard from './components/MovieCard.jsx'
import ShuffleButton from './components/ShuffleButton.jsx'

const FLIP_DURATION = 600   // ms — matches CSS transition
const FLIP_STAGGER  = 120   // ms between card flips

export default function App() {
  const [films, setFilms]         = useState([])
  const [stats, setStats]         = useState(null)
  const [loading, setLoading]     = useState(false)
  const [flipping, setFlipping]   = useState([]) // indices currently flipping
  const [heroIndex, setHeroIndex] = useState(0)
  const [error, setError]         = useState(null)
  // Track last 5 shuffles' tmdb_ids to avoid repeat recommendations
  const shuffleHistory = useRef([])

  useEffect(() => {
    fetchStats()
    fetchRecommendations()
  }, [])

  async function fetchStats() {
    try {
      const { data } = await axios.get(`${API_BASE}/api/stats`)
      setStats(data)
    } catch {
      // stats are decorative — silent fail
    }
  }

  async function fetchRecommendations() {
    setLoading(true)
    setError(null)
    try {
      // Build exclude list from last 5 shuffles
      const recentIds = shuffleHistory.current.slice(-5).flat().join(',')
      const url = recentIds ? `${API_BASE}/api/recommend?exclude=${recentIds}` : `${API_BASE}/api/recommend`
      const { data } = await axios.get(url)

      // Record this shuffle's ids
      const newIds = data.recommendations.map(f => f.tmdb_id)
      shuffleHistory.current = [...shuffleHistory.current, newIds]

      await runFlipAnimation(data.recommendations.length)
      setFilms(data.recommendations)
      setHeroIndex(0)
    } catch (err) {
      setError(err.response?.data?.error || 'Could not load recommendations. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  async function runFlipAnimation(count) {
    // Stagger flip-in across all cards
    for (let i = 0; i < count; i++) {
      setTimeout(() => {
        setFlipping(prev => [...prev, i])
        setTimeout(() => {
          setFlipping(prev => prev.filter(x => x !== i))
        }, FLIP_DURATION)
      }, i * FLIP_STAGGER)
    }
    // Wait for all flips to complete before updating films
    await new Promise(resolve => setTimeout(resolve, count * FLIP_STAGGER + FLIP_DURATION))
  }

  const hero = films[heroIndex] || null
  const row  = films.filter((_, i) => i !== heroIndex)

  return (
    <>
      <div className="bg-blobs">
        <div className="blob blob-1" />
        <div className="blob blob-2" />
        <div className="blob blob-3" />
      </div>

      <div className="app">
        {/* Header */}
        <header className="app-header">
          <div className="header-left">
            <div className="avatar">H</div>
            <div>
              <h1 className="app-title">What to Watch</h1>
              <p className="app-sub">hafsahnasir · Letterboxd</p>
            </div>
          </div>
          {stats && (
            <div className="header-stats">
              <span>{stats.watched_count} films watched</span>
              <span className="stats-watchlist">{stats.watchlist_count} in watchlist</span>
            </div>
          )}
        </header>

        {error ? (
          <div className="error-box glass">{error}</div>
        ) : (
          <>
            {/* Hero */}
            <p className="section-label">Tonight's Pick</p>
            <HeroCard film={hero} isFlipping={flipping.includes(heroIndex)} />

            {/* Row of 5 */}
            <div className="row-header">
              <p className="section-label" style={{ marginBottom: 0 }}>More Picks</p>
            </div>
            <div className="cards-row">
              {row.map((film, i) => (
                <MovieCard
                  key={film.tmdb_id}
                  film={film}
                  isFlipping={flipping.includes(i + (i >= heroIndex ? 1 : 0))}
                  onClick={() => setHeroIndex(films.indexOf(film))}
                />
              ))}
            </div>
          </>
        )}

        {/* Shuffle */}
        <ShuffleButton onClick={fetchRecommendations} loading={loading} />
      </div>
    </>
  )
}
