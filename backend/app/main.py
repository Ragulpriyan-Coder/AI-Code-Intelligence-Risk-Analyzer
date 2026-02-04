"""
AI Code Intelligence & Risk Analyzer - Backend API

Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings, validate_settings
from app.db.session import init_db
from app.auth.routes import router as auth_router
from app.api.analyze import router as analyze_router
from app.api.reports import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Validate configuration
    if not validate_settings():
        print("Warning: Some configuration settings are missing")

    # Initialize database
    init_db()

    yield

    # Shutdown
    print("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    AI-powered code governance platform for analyzing code quality,
    security risks, and technical debt.

    **Core Features:**
    - Static code analysis
    - Security vulnerability detection
    - Maintainability scoring
    - Architecture assessment
    - Technical debt tracking
    - AI-powered explanations (LLM)
    - PDF report generation

    **Note:** This system uses rule-based analysis for scoring.
    LLM is used ONLY for generating explanations, never for decision-making.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Register Routers ==============

app.include_router(auth_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
app.include_router(reports_router, prefix="/api")


# ============== Health Check Endpoints ==============

@app.get("/", tags=["Health"])
def root():
    """Root endpoint - basic health check."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Detailed health check endpoint.
    Returns system status and configuration state.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "connected",
        "llm_configured": bool(settings.GROQ_API_KEY),
        "llm_model": settings.GROQ_MODEL if settings.GROQ_API_KEY else None,
    }


# ============== Run with Uvicorn ==============

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
