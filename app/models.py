from sqlmodel import Field, Relationship, Session, SQLModel, create_engine
from pydantic import BaseModel
from typing import List
from datetime import datetime
import ulid


class Query(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(ulid.from_timestamp(datetime.now())),
        primary_key=True,
    )
    content: str
    insights: List["Insight"] = Relationship(back_populates="query")
    created_at: datetime
    updated_at: datetime


class Insight(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(ulid.new()),
        primary_key=True,
    )
    title: str
    category: str
    content: str
    source: str
    impact: str
    confidence: float
    entity: str
    created_at: datetime
    query_id: str = Field(foreign_key="query.id")  # Add this line
    query: "Query" = Relationship(back_populates="insights")  # Add this line


class QueryFetch(BaseModel):
    query: str
    insights: List[Insight]


class QueryFetchAnswer(BaseModel):
    query: str
    insights: List[Insight]
    answer: str
    follow_up_questions: List[str]


class InsightCreate(BaseModel):
    title: str
    category: str
    content: str
    source: str
    impact: str
    confidence: float
    entity: str
    created_at: datetime
