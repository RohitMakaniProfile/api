# 🚀 Luna AI - Complete Setup Guide

## 📋 Requirements

- **Python 3.9+**
- **Node.js 16+**
- **Gemini API Key** - [Get it here](https://makersuite.google.com/app/apikey)

---

## ⚡ Quick Start (2 Minutes)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_api_key_here

# Run backend server
python main.py
```

Backend will start at: **http://127.0.0.1:8000**

---

### 2. Frontend Setup

```bash
# Open new terminal in root directory

# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Run frontend
npm run dev
```

Frontend will start at: **http://localhost:5173**

---

## 🎯 Usage

1. **Open Browser**: Go to http://localhost:5173
2. **Start Chatting**: Type anything to Luna
3. **Upload Images**: Click 📷 icon to share photos
4. **Generate Photos**: Ask "Show me your photo" or "Send me a picture"
5. **View Memories**: Click "🖼️ Memories" to see uploaded images

---

## 📁 Project Structure

```
luna-ai/
├── backend/
│   ├── core/
│   │   ├── agent.py          # Chat agent logic
│   │   ├── personality.py     # Luna's personality
│   │   ├── photoengine.py     # Photo generation
│   │   └── vision_agent.py    # Image analysis
│   ├── routers/
│   │   ├── chat.py            # Chat endpoint
│   │   ├── vision.py          # Image upload
│   │   ├── gallery.py         # Memory gallery
│   │   ├── generation.py      # Photo generation
│   │   └── history.py         # Chat history
│   ├── database.py            # Local file storage
│   ├── main.py                # FastAPI server
│   ├── requirements.txt
│   └── .env
├── src/
│   ├── App.jsx                # Main React app
│   ├── App.css                # Styles
│   ├── main.jsx               # Entry point
│   └── index.html
├── uploads/                   # User images (auto-created)
├── luna_memory.json           # All data (auto-created)
├── package.json
└── .env
```

---

## 🛠️ Troubleshooting

### Backend not starting?
- Make sure Python 3.9+ is installed: `python --version`
- Check if port 8000 is free
- Verify Gemini API key in `backend/.env`

### Frontend not loading?
- Make sure Node.js is installed: `node --version`
- Check if port 5173 is free
- Run `npm install` again

### Images not showing?
- Check `backend/uploads/` folder exists
- Ensure backend URL in `frontend/.env` is correct

---

## 🎨 Features

✅ **Natural Conversations** - Chat with Luna like a friend
✅ **Image Analysis** - Upload photos and get reactions
✅ **Photo Generation** - Ask for photos on demand
✅ **Memory System** - Luna remembers everything
✅ **Safety Filters** - Blocks inappropriate content
✅ **Local Storage** - No database needed

---

## 🔒 Privacy

- All data stored locally in `luna_memory.json`
- Images saved in `uploads/` folder
- No cloud storage, no external database
- Complete privacy guaranteed

---

## 💡 Tips

- **Clear Chat**: Settings → Clear Chat History
- **Search Memories**: Use search bar in Gallery
- **Better Photos**: Be specific in requests (e.g., "sunset over mountains")
- **Natural Chat**: Luna understands both English and Hinglish

---

## 📞 Need Help?

If you face any issues:
1. Check this guide again
2. Ensure all dependencies are installed
3. Verify API key is correct
4. Check both terminals for error messages

---

**Enjoy chatting with Luna! 🌙✨**
