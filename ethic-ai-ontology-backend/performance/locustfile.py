from locust import HttpUser, task, between

class EthicAIAssessmentUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def assess_endpoint(self):
        payload = {
            "system_name": "PerfTestSystem",
            "ethical_score": 50,
            "legal_score": 50,
            "data_score": 50,
            "technical_score": 50,
            "oversight_score": 50
        }
        with self.client.post("/assess", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"/assess failed: {response.status_code} {response.text}")
            else:
                response.success()
        
    @task(3)
    def violations_endpoint(self):
        with self.client.get("/violations/PerfTestSystem", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"/violations failed: {response.status_code} {response.text}")
            else:
                response.success()

    @task(3)
    def tensions_endpoint(self):
        with self.client.get("/tensions/PerfTestSystem", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"/tensions failed: {response.status_code} {response.text}")
            else:
                response.success()

    @task(1)
    def report_endpoint(self):
        # Report is heavier since it uses LLM or Fallback. 
        # Using a lower weight (1) for this endpoint.
        payload = {
            "system_name": "PerfTestSystem",
            "text": "An AI system that processes biometric data for access control. The system includes explicit consent, human oversight, data minimization, encryption, and purpose limitation."
        }
        # Add timeout to prevent hanging if LLM/GraphRAG gets stuck
        with self.client.post("/report", json=payload, timeout=30, catch_response=True) as response:
            if response.status_code not in [200, 206]:
                response.failure(f"/report failed: {response.status_code} {response.text}")
            else:
                response.success()
