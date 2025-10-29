# 🎨 Zypher AI Logo Generator

An AI-powered logo generator built with **Flux Schnell** and **Gradio**. Zypher features a stunning, **Claude-inspired modern interface** for creating professional logos using text prompts with support for custom LoRA models.

![Powered by Flux Schnell](https://img.shields.io/badge/Powered%20by-Flux%20Schnell-blueviolet)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange)
![UI](https://img.shields.io/badge/UI-Modern%20%26%20Futuristic-blueviolet)

## ✨ Features

### 🎯 Core Features
- 🚀 **Lightning Fast Generation**: Powered by Flux Schnell (optimized for 1-4 step generation)
- 🔮 **Custom LoRA Support**: Seamlessly switch between base model and your trained LoRA
- 💬 **Intelligent Chat Interface**: Claude-inspired conversational UI
- 📜 **Persistent History**: Automatic saving and beautiful display of generation history
- 🖼️ **Smart Image Management**: All generated logos saved automatically with metadata
- ⚙️ **Customizable Settings**: Fine-tune steps, resolution, and LoRA strength
- 📊 **Real-time Status**: Detailed feedback with rich formatting

### 🎨 Modern UI (NEW!)
- ✨ **Claude-Inspired Design**: Clean, professional, and futuristic interface
- 🌈 **Gradient Aesthetics**: Beautiful purple-indigo color scheme
- 💎 **Glassmorphism Effects**: Modern blurred backgrounds and depth
- 🎯 **3-Column Layout**: Optimized workspace with controls, output, and history
- 📱 **Fully Responsive**: Works perfectly on desktop, tablet, and mobile
- 🎭 **Custom Avatars**: Personalized user and AI avatars in chat
- ⚡ **Smooth Animations**: Hover effects, transitions, and micro-interactions
- 🔧 **Collapsible Settings**: Clean interface with advanced options tucked away

## 📁 Project Structure

```
NHA-065/
├── app_flask.py           # Flask web application (NEW)
├── templates/            # HTML templates
│   └── index.html       # ChatGPT-style interface
├── static/              # Static assets
│   ├── css/
│   │   └── style.css   # Modern styling
│   └── js/
│       └── app.js      # Frontend JavaScript
├── app.py                # Original Gradio application
├── config.py             # Configuration settings
├── .env                 # Environment variables (NOT in git)
├── .env.example         # Example environment file
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── models/              # Model storage
│   └── lora/           # Place your LoRA weights here
├── utils/              # Utility modules
│   ├── model_manager.py # Model loading and inference
│   └── chat_history.py  # Chat history management
├── outputs/            # Generated images
└── chat_logs/         # Chat history JSON files
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- NVIDIA GPU with CUDA support (recommended)
- At least 16GB RAM
- 10GB+ free disk space

### Installation

1. **Clone or navigate to the repository**
   ```powershell
   cd d:\NHA-065
   ```

2. **Create a virtual environment** (recommended)
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up your Hugging Face token** (required)
   ```powershell
   # Copy the example env file
   Copy-Item .env.example .env
   
   # Edit .env and add your Hugging Face token
   # Get your token from: https://huggingface.co/settings/tokens
   # You also need to accept the model license at:
   # https://huggingface.co/black-forest-labs/FLUX.1-schnell
   ```
   
   Edit `.env` and replace `your_huggingface_token_here` with your actual token:
   ```
   HUGGINGFACE_TOKEN=hf_your_actual_token_here
   ```

5. **Set up your LoRA model** (optional)
   - Place your trained LoRA weights in `models/lora/`
   - Update the `LORA_WEIGHTS_FILE` in `config.py` with your filename

### Running the Application

```powershell
# Run the modern ChatGPT-style interface (recommended)
python app_flask.py

# Or run the original Gradio interface
python app.py
```

The application will start on `http://localhost:7860`

**Important**: Make sure you have set up your Hugging Face token in the `.env` file before running!

## 🎯 Usage

### Basic Generation

1. **Open the interface** at `http://localhost:7860`
2. **Enter your prompt** in the large text area
   - Example: *"A modern tech startup logo featuring a geometric hexagon, gradient from deep blue to cyan, minimalist professional design"*
3. **Click the "✨ Generate Logo"** button (the big gradient button)
4. **View your logo** in the center panel
5. **Check the status box** below for detailed generation info

### Using LoRA

1. ✅ Check the **"🔮 Use LoRA Fine-tuned Model"** checkbox
2. 💬 Enter your prompt as usual
3. ✨ Click generate
4. 🎨 The system will automatically apply your custom LoRA weights

### Advanced Settings

Click on **"🎛️ Advanced Parameters"** accordion to reveal:
- **⚡ Inference Steps**: 1-8 (recommended: 1-4 for Flux Schnell)
  - Lower = Faster, Higher = More refined
- **📐 Image Dimensions**: 
  - Width: 512-1536 pixels
  - Height: 512-1536 pixels
  - Default: 1024×1024 (perfect for logos)

### Managing History

- **View**: All generations appear in the right sidebar with chat-style formatting
- **Clear**: Click **"🗑️ Clear History"** to reset
- **Persistence**: History is auto-saved to `chat_logs/chat_history.json`
- **Images**: All generated images are in the `outputs/` folder

### Model Status

Click **"📊 Model Info"** to see:
- Base model loading status
- LoRA model availability
- GPU/CPU device information
- Current model configuration

## 🎨 UI Overview

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│              🎨 Zypher AI Logo Generator                    │
│         Powered by Flux Schnell • AI-Driven Generation     │
└─────────────────────────────────────────────────────────────┘

┌──────────────┬─────────────────────┬──────────────────────┐
│  Controls    │   Generated Output  │  Generation History  │
│  (30%)       │        (40%)        │       (30%)          │
├──────────────┼─────────────────────┼──────────────────────┤
│              │                     │                      │
│ 💬 Prompt    │  🖼️ Your Logo      │ 📜 Chat History      │
│  [Text Box]  │                     │                      │
│              │   [Large Image]     │  [Chat Messages]     │
│ ✨ Generate  │                     │                      │
│              │   [Download]        │  [Scrollable]        │
│ ⚙️ Settings  │                     │                      │
│  • LoRA      │                     │                      │
│  • Advanced  │                     │                      │
│              │                     │                      │
│ 📊 Status    │                     │                      │
│              │                     │                      │
└──────────────┴─────────────────────┴──────────────────────┘

💡 Pro Tips • Documentation • Quick Help
```

### Color Scheme

- **Primary**: Indigo (#667eea) → Purple (#764ba2) gradient
- **Background**: Light gradient with depth
- **Cards**: White with soft shadows
- **Text**: Professional dark gray
- **Accents**: Success green, warning amber, error red

### Design Philosophy

The interface follows **Claude AI's design principles**:
1. ✨ **Minimalism** - Focus on what matters
2. 🎯 **Clarity** - Clear visual hierarchy
3. 💼 **Professionalism** - Enterprise-grade appearance
4. 🚀 **Performance** - Smooth and responsive
5. ♿ **Accessibility** - Proper contrast and spacing

For more details, see [UI_FEATURES.md](UI_FEATURES.md) and [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md).

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Model Settings
BASE_MODEL_ID = "black-forest-labs/FLUX.1-schnell"
LORA_SCALE = 0.8  # LoRA strength (0.0 - 1.0)

# Generation Settings
DEFAULT_GENERATION_PARAMS = {
    "num_inference_steps": 4,
    "guidance_scale": 0.0,
    "width": 1024,
    "height": 1024,
}

# UI Settings
SERVER_PORT = 7860
SHARE_LINK = False  # Set True for public link
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

### Authentication Error
- **Error**: "This model requires authentication"
- **Solution**: 
  1. Get your token from https://huggingface.co/settings/tokens
  2. Accept the model license at https://huggingface.co/black-forest-labs/FLUX.1-schnell
  3. Add token to `.env` file: `HUGGINGFACE_TOKEN=hf_your_token`
  4. Restart the application

### .env File Not Working
- Ensure the file is named exactly `.env` (not `.env.txt`)
- Check that `python-dotenv` is installed: `pip install python-dotenv`
- Verify the token format: should start with `hf_`

### Out of Memory Error
- Reduce image resolution in settings
- Close other GPU-intensive applications
- Enable CPU offloading (already enabled by default)

### LoRA Not Loading
- Check file path in `config.py`
- Ensure `.safetensors` file is in `models/lora/`
- Verify file isn't corrupted

### Slow Generation
- Reduce inference steps (try 2-3)
- Lower resolution (try 512x512)
- Ensure CUDA is properly installed

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
- [Gradio](https://gradio.app/) for the web interface
- [Hugging Face](https://huggingface.co/) for model hosting and diffusers

---

**Made with ❤️ for AI-powered creativity**
