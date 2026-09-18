# schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Planner schemas (add to schemas.py) ---
from typing import List


class PlannerInputs(BaseModel):
    productName: str
    category: str
    stage: str
    market: str


class RoadmapStep(BaseModel):
    id: str
    title: str
    description: str


class RoadmapResponse(BaseModel):
    steps: List[RoadmapStep]


class ProgressToggle(BaseModel):
    step_id: str


class ProgressItem(BaseModel):
    step_id: str
    is_checked: bool


class ProgressResponse(BaseModel):
    progress: List[ProgressItem]

class LabMatchRequest(BaseModel):
    category: str
    location: Optional[str] = None


class LabResult(BaseModel):
    id: int
    name: str
    category: str
    location: str
    capability: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class LabMatchResponse(BaseModel):
    results: list[LabResult]

class ImpactCheckRequest(BaseModel):
    standard_code: str
    change_type: str
    description: str
    recommended_action: str


class AffectedProduct(BaseModel):
    product_name: str
    category: str
    standard_code: str


class ImpactCheckResponse(BaseModel):
    standard_code: str
    change_type: str
    description: str
    recommended_action: str
    affected_products: list[AffectedProduct]

class NewsletterPostOut(BaseModel):
    id: int
    title: str
    category: str
    summary: str
    published_at: datetime


class NewsletterFeedResponse(BaseModel):
    posts: list[NewsletterPostOut]


class SubscriptionToggle(BaseModel):
    category: str


class SubscriptionResponse(BaseModel):
    subscribed_categories: list[str]

class AuditFinding(BaseModel):
    status: str      # "pass" | "missing" | "warning"
    message: str


class DocumentAuditResponse(BaseModel):
    filename: str
    readiness_score: int
    findings: list[AuditFinding]

class CopilotRequest(BaseModel):
    requirement_text: str


class CopilotResponse(BaseModel):
    answer: str
    source: str   # "ai" or "fallback"

class ProductCreate(BaseModel):
    product_name: str
    category: str
    standard_code: str


class ProductOut(BaseModel):
    id: int
    product_name: str
    category: str
    standard_code: str


class ProductListResponse(BaseModel):
    products: list[ProductOut]

class ChangeEventOut(BaseModel):
    id: int
    standard_code: str
    change_type: str
    description: str
    recommended_action: str


class ChangeEventListResponse(BaseModel):
    events: list[ChangeEventOut]

class ProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    manufacturer_type: Optional[str] = None
    factory_location: Optional[str] = None
    business_type: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    company_name: Optional[str] = None
    manufacturer_type: Optional[str] = None
    factory_location: Optional[str] = None
    business_type: Optional[str] = None