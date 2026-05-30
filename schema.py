from pydantic import BaseModel, Field
from datetime import datetime

from pydantic import BaseModel, Field
from datetime import datetime


class ReviewResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    missing_skills: list[str]
    recommendations: list[str]
    matched_skills: list[str]
    experience_analysis: str
    education_analysis: str
    projects_analysis: str

class ATSResponse(BaseModel):
    ats_score:int=Field(
        ...,
        ge=0,
        le=100
    )
    keyword_match:int=Field(
        ...,
        ge=0,
        le=1000
    )
    missing_keywords:list[str]
    suggestions:list[str]

class CoverLetterResponse(BaseModel):
    cover_letter:str

class InterviewQuestionsResponse(BaseModel):
    questions:list[str]

class HealthResponse(BaseModel):
    status:str
    service:str
    timestamp:str