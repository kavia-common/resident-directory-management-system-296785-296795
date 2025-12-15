from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr


class Pagination(BaseModel):
    page: int = Field(1, description="Current page number (1-based).")
    page_size: int = Field(10, description="Number of items per page.")
    total: int = Field(..., description="Total number of items.")
    items: int = Field(..., description="Number of items returned in this page.")


class ResidentBase(BaseModel):
    first_name: str = Field(..., description="Resident first name", min_length=1, max_length=100)
    last_name: str = Field(..., description="Resident last name", min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Mailing address")
    photo_url: Optional[str] = Field(None, description="Publicly accessible photo URL")


class ResidentCreate(ResidentBase):
    """Payload to create a new resident."""
    pass


class ResidentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, description="Resident first name", min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, description="Resident last name", min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Mailing address")
    photo_url: Optional[str] = Field(None, description="Publicly accessible photo URL")


class ResidentOut(ResidentBase):
    id: int = Field(..., description="Resident unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")

    class Config:
        from_attributes = True


class ResidentListResponse(BaseModel):
    data: List[ResidentOut]
    pagination: Pagination


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


class LoginRequest(BaseModel):
    username: str = Field(..., description="Admin username")
    password: str = Field(..., description="Admin password")
