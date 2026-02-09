def test_ask_returns_contact(client):
    payload = {"question": "What is the return policy?", "k": 3}
    r = client.post("/ask", json = payload)
    assert r.status_code == 200

    data = r.json()
    assert "answer" in data
    assert "citations" in data
    assert "latency_ms" in data

    assert isinstance(data["citations"], list)
    assert isinstance(data["latency_ms"], (int, float))

    # citations should have the fields we care about
    if data["citations"]:
        c0 = data["citations"][0]
        assert "source_id" in c0
        assert "snippet" in c0
        assert "score" in c0
        assert isinstance(c0["score"], (int, float))