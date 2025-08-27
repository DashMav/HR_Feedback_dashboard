from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
import os

from database import get_db, create_tables
from models import User, Organization, Feedback, Invitation
from schemas import *
from auth import *

# FastAPI app
app = FastAPI(title="Multi-Tenant Feedback System API", version="2.0.0")

# CORS middleware
allowed_origins = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
    "http://localhost:3000",
    "http://localhost:5173",
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()
    # Initialize demo data if needed
    db = next(get_db())
    try:
        init_demo_data(db)
    finally:
        db.close()

def init_demo_data(db: Session):
    """Initialize demo organization and users"""
    if db.query(Organization).first():
        return
    
    # Create demo organization
    demo_org = Organization(name="Demo Company", domain="demo.com")
    db.add(demo_org)
    db.commit()
    db.refresh(demo_org)
    
    # Create demo users
    owner = User(
        email="owner@demo.com",
        name="Organization Owner",
        password_hash=hash_password("password123"),
        role="owner",
        organization_id=demo_org.id
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)
    
    manager = User(
        email="manager@demo.com",
        name="Team Manager",
        password_hash=hash_password("password123"),
        role="manager",
        organization_id=demo_org.id
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    
    employee = User(
        email="employee@demo.com",
        name="Team Employee",
        password_hash=hash_password("password123"),
        role="employee",
        organization_id=demo_org.id,
        manager_id=manager.id
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    
    # Create demo feedback
    feedback = Feedback(
        employee_id=employee.id,
        manager_id=manager.id,
        organization_id=demo_org.id,
        strengths="Excellent communication skills and always meets deadlines.",
        improvements="Could benefit from taking on more leadership responsibilities.",
        sentiment="positive",
        tags=["communication", "reliability"]
    )
    db.add(feedback)
    db.commit()

# Organization endpoints
@app.post("/api/organizations", response_model=OrganizationResponse)
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """Create a new organization (public endpoint for initial setup)"""
    # Check if organization name already exists
    existing_org = db.query(Organization).filter(Organization.name == org_data.name).first()
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization name already exists")
    
    organization = Organization(
        name=org_data.name,
        domain=org_data.domain
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    return organization

@app.get("/api/organizations", response_model=List[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)):
    """List all organizations (for login selection)"""
    organizations = db.query(Organization).filter(Organization.is_active == True).all()
    return organizations

@app.get("/api/organizations/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organization details"""
    if current_user.organization_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    organization = db.query(Organization).filter(Organization.id == org_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organization

# Authentication endpoints
@app.post("/api/auth/register")
def register_user(
    user_data: UserCreate,
    organization_id: int,
    db: Session = Depends(get_db)
):
    """Register first user as organization owner"""
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if organization already has users
    existing_users = db.query(User).filter(User.organization_id == organization_id).count()
    if existing_users > 0:
        raise HTTPException(status_code=400, detail="Organization already has users. Use invitation system.")
    
    # Check if email already exists in organization
    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.organization_id == organization_id
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered in this organization")
    
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hash_password(user_data.password),
        role="owner",  # First user becomes owner
        organization_id=organization_id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.id})
    return {
        "token": access_token,
        "user": UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            organization_id=user.organization_id,
            manager_id=user.manager_id,
            is_active=user.is_active,
            last_login=user.last_login
        )
    }

@app.post("/api/auth/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    query = db.query(User).filter(User.email == user_data.email, User.is_active == True)
    
    if user_data.organization_id:
        query = query.filter(User.organization_id == user_data.organization_id)
    
    user = query.first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.id})
    return {
        "token": access_token,
        "user": UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            organization_id=user.organization_id,
            manager_id=user.manager_id,
            is_active=user.is_active,
            last_login=user.last_login
        )
    }

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        organization_id=current_user.organization_id,
        manager_id=current_user.manager_id,
        is_active=current_user.is_active,
        last_login=current_user.last_login
    )

# User management endpoints
@app.get("/api/users", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(require_role(['owner', 'admin'])),
    db: Session = Depends(get_db)
):
    """List all users in organization"""
    users = db.query(User).filter(User.organization_id == current_user.organization_id).all()
    return [UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        organization_id=user.organization_id,
        manager_id=user.manager_id,
        is_active=user.is_active,
        last_login=user.last_login
    ) for user in users]

@app.put("/api/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_role(['owner', 'admin'])),
    db: Session = Depends(get_db)
):
    """Update user details"""
    target_user = require_same_organization(user_id, current_user, db)
    
    if user_data.name is not None:
        target_user.name = user_data.name
    if user_data.role is not None:
        target_user.role = user_data.role
    if user_data.manager_id is not None:
        # Verify manager is in same organization
        if user_data.manager_id:
            require_same_organization(user_data.manager_id, current_user, db)
        target_user.manager_id = user_data.manager_id
    if user_data.is_active is not None:
        target_user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(target_user)
    
    return UserResponse(
        id=target_user.id,
        email=target_user.email,
        name=target_user.name,
        role=target_user.role,
        organization_id=target_user.organization_id,
        manager_id=target_user.manager_id,
        is_active=target_user.is_active,
        last_login=target_user.last_login
    )

# Invitation endpoints
@app.post("/api/invitations", response_model=InvitationResponse)
def create_invitation(
    invitation_data: InvitationCreate,
    current_user: User = Depends(require_role(['owner', 'admin', 'manager'])),
    db: Session = Depends(get_db)
):
    """Create user invitation"""
    # Check if user already exists in organization
    existing_user = db.query(User).filter(
        User.email == invitation_data.email,
        User.organization_id == current_user.organization_id
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists in organization")
    
    # Check if invitation already exists
    existing_invitation = db.query(Invitation).filter(
        Invitation.email == invitation_data.email,
        Invitation.organization_id == current_user.organization_id,
        Invitation.accepted_at.is_(None),
        Invitation.expires_at > datetime.utcnow()
    ).first()
    if existing_invitation:
        raise HTTPException(status_code=400, detail="Active invitation already exists for this email")
    
    invitation = Invitation(
        email=invitation_data.email,
        organization_id=current_user.organization_id,
        invited_by_id=current_user.id,
        role=invitation_data.role,
        token=generate_invitation_token(),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    return InvitationResponse(
        id=invitation.id,
        email=invitation.email,
        role=invitation.role,
        expires_at=invitation.expires_at,
        accepted_at=invitation.accepted_at,
        created_at=invitation.created_at,
        invited_by_name=current_user.name
    )

@app.get("/api/invitations", response_model=List[InvitationResponse])
def list_invitations(
    current_user: User = Depends(require_role(['owner', 'admin'])),
    db: Session = Depends(get_db)
):
    """List pending invitations"""
    invitations = db.query(Invitation).filter(
        Invitation.organization_id == current_user.organization_id,
        Invitation.accepted_at.is_(None),
        Invitation.expires_at > datetime.utcnow()
    ).all()
    
    return [InvitationResponse(
        id=inv.id,
        email=inv.email,
        role=inv.role,
        expires_at=inv.expires_at,
        accepted_at=inv.accepted_at,
        created_at=inv.created_at,
        invited_by_name=inv.invited_by.name
    ) for inv in invitations]

@app.post("/api/invitations/accept")
def accept_invitation(
    acceptance_data: InvitationAccept,
    db: Session = Depends(get_db)
):
    """Accept invitation and create user account"""
    invitation = db.query(Invitation).filter(
        Invitation.token == acceptance_data.token,
        Invitation.accepted_at.is_(None),
        Invitation.expires_at > datetime.utcnow()
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        User.email == invitation.email,
        User.organization_id == invitation.organization_id
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user = User(
        email=invitation.email,
        name=acceptance_data.name,
        password_hash=hash_password(acceptance_data.password),
        role=invitation.role,
        organization_id=invitation.organization_id
    )
    
    db.add(user)
    
    # Mark invitation as accepted
    invitation.accepted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.id})
    return {
        "token": access_token,
        "user": UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            organization_id=user.organization_id,
            manager_id=user.manager_id,
            is_active=user.is_active,
            last_login=user.last_login
        )
    }

# Employee endpoints
@app.get("/api/employees", response_model=List[EmployeeResponse])
def get_employees(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get employees based on user role"""
    if current_user.role in ['owner', 'admin']:
        # Get all employees in organization
        employees = db.query(User).filter(
            User.organization_id == current_user.organization_id,
            User.role == 'employee'
        ).all()
    elif current_user.role == 'manager':
        # Get direct reports
        employees = db.query(User).filter(
            User.manager_id == current_user.id,
            User.organization_id == current_user.organization_id
        ).all()
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = []
    for employee in employees:
        feedback_count = db.query(Feedback).filter(
            Feedback.employee_id == employee.id,
            Feedback.organization_id == current_user.organization_id
        ).count()
        
        last_feedback = db.query(Feedback).filter(
            Feedback.employee_id == employee.id,
            Feedback.organization_id == current_user.organization_id
        ).order_by(Feedback.created_at.desc()).first()
        
        # Calculate average sentiment
        feedbacks = db.query(Feedback).filter(
            Feedback.employee_id == employee.id,
            Feedback.organization_id == current_user.organization_id
        ).all()
        
        sentiment_scores = []
        for f in feedbacks:
            if f.sentiment == "positive":
                sentiment_scores.append(1.0)
            elif f.sentiment == "neutral":
                sentiment_scores.append(0.5)
            else:
                sentiment_scores.append(0.0)
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.5
        
        result.append(EmployeeResponse(
            id=employee.id,
            name=employee.name,
            email=employee.email,
            role=employee.role,
            is_active=employee.is_active,
            feedback_count=feedback_count,
            last_feedback_date=last_feedback.created_at if last_feedback else None,
            avg_sentiment=avg_sentiment
        ))
    
    return result

# Feedback endpoints (updated with organization filtering)
@app.post("/api/feedback")
def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(require_role(['manager', 'admin', 'owner'])),
    db: Session = Depends(get_db)
):
    """Create feedback"""
    # Verify employee is in same organization
    employee = require_same_organization(feedback_data.employee_id, current_user, db)
    
    # Verify manager can give feedback to this employee
    if current_user.role == 'manager' and employee.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only give feedback to your direct reports")
    
    feedback = Feedback(
        employee_id=feedback_data.employee_id,
        manager_id=current_user.id,
        organization_id=current_user.organization_id,
        strengths=feedback_data.strengths,
        improvements=feedback_data.improvements,
        sentiment=feedback_data.sentiment,
        tags=feedback_data.tags
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return {"message": "Feedback created successfully", "id": feedback.id}

@app.get("/api/feedback/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific feedback"""
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.organization_id == current_user.organization_id
    ).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Check permissions
    if (current_user.role == 'employee' and feedback.employee_id != current_user.id) or \
       (current_user.role == 'manager' and feedback.manager_id != current_user.id and feedback.employee_id not in [e.id for e in current_user.employees]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FeedbackResponse(
        id=feedback.id,
        employee_id=feedback.employee_id,
        manager_id=feedback.manager_id,
        organization_id=feedback.organization_id,
        strengths=feedback.strengths,
        improvements=feedback.improvements,
        sentiment=feedback.sentiment,
        tags=feedback.tags or [],
        acknowledged=feedback.acknowledged,
        employee_comment=feedback.employee_comment,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
        employee_name=feedback.employee.name,
        manager_name=feedback.manager.name
    )

@app.get("/api/feedback/received", response_model=List[FeedbackResponse])
def get_received_feedback(
    current_user: User = Depends(require_role(['employee'])),
    db: Session = Depends(get_db)
):
    """Get feedback received by current user"""
    feedbacks = db.query(Feedback).filter(
        Feedback.employee_id == current_user.id,
        Feedback.organization_id == current_user.organization_id
    ).order_by(Feedback.created_at.desc()).all()
    
    return [FeedbackResponse(
        id=f.id,
        employee_id=f.employee_id,
        manager_id=f.manager_id,
        organization_id=f.organization_id,
        strengths=f.strengths,
        improvements=f.improvements,
        sentiment=f.sentiment,
        tags=f.tags or [],
        acknowledged=f.acknowledged,
        employee_comment=f.employee_comment,
        created_at=f.created_at,
        updated_at=f.updated_at,
        employee_name=f.employee.name,
        manager_name=f.manager.name
    ) for f in feedbacks]

@app.get("/api/feedback/employee/{employee_id}", response_model=List[FeedbackResponse])
def get_employee_feedback(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all feedback for specific employee"""
    # Verify employee is in same organization
    employee = require_same_organization(employee_id, current_user, db)
    
    # Check permissions
    if current_user.role == 'employee' and employee_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own feedback")
    elif current_user.role == 'manager' and employee.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view feedback for your direct reports")
    
    feedbacks = db.query(Feedback).filter(
        Feedback.employee_id == employee_id,
        Feedback.organization_id == current_user.organization_id
    ).order_by(Feedback.created_at.desc()).all()
    
    return [FeedbackResponse(
        id=f.id,
        employee_id=f.employee_id,
        manager_id=f.manager_id,
        organization_id=f.organization_id,
        strengths=f.strengths,
        improvements=f.improvements,
        sentiment=f.sentiment,
        tags=f.tags or [],
        acknowledged=f.acknowledged,
        employee_comment=f.employee_comment,
        created_at=f.created_at,
        updated_at=f.updated_at,
        employee_name=f.employee.name,
        manager_name=f.manager.name
    ) for f in feedbacks]

@app.post("/api/feedback/{feedback_id}/acknowledge")
def acknowledge_feedback(
    feedback_id: int,
    current_user: User = Depends(require_role(['employee'])),
    db: Session = Depends(get_db)
):
    """Acknowledge feedback"""
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.employee_id == current_user.id,
        Feedback.organization_id == current_user.organization_id
    ).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback.acknowledged = True
    db.commit()
    return {"message": "Feedback acknowledged successfully"}

@app.post("/api/feedback/{feedback_id}/comment")
def add_comment(
    feedback_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(require_role(['employee'])),
    db: Session = Depends(get_db)
):
    """Add comment to feedback"""
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.employee_id == current_user.id,
        Feedback.organization_id == current_user.organization_id
    ).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback.employee_comment = comment_data.comment
    feedback.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Comment added successfully"}

@app.get("/api/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(require_role(['manager', 'admin', 'owner'])),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    if current_user.role in ['owner', 'admin']:
        # Organization-wide stats
        total_employees = db.query(User).filter(
            User.organization_id == current_user.organization_id,
            User.role == 'employee'
        ).count()
        
        total_feedback = db.query(Feedback).filter(
            Feedback.organization_id == current_user.organization_id
        ).count()
    else:
        # Manager stats for their team
        total_employees = db.query(User).filter(
            User.manager_id == current_user.id,
            User.organization_id == current_user.organization_id
        ).count()
        
        total_feedback = db.query(Feedback).filter(
            Feedback.manager_id == current_user.id,
            Feedback.organization_id == current_user.organization_id
        ).count()
    
    # Pending invitations
    pending_invitations = db.query(Invitation).filter(
        Invitation.organization_id == current_user.organization_id,
        Invitation.accepted_at.is_(None),
        Invitation.expires_at > datetime.utcnow()
    ).count()
    
    # Sentiment distribution
    feedbacks = db.query(Feedback).filter(
        Feedback.organization_id == current_user.organization_id
    ).all()
    
    sentiment_dist = {"positive": 0, "neutral": 0, "negative": 0}
    for feedback in feedbacks:
        sentiment_dist[feedback.sentiment] += 1
    
    return DashboardStats(
        total_employees=total_employees,
        total_feedback=total_feedback,
        pending_invitations=pending_invitations,
        sentiment_distribution=sentiment_dist
    )

@app.get("/")
def health_check():
    return {"status": "ok", "version": "2.0.0", "features": ["multi-tenant", "postgresql"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)