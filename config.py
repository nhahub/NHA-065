# config.py
"""
Configuration for Zypher AI Logo Generator (Flask)
Exposes a single `config` instance.
"""

import os
from dotenv import load_dotenv

# -------------------------------------------------
# Load .env
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CHAT_LOGS_DIR = os.path.join(BASE_DIR, "chat_logs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(CHAT_LOGS_DIR, exist_ok=True)

# -------------------------------------------------
# Flask / SQLAlchemy
# -------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(BASE_DIR, 'data.db')}"
)

FLASK_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": DATABASE_URL,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}

# -------------------------------------------------
# App meta
# -------------------------------------------------
PROJECT_NAME = "Zypher AI Logo Generator"
VERSION = "1.0.0"
SERVER_PORT = int(os.getenv("SERVER_PORT", "7860"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")

# -------------------------------------------------
# Diffusion model
# -------------------------------------------------
BASE_MODEL_ID = "black-forest-labs/FLUX.1-schnell"
LORA_MODEL_PATH = os.path.join(MODELS_DIR, "lora")
LORA_WEIGHTS_FILE = "logo_lora_weights.safetensors"

DEFAULT_GENERATION_PARAMS = {
    "num_inference_steps": 4,
    "guidance_scale": 0.0,
    "width": 1024,
    "height": 1024,
    "num_images_per_prompt": 1,
}
LORA_SCALE = 0.8

# -------------------------------------------------
# Image handling
# -------------------------------------------------
SAVE_GENERATED_IMAGES = True
IMAGE_FORMAT = "PNG"

# -------------------------------------------------
# GPU
# -------------------------------------------------
USE_GPU = os.getenv("USE_GPU", "true").lower() == "true"
GPU_DEVICE = os.getenv("GPU_DEVICE", "cuda:0")

# -------------------------------------------------
# Firebase
# -------------------------------------------------
FIREBASE_CLIENT_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY", ""),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
    "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
    "appId": os.getenv("FIREBASE_APP_ID", ""),
}

FIREBASE_SERVICE_ACCOUNT = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT",
    os.path.join(BASE_DIR, "utils", "zypher-eb28f-firebase-adminsdk-fbsvc-4bcfb0a550.json"),
)

# -------------------------------------------------
# Brave Search API (for web search functionality)
# -------------------------------------------------
BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY", "")

# -------------------------------------------------
# Mistral AI
# -------------------------------------------------
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
MISTRAL_API_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"

MISTRAL_SYSTEM_PROMPT = """You are Zypher AI, an intelligent assistant that helps users create logos and images. 

When users ask you to create, generate, make, or design a logo, image, picture, or photo, respond with a JSON object:
{"action": "generate_image", "prompt": "detailed description of the image"}

For normal conversation, respond naturally.

Examples:
User: "Create a logo for my tech startup"
Assistant: {"action": "generate_image", "prompt": "A modern tech startup logo featuring geometric shapes, gradient blue colors, minimalist and professional design"}

User: "What's the weather today?"
Assistant: I'm an AI assistant focused on helping you create logos and images. I don't have access to real-time weather data, but I can help you design weather-related graphics!
"""

# -------------------------------------------------
# Chat history
# -------------------------------------------------
MAX_HISTORY_ITEMS = 50
HISTORY_FILE = os.path.join(CHAT_LOGS_DIR, "chat_history.json")

# -------------------------------------------------
# BUILD CONFIG OBJECT SAFELY
# -------------------------------------------------
class _Config:
    pass

# Define exactly what goes into config (avoid iterating locals())
_config_values = {
    "BASE_DIR": BASE_DIR,
    "MODELS_DIR": MODELS_DIR,
    "OUTPUTS_DIR": OUTPUTS_DIR,
    "CHAT_LOGS_DIR": CHAT_LOGS_DIR,
    "PROJECT_NAME": PROJECT_NAME,
    "VERSION": VERSION,
    "SERVER_PORT": SERVER_PORT,
    "SERVER_HOST": SERVER_HOST,
    "DATABASE_URL": DATABASE_URL,
    "FLASK_CONFIG": FLASK_CONFIG,
    "BASE_MODEL_ID": BASE_MODEL_ID,
    "LORA_MODEL_PATH": LORA_MODEL_PATH,
    "LORA_WEIGHTS_FILE": LORA_WEIGHTS_FILE,
    "DEFAULT_GENERATION_PARAMS": DEFAULT_GENERATION_PARAMS,
    "LORA_SCALE": LORA_SCALE,
    "SAVE_GENERATED_IMAGES": SAVE_GENERATED_IMAGES,
    "IMAGE_FORMAT": IMAGE_FORMAT,
    "USE_GPU": USE_GPU,
    "GPU_DEVICE": GPU_DEVICE,
    "FIREBASE_CLIENT_CONFIG": FIREBASE_CLIENT_CONFIG,
    "FIREBASE_SERVICE_ACCOUNT": FIREBASE_SERVICE_ACCOUNT,
    "MISTRAL_API_KEY": MISTRAL_API_KEY,
    "MISTRAL_MODEL": MISTRAL_MODEL,
    "MISTRAL_API_ENDPOINT": MISTRAL_API_ENDPOINT,
    "MISTRAL_SYSTEM_PROMPT": MISTRAL_SYSTEM_PROMPT,
    "MAX_HISTORY_ITEMS": MAX_HISTORY_ITEMS,
    "HISTORY_FILE": HISTORY_FILE,
    "BRAVE_SEARCH_API_KEY": BRAVE_SEARCH_API_KEY,
}

# Attach all values to the config instance
for name, value in _config_values.items():
    setattr(_Config, name, value)

# Export the instance
config = _Config()