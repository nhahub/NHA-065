# 🎨 Zypher AI Logo Generator

An AI-powered logo generator with a modern **ChatGPT-style interface** powered by **Flux Schnell** and **Mistral AI**. Create professional logos through natural conversation with intelligent prompt understanding and automatic image generation.

![Powered by Flux Schnell](https://img.shields.io/badge/Powered%20by-Flux%20Schnell-blueviolet)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)
![Mistral AI](https://img.shields.io/badge/Mistral-AI-orange)

## ✨ Features

### 🎯 Core Features
- 💬 **ChatGPT-Style Interface**: Modern, intuitive chat-based UI with streaming responses
- 🤖 **AI-Powered Conversations**: Natural language understanding with Mistral AI
- 🎨 **Smart Image Generation**: Automatically detects when you want to create logos
- 🔍 **Web Search Integration**: Find existing logo references using Brave Search API
- ⚡ **Lightning Fast**: Powered by Flux Schnell (optimized for 1-4 step generation)
- 🔮 **Custom LoRA Support**: Seamlessly switch between base model and trained LoRA weights
- 🎭 **Markdown Support**: Rich text formatting with bold, italics, lists, and more
- 🔐 **Firebase Authentication**: Secure user accounts with Google Sign-In
- 👤 **User Management**: Personal profiles with usage tracking
- 📊 **Free & Pro Tiers**: Free tier (5 images/day) and unlimited Pro tier
- 📜 **Persistent History**: Auto-saved chat and generation history per user
- 🖼️ **Smart Image Management**: All generated logos saved with metadata
- 🎨 **Branded UI**: Custom Zypher logo throughout the interface

### 🎨 Modern UI
- ✨ **ChatGPT-Inspired Design**: Familiar, professional interface
- � **Dark Theme**: Easy on the eyes with purple gradient accents
- � **Streaming Text**: Real-time word-by-word message display
- � **Animated Indicators**: Typing and generating animations
- 📱 **Fully Responsive**: Works on desktop, tablet, and mobile
- � **Clean Layout**: Sidebar navigation with chat-focused design
- ⚡ **Smooth Animations**: Polished hover effects and transitions

## 📁 Project Structure

```
NHA-065/
├── app_flask.py              # 🌟 Main Flask application (ChatGPT-style interface)
├── config.py                 # ⚙️ Configuration settings
├── migrate_to_postgres.py    # 🔄 Database migration utility
├── pyproject.toml            # 📦 UV/pip project configuration
├── requirements.txt          # 📦 Python dependencies (pip)
├── .env                      # 🔐 Environment variables (NOT in git)
├── README.md                 # 📖 This file
├── data.db                   # 💾 SQLite database (or PostgreSQL)
├── models/                   # 🗄️ Data models
│   ├── __init__.py          #     Models package
│   ├── db.py                #     Database initialization
│   ├── user.py              #     User model
│   ├── chat_history.py      #     Chat history model
│   └── lora/                #     LoRA weights directory
├── routes/                   # 🛣️ API route handlers
│   ├── __init__.py          #     Routes package
│   ├── auth.py              #     Authentication routes
│   ├── user.py              #     User management routes
│   ├── chat.py              #     Chat endpoints
│   ├── generate.py          #     Image generation endpoints
│   ├── history.py           #     Chat history routes
│   └── model.py             #     Model management routes
├── templates/                # 🎭 HTML templates
│   ├── index.html           #     Main chat interface
│   ├── login.html           #     Login page
│   ├── signup.html          #     Signup page
│   ├── admin.html           #     Admin panel
│   └── upgrade.html         #     Upgrade to Pro page
├── static/                   # 🎨 Static assets
│   ├── css/
│   │   ├── style.css        #     Modern dark theme styles
│   │   ├── login.css        #     Login page styles
│   │   ├── signup.css       #     Signup page styles
│   │   └── upgrade.css      #     Upgrade page styles
│   └── js/
│       └── app.js           #     Frontend JavaScript
├── utils/                    # 🛠️ Utility modules
│   ├── model_manager.py     #     Model loading and inference
│   ├── chat_history.py      #     Chat history management
│   ├── mistral_chat.py      #     Mistral AI integration
│   ├── firebase_auth.py     #     Firebase authentication
│   ├── logo_agent.py        #     Logo generation agent
│   └── helpers.py           #     Helper functions
├── outputs/                  # 🖼️ Generated images
├── photos/                   # 🎨 App assets (logo, icons)
│   └── zypher.jpeg          #     Zypher logo
├── chat_logs/                # 📜 Chat history JSON files
└── zypher-*.json            # 🔑 Firebase service account (NOT in git)
```

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.9 or higher
- **GPU**: NVIDIA GPU with CUDA support (recommended, CPU fallback available)
- **RAM**: At least 16GB
- **Disk Space**: 10GB+ free
- **Package Manager**: [UV](https://docs.astral.sh/uv/) (optional but recommended for faster installs)

### Installation

#### Option 1: Using UV (Recommended - Fast & Modern)

[UV](https://docs.astral.sh/uv/) is an extremely fast Python package and project manager written in Rust. It's significantly faster than pip and handles virtual environments automatically.

1. **Install UV** (if not already installed)
   ```powershell
   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or using pip
   pip install uv
   ```

2. **Navigate to the project directory**
   ```powershell
   cd d:\NHA-065
   ```

3. **Sync dependencies** (automatically creates venv and installs all packages)
   ```powershell
   uv sync
   ```
   
   This single command will:
   - Create a virtual environment (`.venv/`)
   - Install all dependencies from `pyproject.toml`
   - Lock versions for reproducibility
   
   **Note**: UV will use the `pyproject.toml` file to manage dependencies.

4. **Activate the virtual environment**
   ```powershell
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   
   # Or using UV's run command (no activation needed)
   uv run python app_flask.py
   ```

#### Option 2: Traditional Installation (pip)

1. **Navigate to the project directory**
   ```powershell
   cd d:\NHA-065
   ```

2. **Create a virtual environment** (recommended)
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

### Configuration

1. **Set up environment variables**
   ```powershell
   # Copy the example env file (if available)
   # Otherwise create a new .env file
   New-Item -Path .\.env -ItemType File
   
   # Edit .env and add your tokens
   notepad .env  # or use your preferred editor
   ```
   
   Required environment variables in `.env`:
   ```bash
   # Hugging Face Token (required for Flux model)
   HUGGINGFACE_TOKEN=hf_your_actual_token_here
   
   # Mistral AI API Key (required for chat features)
   MISTRAL_API_KEY=your_mistral_api_key_here
   
   # Brave Search API Key (optional, for web search feature)
   BRAVE_SEARCH_API_KEY=your_brave_api_key_here
   
   # Firebase Configuration (required for authentication)
   FIREBASE_API_KEY=your_firebase_api_key
   FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   FIREBASE_PROJECT_ID=your_project_id
   FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   FIREBASE_APP_ID=your_app_id
   ```
   
   **Get your tokens:**
   - **Hugging Face**: https://huggingface.co/settings/tokens
     - Accept model license: https://huggingface.co/black-forest-labs/FLUX.1-schnell
   - **Mistral AI**: https://console.mistral.ai/api-keys/
   - **Brave Search**: https://brave.com/search/api/ (free tier: 2,000 queries/month)
   - **Firebase**: https://console.firebase.google.com/

2. **Set up Firebase service account** (for backend authentication)
   - Download your Firebase service account JSON from Firebase Console
   - Place it in the project root directory
   - The file should be named `zypher-eb28f-firebase-adminsdk-*.json`

3. **Set up LoRA model** (optional but recommended)
   - See the [LoRA Setup](#-lora-model-setup) section below for detailed instructions

### Running the Application

**Using UV:**
```powershell
# Run with UV (automatically uses the virtual environment)
uv run python app_flask.py

# Or activate the environment first
.\.venv\Scripts\Activate.ps1
python app_flask.py
```

**Using traditional Python:**
```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Start the application
python app_flask.py
```

The Flask application will start on `http://localhost:7860`

**First Time Setup:**
1. Navigate to `http://localhost:7860`
2. You'll be redirected to the login page
3. Sign in with Google (or create an account)
4. Start chatting and generating logos!

## 💻 Technology Stack

### Backend
- **Framework**: Flask 3.0+ (Python web framework)
- **Database**: SQLAlchemy ORM (SQLite/PostgreSQL)
- **Authentication**: Firebase Admin SDK
- **AI Chat**: Mistral AI (mistral-large-latest)
- **Image Generation**: Hugging Face Diffusers + Flux Schnell
- **LoRA Support**: PEFT library
- **Web Search**: Brave Search API

### Frontend
- **UI**: ChatGPT-inspired responsive design
- **Styling**: Custom CSS (dark theme, purple accents)
- **JavaScript**: Vanilla JS with streaming text
- **Markdown**: Marked.js for rich text rendering
- **Communication**: Fetch API

## 💾 Model Information

### Base Model: Flux Schnell
- **Developer**: Black Forest Labs
- **Type**: Text-to-Image Diffusion Model
- **Optimization**: Fast generation (1-4 inference steps)
- **Link**: [black-forest-labs/FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell)

### 🎯 Fine-Tuned LoRA Model

We've fine-tuned Flux Schnell specifically for professional logo generation:

**Training Specifications:**
- **Model**: [GssHunter/flux_schnell](https://huggingface.co/GssHunter/flux_schnell)
- **Hardware**: NVIDIA H200 GPU
- **Duration**: 2 hours
- **Steps**: 5,000
- **Dataset**: [logo-wizard/modern-logo-dataset](https://huggingface.co/datasets/logo-wizard/modern-logo-dataset)

**Enhanced Capabilities:**
- ✨ Professional logo aesthetics and brand identity
- 🎨 Modern design trends and typography
- 💡 Color theory for branding
- ⚡ Maintains Flux Schnell's speed (1-4 steps)
- 🎯 Specialized training on 5,000 curated logos

## 🎯 Usage Guide

### Chat Interface

The application features an intelligent AI assistant powered by Mistral AI with automatic image generation.

#### Natural Conversation Flow:

1. **Ask Questions**
   ```
   You: "What makes a good logo?"
   AI: "A good logo should be memorable, simple, versatile..."
   ```

2. **Request Logo Generation**
   Just describe what you want naturally:
   ```
   You: "Create a logo for my juice company"
   AI: "Sure! I'll be generating your logo for a juice company. 
        This will just take a moment! ✨"
   [Animated: "Generating your logo..."]
   [Image appears with metadata]
   ```

#### Examples of Natural Requests:
- *"Generate a minimalist tech startup logo"*
- *"Make me a gaming logo with neon effects"*
- *"Design a professional logo for a law firm"*
- *"Create a vibrant logo for a kids' brand"*

#### The AI Automatically:
- ✅ Understands your intent with smart detection
- ✅ Creates friendly, personalized responses
- ✅ Shows progress with animated indicators
- ✅ Generates high-quality images using Flux Schnell
- ✅ Displays results with full metadata
- ✅ Supports **Markdown formatting** (bold, italic, lists, etc.)

### 🔍 Web Search Feature

The web search feature allows you to find existing logo references and use them as inspiration for your designs.

#### How to Use Web Search:

1. **Enable Web Search** (toggle in the UI)
2. **Ask the AI to search**:
   ```
   You: "Search for tech startup logos"
   You: "Find minimalist coffee shop logos"
   You: "Show me modern gaming logos"
   ```

3. **AI returns visual references** with thumbnails
4. **Select a reference image** to use as inspiration
5. **AI generates a similar logo** using the reference

#### Example Workflow:
```
You: "Search for elegant jewelry brand logos"

AI: "🔍 Found 5 logo references for elegant jewelry brands:
     [Shows thumbnails with descriptions]
     
     Would you like to use any of these as inspiration?"

You: "Use image 2"

AI: "Perfect! I'll create a logo inspired by this elegant design. ✨"
     [Generates logo with reference influence]
```

#### Requirements:
- **Brave Search API Key** in `.env` file
- Free tier includes 2,000 queries per month
- Sign up at: https://brave.com/search/api/

### Subscription Tiers

**Free Tier:**
- 5 image generations per day
- Full chat access and all features
- Daily reset at midnight UTC

**Pro Tier:**
- ♾️ Unlimited image generations
- Priority support
- Early access to new features
- Upgrade at `/upgrade`

### User Interface Features
- 💬 Streaming responses word-by-word
- 📝 Full Markdown support in messages
- 🎨 Inline image display
- 📊 Generation metadata (model, steps, dimensions)
- ⬇️ Download generated images directly
- 📜 Persistent conversation history

## ⚙️ Advanced Configuration

Customize the application by editing `config.py`:

**Model Settings:**
```python
BASE_MODEL_ID = "black-forest-labs/FLUX.1-schnell"
LORA_SCALE = 0.8  # Control LoRA influence (0.0-1.0)
LORA_WEIGHTS_FILE = "flux_schnell/pytorch_lora_weights.safetensors"
```

**Generation Defaults:**
```python
DEFAULT_GENERATION_PARAMS = {
    "num_inference_steps": 4,
    "width": 1024,
    "height": 1024,
}
```

**Server Settings:**
```python
SERVER_PORT = 7860
DATABASE_URL = 'sqlite:///data.db'  # Or PostgreSQL
```

**Note:** API keys are configured in `.env` file, not in `config.py`

## 📝 LoRA Model Setup

### Using Our Fine-Tuned LoRA (Recommended)

1. **Download the fine-tuned model**:
   ```powershell
   # Create the lora directory if it doesn't exist
   New-Item -Path ".\models\lora" -ItemType Directory -Force
   
   # Download using git (if git-lfs is installed)
   cd models\lora
   git clone https://huggingface.co/GssHunter/flux_schnell
   ```
   
   Or download manually from: https://huggingface.co/GssHunter/flux_schnell

2. **Update config.py**:
   ```python
   LORA_WEIGHTS_FILE = "flux_schnell/pytorch_lora_weights.safetensors"
   LORA_SCALE = 0.8  # Recommended for our fine-tuned model
   ```

3. **Restart the application**

### Using Your Own Custom LoRA

1. **Train your LoRA** using your preferred training method
2. **Save the weights** as a `.safetensors` file
3. **Copy to the project**:
   ```powershell
   Copy-Item "path\to\your_lora.safetensors" -Destination ".\models\lora\"
   ```
4. **Update config.py**:
   ```python
   LORA_WEIGHTS_FILE = "your_lora.safetensors"
   LORA_SCALE = 0.8  # Adjust based on your model
   ```
5. **Restart the application**

### LoRA Training Details (Our Model)

Our fine-tuned LoRA was trained with the following specifications:
- **Base Model**: Flux Schnell (black-forest-labs/FLUX.1-schnell)
- **Training Dataset**: [logo-wizard/modern-logo-dataset](https://huggingface.co/datasets/logo-wizard/modern-logo-dataset)
- **Hardware**: NVIDIA H200 GPU
- **Training Time**: 2 hours
- **Steps**: 5,000
- **Focus**: Modern logo design, brand identity, professional aesthetics

## 💡 Best Practices

### Model Selection
- **Use Fine-Tuned LoRA** (recommended): Best for professional logo generation
- **Use Base Model**: For experimental designs or non-logo images
- **Inference Steps**: 1-4 steps (optimal for Flux Schnell)
- **LoRA Scale**: 0.8 (adjust in `config.py` to control influence)

### Prompt Engineering
- **Be Descriptive**: Include style, colors, and mood
- **Logo Keywords**: Use "logo", "minimalist", "professional", "clean design"
- **Brand Personality**: Specify "playful", "corporate", "elegant", "tech-forward"
- **Color Preferences**: Mention "blue and white", "monochrome", "vibrant colors"
- **Design Elements**: Include "geometric", "abstract", "lettermark", "icon-based"

## 🧠 How It Works

### AI Workflow

1. **User Input** → Natural language message via chat interface
2. **Intent Detection** → Mistral AI analyzes message to determine action
3. **Prompt Enhancement** → Converts simple requests into detailed prompts
4. **Image Generation** → Flux Schnell + LoRA creates high-quality logo
5. **Result Display** → Image returned with metadata in chat

**Example:**
```
User: "Create a logo for my coffee shop"
  ↓
Mistral AI: Detects generation intent
  ↓
Enhanced Prompt: "Professional coffee shop logo, warm colors, coffee cup element, inviting design"
  ↓
Flux Schnell + LoRA: Generates image (4 steps, 1024x1024)
  ↓
Result: 🖼️ High-quality logo displayed in chat
```

## 🛠️ Troubleshooting

### Authentication Issues

**Error: "Authentication required"**
- Solution: Clear browser cache and cookies, then log in again
- Check Firebase configuration in `.env`
- Ensure Firebase service account JSON file is in the correct location

### API Errors

**Mistral API Error**
- Error: "Mistral API key not configured"
- Solution: 
  1. Get API key from https://console.mistral.ai/api-keys/
  2. Add to `.env`: `MISTRAL_API_KEY=your_key`
  3. Restart application

**Hugging Face Error**
- Error: "This model requires authentication"
- Solution:
  1. Get token from https://huggingface.co/settings/tokens
  2. Accept license at https://huggingface.co/black-forest-labs/FLUX.1-schnell
  3. Add to `.env`: `HUGGINGFACE_TOKEN=hf_your_token`
  4. Restart application

### Database Issues

**Error: "Could not create DB tables"**
- Solution: Check file permissions on `data.db`
- Delete `data.db` and restart (will recreate)

### Generation Issues

**Out of Memory Error**
- Solution:
  - Reduce image resolution (try 512×512)
  - Close other GPU-intensive apps
  - Ensure CUDA is properly installed

**Slow Generation**
- Solution:
  - Reduce inference steps (try 2-3)
  - Lower resolution
  - Check if using GPU (not CPU)

**Free Tier Limit Reached**
- Error: "Free user limit reached"
- Solution: Upgrade to Pro or wait for daily reset (midnight UTC)

### Environment Variables

**.env file not working**
- Ensure file is named `.env` exactly (not `.env.txt`)
- Check `python-dotenv` is installed: `pip install python-dotenv` or `uv add python-dotenv`
- Verify token formats are correct
- Restart application after changes

### UV-Specific Issues

**UV command not found**
- Solution: Install UV using the installation command above
- Or add UV to your PATH environment variable
- Alternative: Use `pip install uv` to install globally

**UV sync fails**
- Solution: Ensure `pyproject.toml` exists in the project root
- Check Python version compatibility (>=3.9)
- Try: `uv sync --reinstall` to force reinstall

**Virtual environment not activating**
- Solution: Use PowerShell (not CMD)
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Or use UV's run command: `uv run python app_flask.py`

## 📦 Dependency Management

### Using UV (Recommended)

**Install a new package:**
```powershell
uv add package-name
```

**Remove a package:**
```powershell
uv remove package-name
```

**Update all dependencies:**
```powershell
uv sync --upgrade
```

**Lock dependencies:**
```powershell
uv lock
```

### Using pip

**Install a new package:**
```powershell
pip install package-name
# Then update requirements.txt:
pip freeze > requirements.txt
```

## 📡 API Reference

The application provides a RESTful API with the following endpoints:

### Authentication Endpoints

#### `GET /`
Main application interface (redirects to login if not authenticated)

#### `GET /login`
Login page with Firebase authentication

#### `GET /signup`
User registration page

### User Management

#### `GET /api/firebase-config`
Returns Firebase client configuration

**Response:**
```json
{
  "apiKey": "your_api_key",
  "authDomain": "your-project.firebaseapp.com",
  "projectId": "your-project-id",
  "storageBucket": "your-project.appspot.com",
  "messagingSenderId": "123456789",
  "appId": "1:123456789:web:abc123"
}
```

#### `GET /api/user/profile`
Get current user profile and usage statistics

**Headers:** `Authorization: Bearer <firebase_token>`

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "display_name": "John Doe",
    "is_pro": false,
    "prompt_count": 3,
    "remaining_prompts": 2,
    "last_prompt_reset": "2025-12-04T00:00:00Z",
    "created_at": "2025-12-01T10:30:00Z"
  }
}
```

#### `POST /api/user/profile`
Update user profile (display name)

**Headers:** `Authorization: Bearer <firebase_token>`

**Request:**
```json
{
  "display_name": "Jane Doe"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

### Chat Endpoints

#### `POST /api/chat`
Send a message to the AI assistant

**Headers:** `Authorization: Bearer <firebase_token>`

**Request:**
```json
{
  "message": "Create a logo for my tech startup",
  "conversation_id": "conv_1234567890_abc123",
  "use_web_search": false
}
```

**Response:**
```json
{
  "success": true,
  "reply": "Sure! I'll be generating your logo for a tech startup. This will just take a moment! ✨",
  "action": "generate",
  "image_prompt": "Professional tech startup logo, modern minimalist design, geometric shapes, blue and white color scheme, clean and innovative",
  "conversation_id": "conv_1234567890_abc123",
  "message_id": 42
}
```

**Web Search Response (when `use_web_search: true`):**
```json
{
  "success": true,
  "reply": "🔍 Found 5 logo references...",
  "action": "photo_search",
  "photo_results": [
    {
      "image_url": "https://example.com/logo1.jpg",
      "thumbnail_url": "https://example.com/thumb1.jpg",
      "title": "Modern Tech Startup Logo",
      "hostname": "example.com",
      "width": 800,
      "height": 600
    }
  ],
  "conversation_id": "conv_1234567890_abc123"
}
```

### Image Generation

#### `POST /api/generate-from-chat`
Generate a logo image from a prompt

**Headers:** `Authorization: Bearer <firebase_token>`

**Request:**
```json
{
  "image_prompt": "Professional tech startup logo, modern minimalist design",
  "conversation_id": "conv_1234567890_abc123",
  "chat_entry_id": 42,
  "use_lora": false,
  "num_steps": 4,
  "width": 1024,
  "height": 1024
}
```

**Response:**
```json
{
  "success": true,
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "filename": "logo_20251204_143022.png",
  "metadata": {
    "prompt": "Professional tech startup logo...",
    "model": "Base Flux Schnell",
    "steps": 4,
    "width": 1024,
    "height": 1024,
    "lora": null,
    "timestamp": "2025-12-04T14:30:22Z"
  },
  "remaining_prompts": 1
}
```

### Chat History

#### `GET /api/history`
Get all conversation summaries for the current user

**Headers:** `Authorization: Bearer <firebase_token>`

**Response:**
```json
{
  "success": true,
  "conversations": [
    {
      "conversation_id": "conv_1234567890_abc123",
      "title": "Tech Startup Logo",
      "last_message": "Sure! I'll be generating your logo...",
      "last_updated": "2025-12-04T14:30:00Z",
      "message_count": 5
    }
  ]
}
```

#### `GET /api/history/<conversation_id>`
Get full conversation details

**Headers:** `Authorization: Bearer <firebase_token>`

**Response:**
```json
{
  "success": true,
  "conversation": {
    "conversation_id": "conv_1234567890_abc123",
    "title": "Tech Startup Logo",
    "messages": [
      {
        "id": 41,
        "role": "user",
        "content": "Create a logo for my tech startup",
        "timestamp": "2025-12-04T14:29:00Z"
      },
      {
        "id": 42,
        "role": "assistant",
        "content": "Sure! I'll be generating your logo...",
        "timestamp": "2025-12-04T14:29:05Z",
        "image_url": "/outputs/logo_20251204_143022.png",
        "metadata": {...}
      }
    ]
  }
}
```

#### `GET /api/history/search?q=<query>`
Search through chat history

**Headers:** `Authorization: Bearer <firebase_token>`

**Query Parameters:**
- `q` (required): Search query string

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "conversation_id": "conv_1234567890_abc123",
      "message_id": 42,
      "role": "user",
      "content": "Create a logo for my tech startup",
      "timestamp": "2025-12-04T14:29:00Z"
    }
  ]
}
```

#### `GET /api/history/stats`
Get user's chat statistics

**Headers:** `Authorization: Bearer <firebase_token>`

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_conversations": 15,
    "total_messages": 127,
    "total_images_generated": 23,
    "avg_messages_per_conversation": 8.5
  }
}
```

### Model Management

#### `GET /api/model/status`
Get current model status and available LoRA models

**Response:**
```json
{
  "success": true,
  "model_loaded": true,
  "base_model": "black-forest-labs/FLUX.1-schnell",
  "current_lora": null,
  "device": "cuda"
}
```

#### `GET /api/model/loras`
List all available LoRA models

**Response:**
```json
{
  "success": true,
  "loras": [
    {
      "filename": "custom_logo_v1.safetensors",
      "size": "142.5 MB",
      "modified": "2025-12-01T10:00:00Z"
    }
  ]
}
```

### Error Responses

All endpoints may return error responses in the following format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User has reached their daily limit (free tier)
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## 🏗️ Architecture Overview

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL support
- **Authentication**: Firebase Admin SDK for secure user authentication
- **AI Integration**: Mistral AI for conversational interface
- **Image Generation**: Hugging Face Diffusers with Flux Schnell model
- **LoRA Support**: PEFT library for custom LoRA weights

### Frontend Architecture
- **Interface**: ChatGPT-inspired responsive design
- **Styling**: Custom CSS with dark theme and purple accents
- **Interactivity**: Vanilla JavaScript with streaming text support
- **Markdown**: Marked.js for rich text rendering
- **Real-time Updates**: Fetch API for seamless server communication

### Key Components
1. **Routes**: Modular blueprint-based routing system
2. **Models**: SQLAlchemy models for User and ChatHistory
3. **Utils**: Helper modules for model management, authentication, and chat processing
4. **Config**: Centralized configuration management

## 📦 Model Information

### Base Model
- **Model**: Flux Schnell by Black Forest Labs
- **Type**: Text-to-Image Diffusion
- **Optimized For**: Fast generation (1-4 steps)
- **License**: Check [Hugging Face model page](https://huggingface.co/black-forest-labs/FLUX.1-schnell)

### 🎯 Fine-Tuned LoRA Model

We've fine-tuned the Flux Schnell model specifically for logo generation to achieve superior results!

**LoRA Details:**
- **Model**: [GssHunter/flux_schnell](https://huggingface.co/GssHunter/flux_schnell)
- **Training Hardware**: NVIDIA H200 GPU
- **Training Duration**: 2 hours
- **Training Steps**: 5,000 steps
- **Dataset**: [logo-wizard/modern-logo-dataset](https://huggingface.co/datasets/logo-wizard/modern-logo-dataset)
- **Purpose**: Enhanced logo generation with better understanding of:
  - Professional logo aesthetics
  - Brand identity principles
  - Modern design trends
  - Typography and iconography
  - Color theory for branding

**Why Use Our Fine-Tuned LoRA?**
- ✨ **Better Logo Quality**: Trained specifically on high-quality modern logos
- 🎨 **Professional Results**: Understands branding and design principles
- ⚡ **Fast Generation**: Maintains Flux Schnell's speed (1-4 steps)
- 🎯 **Specialized Training**: 5,000 steps on curated logo dataset
- 💪 **Powerful Hardware**: Trained on NVIDIA H200 for optimal results

**How to Use:**
The fine-tuned LoRA is automatically available in the application. Simply:
1. Enable LoRA in the settings or generation parameters
2. Select the `flux_schnell` LoRA model
3. Generate your logo with enhanced quality!

Alternatively, you can download and use the LoRA manually:
```python
# The LoRA is loaded automatically by the model manager
# Or download it manually from:
# https://huggingface.co/GssHunter/flux_schnell
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐞 Report bugs or issues
- 💡 Suggest new features
- 🎯 Share your custom LoRA models
- 📝 Improve documentation

## 📜 License

This project is provided as-is. Please review the [Flux Schnell model license](https://huggingface.co/black-forest-labs/FLUX.1-schnell) for commercial use restrictions.

## 🙏 Acknowledgments

### Special Thanks

**Instructor & Mentor:**
- **[Mohamed Elmesawy](https://github.com/mohamedelmesawy)** - For invaluable guidance, support, and mentorship throughout the development of this project. Your expertise and encouragement made this application possible.

### Technologies & Services

- [Black Forest Labs](https://blackforestlabs.ai/) for Flux Schnell
- [Mistral AI](https://mistral.ai/) for the chat API
- [Firebase](https://firebase.google.com/) for authentication
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Hugging Face](https://huggingface.co/) for model hosting and diffusers
- [Marked.js](https://marked.js.org/) for Markdown rendering
- [Astral](https://astral.sh/) for UV - the fast Python package manager

---

**Made with ❤️ for AI-powered creativity**

🎨 **Zypher AI** - Where conversation meets creation
