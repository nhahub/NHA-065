# 🎨 Zypher AI Logo Generator

An AI-powered logo generator with a modern **ChatGPT-style interface** powered by **Flux Schnell** and **Mistral AI**. Create professional logos through natural conversation with intelligent prompt understanding and automatic image generation.

![Powered by Flux Schnell](https://img.shields.io/badge/Powered%20by-Flux%20Schnell-blueviolet)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)
![Mistral AI](https://img.shields.io/badge/Mistral-AI-orange)

## ✨ Features

### 🎯 Core Features
- � **ChatGPT-Style Interface**: Modern, intuitive chat-based UI with streaming responses
- 🤖 **AI-Powered Conversations**: Natural language understanding with Mistral AI
- 🎨 **Smart Image Generation**: Automatically detects when you want to create logos
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
├── models.py                 # 💾 Database models (User, ChatHistory)
├── .env                      # 🔐 Environment variables (NOT in git)
├── .env.example              # 📋 Example environment file
├── requirements.txt          # 📦 Python dependencies
├── README.md                 # 📖 This file
├── data.db                   # 💾 SQLite database
├── templates/                # 🎭 HTML templates
│   ├── index.html           #     Main chat interface
│   ├── login.html           #     Login page
│   ├── signup.html          #     Signup page
│   └── upgrade.html         #     Upgrade to Pro page
├── static/                   # 🎨 Static assets
│   ├── css/
│   │   └── style.css        #     Modern dark theme styles
│   └── js/
│       └── app.js           #     Frontend JavaScript
├── utils/                    # 🛠️ Utility modules
│   ├── model_manager.py     #     Model loading and inference
│   ├── chat_history.py      #     Chat history management
│   ├── mistral_chat.py      #     Mistral AI integration
│   └── firebase_auth.py     #     Firebase authentication
├── models/                   # 🤖 Model storage
│   └── lora/                #     LoRA weights directory
├── outputs/                  # 🖼️ Generated images
├── photos/                   # 🎨 App assets (logo, icons)
│   └── zypher.jpeg          #     Zypher logo
├── chat_logs/                # 📜 Chat history JSON files
└── zypher-*.json            # 🔑 Firebase service account (NOT in git)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- NVIDIA GPU with CUDA support (recommended, CPU fallback available)
- At least 16GB RAM
- 10GB+ free disk space

### Installation

1. **Clone or navigate to the repository**
   ```bash
   cd /workspaces/NHA-065
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # Or on Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env and add your tokens
   nano .env  # or use your preferred editor
   ```
   
   Required environment variables in `.env`:
   ```bash
   # Hugging Face Token (required for Flux model)
   HUGGINGFACE_TOKEN=hf_your_actual_token_here
   
   # Mistral AI API Key (required for chat features)
   MISTRAL_API_KEY=your_mistral_api_key_here
   
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
   - **Firebase**: https://console.firebase.google.com/

5. **Set up Firebase service account** (for backend authentication)
   - Download your Firebase service account JSON from Firebase Console
   - Place it in the project root directory
   - The file should be named `zypher-eb28f-firebase-adminsdk-*.json`

6. **Set up your LoRA model** (optional)
   - Place your trained LoRA weights in `models/lora/`
   - Update the `LORA_WEIGHTS_FILE` in `config.py` with your filename

### Running the Application

**Start the application:**
```bash
python app_flask.py
```

The Flask application will start on `http://localhost:7860`

**First Time Setup:**
1. Navigate to `http://localhost:7860`
2. You'll be redirected to the login page
3. Sign in with Google (or create an account)
4. Start chatting and generating logos!

## 🎯 Usage

### ChatGPT-Style Interface (Main Application)

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

### User Tiers

#### Free Tier
- 5 image generations per day
- Full chat access
- All features available
- Daily reset at midnight UTC

#### Pro Tier
- ♾️ Unlimited image generations
- Priority support
- Early access to new features
- Upgrade via the `/upgrade` page

### Advanced Features

#### Settings (Click your avatar → Settings)
- Update your profile (name)
- View your plan and usage
- Configure generation parameters (coming soon)

#### Chat Features
- 💬 Streaming responses word-by-word
- 📝 Full Markdown support in messages
- 🎨 Inline image display
- 📊 Generation metadata (model, steps, dimensions)
- ⬇️ Download generated images directly
- 📜 Persistent conversation history

## 🎨 UI Overview

### ChatGPT-Style Layout

```
┌─────────────────────────────────────────────────────────────┐
│  [☰]  🎨 Zypher AI                              [Avatar]    │
├─────────────────────────────────────────────────────────────┤
│ Sidebar          │          Chat Messages                   │
│ ┌─────────────┐  │  ┌──────────────────────────────────┐  │
│ │ + New Chat  │  │  │ User: Create a juice logo         │  │
│ ├─────────────┤  │  │ AI: Sure! I'll be generating...   │  │
│ │ Recent:     │  │  │ [Generating your logo...]         │  │
│ │ • Chat 1    │  │  │ [🖼️ Generated Image]              │  │
│ │ • Chat 2    │  │  │ Model: Base Flux Schnell          │  │
│ │ • Chat 3    │  │  │ Steps: 4 | Size: 1024×1024       │  │
│ └─────────────┘  │  └──────────────────────────────────┘  │
│                  │                                         │
│ [Settings]       │  ┌──────────────────────────────────┐  │
│ [Sign Out]       │  │ Type your message...            [↑] │  │
│                  │  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- **🌙 Dark Theme**: Modern dark UI with purple accents
- **💬 Streaming Text**: Real-time word-by-word responses
- **🎭 Custom Logo**: Zypher logo throughout (sidebar, messages, favicon)
- **📝 Markdown**: Full support for **bold**, *italic*, `code`, and more
- **🎬 Animations**: Typing dots and spinning loader during generation
- **📱 Responsive**: Adapts perfectly to any screen size
- **🔐 Secure**: Firebase authentication with Google Sign-In

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Model Settings
BASE_MODEL_ID = "black-forest-labs/FLUX.1-schnell"
LORA_SCALE = 0.8  # LoRA strength (0.0 - 1.0)

# Generation Settings
DEFAULT_GENERATION_PARAMS = {
    "num_inference_steps": 4,  # Flux Schnell optimized for 1-4 steps
    "width": 1024,
    "height": 1024,
}

# Mistral AI Settings
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')
MISTRAL_MODEL = 'mistral-large-latest'

# Firebase Settings
FIREBASE_CLIENT_CONFIG = {...}  # Set in .env
FIREBASE_SERVICE_ACCOUNT = 'path/to/service-account.json'

# Server Settings
SERVER_PORT = 7860
DATABASE_URL = 'sqlite:///data.db'  # Or PostgreSQL URL
```

## 🧠 How the AI Works

### Intelligent Response System

1. **Natural Language Processing**: Mistral AI analyzes your message
2. **Intent Detection**: Determines if you want to chat or generate
3. **Smart Acknowledgment**: AI creates personalized confirmation messages
4. **Prompt Enhancement**: Converts simple requests into detailed prompts
5. **Automatic Generation**: Creates images without manual intervention

### Example Workflow:

```
You: "I need a logo for my coffee shop"

AI (Mistral analyzes request):
   └─> Detects: Image generation intent
   └─> Generates: "Sure! I'll be generating your logo for a coffee shop. 
                   This will just take a moment! ✨"

Frontend:
   └─> Displays streaming response
   └─> Shows: "Generating your logo..."
   └─> Calls image generation endpoint

Backend:
   └─> Creates: Professional coffee shop logo with warm colors,
                coffee cup element, inviting design

Result: 🖼️ Beautiful logo + metadata displayed in chat
```

## 📝 Adding Your LoRA Model

1. **Train your LoRA** using your preferred training method
2. **Save the weights** as a `.safetensors` file
3. **Copy to the project**:
   ```powershell
   Copy-Item "path\to\your_lora.safetensors" -Destination ".\models\lora\"
   ```
4. **Update config.py**:
   ```python
   LORA_WEIGHTS_FILE = "your_lora.safetensors"
   ```
5. **Restart the application**

## 🎨 Tips for Best Results

- **Flux Schnell** works best with **1-4 inference steps**
- Use descriptive prompts: include style, colors, and mood
- For logos, mention: "logo", "minimalist", "professional", "clean design"
- Start with base model, then try LoRA for specialized styles
- Adjust `LORA_SCALE` in config.py to control LoRA influence

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
- Check `python-dotenv` is installed: `pip install python-dotenv`
- Verify token formats are correct
- Restart application after changes

## 📦 Model Information

- **Base Model**: Flux Schnell by Black Forest Labs
- **Model Type**: Text-to-Image Diffusion
- **Optimized For**: Fast generation (1-4 steps)
- **License**: Check [Hugging Face model page](https://huggingface.co/black-forest-labs/FLUX.1-schnell)

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Share your LoRA models
- Improve documentation

## 📄 License

This project is provided as-is. Please check the Flux Schnell model license for commercial use.

## 🙏 Acknowledgments

- [Black Forest Labs](https://blackforestlabs.ai/) for Flux Schnell
- [Mistral AI](https://mistral.ai/) for the chat API
- [Firebase](https://firebase.google.com/) for authentication
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Hugging Face](https://huggingface.co/) for model hosting and diffusers
- [Marked.js](https://marked.js.org/) for Markdown rendering

---

**Made with ❤️ for AI-powered creativity**

🎨 **Zypher AI** - Where conversation meets creation
