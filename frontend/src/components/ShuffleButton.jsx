export default function ShuffleButton({ onClick, loading }) {
  return (
    <div className="shuffle-wrap">
      <button
        className={`shuffle-btn ${loading ? 'loading' : ''}`}
        onClick={onClick}
        disabled={loading}
      >
        <span className={`shuffle-icon ${loading ? 'spinning' : ''}`}>⟳</span>
        {loading ? 'Finding picks…' : 'Shuffle Recommendations'}
      </button>
      {!loading && (
        <p className="shuffle-hint">Cards flip to reveal new picks</p>
      )}
    </div>
  )
}
