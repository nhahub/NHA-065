# GitHub Pages Setup Guide

Your demo has been successfully pushed to GitHub! Follow these steps to deploy it:

## 🚀 Quick Setup (5 minutes)

### Step 1: Enable GitHub Pages

1. Go to your repository: **https://github.com/nhahub/NHA-065**
2. Click **Settings** (top menu)
3. Scroll down and click **Pages** (left sidebar)
4. Under **Source**, select:
   - **Branch**: `main`
   - **Folder**: `/demo`
5. Click **Save**

### Step 2: Wait for Deployment

- GitHub will automatically build and deploy your site
- This usually takes 1-3 minutes
- You'll see a green checkmark when it's ready

### Step 3: Access Your Demo

Your demo will be live at:
```
https://nhahub.github.io/NHA-065/
```

## 📝 What's Deployed

✅ Full demo UI with all features
✅ Reference image upload interface
✅ Web search toggle
✅ Settings modal with all options
✅ Chat history with persistence
✅ Pre-configured mock responses
✅ Responsive design for mobile/desktop
✅ Your Zypher AI logo

## 🎨 Adding Demo Images (Optional)

To show actual logo examples instead of placeholders:

1. Add your logo images to `demo/assets/` folder:
   - `demo-logo-1.png` - Modern tech startup example
   - `demo-logo-2.png` - Coffee shop example
   - `demo-logo-3.png` - Eco-friendly/Fitness example
   - `demo-logo-4.png` - Law firm example
   - `demo-logo-default.png` - Default example

2. Commit and push:
```bash
git add demo/assets/
git commit -m "Add demo logo images"
git push
```

3. Wait 1-2 minutes for GitHub Pages to rebuild

## 🔧 Troubleshooting

**Site shows 404?**
- Wait a few more minutes (can take up to 10 minutes on first deploy)
- Check Settings → Pages to ensure it's enabled
- Make sure you selected `/demo` as the folder

**Images not loading?**
- Verify file names match exactly (case-sensitive)
- Check files are in `demo/assets/` folder
- Clear browser cache (Ctrl+Shift+R)

**Demo not updating?**
- Wait 1-2 minutes after pushing
- Hard refresh your browser (Ctrl+Shift+R)
- Check GitHub Actions tab for build status

## 📱 Share Your Demo

Once live, share your demo with:
- Clients and stakeholders
- Investors for pitches
- Portfolio and resume
- Social media

## 🎯 Next Steps

1. ✅ Enable GitHub Pages (see Step 1 above)
2. 📸 Add your best logo examples to assets folder
3. 🔗 Share the demo URL
4. 📊 Consider adding Google Analytics (optional)
5. 🌐 Use a custom domain (optional)

---

**Your Demo URL**: https://nhahub.github.io/NHA-065/

Need help? Check the [full demo README](demo/README.md) for more details.
