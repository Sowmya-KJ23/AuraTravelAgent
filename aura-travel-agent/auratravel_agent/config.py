import os

# Configuration for the Travel Agent Model
# Can be overridden by setting the TRAVEL_MODEL_NAME environment variable.
MODEL_NAME = os.getenv("TRAVEL_MODEL_NAME", "gemini-2.5-flash")

# Default location for GCP Vertex AI if applicable
DEFAULT_LOCATION = "us-central1"
