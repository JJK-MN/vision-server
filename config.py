import os

# Controls whether heavy AI models are loaded. Set the environment variable
# `ENABLE_MODELS=1` or `ENABLE_MODELS=true` to enable model initialization.
USE_MODELS = os.getenv("ENABLE_MODELS", "false").lower() == "true"
