

from typing import Tuple, List
from app.schemas.risk import RiskScoreRequest

class RiskRuleset:
    version: str

    def calculate(self, payload: RiskScoreRequest) -> Tuple[int, str, List[str]]:
        raise NotImplementedError
