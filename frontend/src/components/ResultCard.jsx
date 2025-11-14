export default function ResultCard({ result }) {
  if (!result) return null

  return (
    <div style={{
      padding: "20px",
      border: "1px solid #ccc",
      borderRadius: "10px",
      background: "#f9f9f9"
    }}>
      <h2>Assessment Result</h2>

      <h3>Score: {result.score}</h3>

      <h4>Frame Score: {result.frame_score}</h4>
      <h4>Phase Score: {result.phase_score}</h4>

      <h3>Feedback:</h3>
      <ul>
        {result.feedback.map((f, i) => (
          <li key={i}>{f}</li>
        ))}
      </ul>
    </div>
  )
}
