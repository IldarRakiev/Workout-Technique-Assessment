import { useState, useRef, useEffect } from "react"
import { assessVideo } from "../api/assessmentApi"
import "../TechniqueAssessment.css"

export default function UploadForm({ onResult }) {
  const [file, setFile] = useState(null)
  const [exercise, setExercise] = useState("pushup")
  const [preview, setPreview] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [loading, setLoading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [previewVideo, setPreviewVideo] = useState(null)

  const openVideo = (file) => {
    setPreviewVideo(URL.createObjectURL(file))
  }

  const closeVideo = () => {
    setPreviewVideo(null)
  }

  const inputRef = useRef()

  const allowedVideoTypes = [
    "video/mp4",
    "video/quicktime",   // .mov
    "video/webm",
    "video/x-matroska"   // .mkv
  ]

  const exerciseOptions = [
    { id: "pushup", label: "Push-up", icon: "💪" },
    { id: "pullup", label: "Pull-up", icon: "🏋️" },
    { id: "squat", label: "Squat", icon: "🦵" },
    { id: "situp", label: "Sit-up", icon: "🤸" },
    { id: "jumping_jack", label: "Jumping Jack", icon: "⚡" }
  ];

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files?.[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    if (e.target.files?.[0]) {

      if (!allowedVideoTypes.includes(e.target.files?.[0].type)) {
        alert("Unsupported format. Allowed: MP4, MOV, WEBM, MKV.")
        return
      }

      setFile(e.target.files[0])
      setPreview(URL.createObjectURL(e.target.files[0]))
    }
  }

  const removeFile = () => {
    setFile(null)
    setPreview(null)
    if (inputRef.current) inputRef.current.value = ""
  }

  const [modalPos, setModalPos] = useState({ x: 200, y: 100 });

  const dragOffset = useRef({ x: 0, y: 0 });
  const isDragging = useRef(false);

  const startDrag = (e) => {
    isDragging.current = true;
    dragOffset.current = {
      x: e.clientX - modalPos.x,
      y: e.clientY - modalPos.y
    };
  };

  const onDrag = (e) => {
    if (!isDragging.current) return;
    setModalPos({
      x: e.clientX - dragOffset.current.x,
      y: e.clientY - dragOffset.current.y
    });
  };

  const stopDrag = () => {
    isDragging.current = false;
  };

  useEffect(() => {
    window.addEventListener("mousemove", onDrag);
    window.addEventListener("mouseup", stopDrag);
    return () => {
      window.removeEventListener("mousemove", onDrag);
      window.removeEventListener("mouseup", stopDrag);
    };
  }, []);

  const handleUpload = async (e) => {
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
    <div className="upload-card">
      <h3 className="upload-title">Select an exercise:</h3>

      <div className="exercise-select">
        <div className="exercise-grid">
          {exerciseOptions.map((ex) => (
            <div
              key={ex.id}
              className={`exercise-card ${exercise === ex.id ? "selected" : ""}`}
              onClick={() => setExercise(ex.id)}
            >
              <div className="exercise-icon">{ex.icon}</div>
              <div className="exercise-name">{ex.label}</div>
            </div>
          ))}
      </div>
      </div>

      <h3 className="upload-title">Upload Your Video:</h3>

      <div
        className={`video-dropzone ${dragActive ? "drag-active" : ""}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
      >
        <input
          type="file"
          accept="video/*"
          ref={inputRef}
          onChange={handleChange}
          style={{ display: "none" }}
        />

        <div className="dropzone-content">
          <div className="drop-icon">📹</div>
          <h3>Drag & drop your video here</h3>
          <p>or click to select a file</p>
          <p>Supported formats: MP4, MOV, AVI, MKV, WEBM</p>
          <p>Maximum size: 50MB per file</p>
        </div>
      </div>

      {file && (
        <div className="uploaded-video-card">
          <div
            className="video-emoji-preview"
            onClick={() => openVideo(file)}
          >
            🎥
          </div>

          <div className="video-info">
            <span className="video-name" title={file.name}>
              {file.name.length > 30
                ? file.name.slice(0, 30) + "..."
                : file.name}
            </span>
            <span className="video-size">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>

          <button
            type="button"
            className="remove-video"
            onClick={removeFile}
          >
            ✕
          </button>
        </div>
      )}

      {previewVideo && (
        <div className="video-modal">
          <div className="video-modal-content" 
              onMouseDown={startDrag}
              onMouseUp={stopDrag}
              onMouseMove={onDrag}
              onClick={(e) => e.stopPropagation()}
              style={{ left: modalPos.x, top: modalPos.y }} >  
            <button className="modal-close" 
                    onClick={(e) => {
                      e.stopPropagation()
                      closeVideo()
                    }}>✕</button>
            <video src={previewVideo} className="video-preview" controls autoPlay onClick={(e) => e.preventDefault()}/>
          </div>
        </div>
      )}

      <button
        className="btn-ai-upload"
        disabled={loading || !file}
        onClick={handleUpload}
      >
        {loading ? "Processing..." : "Assess Technique"}
      </button>
    </div>
  )
}
