def test_ai_chat_returns_demo_response(client, auth_headers):
    response = client.post(
        "/api/v1/ai-mentor/chat",
        headers=auth_headers,
        json={"query": "Explain Indian federalism.", "mode": "mains"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "AI Mentor (Demo Mode)" in data["response"]


def test_ai_chat_stream_accepts_token_query(client, auth_headers):
    token = auth_headers["Authorization"].split(" ", 1)[1]
    response = client.post(
        f"/api/v1/ai-mentor/chat/stream?token={token}",
        json={"query": "Explain Indian federalism.", "mode": "mains"},
    )

    assert response.status_code == 200
    body = response.text
    assert body.startswith("data: ")
    assert "**AI " in body or "Mentor " in body
