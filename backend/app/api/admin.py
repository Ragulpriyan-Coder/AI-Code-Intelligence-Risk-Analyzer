"""
Admin API endpoints for database management.
Requires admin privileges.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.db.models import User, AnalysisReport
from app.core.security import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============== Pydantic Models ==============

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    id: int
    user_id: int
    repo_url: str
    repo_name: str
    branch: str
    security_score: float
    maintainability_score: float
    architecture_score: float
    tech_debt_index: float
    refactor_urgency: str
    files_analyzed: int
    total_lines: int
    analysis_duration_seconds: float
    created_at: datetime
    username: Optional[str] = None

    class Config:
        from_attributes = True


class AdminStats(BaseModel):
    total_users: int
    total_reports: int
    active_users: int
    admin_users: int
    avg_security_score: float
    avg_maintainability_score: float
    avg_architecture_score: float
    reports_today: int


class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class CreateSuperuserRequest(BaseModel):
    email: str
    username: str
    password: str


class CreateSuperuserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    message: str


# ============== Helper Functions ==============

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


# ============== Admin Endpoints ==============

@router.get("/stats", response_model=AdminStats)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get admin dashboard statistics."""
    from sqlalchemy import func
    from datetime import date

    total_users = db.query(User).count()
    total_reports = db.query(AnalysisReport).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()

    # Average scores
    avg_scores = db.query(
        func.avg(AnalysisReport.security_score),
        func.avg(AnalysisReport.maintainability_score),
        func.avg(AnalysisReport.architecture_score)
    ).first()

    # Reports today
    today = date.today()
    reports_today = db.query(AnalysisReport).filter(
        func.date(AnalysisReport.created_at) == today
    ).count()

    return AdminStats(
        total_users=total_users,
        total_reports=total_reports,
        active_users=active_users,
        admin_users=admin_users,
        avg_security_score=round(avg_scores[0] or 0, 1),
        avg_maintainability_score=round(avg_scores[1] or 0, 1),
        avg_architecture_score=round(avg_scores[2] or 0, 1),
        reports_today=reports_today
    )


@router.get("/users", response_model=List[UserResponse])
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all users (admin only)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get a specific user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update user status (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-demotion
    if user_id == current_user.id and user_update.is_admin == False:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove your own admin privileges"
        )

    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    if user_update.is_admin is not None:
        user.is_admin = user_update.is_admin

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user and their reports (admin only)."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user's reports first
    db.query(AnalysisReport).filter(AnalysisReport.user_id == user_id).delete()

    # Delete user
    db.delete(user)
    db.commit()

    return {"message": f"User {user.username} deleted successfully"}


@router.get("/reports", response_model=List[ReportResponse])
def list_all_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all analysis reports (admin only)."""
    reports = db.query(AnalysisReport).order_by(
        AnalysisReport.created_at.desc()
    ).offset(skip).limit(limit).all()

    # Add username to each report
    result = []
    for report in reports:
        user = db.query(User).filter(User.id == report.user_id).first()
        report_dict = ReportResponse.model_validate(report)
        report_dict.username = user.username if user else "Unknown"
        result.append(report_dict)

    return result


@router.delete("/reports/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete an analysis report (admin only)."""
    report = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()

    return {"message": f"Report {report_id} deleted successfully"}


@router.post("/users/{user_id}/toggle-admin")
def toggle_admin_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Toggle admin status for a user."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot modify your own admin status"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_admin = not user.is_admin
    db.commit()

    return {
        "message": f"User {user.username} is now {'an admin' if user.is_admin else 'not an admin'}",
        "is_admin": user.is_admin
    }


@router.post("/create-superuser", response_model=CreateSuperuserResponse)
def create_superuser(
    request: CreateSuperuserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new superuser/admin account.
    Only existing admins can create new admins.
    """
    from app.auth.utils import (
        hash_password,
        validate_email,
        validate_username,
        validate_password_strength
    )

    # Validate email
    is_valid, error_msg = validate_email(request.email)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Validate username
    is_valid, error_msg = validate_username(request.username)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists"
        )

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists"
        )

    # Create new superuser
    hashed_pw = hash_password(request.password)
    new_user = User(
        email=request.email,
        username=request.username,
        hashed_password=hashed_pw,
        is_admin=True,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return CreateSuperuserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        is_admin=new_user.is_admin,
        message=f"Superuser '{new_user.username}' created successfully"
    )
