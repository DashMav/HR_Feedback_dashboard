from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import os

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    domain = Column(String, nullable=True)  # Optional email domain for auto-assignment
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    invitations = relationship("Invitation", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    name = Column(String)
    password_hash = Column(String)
    role = Column(String)  # 'owner', 'admin', 'manager', 'employee'
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Unique constraint for email within organization
    __table_args__ = (UniqueConstraint('email', 'organization_id', name='unique_email_per_org'),)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    manager = relationship("User", remote_side=[id], back_populates="employees")
    employees = relationship("User", back_populates="manager")
    given_feedback = relationship("Feedback", foreign_keys="Feedback.manager_id", back_populates="manager")
    received_feedback = relationship("Feedback", foreign_keys="Feedback.employee_id", back_populates="employee")

class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    invited_by_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)  # Role to assign when invitation is accepted
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="invitations")
    invited_by = relationship("User")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"))
    manager_id = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))  # For data isolation
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
    organization = relationship("Organization")