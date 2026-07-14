from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime

# Association Table for Club Members
club_members = Table(
    'club_members',
    Base.metadata,
    Column('club_id', Integer, ForeignKey('clubs.id', ondelete='CASCADE'), primary_key=True),
    Column('employee_id', Integer, ForeignKey('employees.id', ondelete='CASCADE'), primary_key=True)
)

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True, index=True) # slug like 'acme'
    name = Column(String, nullable=False)
    sso_domain = Column(String, nullable=False) # e.g. 'acme.com'
    
    employees = relationship("Employee", back_populates="tenant", cascade="all, delete-orphan")
    coupons = relationship("Coupon", back_populates="tenant", cascade="all, delete-orphan")
    clubs = relationship("Club", back_populates="tenant", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="tenant", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="tenant", cascade="all, delete-orphan")
    survey_responses = relationship("SurveyResponse", back_populates="tenant", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="tenant", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="tenant", cascade="all, delete-orphan")


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    department = Column(String, nullable=False)
    birthday = Column(Date, nullable=True)
    anniversary = Column(Date, nullable=True)
    joining_date = Column(Date, default=datetime.date.today)
    status = Column(String, default="ACTIVE") # ACTIVE, OFFBOARDING, INACTIVE
    system_access_revoked = Column(Boolean, default=False)
    
    tenant = relationship("Tenant", back_populates="employees")
    payrolls = relationship("Payroll", back_populates="employee", cascade="all, delete-orphan")
    document_requests = relationship("DocumentRequest", back_populates="employee", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="assigned_employee")
    clubs = relationship("Club", secondary=club_members, back_populates="members")


class Payroll(Base):
    __tablename__ = "payrolls"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    base_salary = Column(Float, nullable=False)
    allowances = Column(Float, default=0.0)
    deductions = Column(Float, default=0.0)
    net_salary = Column(Float, nullable=False)
    pay_period = Column(String, nullable=False) # e.g. '2026-06'
    status = Column(String, default="PENDING") # PENDING, SENT
    
    employee = relationship("Employee", back_populates="payrolls")


class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    author = Column(String, default="Unknown")


class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    brand = Column(String, nullable=False) # e.g. Amazon, Starbucks
    assigned_to_email = Column(String, nullable=True)
    is_redeemed = Column(Boolean, default=False)
    
    tenant = relationship("Tenant", back_populates="coupons")


class Club(Base):
    __tablename__ = "clubs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    tenant = relationship("Tenant", back_populates="clubs")
    members = relationship("Employee", secondary=club_members, back_populates="clubs")


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    
    tenant = relationship("Tenant", back_populates="events")


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    hardware_name = Column(String, nullable=False)
    serial_number = Column(String, unique=True, index=True, nullable=False)
    assigned_to = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, default="AVAILABLE") # AVAILABLE, CHECKED_OUT
    checkout_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    tenant = relationship("Tenant", back_populates="assets")
    assigned_employee = relationship("Employee", back_populates="assets")


class DocumentRequest(Base):
    __tablename__ = "document_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String, nullable=False) # e.g. EMPLOYMENT_PROOF
    status = Column(String, default="PENDING") # PENDING, GENERATED
    file_path = Column(String, nullable=True)
    request_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    employee = relationship("Employee", back_populates="document_requests")


class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    survey_month = Column(String, nullable=False) # e.g. '2026-06'
    q1_burnout = Column(Integer, nullable=False) # 1-5
    q2_alignment = Column(Integer, nullable=False) # 1-5
    q3_satisfaction = Column(Integer, nullable=False) # 1-5
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="survey_responses")


class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    category = Column(String, nullable=False) # e.g. WFH, Leave, Travel
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    tenant = relationship("Tenant", back_populates="policies")


class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    candidate_name = Column(String, nullable=False)
    candidate_email = Column(String, nullable=False)
    interview_time = Column(DateTime, nullable=False)
    jd_title = Column(String, nullable=False)
    meeting_link = Column(String, nullable=True)
    status = Column(String, default="SCHEDULED") # SCHEDULED, COMPLETED, CANCELLED
    
    tenant = relationship("Tenant", back_populates="interviews")
