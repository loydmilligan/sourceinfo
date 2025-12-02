"""SourceInfo API - Main application entry point."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routes import analyze, sources, content

# Create FastAPI app
app = FastAPI(
    title="SourceInfo API",
    description="""
    API for news source credibility assessment, bias detection, and counternarrative discovery.

    ## Features

    * **Analyze article URLs** - Extract domain and get source credibility information
    * **Counternarratives** - Find credible sources from opposing political viewpoints
    * **Weighted scoring** - Context-aware evidence quality assessment
    * **Batch operations** - Process multiple URLs efficiently
    * **Flexible filtering** - Query sources by credibility, bias, type

    ## Use Cases

    * **Trump Admin Tracker** - Assess source bias and find counternarratives for timeline events
    * **Claim Analysis Tool** - Evaluate evidence quality for logical argument trees
    * **Research & Learning** - Understand source background and discover diverse perspectives
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze.router, prefix="/api")
app.include_router(sources.router, prefix="/api")
app.include_router(content.router, prefix="/api")


# Mount static files if they exist (production Docker build)
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/assets", StaticFiles(directory=static_path / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    async def root():
        """Serve the frontend."""
        return FileResponse(static_path / "index.html")

    @app.get("/{path:path}", include_in_schema=False)
    async def catch_all(path: str):
        """Serve frontend for all non-API routes (SPA support)."""
        # Skip API routes
        if path.startswith("api/") or path in ["docs", "redoc", "openapi.json", "health"]:
            return RedirectResponse(url=f"/{path}")

        # Try to serve static file
        file_path = static_path / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Fall back to index.html for SPA routing
        return FileResponse(static_path / "index.html")
else:
    @app.get("/", include_in_schema=False)
    async def root():
        """Redirect root to API documentation (dev mode)."""
        return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "database": str(settings.db_path)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
