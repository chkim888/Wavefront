from locust import HttpUser, task, between
import uuid
import random

# Constants
PROJECT_ID = "f2686214-7431-4ce1-8fe0-aed2a6b8c658"
EXPERIMENT_ID = "cc799ad3-6779-457d-b342-ab27b5d8c65e"
TOPIC_ID = "d66bf159-f3ce-450c-b4d5-3bcc26c51cb3"

'''
For simulating Wavefront user (analyst/project manager/etc.)
'''
class AnalystUser(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 3)
    weight = 1

    # Login & save returned JWT token
    def on_start(self):
        response = self.client.post("/auth/login", json={
            "username": "locust_test",
            "password": "locust_test"
        })
        # Get JWT token from the response & attach to headers
        token = response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(5)
    def get_all_projects(self):
        with self.client.get("/projects/all-projects", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Got status code {response.status_code}")

    @task(5)
    def get_posts_for_topic(self):
        with self.client.get(f"/topics/posts/{TOPIC_ID}", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"got status code {response.status_code}")

    @task(5)
    def get_all_experiments(self):
        with self.client.get(f"/experiments/project/{PROJECT_ID}", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"got status code {response.status_code}")
    
    @task(5)
    def get_alerts_by_project(self):
        with self.client.get(f"/alerts/{PROJECT_ID}", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"got status code {response.status_code}")

    @task(1)
    def create_experiment(self):
        with self.client.post("/experiments", catch_response=True, json={
            "project_id": PROJECT_ID,
            "title": f"locust_{random.randint(0, 10000)}",
            "description": "locust testing",
            "traffic_split": random.randint(20, 80),
            "success_metric": "button_click"
        }) as response:
            if response.status_code == 409:
                response.success() # count as success if naming conflict rises
            elif response.status_code != 200:
                response.failure(f"got status code {response.status_code}")

    @task(1)
    def start_experiment(self):
        with self.client.post(f"/experiments/{EXPERIMENT_ID}/start", catch_response=True) as response:
            if response.status_code == 409:
                response.success() # count as success if experiment is not eligible for starting
            elif response.status_code != 200:
                response.failure(f"got status code {response.status_code}")

    @task(1)
    def stop_experiment(self):
        with self.client.post(f"/experiments/{EXPERIMENT_ID}/stop", catch_response=True) as response:
            if response.status_code == 409:
                response.success() # if the experiment is not running, count as success
            elif response.status_code != 200:
                response.failure(f"got status code {response.status_code}")

'''
For simulating end user (streaming service)
'''
class EndTrafficUser(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(0.5, 1)
    weight = 20

    def on_start(self):
        self.session_id = str(uuid.uuid4())

    @task
    def assign_variant(self):
        with self.client.post(f"/assignments/{EXPERIMENT_ID}/{self.session_id}", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"got status code {response.status_code}")
