export default function MovieCard({ film, isFlipping, onClick }) {
  return (
    <div
      className="flip-container movie-card-wrapper"
      onClick={() => onClick && onClick(film)}
    >
      <div className={`flip-inner ${isFlipping ? 'is-flipping' : ''}`}>
        <div className="flip-front">
          <MovieCardInner film={film} />
        </div>
        <div className="flip-back">
          <MovieCardInner film={film} />
        </div>
      </div>
    </div>
  )
}

function MovieCardInner({ film }) {
  return (
    <div className="glass movie-card">
      <div className="movie-poster">
        {film.poster_url ? (
          <img src={film.poster_url} alt={film.title} />
        ) : (
          <div className="poster-placeholder" style={{ fontSize: '1.2rem' }}>🎬</div>
        )}
      </div>
      <div className="movie-body">
        <div className="movie-title">{film.title}</div>
        <div className="movie-year">{film.year} · {film.director}</div>
        {film.why && <div className="movie-why">{film.why}</div>}
      </div>
    </div>
  )
}
