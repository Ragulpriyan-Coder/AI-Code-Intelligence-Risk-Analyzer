"""API routes module."""
from app.api.analyze import router as analyze_router
from app.api.reports import router as reports_router

__all__ = ["analyze_router", "reports_router"]
