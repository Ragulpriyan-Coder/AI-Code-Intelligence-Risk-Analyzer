"""
Analysis API endpoints.
Main endpoint for code analysis workflow.
"""
import time
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.db.models import AnalysisReport

from app.ingestion.github_loader import load_repository, cleanup_repository
from app.utils.file_utils import ProjectStructure, FileInfo

from app.analyzers.structure import analyze_file_structure, FileStructure
from app.analyzers.complexity import analyze_file_complexity, get_complexity_summary
from app.analyzers.security import analyze_file_security, get_security_summary
from app.analyzers.architecture import analyze_architecture, get_architecture_summary
from app.analyzers.maintainability import analyze_file_maintainability, get_maintainability_summary

from app.scoring.security_score import calculate_security_score
from app.scoring.maintainability_score import calculate_maintainability_score
from app.scoring.architecture_score import calculate_architecture_score
from app.scoring.tech_debt import calculate_tech_debt, get_overall_health_score

from app.llm.groq_client import groq_client, get_fallback_explanation


router = APIRouter(prefix="/analyze", tags=["Analysis"])


# ============== Request/Response Schemas ==============

class AnalyzeRequest(BaseModel):
    """Request schema for repository analysis."""
    repo_url: str
    branch: str = "main"


class AnalysisScores(BaseModel):
    """Score results from analysis."""
    security_score: float
    maintainability_score: float
    architecture_score: float
    tech_debt_index: float
    refactor_urgency: str


class AnalysisResponse(BaseModel):
    """Response schema for analysis results."""
    id: int
    repo_name: str
    repo_url: str
    branch: str
    metrics: Dict[str, Any]
    scores: AnalysisScores
    llm_explanation: str
    files_analyzed: int
    total_lines: int
    analysis_duration_seconds: float


class AnalysisListItem(BaseModel):
    """Item in analysis history list."""
    id: int
    repo_name: str
    repo_url: Optional[str]
    security_score: float
    maintainability_score: float
    architecture_score: float
    refactor_urgency: str
    created_at: str


# ============== Analysis Logic ==============

def run_full_analysis(
    project: ProjectStructure,
    repo_name: str
) -> Dict[str, Any]:
    """
    Run complete analysis pipeline on a project.

    Args:
        project: ProjectStructure with loaded files
        repo_name: Repository name

    Returns:
        Complete analysis results
    """
    # Analyze each file
    structures: List[FileStructure] = []
    complexities = []
    security_analyses = []
    maintainabilities = []

    for file_info in project.files:
        # Structure analysis
        structure = analyze_file_structure(file_info)
        structures.append(structure)

        # Complexity analysis
        complexity = analyze_file_complexity(file_info)
        complexities.append(complexity)

        # Security analysis
        security = analyze_file_security(file_info)
        security_analyses.append(security)

        # Maintainability analysis
        maintainability = analyze_file_maintainability(file_info, structure, complexity)
        maintainabilities.append(maintainability)

    # Architecture analysis (project-wide)
    architecture = analyze_architecture(project, structures)

    # Generate summaries
    complexity_summary = get_complexity_summary(complexities)
    security_summary = get_security_summary(security_analyses)
    architecture_summary = get_architecture_summary(architecture)
    maintainability_summary = get_maintainability_summary(maintainabilities)

    # Calculate scores
    security_score = calculate_security_score(
        security_analyses,
        project.total_files
    )

    maintainability_score = calculate_maintainability_score(
        complexities,
        maintainabilities
    )

    architecture_score = calculate_architecture_score(architecture)

    tech_debt = calculate_tech_debt(
        security_score,
        maintainability_score,
        architecture_score,
        project.total_lines,
        project.total_files
    )

    # Prepare scores dict
    scores = {
        "security_score": security_score.score,
        "maintainability_score": maintainability_score.score,
        "architecture_score": architecture_score.score,
        "tech_debt_index": tech_debt.index,
        "refactor_urgency": tech_debt.urgency.value,
    }

    # Prepare summaries for LLM and storage
    summaries = {
        "security": {
            "score": security_score.score,
            "grade": security_score.grade,
            "risk_level": security_score.risk_level,
            "total_issues": security_summary.get("total_issues", 0),
            "critical_count": security_summary.get("critical_count", 0),
            "high_count": security_summary.get("high_count", 0),
            "severity_breakdown": security_summary.get("severity_breakdown", {}),
            "top_issues": security_summary.get("top_issues", [])[:10],
            "summary": security_score.summary,
        },
        "maintainability": {
            "score": maintainability_score.score,
            "grade": maintainability_score.grade,
            "breakdown": maintainability_score.breakdown,
            "average_complexity": complexity_summary.get("average_complexity", 0),
            "average_maintainability_index": complexity_summary.get("average_maintainability_index", 0),
            "high_complexity_functions": complexity_summary.get("high_complexity_functions", []),
            "files_analyzed": complexity_summary.get("files_analyzed", 0),
            "summary": maintainability_score.summary,
        },
        "architecture": {
            "score": architecture_score.score,
            "grade": architecture_score.grade,
            "breakdown": architecture_score.breakdown,
            "total_modules": architecture_summary.get("total_modules", 0),
            "total_packages": architecture_summary.get("total_packages", 0),
            "modularity_score": architecture_summary.get("modularity_score", 0),
            "circular_dependencies_count": architecture_summary.get("circular_dependencies_count", 0),
            "hub_modules": architecture_summary.get("hub_modules", []),
            "top_issues": architecture_summary.get("top_issues", []),
            "summary": architecture_score.summary,
        },
        "tech_debt": {
            "index": tech_debt.index,
            "urgency": tech_debt.urgency.value,
            "breakdown": tech_debt.breakdown,
            "priority_items": tech_debt.priority_items,
            "estimated_effort": tech_debt.estimated_effort,
            "summary": tech_debt.summary,
        },
    }

    # Generate LLM explanation
    llm_explanation = ""

    if groq_client.is_configured():
        llm_response = groq_client.generate_analysis_explanation(
            scores=scores,
            security_summary=summaries["security"],
            maintainability_summary=summaries["maintainability"],
            architecture_summary=summaries["architecture"],
            tech_debt=summaries["tech_debt"],
            repo_name=repo_name
        )

        if llm_response.success:
            llm_explanation = llm_response.content
        else:
            # Use fallback if LLM fails
            llm_explanation = get_fallback_explanation(
                scores, summaries["security"], summaries["tech_debt"]
            )
    else:
        # Use fallback if LLM not configured
        llm_explanation = get_fallback_explanation(
            scores, summaries["security"], summaries["tech_debt"]
        )

    return {
        "scores": scores,
        "summaries": summaries,
        "llm_explanation": llm_explanation,
        "metrics": {
            "security": summaries["security"],
            "maintainability": summaries["maintainability"],
            "architecture": summaries["architecture"],
            "tech_debt": summaries["tech_debt"],
        },
    }


# ============== API Endpoints ==============

@router.post("", response_model=AnalysisResponse)
def analyze_repository(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """
    Analyze a GitHub repository.

    This endpoint:
    1. Clones the repository
    2. Runs static analysis (structure, complexity, security, architecture)
    3. Calculates deterministic scores
    4. Generates LLM explanation (if configured)
    5. Stores results in database
    6. Returns complete analysis

    Args:
        request: Analysis request with repo URL and branch
        background_tasks: FastAPI background tasks
        user_id: Current user ID from JWT
        db: Database session

    Returns:
        Complete analysis results
    """
    start_time = time.time()

    # Load repository
    repo_info, project = load_repository(request.repo_url, request.branch)

    if not repo_info.is_valid or project is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=repo_info.error_message or "Failed to load repository"
        )

    if project.total_files == 0:
        # Cleanup and return error
        if repo_info.local_path:
            background_tasks.add_task(cleanup_repository, repo_info.local_path)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analyzable files found in repository"
        )

    try:
        # Run analysis
        analysis_results = run_full_analysis(project, repo_info.name)

        duration = time.time() - start_time

        # Create database record
        report = AnalysisReport(
            user_id=user_id,
            repo_url=request.repo_url,
            repo_name=repo_info.name,
            branch=repo_info.branch,
            metrics=analysis_results["metrics"],
            security_score=analysis_results["scores"]["security_score"],
            maintainability_score=analysis_results["scores"]["maintainability_score"],
            architecture_score=analysis_results["scores"]["architecture_score"],
            tech_debt_index=analysis_results["scores"]["tech_debt_index"],
            refactor_urgency=analysis_results["scores"]["refactor_urgency"],
            llm_explanation=analysis_results["llm_explanation"],
            files_analyzed=project.total_files,
            total_lines=project.total_lines,
            analysis_duration_seconds=duration,
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        # Schedule cleanup
        background_tasks.add_task(cleanup_repository, repo_info.local_path)

        return AnalysisResponse(
            id=report.id,
            repo_name=repo_info.name,
            repo_url=request.repo_url,
            branch=repo_info.branch,
            metrics=analysis_results["metrics"],
            scores=AnalysisScores(**analysis_results["scores"]),
            llm_explanation=analysis_results["llm_explanation"],
            files_analyzed=project.total_files,
            total_lines=project.total_lines,
            analysis_duration_seconds=duration,
        )

    except Exception as e:
        # Cleanup on error
        if repo_info.local_path:
            background_tasks.add_task(cleanup_repository, repo_info.local_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """
    Get a specific analysis by ID.

    Args:
        analysis_id: Analysis report ID
        user_id: Current user ID from JWT
        db: Database session

    Returns:
        Analysis results
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

    return AnalysisResponse(
        id=report.id,
        repo_name=report.repo_name,
        repo_url=report.repo_url or "",
        branch=report.branch,
        metrics=report.metrics,
        scores=AnalysisScores(
            security_score=report.security_score,
            maintainability_score=report.maintainability_score,
            architecture_score=report.architecture_score,
            tech_debt_index=report.tech_debt_index,
            refactor_urgency=report.refactor_urgency,
        ),
        llm_explanation=report.llm_explanation or "",
        files_analyzed=report.files_analyzed,
        total_lines=report.total_lines,
        analysis_duration_seconds=report.analysis_duration_seconds,
    )


@router.get("", response_model=List[AnalysisListItem])
def list_analyses(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
) -> List[AnalysisListItem]:
    """
    List user's analysis history.

    Args:
        user_id: Current user ID from JWT
        db: Database session
        limit: Max results to return
        offset: Pagination offset

    Returns:
        List of analysis summaries
    """
    reports = db.query(AnalysisReport).filter(
        AnalysisReport.user_id == user_id
    ).order_by(
        AnalysisReport.created_at.desc()
    ).offset(offset).limit(limit).all()

    return [
        AnalysisListItem(
            id=r.id,
            repo_name=r.repo_name,
            repo_url=r.repo_url,
            security_score=r.security_score,
            maintainability_score=r.maintainability_score,
            architecture_score=r.architecture_score,
            refactor_urgency=r.refactor_urgency,
            created_at=r.created_at.isoformat(),
        )
        for r in reports
    ]


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete an analysis report.

    Args:
        analysis_id: Analysis report ID
        user_id: Current user ID from JWT
        db: Database session

    Returns:
        Success message
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

    db.delete(report)
    db.commit()

    return {"message": "Analysis deleted successfully"}
