import scipy.stats as stats
from scipy.stats import beta
from sqlalchemy import Float

def beta_lower_bound(success, failure, confidence=0.95):
    alpha = success + 1
    beta = failure + 1
    return stats.beta.ppf(1 - confidence, alpha, beta)

def beta_bounds(alpha: Float, beta_param: Float, confidence: Float = 0.95):
    lower = beta.ppf((1-confidence)/2, alpha, beta_param)
    upper = beta.ppf(1-(1-confidence)/2, alpha, beta_param)

    return lower, upper