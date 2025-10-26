"""
FastAPI Backend for Context-Aware PDF Summarizer
UPDATED: CORS fix added directly
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

# Configure CORS - HARDCODED FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",      # ← Your frontend
        "http://127.0.0.1:8080",      # ← Alternative
        "http://localhost:5173",
        "http://localhost:3000",
        "*"  # ← TEMPORARY: Allow all origins for testing
    ],
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
        reload=True
    )