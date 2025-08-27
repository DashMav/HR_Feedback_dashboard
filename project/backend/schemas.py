from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# Organization schemas
class OrganizationCreate(BaseModel):
    name: str
    domain: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: int
    name: str
    domain: Optional[str]
    created_at: datetime
    is_active: bool

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str
    manager_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    organization_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    organization_id: int
    manager_id: Optional[int] = None
    is_active: bool
    last_login: Optional[datetime] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None

# Invitation schemas
class InvitationCreate(BaseModel):
    email: EmailStr
    role: str

class InvitationResponse(BaseModel):
    id: int
    email: str
    role: str
    expires_at: datetime
    accepted_at: Optional[datetime]
    created_at: datetime
    invited_by_name: str

class InvitationAccept(BaseModel):
    token: str
    name: str
    password: str

# Feedback schemas
class FeedbackCreate(BaseModel):
    employee_id: int
    strengths: str
    improvements: str
    sentiment: str
    tags: List[str] = []

class FeedbackUpdate(BaseModel):
    strengths: str
    improvements: str
    sentiment: str
    tags: List[str] = []

class FeedbackResponse(BaseModel):
    id: int
    employee_id: int
    manager_id: int
    organization_id: int
    strengths: str
    improvements: str
    sentiment: str
    tags: List[str]
    acknowledged: bool
    employee_comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    employee_name: str
    manager_name: str

class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    feedback_count: int
    last_feedback_date: Optional[datetime]
    avg_sentiment: float

class CommentCreate(BaseModel):
    comment: str

class DashboardStats(BaseModel):
    total_employees: int
    total_feedback: int
    pending_invitations: int
    sentiment_distribution: dict