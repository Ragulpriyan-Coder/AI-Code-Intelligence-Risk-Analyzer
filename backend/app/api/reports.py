"""
Reports API endpoints.
PDF report generation and download.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.db.models import AnalysisReport
from app.reports.pdf_generator import generate_pdf_report


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{analysis_id}/pdf")
def download_pdf_report(
    analysis_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Generate and download PDF report for an analysis.

    Args:
        analysis_id: Analysis report ID
        user_id: Current user ID from JWT
        db: Database session

    Returns:
        PDF file as streaming response
    """
    # Get analysis report
    report = db.query(AnalysisReport).filter(
        AnalysisReport.id == analysis_id,
        AnalysisReport.user_id == user_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Extract metrics from stored data
    metrics = report.metrics or {}

    security_summary = metrics.get("security", {
        "risk_level": "Unknown",
        "total_issues": 0,
        "severity_breakdown": {},
        "top_issues": [],
    })

    maintainability_summary = metrics.get("maintainability", {
        "average_complexity": 0,
        "average_maintainability_index": 0,
        "files_analyzed": report.files_analyzed,
    })

    architecture_summary = metrics.get("architecture", {
        "total_modules": report.files_analyzed,
        "total_packages": 0,
        "modularity_score": 0,
        "circular_dependencies_count": 0,
        "hub_modules": [],
    })

    tech_debt = metrics.get("tech_debt", {
        "index": report.tech_debt_index,
        "urgency": report.refactor_urgency,
        "priority_items": [],
        "summary": "",
    })

    scores = {
        "security_score": report.security_score,
        "maintainability_score": report.maintainability_score,
        "architecture_score": report.architecture_score,
        "tech_debt_index": report.tech_debt_index,
        "refactor_urgency": report.refactor_urgency,
    }

    analysis_metadata = {
        "files_analyzed": report.files_analyzed,
        "total_lines": report.total_lines,
        "duration": report.analysis_duration_seconds,
    }

    try:
        # Generate PDF
        pdf_bytes = generate_pdf_report(
            repo_name=report.repo_name,
            scores=scores,
            security_summary=security_summary,
            maintainability_summary=maintainability_summary,
            architecture_summary=architecture_summary,
            tech_debt=tech_debt,
            llm_explanation=report.llm_explanation,
            analysis_metadata=analysis_metadata,
        )

        # Create filename
        safe_name = "".join(c for c in report.repo_name if c.isalnum() or c in "-_")
        filename = f"analysis-{safe_name}-{report.id}.pdf"

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes)),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.get("/{analysis_id}/summary")
def get_report_summary(
    analysis_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a summary of an analysis report.

    Args:
        analysis_id: Analysis report ID
        user_id: Current user ID from JWT
        db: Database session

    Returns:
        Report summary data
    """
    report = db.query(AnalysisReport).filter(
        AnalysisReport.id == analysis_id,
        AnalysisReport.user_id == user_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Calculate overall health
    avg_score = (
        report.security_score +
        report.maintainability_score +
        report.architecture_score
    ) / 3

    if avg_score >= 80:
        health_status = "Healthy"
    elif avg_score >= 60:
        health_status = "Fair"
    elif avg_score >= 40:
        health_status = "Concerning"
    else:
        health_status = "Critical"

    return {
        "id": report.id,
        "repo_name": report.repo_name,
        "overall_health": {
            "score": round(avg_score, 1),
            "status": health_status,
        },
        "scores": {
            "security": report.security_score,
            "maintainability": report.maintainability_score,
            "architecture": report.architecture_score,
            "tech_debt_index": report.tech_debt_index,
        },
        "refactor_urgency": report.refactor_urgency,
        "files_analyzed": report.files_analyzed,
        "total_lines": report.total_lines,
        "created_at": report.created_at.isoformat(),
    }
