"""Compatibility shim for behavior escalation service.

Keeps older import path stable:
from app.services.behavior_escalation import evaluate_behavior_escalation
"""

from app.services.behavior_escalation_engine import evaluate_behavior_escalation
from app.models.escalation_feedback import EscalationFeedback


__all__ = ["evaluate_behavior_escalation", "EscalationFeedback"]
