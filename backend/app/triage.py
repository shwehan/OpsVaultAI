from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TriageDecision:
    category: str
    priority: str
    risk_score: float
    rationale: List[str]
    next_action: str
    suggested_reply: str


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)


def triage_message(message: str) -> TriageDecision:
    """
    Deterministic rules-first triage:
    - explainable (great for interviews)
    - testable
    - later you can add an LLM structured-output mode behind a flag
    """
    msg = (message or "").strip().lower()
    rationale: List[str] = []

    # Keyword groups (small starter set)
    ato = ["hacked", "unauthorized", "account takeover", "stolen", "compromised", "phishing", "otp", "2fa", "reset password"]
    dispute = ["chargeback", "dispute", "fraud charge", "didn't authorize", "did not authorize"]
    refund = ["refund", "return", "charged twice", "cancel", "money back"]
    policy = ["policy", "pricing", "sla", "support hours", "terms", "return policy"]
    bug = ["bug", "error", "broken", "not working", "crash", "issue"]

    # Risk scoring (simple, cost-sensitive intuition)
    risk = 0.05

    if _contains_any(msg, ["chargeback", "unauthorized", "hacked", "stolen", "compromised", "phishing"]):
        risk += 0.45
        rationale.append("high-risk: account/security or payment dispute keywords")

    if _contains_any(msg, ["otp", "2fa", "reset password", "password reset"]):
        risk += 0.20
        rationale.append("risk: authentication/reset signal")

    if _contains_any(msg, ["wire", "bank transfer", "gift card", "crypto"]):
        risk += 0.15
        rationale.append("risk: high-risk payment method mention")

    if _contains_any(msg, ["refund", "return", "charged twice", "money back"]):
        risk += 0.10
        rationale.append("signal: refund/return language")

    # Category (risk-sensitive ordering)
    if _contains_any(msg, ato):
        category = "account_takeover"
    elif _contains_any(msg, dispute):
        category = "payment_dispute"
    elif _contains_any(msg, refund):
        category = "refund_request"
    elif _contains_any(msg, bug):
        category = "bug_report"
    elif _contains_any(msg, policy):
        category = "policy_question"
    else:
        category = "general"

    # Priority mapping
    if risk >= 0.75:
        priority = "P0"
        next_action = "Escalate to Risk/Security queue; require identity verification before account changes."
    elif risk >= 0.45:
        priority = "P1"
        next_action = "Route to senior support/risk review; request additional verification details."
    elif category in {"refund_request", "bug_report"}:
        priority = "P2"
        next_action = "Route to support; follow standard playbook and gather required details."
    else:
        priority = "P3"
        next_action = "Respond with relevant policy/KB info; close if resolved."

    # Reply templates
    if category == "account_takeover":
        suggested_reply = (
            "Thanks for flagging this. For your security, please confirm recent login activity and complete verification. "
            "We’ve escalated this and will help secure your account."
        )
    elif category == "payment_dispute":
        suggested_reply = (
            "Sorry about the charge issue. Please share the transaction details (date, amount, last 4 digits) and any order IDs. "
            "We’ll investigate and advise on next steps."
        )
    elif category == "refund_request":
        suggested_reply = (
            "Happy to help with a refund/return. Please share the order ID and the reason for the request. "
            "I’ll confirm eligibility based on the return/refund policy."
        )
    elif category == "bug_report":
        suggested_reply = (
            "Thanks—can you share steps to reproduce, screenshots, and your environment (device/app version)? "
            "We’ll investigate and follow up."
        )
    elif category == "policy_question":
        suggested_reply = "I can help with that—I'll pull the relevant policy/KB excerpt and confirm the details with citations."
    else:
        suggested_reply = "Thanks for reaching out—can you share a bit more detail so I can route this correctly?"

    # Clamp and defaults
    risk = max(0.0, min(1.0, float(risk)))
    if not rationale:
        rationale.append("no strong risk signals detected (baseline routing)")

    return TriageDecision(
        category=category,
        priority=priority,
        risk_score=risk,
        rationale=rationale,
        next_action=next_action,
        suggested_reply=suggested_reply,
    )
