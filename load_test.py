from locust import HttpUser, task, between
import random
import os

TENANT_ID = os.getenv("TENANT_ID", "demo")
API_KEY = os.getenv("API_KEY", "sk_demo_123")

INDUSTRIES = [
    "fintech",
    "healthcare",
    "ecommerce",
    "manufacturing",
    "logistics",
    "education",
]

COMPANY_SIZES = ["micro", "small", "medium", "large"]


class RiskUser(HttpUser):
    wait_time = between(0.5, 1.5)

    headers = {
        "X-Tenant-Id": TENANT_ID,
        "X-API-Key": API_KEY,
    }

    def _base_payload(self) -> dict:
        return {
            "company_size": random.choice(COMPANY_SIZES),
            "industry": random.choice(INDUSTRIES),
            "has_gst": random.choice([True, False]),
            "has_pan": random.choice([True, False]),
        }

    @task(3)
    def normal_risk(self):
        payload = self._base_payload()
        self.client.post(
            "/api/public/risk/score",
            json=payload,
            headers=self.headers
        )

    @task(1)
    def escalation_risk(self):
        payload = self._base_payload()
        self.client.post(
            "/api/public/risk/score",
            json=payload,
            headers=self.headers
        )
