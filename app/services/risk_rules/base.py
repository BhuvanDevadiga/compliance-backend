from dataclasses import dataclass
from typing import List

class RiskRuleset:
    version: str = "unknown"
    status: str = "active"
    introduced_on: str = "unknown"
    description: str = ""

    @classmethod
    def metadata(cls):
        return {
            "version": cls.version,
            "status": cls.status,
            "introduced_on": cls.introduced_on,
            "description": cls.description,
        }


@dataclass
class RuleHit:
    rule: str
    points: int


@dataclass
class RiskDecision:
    score: int
    level: str
    reasons: List[str]
    rules_fired: List[RuleHit]
