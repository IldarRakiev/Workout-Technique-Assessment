import "../TechniqueAssessment.css"
import { useEffect, useState } from "react";

export default function ResultCard({ result, onClose }) {

  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (result) {
      setTimeout(() => {
        setProgress(result.score);
      }, 200);
    }
  }, [result]);

  if (!result) return null

  return (
    <>
      <div className="result-overlay" onClick={onClose} />
      <div className="result-modal" role="dialog" aria-modal="true" aria-label="Assessment result">
        <button className="result-close" onClick={onClose} aria-label="Close result">✕</button>

        <div className="result-card">
          <h2 className="result-title">Assessment Result</h2>

          <div className="circle-wrapper">
            <svg className="progress-ring" width="160" height="160">
              <circle
                className="ring-bg"
                cx="80"
                cy="80"
                r="70"
              />
              <circle
                className="ring-progress"
                cx="80"
                cy="80"
                r="70"
                style={{
                  strokeDashoffset: `calc(440 - (440 * ${progress}) / 100)`,
                }}
              />
            </svg>

            <div className="circle-center">
              {Math.round(progress)}/100
            </div>
          </div>

          <div className="result-section">

            <div className="result-sub-scores">
              <div className="sub-score">
                <span className="label">Total Score: </span>
                <strong>{result.score}</strong>
                <span className="label"> out of 100</span>
              </div>
              <div className="sub-score">
                <span>Frame Score: </span>
                <strong>{result.frame_score}</strong>
                <span className="label"> out of 100</span>
              </div>
              <div className="sub-score">
                <span>Phase Score: </span>
                <strong>{result.phase_score}</strong>
                <span className="label"> out of 100</span>
              </div>
            </div>
          </div>

          <h3 className="result-subtitle">Feedback</h3>
          <div className="feedback-section">
            <ul>
              {result.feedback.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </>
  )
}
