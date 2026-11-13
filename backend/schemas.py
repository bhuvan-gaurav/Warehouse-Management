from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# Role & Auth Schemas (RBAC)
# ==========================================

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="bhuvan", description="Unique username")
    password: str = Field(..., min_length=6, example="secret123", description="Password (at least 6 characters)")
    role: Optional[UserRole] = Field(default=UserRole.STAFF, example=UserRole.STAFF, description="Role: admin, manager, or staff")


class UserLogin(BaseModel):
    username: str = Field(..., example="bhuvan")
    password: str = Field(..., example="secret123")


class UserResponse(BaseModel):
    user_id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    role: Optional[str] = None
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = Field(default=None, example="eyJhbGciOiJIUzI1NiIsIn...")
    token: Optional[str] = Field(default=None, description="Alternative field for refresh token")

    def get_token(self) -> str:
        return self.refresh_token or self.token or ""


class MessageResponse(BaseModel):
    message: str


# ==========================================
# Package Schemas (Pydantic Validation)
# ==========================================

class PackageBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Electronics Box", description="Name/description of package")
    destination: str = Field(..., min_length=1, max_length=100, example="New York", description="Delivery destination")
    weight: float = Field(..., gt=0, example=5.5, description="Package weight in kg (must be greater than 0)")
    arrival_date: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Package arrival timestamp")
    status: Optional[str] = Field(default="pending", example="pending", description="Status: pending, dispatched, delivered")


class PackageCreate(PackageBase):
    pass


class PackageUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, example="Updated Package Name")
    destination: Optional[str] = Field(default=None, min_length=1, max_length=100, example="Chicago")
    weight: Optional[float] = Field(default=None, gt=0, example=6.0)
    arrival_date: Optional[datetime] = None
    status: Optional[str] = Field(default=None, example="dispatched")


class PackageResponse(BaseModel):
    id: int
    name: str
    destination: str
    weight: float
    arrival_date: Optional[datetime] = None
    status: str
    batch_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Dispatch Batch Schemas
# ==========================================

class DispatchBatchBase(BaseModel):
    destination: str = Field(..., min_length=1, example="New York", description="Destination for the batch")
    vehicle_number: str = Field(..., min_length=1, example="TRUCK-101", description="Vehicle assigned to the batch")
    dispatch_date: Optional[datetime] = Field(default=None, description="Date of dispatch")
    status: Optional[str] = Field(default="scheduled", example="scheduled", description="Batch status")


class DispatchBatchCreate(DispatchBatchBase):
    package_ids: Optional[List[int]] = Field(default=None, description="Optional list of specific package IDs to assign")


class DispatchBatchResponse(BaseModel):
    id: int
    destination: str
    vehicle_number: str
    dispatch_date: Optional[datetime] = None
    status: str
    packages_dispatched: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Warehouse Analytics / Statistics Schemas
# ==========================================

class DestinationCount(BaseModel):
    destination: str
    count: int


class WarehouseSummaryResponse(BaseModel):
    total_received: int
    total_pending: int
    total_dispatched: int
    destination_wise_count: List[DestinationCount]
