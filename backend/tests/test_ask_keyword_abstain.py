def test_ask_abstains_when_keywords_missing(client):
    payload = {"question": "What is your shipping policy?", "k": 3, "min_score": 0.0}
    r = client.post("/ask", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["abstained"] is True
    assert data["abstain_reason"]
