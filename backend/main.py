import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import routers
from routers import chat, vision, gallery, generation, history

load_dotenv()

app = FastAPI(title="Luna AI Backend")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files for image serving
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(vision.router, prefix="/api", tags=["vision"])
app.include_router(gallery.router, prefix="/api", tags=["gallery"])
app.include_router(generation.router, prefix="/api", tags=["generation"])
app.include_router(history.router, prefix="/api", tags=["history"])

@app.get("/")
async def root():
    return {
        "message": "Luna AI Backend is running!",
        "version": "1.0.0",
        "storage": "Local File System"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "storage": "local"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
