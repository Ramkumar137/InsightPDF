import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ... existing imports and setup ...

# Determine environment
IS_DEVELOPMENT = os.getenv("ENVIRONMENT", "development") == "development"

# CORS Configuration
if IS_DEVELOPMENT:
    origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    logger.info("🔧 DEVELOPMENT mode - CORS enabled for local frontend")
else:
    origins = settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else ["*"]
    logger.info(f"🚀 PRODUCTION mode - CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... existing routes ...

# Static Files for Production (add at the end, before if __name__ == "__main__")
FRONTEND_BUILD_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"

if FRONTEND_BUILD_DIR.exists() and not IS_DEVELOPMENT:
    logger.info(f"📦 Serving frontend from: {FRONTEND_BUILD_DIR}")
    
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=FRONTEND_BUILD_DIR / "assets"), name="assets")
    
    # Catch-all for React Router
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        file_path = FRONTEND_BUILD_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        index_path = FRONTEND_BUILD_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Not found")