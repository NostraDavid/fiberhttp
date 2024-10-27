# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "flask",
# ]
# ///

import random
import logging
import sys
from flask import Flask, Response
from settings import settings

# Set up logging using settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(settings.log_file),
    logging.StreamHandler(sys.stdout)
])

logger = logging.getLogger("server")

# Flask app setup
app = Flask(__name__)

@app.route("/", methods=["GET"])
def get_random_payload() -> Response:
    """Handles GET requests and returns a random payload."""
    try:
        # Generate random payload similar to the old version
        data = f"random-{random.randint(0, 1000)}"
        logger.info("Generated random data payload")

        # Return the data as the response
        return Response(data, status=200, content_type='text/plain')
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return Response("Internal server error", status=500, content_type='text/plain')

if __name__ == "__main__":
    logger.info(f"Starting server at http://{settings.host}:{settings.port}")
    app.run(host=settings.host, port=settings.port)
