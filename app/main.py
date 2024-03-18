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


# Models
# class Company(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     domain: str
#     industry: str
#     location: str
#     size: int
#     recent_news: str
#     profiles: List["Profile"] = Relationship(back_populates="company")


# class Profile(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     company_id: Optional[int] = Field(default=None, foreign_key="company.id")
#     company: Optional[Company] = Relationship(back_populates="profiles")
#     insights: List["Insight"] = Relationship(back_populates="profile")


# class Insight(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     text: str
#     profile_id: Optional[int] = Field(default=None, foreign_key="profile.id")
#     profile: Optional[Profile] = Relationship(back_populates="insights")


# class ResearchTrace(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     data: str = Field(default=None)

#     @property
#     def data_list(self) -> List[str]:
#         return json.loads(self.data)

#     @data_list.setter
#     def data_list(self, value: List[str]):
#         self.data = json.dumps(value)


# class CompanyCreate(BaseModel):
#     name: str
#     domain: str
#     industry: str
#     location: str
#     size: int
#     recent_news: str


# class ProfileCreate(BaseModel):
#     name: str
#     company_id: int


# class InsightCreate(BaseModel):
#     text: str
#     profile_id: int


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


# # 1. User Interface
# @app.post("/chat")
# async def handle_chat(request: Request):
#     query = await request.json()
#     # Process the user's query or command from the chat interface
#     # Call other endpoints like /process-query, /validate-query, etc.
#     return {"message": "Query received from chat"}


# @app.post("/search")
# async def handle_search(request: Request):
#     search_query = await request.json()
#     # Process the user's search query for companies
#     # Call other endpoints like /process-query, /validate-query, etc.
#     return {"message": "Search query received"}


# # 2. Query Processing
# @app.post("/process-query")
# async def process_query(request: Request):
#     query = await request.json()
#     # Analyze the query and identify key areas of interest
#     return {"message": "Query processed"}


# # 3. Query Validation and Subtask Generation
# @app.post("/validate-query")
# async def validate_query(request: Request):
#     query = await request.json()
#     # Validate the user's query
#     return {"message": "Query validated"}


# @app.post("/generate-subtasks")
# async def generate_subtasks(request: Request):
#     query = await request.json()
#     # Break down the complex query into smaller subtasks
#     return {"message": "Subtasks generated"}


# # 4. Data Compilation
# @app.post("/compile-data")
# async def compile_data(query: str, session: Session = Depends(get_session)):
#     # Initiate the data compilation process for the given query
#     # Fetch relevant data from the database
#     company_data = session.exec(
#         select(Company).where(Company.name.ilike(f"%{query}%"))
#     ).all()
#     profile_data = session.exec(
#         select(Profile).join(Company).where(Company.name.ilike(f"%{query}%"))
#     ).all()
#     insight_data = session.exec(
#         select(Insight)
#         .join(Profile)
#         .join(Company)
#         .where(Company.name.ilike(f"%{query}%"))
#     ).all()

#     # Simulate data compilation progress
#     dummy_progress[query] = 0.0
#     while dummy_progress[query] < 1.0:
#         dummy_progress[query] += 0.1
#         # Perform data compilation tasks here

#     return {"message": "Data compilation completed"}


# @app.get("/data-progress/{query}")
# async def get_data_progress(query: str):
#     if query not in dummy_progress:
#         raise HTTPException(status_code=404, detail="Query not found")
#     return {"progress": dummy_progress[query]}


# # 5. Company Profile
# @app.post("/companies", response_model=Company)
# async def create_company(
#     company: CompanyCreate, session: Session = Depends(get_session)
# ):
#     db_company = Company.from_orm(company)
#     session.add(db_company)
#     session.commit()
#     session.refresh(db_company)
#     return db_company


# @app.get("/companies/{company_id}", response_model=Company)
# async def get_company(company_id: int, session: Session = Depends(get_session)):
#     company = session.get(Company, company_id)
#     if not company:
#         raise HTTPException(status_code=404, detail="Company not found")
#     return company


# @app.post("/profiles", response_model=Profile)
# async def create_profile(
#     profile: ProfileCreate, session: Session = Depends(get_session)
# ):
#     db_profile = Profile.from_orm(profile)
#     session.add(db_profile)
#     session.commit()
#     session.refresh(db_profile)
#     return db_profile


# @app.get("/profiles/{profile_id}", response_model=Profile)
# async def get_profile(profile_id: int, session: Session = Depends(get_session)):
#     profile = session.get(Profile, profile_id)
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     return profile


# @app.post("/insights", response_model=Insight)
# async def create_insight(
#     insight: InsightCreate, session: Session = Depends(get_session)
# ):
#     db_insight = Insight.from_orm(insight)
#     session.add(db_insight)
#     session.commit()
#     session.refresh(db_insight)
#     return db_insight


# @app.get("/insights/{insight_id}", response_model=Insight)
# async def get_insight(insight_id: int, session: Session = Depends(get_session)):
#     insight = session.get(Insight, insight_id)
#     if not insight:
#         raise HTTPException(status_code=404, detail="Insight not found")
#     return insight


# # 6. Deep Dive Analysis
# @app.post("/web-scraping")
# async def web_scraping(request: Request):
#     company_data = await request.json()
#     # Initiate web scraping for additional insights on the company
#     return {"message": "Web scraping initiated"}


# @app.post("/social-media-analysis")
# async def social_media_analysis(request: Request):
#     company_data = await request.json()
#     # Perform social media analysis for the company
#     return {"message": "Social media analysis initiated"}


# # 7. Trace Management
# @app.post("/create-trace", response_model=Insight)
# async def create_trace(trace: ResearchTrace, session: Session = Depends(get_session)):
#     db_trace = Insight.from_orm(trace)
#     session.add(db_trace)
#     session.commit()
#     session.refresh(db_trace)
#     return db_trace


# @app.put("/update-trace", response_model=Insight)
# async def update_trace(
#     trace_id: int, trace: ResearchTrace, session: Session = Depends(get_session)
# ):
#     db_trace = session.get(Insight, trace_id)
#     if not db_trace:
#         raise HTTPException(status_code=404, detail="Research trace not found")
#     trace_data = trace.dict(exclude_unset=True)
#     for key, value in trace_data.items():
#         setattr(db_trace, key, value)
#     session.add(db_trace)
#     session.commit()
#     session.refresh(db_trace)
#     return db_trace


# @app.get("/get-trace/{trace_id}", response_model=Insight)
# async def get_trace(trace_id: int, session: Session = Depends(get_session)):
#     trace = session.get(Insight, trace_id)
#     if not trace:
#         raise HTTPException(status_code=404, detail="Research trace not found")
#     return trace


# @app.delete("/delete-trace/{trace_id}")
# async def delete_trace(trace_id: int, session: Session = Depends(get_session)):
#     trace = session.get(Insight, trace_id)
#     if not trace:
#         raise HTTPException(status_code=404, detail="Research trace not found")
#     session.delete(trace)
#     session.commit()
#     return {"message": f"Research trace {trace_id} deleted"}


# # 8. Dashboard
# @app.get("/dashboard", response_model=List[Insight])
# async def get_dashboard(user_id: str, session: Session = Depends(get_session)):
#     insights = session.exec(select(Insight)).all()
#     return insights


# @app.post("/profile-management", response_model=Company)
# async def create_profile(
#     company: CompanyCreate, session: Session = Depends(get_session)
# ):
#     db_company = Company.from_orm(company)
#     session.add(db_company)
#     session.commit()
#     session.refresh(db_company)
#     return db_company


# @app.put("/profile-management", response_model=Company)
# async def update_profile(
#     company_id: int, company: CompanyCreate, session: Session = Depends(get_session)
# ):
#     db_company = session.get(Company, company_id)
#     if not db_company:
#         raise HTTPException(status_code=404, detail="Company not found")
#     company_data = company.dict(exclude_unset=True)
#     for key, value in company_data.items():
#         setattr(db_company, key, value)
#     session.add(db_company)
#     session.commit()
#     session.refresh(db_company)
#     return db_company


# @app.delete("/profile-management/{company_id}")
# async def delete_profile(company_id: int, session: Session = Depends(get_session)):
#     company = session.get(Company, company_id)
#     if not company:
#         raise HTTPException(status_code=404, detail="Company not found")
#     session.delete(company)
#     session.commit()
#     return {"message": f"Company {company_id} deleted"}
