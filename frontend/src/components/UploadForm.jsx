import { useState } from "react"
import { assessVideo } from "../api/assessmentApi"

export default function UploadForm({ onResult }) {
  const [file, setFile] = useState(null)
  const [exercise, setExercise] = useState("pushup")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    try {
      const result = await assessVideo(file, exercise)
      onResult(result)
    } catch (err) {
      alert("Error: " + err.message)
    }
    setLoading(false)
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
      <h2>Upload your workout video</h2>

      <div>
        <label>Exercise type:</label>
        <select value={exercise} onChange={(e) => setExercise(e.target.value)}>
          <option value="pushup">Push-up</option>
          <option value="pullup">Pull-up</option>
          <option value="squat">Squat</option>
          <option value="situp">Sit-up</option>
          <option value="jumping_jack">Jumping Jack</option>
        </select>
      </div>

      <div>
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files[0])}
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "Processing..." : "Assess Technique"}
      </button>
    </form>
  )
}
