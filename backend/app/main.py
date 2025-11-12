from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import app as core_app
from app.routes import assessment, health

# --- CORS ---
core_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTES REGISTRATION ---
core_app.include_router(health.router)
core_app.include_router(assessment.router)

# --- ROOT ROUTE ---
@core_app.get("/", tags=["Root"])
def root():
    return {"message": "Workout Technique Assessment API is running!"}


# --- ENTRY POINT ---
app = core_app  # uvicorn expects variable "app"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
