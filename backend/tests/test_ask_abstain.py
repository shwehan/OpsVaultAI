def test_ask_can_abstain_when_threshold_high(client):
    payload = {"question": "What is the return policy?", "k": 3, "min_score": 0.99}
    r = client.post("/ask", json=payload)
    assert r.status_code == 200

    data = r.json()
    assert data["abstained"] is True
    assert data["abstain_reason"]
