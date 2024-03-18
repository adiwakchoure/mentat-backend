from typing import List, Dict, Any
from pydantic import BaseModel, HttpUrl, validator
from datetime import date


class InsightPoint(BaseModel):
    title: str
    category: str
    content: str
    sources: List[HttpUrl]
    impact: str
    date: date
    confidence: float


mockData = [
    InsightPoint(
        title="Amazon is a leading provider of e-commerce solutions",
        category="Company Overview",
        content="Amazon, founded by Jeff Bezos, has revolutionized the e-commerce industry. With its vast network and advanced logistics systems, it provides a wide range of products and services to customers around the globe.",
        sources=["https://www.amazon.com/"],
        impact="High",
        date=date.today(),
        confidence=0.95,
    ),
    InsightPoint(
        title="Amazon has a competitive edge due to its advanced logistics systems",
        category="Competitive Position",
        content="Amazon's advanced logistics systems, including its use of robotics and AI, give it a competitive edge in the e-commerce industry. This allows Amazon to deliver products faster and more efficiently than its competitors.",
        sources=["https://www.amazon.com/"],
        impact="Medium",
        date=date.today(),
        confidence=0.85,
    ),
    InsightPoint(
        title="Amazon is well-positioned to capitalize on the growing demand for cloud computing",
        category="Market Analysis",
        content="With its AWS (Amazon Web Services) division, Amazon is well-positioned to capitalize on the growing demand for cloud computing services. AWS provides a wide range of services, including computing power, storage, and databases, to businesses of all sizes.",
        sources=["https://www.amazon.com/"],
        impact="High",
        date=date.today(),
        confidence=0.90,
    ),
]


def query_handler(query: str) -> str:
    # Simulate the process of performing market research based on the query and return a bunch of InsightPoints
    ## Mock fake data of 3 InsightPoints about Amazon
    InsightPoints = []
    return mockData
