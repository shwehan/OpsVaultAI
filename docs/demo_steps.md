# Demo Steps (Day 1)

- [ ] docker run ...
- [ ] curl /health
- [ ] curl /ask
- [ ] run eval

## Triage
```bash
curl -X POST "http://localhost:8000/triage" -H "Content-Type: application/json" -d "{\"message\":\"I did not authorize this charge. My account was hacked and I need a refund.\"}"
