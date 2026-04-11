import os
from dotenv import load_dotenv

load_dotenv()

ENGINE_VERSION = "2.1.0"
MAX_ALLOWED_REGRET = 0.15
AUTO_FREEZE_ON_REGRET = True
BASELINE_STRATEGY = "monitor"

ENGINE_METADATA = {
    "bandit" : "Contextual Thompson Sampling",
    "retirement_logic" : "Bayesian Dominance",
    "decay_strategy" : "Volatility Adaptive",
    "priors" : "Strategy Weighted Priors v1",
    "risk_thresholding" : "Hybrid Score v2",
}

GOVERNANCE_SIGNING_SECRET = os.getenv(
    "GOVERNANCE_SIGNING_SECRET",
    "super_secret_key_change_in_prod"
)
GOVERNANCE_KEY_ID = "platform-key-v1"
