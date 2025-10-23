"""
Startup script for PDF Summarizer API
"""
import uvicorn
import sys
import os


def main():
    """Run the FastAPI application"""

    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Warning: .env file not found!")
        print("Please create .env file from .env.example")
        print("cp .env.example .env")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

    print("=" * 50)
    print("Starting PDF Summarizer API")
    print("=" * 50)
    print("\nAPI will be available at:")
    print("  - Local: http://localhost:8000")
    print("  - Docs: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("\nPress CTRL+C to stop the server")
    print("=" * 50)
    print()

    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()