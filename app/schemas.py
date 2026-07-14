from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

# --- Tenant Schemas ---
class TenantBase(BaseModel):
    id: str
    name: str
    sso_domain: str

class TenantCreate(TenantBase):
    pass

class TenantResponse(TenantBase):
    class Config:
        from_attributes = True

# --- Employee Schemas ---
class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    role: str
    department: str
    birthday: Optional[datetime.date] = None
    anniversary: Optional[datetime.date] = None
    joining_date: Optional[datetime.date] = None
    status: Optional[str] = "ACTIVE"
    system_access_revoked: Optional[bool] = False

class EmployeeCreate(EmployeeBase):
    tenant_id: str

class EmployeeResponse(EmployeeBase):
    id: int
    tenant_id: str
    class Config:
        from_attributes = True

# --- Payroll Schemas ---
class PayrollBase(BaseModel):
    employee_id: int
    base_salary: float
    allowances: Optional[float] = 0.0
    deductions: Optional[float] = 0.0
    pay_period: str
    status: Optional[str] = "PENDING"

class PayrollCreate(PayrollBase):
    pass

class PayrollResponse(PayrollBase):
    id: int
    net_salary: float
    employee: Optional[EmployeeResponse] = None
    class Config:
        from_attributes = True

# --- Quote Schemas ---
class QuoteBase(BaseModel):
    text: str
    author: Optional[str] = "Unknown"

class QuoteCreate(QuoteBase):
    pass

class QuoteResponse(QuoteBase):
    id: int
    class Config:
        from_attributes = True

# --- Coupon Schemas ---
class CouponBase(BaseModel):
    code: str
    amount: float
    brand: str
    assigned_to_email: Optional[str] = None
    is_redeemed: Optional[bool] = False

class CouponCreate(CouponBase):
    tenant_id: str

class CouponResponse(CouponBase):
    id: int
    tenant_id: str
    class Config:
        from_attributes = True

# --- Club Schemas ---
class ClubBase(BaseModel):
    name: str
    description: Optional[str] = None

class ClubCreate(ClubBase):
    tenant_id: str

class ClubResponse(ClubBase):
    id: int
    tenant_id: str
    members: List[EmployeeResponse] = []
    class Config:
        from_attributes = True

class ClubMemberUpdate(BaseModel):
    employee_ids: List[int]

# --- Event Schemas ---
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime.datetime
    location: Optional[str] = None

class EventCreate(EventBase):
    tenant_id: str

class EventResponse(EventBase):
    id: int
    tenant_id: str
    class Config:
        from_attributes = True

# --- Asset Schemas ---
class AssetBase(BaseModel):
    hardware_name: str
    serial_number: str
    assigned_to: Optional[int] = None
    status: Optional[str] = "AVAILABLE"
    checkout_date: Optional[datetime.datetime] = None
    due_date: Optional[datetime.datetime] = None

class AssetCreate(AssetBase):
    tenant_id: str

class AssetResponse(AssetBase):
    id: int
    tenant_id: str
    assigned_employee: Optional[EmployeeResponse] = None
    class Config:
        from_attributes = True

class AssetCheckout(BaseModel):
    employee_id: int
    duration_days: int

# --- Document Request Schemas ---
class DocumentRequestBase(BaseModel):
    document_type: str

class DocumentRequestCreate(DocumentRequestBase):
    employee_id: int

class DocumentRequestResponse(DocumentRequestBase):
    id: int
    employee_id: int
    status: str
    file_path: Optional[str] = None
    request_date: datetime.datetime
    employee: Optional[EmployeeResponse] = None
    class Config:
        from_attributes = True

# --- Survey Response Schemas ---
class SurveyResponseBase(BaseModel):
    survey_month: str
    q1_burnout: int
    q2_alignment: int
    q3_satisfaction: int

class SurveyResponseCreate(SurveyResponseBase):
    tenant_id: str

class SurveyResponseResponse(SurveyResponseBase):
    id: int
    tenant_id: str
    submitted_at: datetime.datetime
    class Config:
        from_attributes = True

# --- Policy Schemas ---
class PolicyBase(BaseModel):
    category: str
    title: str
    content: str

class PolicyCreate(PolicyBase):
    tenant_id: str

class PolicyResponse(PolicyBase):
    id: int
    tenant_id: str
    class Config:
        from_attributes = True

# --- Interview Schemas ---
class InterviewBase(BaseModel):
    candidate_name: str
    candidate_email: EmailStr
    interview_time: datetime.datetime
    jd_title: str
    meeting_link: Optional[str] = None
    status: Optional[str] = "SCHEDULED"

class InterviewCreate(InterviewBase):
    tenant_id: str

class InterviewResponse(InterviewBase):
    id: int
    tenant_id: str
    class Config:
        from_attributes = True
