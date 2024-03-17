from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select
from pydantic import BaseModel
from app import settings


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


# Models
class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    domain: str
    industry: str
    location: str
    size: int
    recent_news: str
    profiles: List["Profile"] = Relationship(back_populates="company")


class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    company: Optional[Company] = Relationship(back_populates="profiles")
    insights: List["Insight"] = Relationship(back_populates="profile")


class Insight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    profile_id: Optional[int] = Field(default=None, foreign_key="profile.id")
    profile: Optional[Profile] = Relationship(back_populates="insights")


class CompanyCreate(BaseModel):
    name: str
    domain: str
    industry: str
    location: str
    size: int
    recent_news: str


class ProfileCreate(BaseModel):
    name: str
    company_id: int


class InsightCreate(BaseModel):
    text: str
    profile_id: int


# Endpoints
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Company endpoints
@app.post("/companies/", response_model=Company)
def create_company(company: CompanyCreate, session: Session = Depends(get_session)):
    db_company = Company.model_validate(company)
    session.add(db_company)
    session.commit()
    session.refresh(db_company)
    return db_company


@app.get("/companies/", response_model=List[Company])
def read_companies(session: Session = Depends(get_session)):
    companies = session.exec(select(Company)).all()
    return companies


@app.get("/companies/{company_id}", response_model=Company)
def read_company(company_id: int, session: Session = Depends(get_session)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


# Profile endpoints
@app.post("/profiles/", response_model=Profile)
def create_profile(profile: ProfileCreate, session: Session = Depends(get_session)):
    db_profile = Profile.model_validate(profile)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@app.get("/profiles/", response_model=List[Profile])
def read_profiles(session: Session = Depends(get_session)):
    profiles = session.exec(select(Profile)).all()
    return profiles


@app.get("/profiles/{profile_id}", response_model=Profile)
def read_profile(profile_id: int, session: Session = Depends(get_session)):
    profile = session.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


# Insight endpoints
@app.post("/insights/", response_model=Insight)
def create_insight(insight: InsightCreate, session: Session = Depends(get_session)):
    db_insight = Insight.model_validate(insight)
    session.add(db_insight)
    session.commit()
    session.refresh(db_insight)
    return db_insight


@app.get("/insights/", response_model=List[Insight])
def read_insights(session: Session = Depends(get_session)):
    insights = session.exec(select(Insight)).all()
    return insights


@app.get("/insights/{insight_id}", response_model=Insight)
def read_insight(insight_id: int, session: Session = Depends(get_session)):
    insight = session.get(Insight, insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return insight
