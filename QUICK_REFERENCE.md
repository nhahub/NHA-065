# Zypher AI - Quick Reference Card

## 🚀 Quick Start Commands

```bash
# First time setup
./setup.sh

# Activate environment
source venv/bin/activate

# Run application
python app_flask.py

# Migrate to PostgreSQL
python migrate_to_postgres.py postgresql://user:pass@localhost/zypher_ai
```

## 🔑 API Keys Needed

| Service | URL | Purpose |
|---------|-----|---------|
| Brave Search | https://brave.com/search/api/ | Logo design references |
| Mistral AI | https://console.mistral.ai/api-keys/ | AI chat & detection |
| Hugging Face | https://huggingface.co/settings/tokens | Download Flux model |
| Firebase | https://console.firebase.google.com/ | Authentication |

## 📍 URLs

| Page | URL | Description |
|------|-----|-------------|
| Main App | http://localhost:7860 | Chat & generate logos |
| Login | http://localhost:7860/login | User authentication |
| Signup | http://localhost:7860/signup | New user registration |
| Upgrade | http://localhost:7860/upgrade | Pro plan info |
| Admin | http://localhost:7860/admin | User management |

## 🎨 Logo Agent Features

### User Commands
- "Create a logo for [my business]"
- "Design a [industry] logo"
- "Make a logo with [colors/style]"

### Agent Process
1. 🔍 Searches web for design references
2. 🎨 Extracts visual patterns (shapes, colors, icons)
3. 📝 Generates optimized prompt
4. 👁️ Shows preview with features
5. ✅ User confirms or refines
6. 🖼️ Generates logo

### Preview Actions
- **✅ Confirm & Generate** - Proceed with logo generation
- **🔄 Refine Search** - Request new search with refinements

## 💾 Database Commands

### SQLite (Default)
```bash
# Location
./data.db

# Backup
cp data.db data.db.backup
```

### PostgreSQL

```bash
# Local setup
sudo apt install postgresql
sudo -u postgres psql

# In psql:
CREATE DATABASE zypher_ai;
CREATE USER zypher_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE zypher_ai TO zypher_user;
\q

# Connection string
DATABASE_URL=postgresql://zypher_user:password@localhost:5432/zypher_ai

# Migrate
python migrate_to_postgres.py
```

## 🔒 Admin Dashboard

### Access
http://localhost:7860/admin

### Features
- 👥 View all users
- 📊 Statistics (users, generations)
- 🔍 Search by email
- 🏷️ Filter by plan (Pro/Free)
- 📅 Sort by date/name/count
- 👁️ View user history

### API Endpoints
```
GET  /api/admin/users              # List all users
GET  /api/admin/users/:id/history  # User's history
```

## 🌐 API Endpoints

### Chat & Generation
```
POST /api/chat                  # Chat with AI (with logo detection)
POST /api/generate-from-chat    # Generate from detected request
POST /api/generate              # Direct generation
```

### User Management
```
GET  /api/user/profile          # Get user profile
POST /api/user/profile          # Update profile
GET  /api/history               # Get user's history
GET  /api/history/:id           # Get specific history item
DELETE /api/history/:id         # Delete history item
POST /api/history/clear         # Clear all history
```

### Subscription
```
POST /api/payment/success       # Upgrade to Pro
POST /api/unsubscribe          # Cancel Pro
```

### Admin (Auth Required)
```
GET  /api/admin/users               # All users + stats
GET  /api/admin/users/:id/history   # User's full history
```

## 🔧 Environment Variables

### Required
```env
MISTRAL_API_KEY=xxx
BRAVE_SEARCH_API_KEY=xxx
HUGGINGFACE_TOKEN=xxx
FIREBASE_API_KEY=xxx
FIREBASE_AUTH_DOMAIN=xxx
FIREBASE_PROJECT_ID=xxx
```

### Optional
```env
DATABASE_URL=postgresql://...      # Default: SQLite
MISTRAL_MODEL=mistral-large-latest # Default shown
SERVER_PORT=7860                   # Default shown
```

## 📦 Project Structure

```
NHA-065/
├── app_flask.py              # Main Flask app
├── config.py                 # Configuration
├── models.py                 # Database models
├── migrate_to_postgres.py    # Migration script
├── requirements.txt          # Dependencies
├── setup.sh                  # Setup script
├── utils/
│   ├── logo_agent.py        # Logo Reference Agent
│   ├── mistral_chat.py      # Chat manager
│   ├── model_manager.py     # Image generation
│   └── firebase_auth.py     # Authentication
├── templates/
│   ├── index.html           # Main UI
│   └── admin.html           # Admin dashboard
└── static/
    ├── css/style.css        # Styles
    └── js/app.js            # Frontend logic
```

## 🐛 Troubleshooting

### Logo preview not showing
- Check BRAVE_SEARCH_API_KEY is set
- Check browser console for errors
- Verify Mistral API is responding

### Database errors
- SQLite: Check file permissions on data.db
- PostgreSQL: Verify connection string
- Check user has database privileges

### Images not generating
- Check HUGGINGFACE_TOKEN is valid
- Verify model license accepted
- Check GPU/CUDA availability

### Admin dashboard empty
- Verify users exist in database
- Check authentication token is valid
- Check browser console for API errors

## 📊 Resource Limits

### Free Tier
- **Images**: 5 per day per user
- **Brave Search**: 2,000 queries/month
- **Database**: SQLite (unlimited local)

### Pro Tier
- **Images**: Unlimited
- **Brave Search**: Same (or upgrade)
- **Database**: PostgreSQL recommended

## 🎯 Testing Checklist

- [ ] Create logo with company name
- [ ] Preview shows correctly
- [ ] Confirm generates logo
- [ ] Refine search works
- [ ] History saves
- [ ] Admin dashboard loads
- [ ] View user history works
- [ ] PostgreSQL migration (if used)

## 📞 Quick Help

### Files to Check
- `.env` - API keys and configuration
- `data.db` - SQLite database
- `outputs/` - Generated images
- `chat_logs/` - Chat history backups

### Logs
```bash
# Application logs (in terminal where app runs)
# Database logs (PostgreSQL)
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Common Fixes
```bash
# Reset environment
rm -rf venv
./setup.sh

# Reset database (⚠️ deletes data)
rm data.db
python app_flask.py  # Creates new DB

# Clear cache
rm -rf __pycache__
rm -rf utils/__pycache__
```

---

**Need more help?** See:
- `README_NEW_FEATURES.md` - Detailed documentation
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `.env.example` - Configuration reference
