from pydantic import BaseModel, HttpUrl
from typing import List
from datetime import date
from enum import Enum


class InsightType(str, Enum):
    COMPANY_OVERVIEW = "COMPANY_OVERVIEW"
    PRODUCTS_SERVICES = "PRODUCTS_SERVICES"
    COMPETITIVE_POSITION = "COMPETITIVE_POSITION"
    MARKET_ANALYSIS = "MARKET_ANALYSIS"
    FINANCIAL_PERFORMANCE = "FINANCIAL_PERFORMANCE"
    MANAGEMENT_LEADERSHIP = "MANAGEMENT_LEADERSHIP"
    STRATEGY_DIRECTION = "STRATEGY_DIRECTION"
    BUSINESS_MODEL = "BUSINESS_MODEL"
    INDUSTRY_INSIGHTS = "INDUSTRY_INSIGHTS"


class InsightPoint(BaseModel):
    title: str
    category: str
    content: str
    sources: str
    impact: str
    date: date
    confidence: float


class CompanyInfo(BaseModel):
    url: HttpUrl
    summary: str
    key_points: List[str]


class UrlRelevance(BaseModel):
    url: str
    is_relevant: bool
    relevance_score: float
    insights: List[InsightType]
    description: str
