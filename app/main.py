from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine
from datetime import datetime
import ulid
from pydantic import BaseModel
from app import settings

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)
engine = create_engine(connection_string)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    """
    Handles IntegrityError exceptions, which are raised when a database constraint is violated.
    """
    return HTTPException(
        status_code=400,
        detail="A record with the same unique constraint already exists.",
    )


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
    created_at: datetime
    confidence: float
    entity: str
    query_id: str = Field(foreign_key="query.id")  # Add this line
    query: "Query" = Relationship(back_populates="insights")  # Add this line


class InsightCreate(BaseModel):
    title: str
    category: str
    content: str
    source: str
    impact: str
    created_at: datetime
    confidence: float
    entity: str


# Dummy data
dummy_insights = [
    Insight(
        title="Amazon is a leading provider of e-commerce solutions",
        category="Company Overview",
        content="Amazon, founded by Jeff Bezos, has revolutionized the e-commerce industry. With its vast network and advanced logistics systems, it provides a wide range of products and services to customers around the globe.",
        source="https://www.amazon.com/",
        impact="High",
        created_at=datetime.now(),
        confidence=0.95,
        entity="Amazon",
    ),
    Insight(
        title="Amazon has a competitive edge due to its advanced logistics systems",
        category="Competitive Position",
        content="Amazon's advanced logistics systems, including its use of robotics and AI, give it a competitive edge in the e-commerce industry. This allows Amazon to deliver products faster and more efficiently than its competitors.",
        source="https://www.amazon.com/",
        impact="Medium",
        created_at=datetime.now(),
        confidence=0.85,
        entity="Amazon",
    ),
]


# 0. MVP
@app.post("/query/send", response_model=str)
async def handle_query(query: str, session: Session = Depends(get_session)):
    query_id = str(
        ulid.from_timestamp(datetime.now())
    )  # Generate a new unique ID for the query

    # Save the query and its dummy insights to the database
    db_query = Query(
        id=query_id,
        content=query,
        insights=[
            Insight(**insight.dict(), query_id=query_id) for insight in dummy_insights
        ],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    session.add(db_query)
    session.commit()

    # Return the query ID
    return query_id


@app.get("/query/fetch/{query_id}", response_model=List[Insight])
async def fetch_query(query_id: str, session: Session = Depends(get_session)):
    insights = session.query(Insight).filter(Insight.query_id == query_id).all()
    return insights


@app.post("/query/{query_id}/insight", response_model=Insight)
async def append_insight(
    query_id: str, insight: InsightCreate, session: Session = Depends(get_session)
):
    try:
        # Fetch the query
        query = session.query(Query).filter(Query.id == query_id).first()

        if query:
            # Create a new insight and associate it with the query
            db_insight = Insight(**insight.dict(), query_id=query_id)
            session.add(db_insight)

            # Update the query's updated_at field
            query.updated_at = datetime.now()

            session.commit()
            session.refresh(db_insight)
            return db_insight
        else:
            raise HTTPException(
                status_code=404, detail=f"Query with ID {query_id} not found."
            )
    except IntegrityError:
        # Handle the exception by raising a custom HTTPException
        raise HTTPException(
            status_code=400,
            detail="A record with the same unique constraint already exists.",
        )


@app.put("/query/update/{query_id}", response_model=List[Insight])
async def update_query(
    query_id: str, new_query: str, session: Session = Depends(get_session)
):
    # Update the query content
    query = session.query(Query).filter(Query.id == query_id).first()
    if query:
        query.content = new_query
        session.commit()

        # Update the insights with dummy insights
        query.insights = [
            Insight(**insight, query_id=query_id) for insight in dummy_insights
        ]
        session.commit()

        # Return the updated insights
        updated_insights = (
            session.query(Insight).filter(Insight.query_id == query_id).all()
        )
        return updated_insights
    else:
        raise HTTPException(
            status_code=404, detail=f"Query with ID {query_id} not found."
        )


@app.delete("/query/delete/{query_id}", response_model=str)
async def delete_query(query_id: str, session: Session = Depends(get_session)):
    # Delete the query and its associated insights
    query = session.query(Query).filter(Query.id == query_id).first()
    if query:
        session.delete(query)
        session.commit()
        return f"Query with ID {query_id} has been deleted."
    else:
        raise HTTPException(
            status_code=404, detail=f"Query with ID {query_id} not found."
        )
