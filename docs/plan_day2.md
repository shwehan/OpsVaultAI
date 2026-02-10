# Day 2 Plan — Triage MVP + Observability + Cloud Runbook

## Day 2 Repo Milestone (must ship)
**/triage returns structured decisions + contract tests + demo steps.**

### Acceptance criteria
- [ ] `POST /triage` returns:
  - `category` (e.g., account_takeover, payment_dispute, refund_request, policy_question, bug_report, general)
  - `priority` (P0–P3)
  - `risk_score` (0–1)
  - `rationale` (list of strings)
  - `next_action`
  - `suggested_reply`
- [ ] `pytest` passes (including triage tests)
- [ ] `docs/demo_steps.md` includes a triage curl example

## Stretch goals (if time)
- [ ] Add request_id + latency logging middleware
- [ ] Add minimal `/metrics` OR structured log output
- [ ] Add `docs/deploy-ecs-fargate.md` runbook (ECR→ECS)

