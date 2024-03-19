from typing import List, Dict, Any, Optional
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select, JSON
from pydantic import BaseModel
from app import settings
import datetime, ulid

from app.utils import query_handler, Insight

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("startup")
async def startup_event():
    create_db_and_tables()


from fastapi.responses import RedirectResponse


@app.get("/")
def read_root():
    return RedirectResponse(url="/health")


@app.get("/health")
def health_check():
    return {"status": "ok"}


from pydantic import HttpUrl
from datetime import date
from sqlmodel import JSON
import json


class Insight(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    category: str
    content: str
    source: str
    impact: str
    date: date
    confidence: float
    query_id: str = Field(default=None, foreign_key="query.id")  # Add this line
    query: "Query" = Relationship(back_populates="insights")  # Add this line


class Query(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    content: str
    insights: List[Insight] = Relationship(back_populates="query")


import time

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
]


def query_handler(self, query: str, id: str) -> List[InsightPoint]:
    # Simulate the process of performing market research based on the query and return a bunch of InsightPoints
    return mockData


# 0. MVP
@app.get("/query/send")
async def handle_query(query: str, session: Session = Depends(get_session)):

    query_id = ulid.from_timestamp(time.time())
    insights = query_handler(query=query, id=query_id)

    # Save the query and its insights to the database
    db_query = Query(id=query_id, content=query, insights=insights)
    session.add(db_query)
    session.commit()

    print("Added Query!")
    session.commit()

    for insight in insights:
        insight_dict = insight.dict()  # Convert the InsightPoint object to a dictionary
        insight_dict["query_id"] = query_id  # Add the query_id field
        db_insight = Insight(**insight_dict)  # Create the Insight object
        session.add(db_insight)
    session.commit()

    # Return the UUID
    return query_id


@app.get("/query/fetch")
async def fetch_query(query_id: str, session: Session = Depends(get_session)):
    insights = session.query(Insight).filter(Insight.query_id == query_id).all()
    return [insight.to_dict() for insight in insights]
