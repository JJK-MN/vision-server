import os
from dotenv import load_dotenv
load_dotenv()


# Controls whether heavy AI models are loaded. Set the environment variable
# `ENABLE_MODELS=1` or `ENABLE_MODELS=true` to enable model initialization.
USE_MODELS = str(os.getenv("ENABLE_MODELS", "false")).lower() == "true"
USE_VOICE = str(os.getenv("ENABLE_VOICE", "false")).lower() == "true"

print(f"Model loading is {'enabled' if USE_MODELS else 'disabled'}.")
print(f"Voice features are {'enabled' if USE_VOICE else 'disabled'}.")