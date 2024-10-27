# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fastapi",
#     "flask",
#     "uvicorn",
# ]
# ///

import random
import logging
import sys
from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
from settings import settings

# Set up logging using settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(settings.log_file),
    logging.StreamHandler(sys.stdout)
])

logger = logging.getLogger("server")

# FastAPI app setup
app = FastAPI()

@app.get("/")
async def get_random_payload() -> Response:
    """Handles GET requests and returns a random payload."""
    try:
        # Generate random payload similar to the old version
        data = f"random-{random.randint(0, 1000)}"
        logger.info("Generated random data payload")

        # Return the data as the response
        return PlainTextResponse(data, status_code=200)
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return PlainTextResponse("Internal server error", status_code=500)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server at http://{settings.host}:{settings.port}")
    uvicorn.run(app, host=settings.host, port=settings.port)
