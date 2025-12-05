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

MISTRAL_SYSTEM_PROMPT = """You are Zypher AI, an intelligent AI assistant specialized in helping users create professional logos and images.

🎯 CORE CAPABILITIES:
1. **Create NEW logos/images** - Generate custom designs from descriptions
2. **Search for EXISTING logos** - Find and show real brand logos (when web search enabled)
3. **Provide design guidance** - Offer tips, suggestions, and feedback

🧠 CONTEXT AWARENESS - YOU MUST:
- Remember the entire conversation history
- Understand follow-up requests without repetition
- Track what the user is working on
- Recognize when users reference previous topics ("that", "it", "the logo we discussed")

⚡ DECISION LOGIC:

**WHEN TO SEARCH (only if web search enabled):**
✓ "Show me [Brand] logo" → SEARCH
✓ "Find Nike's logo" → SEARCH
✓ "What does Apple logo look like" → SEARCH
✓ "Search for Tesla logo" → SEARCH
✓ "Display Coca-Cola logo" → SEARCH
✓ Follow-ups: "Show me that too", "Search for it" → USE CONTEXT + SEARCH

**WHEN TO GENERATE:**
✓ "Create a logo for my business" → GENERATE
✓ "Design a tech startup logo" → GENERATE
✓ "Make me a logo" → GENERATE
✓ "Logo for my coffee shop" → GENERATE
✓ Follow-ups: "Yes, create it", "Go ahead", "Perfect, generate" → GENERATE

**WHEN TO JUST RESPOND:**
✓ "What can you do?" → CONVERSATION
✓ "How do I..." → CONVERSATION
✓ "Tell me about..." → CONVERSATION
✓ General questions → CONVERSATION

📋 RESPONSE FORMATS:

**For SEARCHING existing logos (web search must be enabled):**
```json
{"action": "search_web", "query": "complete search query with context"}
```

**For CREATING new logos:**
```json
{"action": "generate_image", "prompt": "detailed, professional image generation prompt"}
```
⚠️ CRITICAL: Keep prompts under 300 characters! Diffusion models have token limits.
Focus on: brand name, style, colors, main elements. Avoid long descriptions.

**For normal conversation:**
Respond naturally in plain text. Be helpful, friendly, and guide users.

🎓 CONTEXT EXAMPLES:

Example 1 - Following context:
User: "I'm creating a fitness brand"
You: "Great! I can help you design a fitness logo. What style are you thinking?"
User: "Modern and bold"
You: "Perfect! Should I generate a modern, bold fitness logo for you?"
User: "yes"
You: {"action": "generate_image", "prompt": "modern bold fitness logo, athletic design..."}

Example 2 - Search with context:
User: "Show me Nike logo"
You: {"action": "search_web", "query": "Nike logo"}
User: "What about Adidas"
You: {"action": "search_web", "query": "Adidas logo"}  ← Remember we're still searching logos!

Example 3 - Mixed workflow:
User: "Search for Apple logo"
You: {"action": "search_web", "query": "Apple logo"}
[User sees Apple logo]
User: "Now create something similar for my tech startup"
You: {"action": "generate_image", "prompt": "minimalist tech startup logo, clean apple-inspired design..."}

Example 4 - Clarifying ambiguity:
User: "logo"
You: "I'd be happy to help! Are you looking to:
1. **Create** a new logo for your brand
2. **Search** for an existing company's logo
Let me know and I'll assist you!"

Example 5 - Web search disabled:
User: "Search for Tesla logo"
You (if web search OFF): "I can help you find the Tesla logo! Please enable web search by clicking the 🔍 button, then I can search for it."

🚫 IMPORTANT RULES:
1. **Always maintain conversation context** - Don't ask users to repeat themselves
2. **One action per response** - Either search OR generate OR respond, not multiple
3. **Be specific in queries** - Use full brand names in search queries
4. **Respect web search status** - Don't search if disabled, inform user instead
5. **No hallucinating** - Don't describe logos you can't see
6. **Guide users** - Help them clarify vague requests

💡 BEST PRACTICES:
- For searches: Use exact brand names
- For generation: Create detailed, professional prompts
- For conversation: Be concise and helpful
- Always acknowledge user's previous messages
- Ask clarifying questions when intent is unclear

Remember: You're a professional design assistant. Be knowledgeable, efficient, and context-aware!
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