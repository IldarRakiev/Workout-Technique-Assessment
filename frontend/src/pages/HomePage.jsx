import { useState } from "react"
import UploadForm from "../components/UploadForm"
import ResultCard from "../components/ResultCard"
import "../TechniqueAssessment.css"

export default function HomePage() {
  const [result, setResult] = useState(null)

  const closeResult = () => setResult(null)

  return (
    <div className="basic-page">

      <div style={{ position: "relative" }}>
          <svg
              width="1200"
              height="1200"
              viewBox="0 0 1200 1200"
              style={{
                  position: "absolute",
                  top: "-300px",
                  right: "-400px",
                  zIndex: 1,
                  pointerEvents: "none"
              }}
              >
              <defs>
                  <filter
                  id="blurOval"
                  x="-50%"
                  y="-50%"
                  width="200%"
                  height="200%"
                  filterUnits="objectBoundingBox"
                  >
                  <feGaussianBlur in="SourceGraphic" stdDeviation="80" />
                  </filter>

                  <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="rgba(229, 46, 232, 0.25)" />
                  <stop offset="100%" stopColor="rgba(32, 228, 193, 0.25)" />
                  </linearGradient>
              </defs>

              <ellipse
                  cx="600"
                  cy="600"
                  rx="300"
                  ry="200"
                  fill="url(#grad)"
                  filter="url(#blurOval)"
              />
          </svg>
      </div>

      <div style={{ position: "relative" }}>
          <svg
              width="1200"
              height="1200"
              viewBox="0 0 1200 1200"
              style={{
              position: "absolute",
              top: "-150px",    // ниже
              left: "-500px",
              zIndex: 1,
              }}
          >
              <defs>
              <filter id="blurOval">
                  <feGaussianBlur in="SourceGraphic" stdDeviation="60" />
              </filter>
              <linearGradient id="grad" x1="0%" y1="100%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="rgba(229, 46, 232, 0.2)" />
                  <stop offset="100%" stopColor="rgba(32, 228, 193, 0.2)" />
              </linearGradient>
              </defs>
              <ellipse
              cx="600"
              cy="600"
              rx="300"
              ry="200"
              fill="url(#grad)"
              filter="url(#blurOval)"
              />
          </svg>
      </div>

      <div className="technique-container">
        <div className="technique-header">
          <div className="technique-title">
            <span className="technique-icon">🏋️‍♂️</span>
            Workout Technique Assessment
          </div>
          <p className="technique-subtitle">
            Upload a workout video and get computer vision-powered technique scoring and feedback
          </p>
        </div>

      <UploadForm onResult={setResult} />
      {result && (
        <div className="modal-overlay">
          <div className="modal-content">
            <ResultCard result={result} onClose={closeResult} />
          </div>
        </div>
      )}
      </div>
    </div>
  )
}
