export async function assessVideo(file, exercise) {
  const formData = new FormData()
  formData.append("exercise_type", exercise)
  formData.append("file", file)

  const response = await fetch("http://localhost:8000/assessment/", {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    throw new Error("Failed to get assessment")
  }

  return await response.json()
}
