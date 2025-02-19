# How to run:

### Download models

```
python download_models.py
```

##### Troubleshooting

- In case they are missing you might need to install the dependencies:

```
pip install transformers torch
```

- If you get this error:

```
OSError: [WinError 126] The specified module could not be found. Error loading "C:\Users\panos\AppData\Local\Programs\Python\Python311\Lib\site-packages\torch\lib\fbgemm.dll" or one of its dependencies.
```

it probably means that the **libomp140.x86_64.dll** dependency is missing (according to https://discuss.pytorch.org/t/failed-to-import-pytorch-fbgemm-dll-or-one-of-its-dependencies-is-missing/201969/40).

To fix it in Win10 versions, download the dependency (https://www.dllme.com/dll/files/libomp140_x86_64?sort=upload&arch=0x8664) and extract it under the System32 directory:

```
C:\Windows\System32
```

<p>&nbsp;</p>

### Build images

```
docker-compose -f app/docker-compose.yml build
```

<p>&nbsp;</p>

### Start container

```
docker-compose -f app/docker-compose.yml up
```

<p>&nbsp;</p>

### Send requests with Postman:

POST: http://localhost:8000/suggest

Authorization:

> Type: Basic Auth

> Username: admin

> Password: secret

Body:

> Select: raw Text

> Write a sentence with a <blank> placeholder

### Alternatively invoke from command prompt:

```
curl -X POST "http://localhost:8000/suggest" -H "Content-Type: text/plain" -d "have a <blank> day" -u admin:secret
```

<p>&nbsp;</p>

### Access metrics:

http://localhost:8000/metrics

<p>&nbsp;</p>

### Access Prometheus:

http://localhost:9090

<p>&nbsp;</p>

### Access Grafana:

http://localhost:3000/

Username: admin

Password: admin

<p>&nbsp;</p>

### Configure Prometheus Data Source in Grafana:

Connections -> Data sources -> Add new data source -> Prometheus

Connection:

> Prometheus server URL: http://app-prometheus-1:9090

<p>&nbsp;</p>

### Access Locust:

http://localhost:8089/

Configure host:

> http://app-fastapi-app-1:8000

<p>&nbsp;</p>

# Future work:

- ~~Test jenkins_pipeline.groovy~~
- Modify Jenkins pipeline to push to a Docker Hub repo instead of local
- Implement better authentication (OAuth2)
- Deployment scripts and configurations that demonstrate how you would do load balancing of requests to increase scalability (e.g. with Kubernetes)
