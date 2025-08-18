from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
import bcrypt
import os
from contextlib import contextmanager

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./feedback.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String)
    role = Column(String)  # 'manager' or 'employee'
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    manager = relationship("User", remote_side=[id], back_populates="employees")
    employees = relationship("User", back_populates="manager")
    given_feedback = relationship("Feedback", foreign_keys="Feedback.manager_id", back_populates="manager")
    received_feedback = relationship("Feedback", foreign_keys="Feedback.employee_id", back_populates="employee")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"))
    manager_id = Column(Integer, ForeignKey("users.id"))
    strengths = Column(Text)
    improvements = Column(Text)
    sentiment = Column(String)  # 'positive', 'neutral', 'negative'
    tags = Column(JSON, default=list)
    acknowledged = Column(Boolean, default=False)
    employee_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("User", foreign_keys=[employee_id], back_populates="received_feedback")
    manager = relationship("User", foreign_keys=[manager_id], back_populates="given_feedback")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str
    manager_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    manager_id: Optional[int] = None

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
    feedback_count: int
    last_feedback_date: Optional[datetime]
    avg_sentiment: float

class CommentCreate(BaseModel):
    comment: str

# FastAPI app
app = FastAPI(title="Feedback System API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173"), "http://localhost:3000", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth utilities
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Initialize demo data
def init_demo_data(db: Session):
    # Check if demo data already exists
    if db.query(User).first():
        return
    
    # Create demo users
    manager = User(
        email="manager@company.com",
        name="John Manager",
        password_hash=hash_password("password123"),
        role="manager"
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    
    employee = User(
        email="employee@company.com",
        name="Jane Employee",
        password_hash=hash_password("password123"),
        role="employee",
        manager_id=manager.id
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    
    # Create demo feedback
    feedback = Feedback(
        employee_id=employee.id,
        manager_id=manager.id,
        strengths="Excellent communication skills and always meets deadlines. Shows great initiative in problem-solving.",
        improvements="Could benefit from taking on more leadership responsibilities and mentoring junior team members.",
        sentiment="positive",
        tags=["communication", "reliability", "problem-solving"]
    )
    db.add(feedback)
    db.commit()

# Initialize demo data on startup
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        init_demo_data(db)
    finally:
        db.close()

# Routes
@app.post("/api/auth/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
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
            manager_id=user.manager_id
        )
    }

@app.get("/api/auth/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        manager_id=current_user.manager_id
    )

@app.get("/api/employees")
def get_employees(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can view employees")
    
    employees = db.query(User).filter(User.manager_id == current_user.id).all()
    result = []
    
    for employee in employees:
        feedback_count = db.query(Feedback).filter(Feedback.employee_id == employee.id).count()
        last_feedback = db.query(Feedback).filter(Feedback.employee_id == employee.id).order_by(Feedback.created_at.desc()).first()
        
        # Calculate average sentiment
        feedbacks = db.query(Feedback).filter(Feedback.employee_id == employee.id).all()
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
            feedback_count=feedback_count,
            last_feedback_date=last_feedback.created_at if last_feedback else None,
            avg_sentiment=avg_sentiment
        ))
    
    return result

@app.get("/api/employees/{employee_id}")
def get_employee(employee_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    employee = db.query(User).filter(User.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check permissions
    if current_user.role == "manager" and employee.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your team members")
    elif current_user.role == "employee" and employee.id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own profile")
    
    return UserResponse(
        id=employee.id,
        email=employee.email,
        name=employee.name,
        role=employee.role,
        manager_id=employee.manager_id
    )

@app.post("/api/feedback")
def create_feedback(feedback_data: FeedbackCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can give feedback")
    
    # Verify employee belongs to manager
    employee = db.query(User).filter(User.id == feedback_data.employee_id, User.manager_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found or not in your team")
    
    feedback = Feedback(
        employee_id=feedback_data.employee_id,
        manager_id=current_user.id,
        strengths=feedback_data.strengths,
        improvements=feedback_data.improvements,
        sentiment=feedback_data.sentiment,
        tags=feedback_data.tags
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return {"message": "Feedback created successfully", "id": feedback.id}

@app.get("/api/feedback/{feedback_id}")
def get_feedback(feedback_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    # Check permissions
    if current_user.role == "manager" and feedback.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view feedback you've given")
    elif current_user.role == "employee" and feedback.employee_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view feedback you've received")
    
    return FeedbackResponse(
        id=feedback.id,
        employee_id=feedback.employee_id,
        manager_id=feedback.manager_id,
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

@app.put("/api/feedback/{feedback_id}")
def update_feedback(feedback_id: int, feedback_data: FeedbackUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can update feedback")
    
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id, Feedback.manager_id == current_user.id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback.strengths = feedback_data.strengths
    feedback.improvements = feedback_data.improvements
    feedback.sentiment = feedback_data.sentiment
    feedback.tags = feedback_data.tags
    feedback.updated_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Feedback updated successfully"}

@app.delete("/api/feedback/{feedback_id}")
def delete_feedback(feedback_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can delete feedback")
    
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id, Feedback.manager_id == current_user.id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    db.delete(feedback)
    db.commit()
    return {"message": "Feedback deleted successfully"}

@app.get("/api/feedback/employee/{employee_id}")
def get_employee_feedback(employee_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check permissions
    if current_user.role == "manager":
        employee = db.query(User).filter(User.id == employee_id, User.manager_id == current_user.id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found or not in your team")
    elif current_user.role == "employee" and employee_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own feedback")
    
    feedbacks = db.query(Feedback).filter(Feedback.employee_id == employee_id).order_by(Feedback.created_at.desc()).all()
    
    result = []
    for feedback in feedbacks:
        result.append(FeedbackResponse(
            id=feedback.id,
            employee_id=feedback.employee_id,
            manager_id=feedback.manager_id,
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
        ))
    
    return result

@app.get("/api/feedback/received")
def get_received_feedback(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Only employees can view received feedback")
    
    feedbacks = db.query(Feedback).filter(Feedback.employee_id == current_user.id).order_by(Feedback.created_at.desc()).all()
    
    result = []
    for feedback in feedbacks:
        result.append(FeedbackResponse(
            id=feedback.id,
            employee_id=feedback.employee_id,
            manager_id=feedback.manager_id,
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
        ))
    
    return result

@app.post("/api/feedback/{feedback_id}/acknowledge")
def acknowledge_feedback(feedback_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Only employees can acknowledge feedback")
    
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id, Feedback.employee_id == current_user.id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback.acknowledged = True
    db.commit()
    return {"message": "Feedback acknowledged successfully"}

@app.post("/api/feedback/{feedback_id}/comment")
def add_comment(feedback_id: int, comment_data: CommentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Only employees can comment on feedback")
    
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id, Feedback.employee_id == current_user.id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback.employee_comment = comment_data.comment
    feedback.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Comment added successfully"}

@app.get("/api/dashboard/stats")
def get_dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can view dashboard stats")
    
    total_employees = db.query(User).filter(User.manager_id == current_user.id).count()
    total_feedback = db.query(Feedback).filter(Feedback.manager_id == current_user.id).count()
    
    # Get sentiment distribution
    feedbacks = db.query(Feedback).filter(Feedback.manager_id == current_user.id).all()
    sentiment_dist = {"positive": 0, "neutral": 0, "negative": 0}
    for feedback in feedbacks:
        sentiment_dist[feedback.sentiment] += 1
    
    return {
        "total_employees": total_employees,
        "total_feedback": total_feedback,
        "pending_requests": 0,  # Placeholder for future feature
        "sentiment_distribution": sentiment_dist
    }

@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
