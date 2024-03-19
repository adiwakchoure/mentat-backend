import ulid
import marvin
from typing import List, Dict
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, create_engine
from datetime import datetime
from app import settings
from app.models import Insight, InsightCreate, Query, QueryFetch, QueryFetchAnswer

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(connection_string, pool_pre_ping=True)


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


@marvin.fn
def follow_up_questions(query: str, insights: List[Dict]) -> List[str]:
    """
    Generate 2 worthwhile follow up questions, to aid market research or oppositional research in the context of the given query and insights.
    The questions must be under 15 words each
    """
    pass


@marvin.fn
def answer_with_insights(question: str, insights: List[Dict]) -> str:
    """
    This function takes a question and a list of insights as input and returns a concise and informative answer as output. Just start answering the question, no need to repeat the question.
    The answer is generated for the purpose of market research or oppositional research based on the given question and insights. It is a markdown formatted summary of no more than 200 words.
    Do not just repeat the details from the insights, synthesize it into an informative and concise answer.

    str: A markdown formatted string, containing an informative and concise answer generated based on the question and insights. It must be no more than 200 words.
    """
    pass


@app.get("/query/fetch/{query_id}", response_model=QueryFetch)
async def fetch_query(query_id: str, session: Session = Depends(get_session)):
    query = session.query(Query).filter(Query.id == query_id).first()
    if query is None:
        raise HTTPException(status_code=404, detail="Query not found")
    insights = session.query(Insight).filter(Insight.query_id == query_id).all()
    return {"query": query.content, "insights": insights}


@app.get("/query/fetch-answer/{query_id}", response_model=QueryFetchAnswer)
async def fetch_query(query_id: str, session: Session = Depends(get_session)):
    query = session.query(Query).filter(Query.id == query_id).first()
    if query is None:
        raise HTTPException(status_code=404, detail="Query not found")
    question = query.content
    insights = session.query(Insight).filter(Insight.query_id == query_id).all()
    return {
        "query": question,
        "insights": insights,
        "answer": answer_with_insights(question, insights),
        "follow_up_questions": follow_up_questions(question, insights),
    }


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
