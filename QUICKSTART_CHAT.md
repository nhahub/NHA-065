# 🚀 Quick Start Guide - Chat Feature

## Setup in 3 Steps

### Step 1: Get Your API Keys

1. **Hugging Face Token** (for Flux Schnell model)
   - Visit: https://huggingface.co/settings/tokens
   - Create a new token
   - Accept license: https://huggingface.co/black-forest-labs/FLUX.1-schnell

2. **Mistral AI API Key** (for chat feature)
   - Visit: https://console.mistral.ai/
   - Sign up / Log in
   - Create API key in the API Keys section

### Step 2: Configure Environment

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your keys:
   ```bash
   HUGGINGFACE_TOKEN=hf_your_token_here
   MISTRAL_API_KEY=your_mistral_key_here
   ```

### Step 3: Install and Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app_flask.py
   ```

3. Open in browser:
   ```
   http://localhost:7860
   ```

## ✅ Verify It's Working

### Test 1: Normal Chat
Type: `What makes a good logo?`

Expected: AI responds with design advice

### Test 2: Image Generation
Type: `Create a modern tech logo with blue colors`

Expected: AI generates and displays a logo

### Test 3: Conversation Flow
```
You: "What colors work for a restaurant?"
AI: [Provides color advice]

You: "Create a logo using those colors"
AI: [Generates logo automatically]
```

## 🎯 Example Prompts

### For Conversation:
- "What design principles should I follow?"
- "Tell me about minimalist design"
- "How do I choose colors for my brand?"
- "What fonts work well for logos?"

### For Generation:
- "Create a logo for my coffee shop"
- "Generate a minimalist tech startup logo"
- "Design a professional law firm logo"
- "Make a colorful gaming logo with neon effects"

## 🐛 Common Issues

### Issue: "Mistral API key not configured"
**Solution:** Add `MISTRAL_API_KEY=your_key` to `.env` file

### Issue: Chat works but no images generate
**Solution:** Check that Flux Schnell model downloaded correctly
- First run takes time to download (~5GB)
- Check console for download progress

### Issue: Out of memory error
**Solution:** Reduce image size in settings or close other applications

## 💰 Cost Estimate

With Mistral Large (recommended):
- Text conversations: ~$0.0008 per message
- Image generation: ~$0.008 per image (includes enhanced prompt)

**Monthly estimates:**
- Light use (10 images/day): ~$2.40
- Medium use (50 images/day): ~$12.00
- Heavy use (100 images/day): ~$24.00

💡 Tip: Use `mistral-small-latest` in config.py to reduce costs by 80%

## 📖 Learn More

- Full documentation: `README.md`
- Detailed chat guide: `CHAT_FEATURE_GUIDE.md`
- Design system: `DESIGN_SYSTEM.md`

## 🆘 Need Help?

Check these files for solutions:
1. `README.md` - Full setup guide
2. `CHAT_FEATURE_GUIDE.md` - Chat system details
3. Console logs - Error messages and debugging info

---

**Ready to create amazing logos! 🎨**
