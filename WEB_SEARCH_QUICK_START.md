# Web Search Feature - Quick Start Guide

## 🚀 How to Use

### Step 1: Enable Web Search
1. Click the **Settings** button (⚙️) in the top-right corner
2. Scroll to **"Generation Settings"**
3. Check the box: **"Enable Web Search for Photos/Logos"**
4. The toggle is now active for your session

### Step 2: Search for a Photo
Simply ask the AI to search for a specific photo or logo:

**Examples:**
- "Search for a photo of the Nike logo"
- "Find an image of the Tesla logo"
- "Get a picture of Starbucks logo"
- "Show me a photo of the Apple logo"

### Step 3: Review the Result
The AI will display:
- 🖼️ **Preview image** from the web
- 📝 **Title and description**
- 🔗 **Source URL**
- Two action buttons

### Step 4: Confirm or Refine
Choose one:
- ✅ **"This is correct - Use it"** → Confirms the photo
- ❌ **"Search again"** → Finds a different photo

### Step 5: Use as Reference
Once confirmed, you can:
- Generate a logo inspired by it
- Ask for design variations
- Request similar styles

---

## 💡 Pro Tips

### Best Search Queries
✅ **Good:**
- "Search for a photo of McDonald's golden arches"
- "Find an image of Coca-Cola bottle"
- "Get the Adidas three stripes logo"

❌ **Less Effective:**
- "Logo" (too vague)
- "Red thing" (not specific)
- "That swoosh" (unclear)

### What You Can Search For
- 🏢 Brand logos (Nike, Apple, Google, etc.)
- 🎨 Design elements (symbols, icons, patterns)
- 📸 Reference photos (products, styles)
- 🖼️ Inspiration images (art, graphics)

### Workflow Tips
1. **Enable once**: Toggle stays on during your session
2. **Be specific**: More details = better results
3. **Refine if needed**: Don't hesitate to search again
4. **Combine features**: Use with LoRA models for enhanced results

---

## 🔧 Setup Requirements

### For Users
- ✅ Create an account and sign in
- ✅ Enable the toggle in settings
- ✅ That's it! Start searching

### For Administrators
Required environment variable:
```bash
BRAVE_SEARCH_API_KEY=your_api_key_here
```

Get your API key from: https://brave.com/search/api/

---

## ❓ FAQ

**Q: Does web search cost extra?**
A: No, it's included in your plan. Free users: 5 generations/day, Pro: unlimited.

**Q: Can I use my own image URL?**
A: Currently, you search from the web. Direct URL support is coming soon!

**Q: What if no results are found?**
A: Try a different search term or be more specific about what you're looking for.

**Q: Is the search safe/appropriate?**
A: Yes, we use 'moderate' safe search filtering to avoid inappropriate content.

**Q: Can I search in other languages?**
A: Currently English only, but multilingual support is planned.

**Q: Does this replace the reference image upload?**
A: No, they complement each other. Use upload for your own images, search for web images.

---

## 🎯 Example Workflow

```
1. Enable toggle in settings ⚙️

2. Ask: "Search for a photo of the Spotify logo"

3. Review preview:
   ┌────────────────────────────┐
   │ [SPOTIFY LOGO IMAGE]       │
   │ Title: Spotify Logo        │
   │ Source: spotify.com        │
   └────────────────────────────┘

4. Confirm: "Yes, this is correct"

5. Generate: "Create a music streaming logo inspired by this"

6. Result: AI generates logo with Spotify-style elements! 🎨
```

---

## 🐛 Troubleshooting

**Toggle doesn't work:**
- Refresh the page
- Check settings were saved
- Clear browser cache

**No search results:**
- Check internet connection
- Try different keywords
- Verify API is configured (admins)

**Image won't load:**
- Check source URL is valid
- Try searching again
- Report to admin if persistent

---

## 🎓 Next Steps

After mastering web search:
1. Explore **LoRA models** for custom styles
2. Try **IP-Adapter** for reference images
3. Combine multiple features for best results
4. Upgrade to **Pro** for unlimited generations

---

## 📞 Support

Need help? 
- Check full docs: `WEB_SEARCH_FEATURE.md`
- Review main README: `README.md`
- Contact support team

Happy creating! 🎨✨
