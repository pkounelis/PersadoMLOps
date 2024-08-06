from locust import HttpUser, TaskSet, task, between


class UserBehavior(TaskSet):
    @task
    def suggest(self):
        self.client.post("/suggest", data="have a <blank> day",
                         auth=('admin', 'secret'))


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(5, 15)
