def test_triage_contract(client):
    payload = {"message": "What is your return policy?"}
    r = client.post("/triage", json=payload)
    assert r.status_code == 200
    data = r.json()

    for k in ["category", "priority", "risk_score", "rationale", "next_action", "suggested_reply"]:
        assert k in data

    assert 0.0 <= float(data["risk_score"]) <= 1.0
    assert isinstance(data["rationale"], list)


def test_triage_risk_sanity(client):
    high_risk = {"message": "My account was hacked and I did not authorize this charge. I want to reset my password."}
    low_risk = {"message": "What are your support hours?"}

    r1 = client.post("/triage", json=high_risk).json()
    r2 = client.post("/triage", json=low_risk).json()

    assert r1["risk_score"] > r2["risk_score"]
    assert r1["priority"] in ["P0", "P1"]