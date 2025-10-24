"""
Configuration file for Zypher AI Logo Generator
"""
import os

# Project Settings
PROJECT_NAME = "Zypher AI Logo Generator"
VERSION = "1.0.0"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CHAT_LOGS_DIR = os.path.join(BASE_DIR, "chat_logs")

# Model Configuration
# Flux Schnell base model from Hugging Face
BASE_MODEL_ID = "black-forest-labs/FLUX.1-schnell"

# LoRA Configuration
# Place your trained LoRA weights in the models/lora folder
LORA_MODEL_PATH = os.path.join(MODELS_DIR, "lora")
LORA_WEIGHTS_FILE = "logo_lora_weights.safetensors"  # Change to your LoRA filename

# Generation Settings
DEFAULT_GENERATION_PARAMS = {
    "num_inference_steps": 4,  # Flux Schnell is optimized for 1-4 steps
    "guidance_scale": 0.0,  # Flux Schnell works best with guidance_scale=0
    "width": 1024,
    "height": 1024,
    "num_images_per_prompt": 1,
}

# LoRA Settings
LORA_SCALE = 0.8  # Adjust between 0.0 and 1.0 for LoRA strength

# UI Settings
GRADIO_THEME = "soft"  # Options: "soft", "default", "monochrome"
SHARE_LINK = False  # Set to True to create a public share link
SERVER_PORT = 7860
SERVER_NAME = "0.0.0.0"  # Use "127.0.0.1" for localhost only

# Chat History
MAX_HISTORY_ITEMS = 50
HISTORY_FILE = os.path.join(CHAT_LOGS_DIR, "chat_history.json")

# Image Save Settings
SAVE_GENERATED_IMAGES = True
IMAGE_FORMAT = "PNG"

# GPU/CPU Settings
USE_GPU = True  # Set to False to use CPU (slower)
GPU_DEVICE = "cuda:0"  # Change if you have multiple GPUs
