export default function HeroCard({ film, isFlipping }) {
  if (!film) return null

  return (
    <div className="flip-container" style={{ marginBottom: '20px' }}>
      <div className={`flip-inner ${isFlipping ? 'is-flipping' : ''}`}>
        <div className="flip-front">
          <HeroCardInner film={film} />
        </div>
        <div className="flip-back">
          <HeroCardInner film={film} />
        </div>
      </div>
    </div>
  )
}

function HeroCardInner({ film }) {
  return (
    <div className="glass hero-card">
      <div className="hero-poster">
        {film.poster_url ? (
          <img src={film.poster_url} alt={film.title} />
        ) : (
          <div className="poster-placeholder">🎬</div>
        )}
      </div>
      <div className="hero-body">
        <div>
          <div className="source-tag">
            <span className="dot" />
            {film.source === 'watchlist' ? 'From your watchlist' : 'Discovered for you'}
          </div>
          <h2 className="hero-title">{film.title}</h2>
          <div className="hero-meta">
            <span>{film.year}</span>
            <span>{film.director}</span>
            {film.runtime && <span>{film.runtime} min</span>}
            {film.tmdb_rating > 0 && <span>★ {film.tmdb_rating}</span>}
          </div>
          <p className="hero-description">{film.overview}</p>
          {film.why && (
            <div className="why-tag">
              <span className="why-icon">✦</span>
              <span>{film.why}</span>
            </div>
          )}
        </div>
        <div className="hero-genres">
          {(film.genres || []).map(g => (
            <span key={g} className="genre-chip">{g}</span>
          ))}
        </div>
      </div>
    </div>
  )
}
