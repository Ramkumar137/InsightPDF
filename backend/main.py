"""
FastAPI Backend for Context-Aware PDF Summarizer
Entry point for the application with CORS and route configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.routes import summarize, summaries, download
from app.database import engine, Base
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="PDF Summarizer API",
    description="Context-aware PDF summarization with multi-format export",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "PDF Summarizer API is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(summarize.router, prefix="/api", tags=["Summarization"])
app.include_router(summaries.router, prefix="/api", tags=["Summaries"])
app.include_router(download.router, prefix="/api", tags=["Download"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "code": "INTERNAL_SERVER_ERROR"
            }
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )


# """
# FastAPI Backend for Context-Aware PDF Summarizer
# Unified entry point serving both API and frontend
# """
# import os
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import JSONResponse, FileResponse
# from dotenv import load_dotenv

# from app.routes import summarize, summaries, download
# from app.database import engine, Base
# from app.config import settings

# # --- Setup directories and environment ---
# BASE_DIR = os.path.dirname(__file__)
# PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

# env_path = os.path.join(BASE_DIR, ".env")
# if os.path.exists(env_path):
#     load_dotenv(env_path)
# else:
#     load_dotenv()

# # --- Database Initialization ---
# Base.metadata.create_all(bind=engine)

# # --- Initialize FastAPI app ---
# app = FastAPI(
#     title="PDF Summarizer API",
#     description="Context-aware PDF summarization with multi-format export",
#     version="1.0.0",
# )

# # --- CORS Configuration ---
# origins_env = os.getenv(
#     "CORS_ORIGINS",
#     "http://localhost:3000,http://localhost:5173,http://localhost:8000"
# )
# origins = [o.strip() for o in origins_env.split(",") if o.strip()]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Include Routers ---
# app.include_router(summarize.router, prefix="/api", tags=["Summarization"])
# app.include_router(summaries.router, prefix="/api", tags=["Summaries"])
# app.include_router(download.router, prefix="/api", tags=["Download"])

# # --- Health endpoint (for backend) ---
# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}

# # --- Frontend static files ---
# frontend_dist_env = os.getenv("FRONTEND_DIST", os.path.join(PROJECT_ROOT, "frontend", "dist"))
# frontend_dist_path = (
#     frontend_dist_env
#     if os.path.isabs(frontend_dist_env)
#     else os.path.abspath(os.path.join(PROJECT_ROOT, frontend_dist_env))
# )

# # --- Root route (serve index.html) ---
# @app.get("/")
# async def serve_root():
#     index_path = os.path.join(frontend_dist_path, "./index.html")
#     if not os.path.isfile(index_path):
#         raise HTTPException(
#             status_code=404,
#             detail=f"Frontend not built. Missing '{index_path}'. Run 'npm run build' in frontend directory."
#         )
#     return FileResponse(index_path)

# # --- SPA Fallback for React Router ---
# @app.get("/{full_path:path}")
# async def spa_fallback(full_path: str):
#     blocked_prefixes = ("api/")
#     if any(full_path.startswith(p) for p in blocked_prefixes):
#         raise HTTPException(status_code=404, detail="Not Found")

#     index_path = os.path.join(frontend_dist_path, "index.html")
#     if not os.path.isfile(index_path):
#         raise HTTPException(status_code=404, detail="Frontend not built.")
#     return FileResponse(index_path)

# # --- Global Exception Handler ---
# @app.exception_handler(Exception)
# async def global_exception_handler(request, exc):
#     return JSONResponse(
#         status_code=500,
#         content={"error": {"message": str(exc), "code": "INTERNAL_SERVER_ERROR"}}
#     )

# # --- Uvicorn Entrypoint ---
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8080,
#         reload=True
#     )
