import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PredictionRequest(BaseModel):
    age: int = Field(ge=20, le=100)
    sex: int = Field(ge=0, le=1)
    cp: int = Field(ge=0, le=3)
    trestbps: int = Field(ge=80, le=200)
    chol: int = Field(ge=100, le=600)
    fbs: int = Field(ge=0, le=1)
    restecg: int = Field(ge=0, le=2)
    thalach: int = Field(ge=60, le=220)
    exang: int = Field(ge=0, le=1)
    oldpeak: float = Field(ge=0.0, le=10.0)
    slope: int = Field(ge=0, le=2)
    ca: int = Field(ge=0, le=3)
    thal: int = Field(ge=1, le=3)


class RecommendationItem(BaseModel):
    category: str
    advice: str
    steps: list[str]


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    risk_score: float
    risk_level: str
    recommendations: list[RecommendationItem]
    created_at: datetime


class AssessmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    risk_score: float
    risk_level: str
    created_at: datetime


class AssessmentDetail(AssessmentSummary):
    input_data: dict
    recommendations: list[RecommendationItem]


class MessageResponse(BaseModel):
    message: str
