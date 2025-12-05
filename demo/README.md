# Zypher AI Logo Generator - Demo Version

A static demonstration of the Zypher AI Logo Generator that runs entirely in the browser. Perfect for showcasing on GitHub Pages without requiring backend services or API keys.

## 🎨 What This Is

This is a **demo version** of the Zypher AI Logo Generator with:
- ✅ Full UI/UX experience
- ✅ Pre-configured responses
- ✅ Image upload functionality (demo only)
- ✅ Chat history
- ✅ Responsive design
- ❌ No actual AI model inference
- ❌ No API calls
- ❌ No backend required

Perfect for presentations, portfolio showcases, or giving stakeholders a feel for the interface.

## 🚀 Quick Start

### Option 1: Local Testing

Simply open `index.html` in your web browser:

```bash
# Windows
start index.html

# Or just double-click the index.html file
```

### Option 2: Local Server (Recommended)

For a more realistic experience, run a local server:

**Using Python:**
```bash
cd demo
python -m http.server 8000
# Visit http://localhost:8000
```

**Using Node.js:**
```bash
cd demo
npx serve
# Visit the URL shown in terminal
```

**Using VS Code:**
Install the "Live Server" extension and right-click `index.html` → "Open with Live Server"

## 📦 Deploying to GitHub Pages

### Step 1: Prepare Your Repository

1. Ensure this `demo` folder is in your repository
2. Add your demo images to `demo/assets/` (see instructions below)

### Step 2: Configure GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Source", select **Deploy from a branch**
4. Choose the branch (usually `main`) and set folder to `/demo`
5. Click **Save**

### Step 3: Access Your Demo

Your demo will be available at:
```
https://[your-username].github.io/[repository-name]/
```

For example:
```
https://nhahub.github.io/NHA-065/
```

## 🖼️ Adding Your Demo Images

### Required Images

Place these images in the `assets/` folder:

1. **Demo Logo Outputs** (what the AI "generates"):
   - `demo-logo-1.png` - Modern tech startup example
   - `demo-logo-2.png` - Coffee shop example
   - `demo-logo-3.png` - Fitness brand example
   - `demo-logo-4.png` - Law firm example
   - `demo-logo-default.png` - Default fallback

2. **Branding**:
   - `zypher.jpeg` - Your Zypher AI logo (appears in header)

### Image Specifications

- **Logo examples**: 1024x1024px, PNG format
- **Zypher logo**: 512x512px, JPEG or PNG
- Keep file sizes under 500KB for fast loading

### What If I Don't Have Images?

No problem! The demo includes placeholder graphics that will display if images are missing. However, for the best impression, use actual logo examples.

## 🎯 How It Works

The demo responds to keywords in user prompts:

| Keywords | Response Type |
|----------|--------------|
| "modern", "tech", "startup" | Tech startup logo |
| "coffee", "cafe", "minimalist" | Coffee shop logo |
| "fitness", "gym", "vibrant" | Fitness brand logo |
| "law", "legal", "professional" | Law firm logo |
| Anything else | Default response |

## 📱 Features

- **Chat Interface**: Full conversational UI
- **Chat History**: Saved in browser localStorage
- **Settings Panel**: Mock configuration options
- **Image Upload**: Demonstrates file upload UI
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Modern, professional appearance
- **Smooth Animations**: Polished user experience

## 🛠️ Customization

### Change Mock Responses

Edit `app.js` and modify the `mockResponses` object:

```javascript
const mockResponses = {
    "your keyword": {
        text: "Your custom response text",
        image: "assets/your-image.png"
    },
    // ... more responses
};
```

### Adjust Styling

Edit `style.css` to customize:
- Colors (see CSS variables at the top)
- Fonts
- Layout
- Animations

### Modify Content

Edit `index.html` to change:
- Page title
- Welcome message
- Example prompts
- Settings options

## 📋 File Structure

```
demo/
├── index.html          # Main HTML file
├── style.css           # All styling
├── app.js              # Demo logic and responses
├── assets/             # Images folder
│   ├── README.md       # Image instructions
│   ├── .gitkeep        # Keeps folder in git
│   └── (your images)   # Place images here
└── README.md           # This file
```

## 🔧 Troubleshooting

**Images not loading?**
- Check file names match exactly (case-sensitive on some systems)
- Ensure images are in the `assets/` folder
- Check browser console for errors (F12)

**GitHub Pages shows 404?**
- Wait a few minutes after setup (can take 5-10 minutes)
- Ensure the path in Settings → Pages is set to `/demo`
- Check if `index.html` exists in the demo folder

**Styling looks broken?**
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check that `style.css` is in the same folder as `index.html`
- Open browser console to check for loading errors

## 💡 Tips for Best Results

1. **Use Real Logo Examples**: The demo is much more impressive with actual generated logos
2. **Optimize Images**: Compress images before uploading to keep the page fast
3. **Test Locally First**: Always test the full experience before deploying
4. **Custom Domain**: Consider using a custom domain for GitHub Pages for a more professional URL
5. **Add Analytics**: You can add Google Analytics to track demo usage

## 🎓 For Presentations

This demo is perfect for:
- Client presentations
- Investor pitches  
- Portfolio showcases
- User testing
- Feature demonstrations
- Marketing materials

**Pro tip**: Open the demo in presentation mode (F11) for a distraction-free showcase.

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all files are in the correct locations
3. Review browser console for specific errors
4. Verify GitHub Pages is properly configured

## 📄 License

This demo version follows the same license as the main Zypher AI project.

---

**Ready to deploy?** Follow the GitHub Pages steps above and your demo will be live in minutes! 🚀
