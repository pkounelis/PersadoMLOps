from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from transformers import pipeline
import redis.asyncio as redis
import os
from contextlib import asynccontextmanager
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import logging
from logging.handlers import TimedRotatingFileHandler
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Basic authentication
security = HTTPBasic()


async def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("BASIC_AUTH_USERNAME", "username")
    correct_password = os.getenv("BASIC_AUTH_PASSWORD", "password")
    if not (credentials.username == correct_username and credentials.password == correct_password):
        logger.error("Invalid authentication credentials")
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials")
    return credentials

# Ensure the logs directory exists
log_directory = './logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configure logging with rotation
log_filename = os.path.join(log_directory, 'app.log')
rotation_interval = 'midnight'
interval_between_rotations = 1
backup_count = 7

# Create a timed rotating file handler
timed_handler = TimedRotatingFileHandler(
    log_filename, when=rotation_interval, interval=interval_between_rotations, backupCount=backup_count)
timed_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
timed_handler.setFormatter(formatter)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        timed_handler,
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNTER = Counter('requests_total', 'Total number of requests')

# Configure Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

# Define paths to local model directories
fill_mask_model_path = "./models/fill-mask"
sentiment_analysis_model_path = "./models/sentiment-analysis"

# Load pre-trained models from local path
mlm = pipeline("fill-mask", model=fill_mask_model_path)
sentiment_analysis = pipeline(
    "sentiment-analysis", model=sentiment_analysis_model_path)


@asynccontextmanager
async def lifespan_events(app: FastAPI):
    global redis_client
    redis_client = redis.Redis(
        host=redis_host, port=redis_port, decode_responses=True)

    yield

    await redis_client.aclose()

# Function to validate input


def validate_input(text: str):
    # Check whether input is of type 'str'
    if not isinstance(text, str):
        logger.error("Input type error: %s", text)
        raise HTTPException(
            status_code=400, detail="Input must be a string.")
    # Check whether input contains exactly 1 '<blank>' as per requirements
    if text.count("<blank>") != 1:
        logger.error("Invalid input placeholder: %s", text)
        raise HTTPException(
            status_code=400, detail="Input must contain exactly one '<blank>' placeholder.")

# Endpoint to generate suggestions


# App initialization
app = FastAPI(lifespan=lifespan_events)


@app.post("/suggest")
async def suggest(request: Request, response: Response, credentials: HTTPBasicCredentials = Depends(authenticate)):
    """
    Generate suggestions for the given input text.
    """
    # Increase request counter
    REQUEST_COUNTER.inc()

    # Read the request body as raw bytes
    input = await request.body()

    # Decode the bytes into a string
    try:
        input = input.decode("utf-8")
    except UnicodeDecodeError:
        logger.error("Invalid text encoding")
        raise HTTPException(status_code=400, detail="Invalid text encoding.")

    # Validate input
    validate_input(input)

    # Define cache expiration time
    expiration_time = 5

    # Check cache
    cache = await redis_client.get(input)
    if cache:
        logger.info("Cache hit for input: %s", input)
        return cache

    # Replace '<blank>' with '<mask>'
    masked_text = input.replace("<blank>", mlm.tokenizer.mask_token)
    # Generate suggestions
    suggestions = mlm(masked_text)
#    print(suggestions)

    # Filter suggestions based on sentiment analysis
    positive_suggestions = []
    for suggestion in suggestions:
        candidate = suggestion['sequence']
        # Predict sentiment of sequence
        sentiment = sentiment_analysis(candidate)
#        print(candidate)
#        print(sentiment)
        # If sentiment is positive append it to the positive_suggestions list
        if sentiment[0]['label'] == 'POSITIVE':
            positive_suggestions.append(suggestion['token_str'].strip())

    output = ", ".join(
        positive_suggestions) if positive_suggestions else "No positive suggestions found."

    # Cache the response
    await redis_client.set(input, output, ex=expiration_time)

    logger.info("Response generated and cached for input: %s", input)
    return Response(content=output, media_type="text/plain")

# Metrics endpoint


@app.get("/metrics")
async def metrics():
    """
    Provide Prometheus metrics.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Start the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
