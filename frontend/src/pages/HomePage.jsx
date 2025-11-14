import { useState } from "react"
import UploadForm from "../components/UploadForm"
import ResultCard from "../components/ResultCard"

export default function HomePage() {
  const [result, setResult] = useState(null)

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      <UploadForm onResult={setResult} />
      <ResultCard result={result} />
    </div>
  )
}
