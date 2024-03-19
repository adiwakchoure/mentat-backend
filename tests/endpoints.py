import pytest
from fastapi.testclient import TestClient
from datetime import date

from app.main import app  # Import your FastAPI app instance

base_url = "http://localhost:8000"

client = TestClient(app)  # Create a TestClient instance


@pytest.fixture
def dummy_insight():
    return {
        "title": "Amazon is a leading provider of e-commerce solutions",
        "category": "Company Overview",
        "content": "Amazon, founded by Jeff Bezos, has revolutionized the e-commerce industry. With its vast network and advanced logistics systems, it provides a wide range of products and services to customers around the globe.",
        "source": "https://www.amazon.com/",
        "impact": "High",
        "date": date.today().isoformat(),
        "confidence": 0.95,
        "entity": "Amazon",
    }


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API!"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_send_query(dummy_insight):
    query = "Who is Bezos"
    response = client.post("/query/send", json={"query": query})
    assert response.status_code == 200
    query_id = response.text

    insights_response = client.get(f"/query/fetch/{query_id}")
    assert insights_response.status_code == 200
    insights = insights_response.json()
    assert len(insights) == 2
    assert insights[0]["title"] == dummy_insight["title"]


def test_append_insight(dummy_insight):
    query = "Who is Bezos"
    response = client.post("/query/send", json={"query": query})
    assert response.status_code == 200
    query_id = response.text

    new_insight = dummy_insight.copy()
    new_insight["title"] = "Amazon is a leading provider of cloud services"
    response = client.post(f"/query/{query_id}/insight", json=new_insight)
    assert response.status_code == 200
    insight = response.json()
    assert insight["title"] == new_insight["title"]


def test_update_query(dummy_insight):
    query = "Who is Bezos"
    response = client.post("/query/send", json={"query": query})
    assert response.status_code == 200
    query_id = response.text

    new_query = "What is Amazon's business model?"
    response = client.put(f"/query/update/{query_id}", json={"new_query": new_query})
    assert response.status_code == 200
    insights = response.json()
    assert len(insights) == 2
    assert insights[0]["title"] == dummy_insight["title"]


def test_delete_query():
    query = "Who is Bezos"
    response = client.post("/query/send", json={"query": query})
    assert response.status_code == 200
    query_id = response.text

    response = client.delete(f"/query/delete/{query_id}")
    assert response.status_code == 200
    assert response.text == f"Query with ID {query_id} has been deleted."
