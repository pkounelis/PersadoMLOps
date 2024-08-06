# How to run:

### Build images

docker-compose build

### Start container

docker-compose up

### Send requests with Postman:

POST: http://localhost:8000/suggest

Authorization:

> Type: Basic Auth

> Username: admin

> Password: secret

Body:

> Select: raw Text

> Write a sentence with a <blank> placeholder

Alternatively invoke from command prompt:

> curl -X POST "http://localhost:8000/suggest" -H "Content-Type: text/plain" -d "have a <blank> day" -u admin:secret

### Access metrics:

http://localhost:8000/metrics

### Access Prometheus:

http://localhost:9090

### Access Grafana:

http://localhost:3000/

Username: admin

Password: admin

### Configure Prometheus Data Source in Grafana:

Connections -> Data sources -> Add new data source -> Prometheus

Connection:

> Prometheus server URL: http://app-prometheus-1:9090

### Access Locust:

http://localhost:8089/

Configure host: http://app-fastapi-app-1:8000

### Future work:

- Test jenkins_pipeline.groovy (integrate git with jenkins in order to checkout the repo)
- Implement better authentication (OAuth2)
- Deployment scripts and configurations that demonstrate how you would do load balancing of requests to increase scalability (e.g. with Kubernetes)
