# 🌙 Luna AI - Your Cosmic Companion

A beautiful, intelligent AI chatbot with memory, vision, and photo generation capabilities. Built with React and FastAPI, using **only local storage** - no database required!

## ✨ Features

- 💬 **Natural Conversations** - Chat with Luna like a real friend
- 👁️ **Image Analysis** - Upload images and get human-like reactions
- 📸 **Photo Generation** - Ask Luna for photos and she'll create them
- 🧠 **Memory System** - Luna remembers your conversations and images
- 🛡️ **Safety First** - Built-in content filtering
- 🎨 **Beautiful UI** - Modern, responsive design with smooth animations

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Gemini API Key ([Get here](https://makersuite.google.com/app/apikey))

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
python main.py
```

### Frontend Setup

```bash
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:5173`

## 📁 Storage

Everything is stored locally:
- **luna_memory.json** - All conversations and memories
- **uploads/** - User uploaded images
- **Browser localStorage** - User preferences

No database, no cloud storage required!

## 🎯 Usage Examples

**Normal Chat:**
- "Hey Luna, how are you?"
- "Tell me something interesting"

**Image Upload:**
- Upload any image and Luna will react naturally

**Photo Generation:**
- "Show me your photo"
- "Send me a picture"
- "Generate a sunset image"

## 🛡️ Safety

Luna has built-in safety filters that:
- Block inappropriate image uploads
- Filter harmful content
- Protect user privacy

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Credits

- Built with ❤️ using FastAPI and React
- Powered by Google Gemini 2.0
- Photo generation via Pollinations AI
