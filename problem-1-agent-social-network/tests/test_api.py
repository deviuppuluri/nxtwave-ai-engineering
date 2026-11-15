import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def register_test_agent():
    unique = uuid.uuid4().hex[:8]
    response = client.post(
        "/agents",
        json={
            "company_name": f"Test Company {unique}",
            "industry": "Technology",
            "interest_description": (
                "Interested in software technology, "
                "business automation and logistics."
            ),
            "webhook_url": None,
        },
    )
    assert response.status_code in (200, 201), response.text
    data = response.json()
    assert "api_key" in data, data
    return data


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200


def test_agent_registration():
    data = register_test_agent()
    assert data["api_key"]


def test_post_requires_authentication():
    response = client.post(
        "/posts",
        json={
            "title": "Test business update",
            "content": "This is a test business update.",
        },
    )
    assert response.status_code in (401, 403)


def test_authenticated_agent_can_publish_post():
    agent = register_test_agent()
    response = client.post(
        "/posts",
        headers={"X-Agent-Api-Key": agent["api_key"]},
        json={
            "title": "Technology business update",
            "content": (
                "We are improving logistics, automation "
                "and customer delivery technology."
            ),
        },
    )
    assert response.status_code in (200, 201), response.text
    result = response.json()
    assert "threshold" in result
    assert "notified_agents" in result
    assert "candidate_scores" in result


def test_agents_endpoint():
    response = client.get("/agents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
