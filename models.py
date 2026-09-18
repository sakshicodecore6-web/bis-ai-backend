# models.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BISyncProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)

    company_name: Optional[str] = None
    manufacturer_type: Optional[str] = None
    factory_location: Optional[str] = None
    business_type: Optional[str] = None
    
class PlannerProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    step_id: str
    is_checked: bool = Field(default=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Laboratory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str          # e.g. "Electronics", "Textiles", "Food & Beverage"
    location: str           # e.g. city name, matched against user input
    capability: str         # short description of what they test
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class UserProduct(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    product_name: str
    category: str
    standard_code: str = Field(index=True)   # e.g. "IS 302", "IS 16046"


class StandardChangeEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    standard_code: str = Field(index=True)
    change_type: str          # "amended" | "replaced" | "updated" | "withdrawn"
    description: str
    recommended_action: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NewsletterPost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    category: str
    summary: str
    published_at: datetime = Field(default_factory=datetime.utcnow)


class UserSubscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    category: str = Field(index=True)

class DocumentAuditResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    filename: str
    readiness_score: int
    findings_json: str   # stored as JSON string: list of {status, message}
    created_at: datetime = Field(default_factory=datetime.utcnow)