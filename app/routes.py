from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/chat")
async def handle_chat(request: Request):
    query = await request.json()
    # Process the user's query or command from the chat interface
    # Call other endpoints like /process-query, /validate-query, etc.
    return {"message": "Query received from chat"}


@router.post("/search")
async def handle_search(request: Request):
    search_query = await request.json()
    # Process the user's search query for companies
    # Call other endpoints like /process-query, /validate-query, etc.
    return {"message": "Search query received"}


# 2. Query Processing
@router.post("/process-query")
async def process_query(request: Request):
    query = await request.json()
    # Analyze the query and identify key areas of interest
    return {"message": "Query processed"}


# 3. Query Validation and Subtask Generation
@router.post("/validate-query")
async def validate_query(request: Request):
    query = await request.json()
    # Validate the user's query
    return {"message": "Query validated"}


@router.post("/generate-subtasks")
async def generate_subtasks(request: Request):
    query = await request.json()
    # Break down the complex query into smaller subtasks
    return {"message": "Subtasks generated"}


# 4. Data Compilation
@router.post("/compile-data")
async def compile_data(query: str, session: Session = Depends(get_session)):
    # Initiate the data compilation process for the given query
    # Fetch relevant data from the database
    company_data = session.exec(
        select(Company).where(Company.name.ilike(f"%{query}%"))
    ).all()
    profile_data = session.exec(
        select(Profile).join(Company).where(Company.name.ilike(f"%{query}%"))
    ).all()
    insight_data = session.exec(
        select(Insight)
        .join(Profile)
        .join(Company)
        .where(Company.name.ilike(f"%{query}%"))
    ).all()

    # Simulate data compilation progress
    dummy_progress[query] = 0.0
    while dummy_progress[query] < 1.0:
        dummy_progress[query] += 0.1
        # Perform data compilation tasks here

    return {"message": "Data compilation completed"}


@router.get("/data-progress/{query}")
async def get_data_progress(query: str):
    if query not in dummy_progress:
        raise HTTPException(status_code=404, detail="Query not found")
    return {"progress": dummy_progress[query]}


# 5. Company Profile
@router.post("/companies", response_model=Company)
async def create_company(
    company: CompanyCreate, session: Session = Depends(get_session)
):
    db_company = Company.from_orm(company)
    session.add(db_company)
    session.commit()
    session.refresh(db_company)
    return db_company


@router.get("/companies/{company_id}", response_model=Company)
async def get_company(company_id: int, session: Session = Depends(get_session)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/profiles", response_model=Profile)
async def create_profile(
    profile: ProfileCreate, session: Session = Depends(get_session)
):
    db_profile = Profile.from_orm(profile)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@router.get("/profiles/{profile_id}", response_model=Profile)
async def get_profile(profile_id: int, session: Session = Depends(get_session)):
    profile = session.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/insights", response_model=Insight)
async def create_insight(
    insight: InsightCreate, session: Session = Depends(get_session)
):
    db_insight = Insight.from_orm(insight)
    session.add(db_insight)
    session.commit()
    session.refresh(db_insight)
    return db_insight


@router.get("/insights/{insight_id}", response_model=Insight)
async def get_insight(insight_id: int, session: Session = Depends(get_session)):
    insight = session.get(Insight, insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return insight


# 6. Deep Dive Analysis
@router.post("/web-scraping")
async def web_scraping(request: Request):
    company_data = await request.json()
    # Initiate web scraping for additional insights on the company
    return {"message": "Web scraping initiated"}


@router.post("/social-media-analysis")
async def social_media_analysis(request: Request):
    company_data = await request.json()
    # Perform social media analysis for the company
    return {"message": "Social media analysis initiated"}


# 7. Trace Management
@router.post("/create-trace", response_model=Insight)
async def create_trace(trace: ResearchTrace, session: Session = Depends(get_session)):
    db_trace = Insight.from_orm(trace)
    session.add(db_trace)
    session.commit()
    session.refresh(db_trace)
    return db_trace


@router.put("/update-trace", response_model=Insight)
async def update_trace(
    trace_id: int, trace: ResearchTrace, session: Session = Depends(get_session)
):
    db_trace = session.get(Insight, trace_id)
    if not db_trace:
        raise HTTPException(status_code=404, detail="Research trace not found")
    trace_data = trace.dict(exclude_unset=True)
    for key, value in trace_data.items():
        setattr(db_trace, key, value)
    session.add(db_trace)
    session.commit()
    session.refresh(db_trace)
    return db_trace


@router.get("/get-trace/{trace_id}", response_model=Insight)
async def get_trace(trace_id: int, session: Session = Depends(get_session)):
    trace = session.get(Insight, trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Research trace not found")
    return trace


@router.delete("/delete-trace/{trace_id}")
async def delete_trace(trace_id: int, session: Session = Depends(get_session)):
    trace = session.get(Insight, trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Research trace not found")
    session.delete(trace)
    session.commit()
    return {"message": f"Research trace {trace_id} deleted"}


# 8. Dashboard
@router.get("/dashboard", response_model=List[Insight])
async def get_dashboard(user_id: str, session: Session = Depends(get_session)):
    insights = session.exec(select(Insight)).all()
    return insights


@router.post("/profile-management", response_model=Company)
async def create_profile(
    company: CompanyCreate, session: Session = Depends(get_session)
):
    db_company = Company.from_orm(company)
    session.add(db_company)
    session.commit()
    session.refresh(db_company)
    return db_company


@router.put("/profile-management", response_model=Company)
async def update_profile(
    company_id: int, company: CompanyCreate, session: Session = Depends(get_session)
):
    db_company = session.get(Company, company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    company_data = company.dict(exclude_unset=True)
    for key, value in company_data.items():
        setattr(db_company, key, value)
    session.add(db_company)
    session.commit()
    session.refresh(db_company)
    return db_company


@router.delete("/profile-management/{company_id}")
async def delete_profile(company_id: int, session: Session = Depends(get_session)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    session.delete(company)
    session.commit()
    return {"message": f"Company {company_id} deleted"}
