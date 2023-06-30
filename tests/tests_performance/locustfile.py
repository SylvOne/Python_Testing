from locust import HttpUser, task, between


class ProjectPerfTest(HttpUser):
    wait_time = between(1, 2)  # Temps d'attente entre les taches/utilisateurs

    @task
    def club_table(self):
        self.client.get("/points", name="Load club points")

    @task
    def on_start(self):
        self.client.post("/showSummary", {"email": "john@simplylift.co"}, name="Show summary")

    @task
    def perf_index(self):
        self.client.get("/", name="Load index")

    @task
    def booking(self):
        self.client.get("/book/Fall Classic/She Lifts", name="Book Fall Classic She Lifts")
        self.client.get("/book/Spring Festival/Iron Temple", name="Book Spring Festival Iron Temple")

    @task
    def purchase_places(self):
        self.client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Iron Temple",
                "places": 4,
            },
            name="Buy and update points"
        )

    @task
    def on_stop(self):
        self.client.get("/logout", name="Logout")
