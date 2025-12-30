# Luna AI Backend

Simple FastAPI backend with **local file storage** - no database needed!

## Features

✅ Local JSON file storage for all data
✅ Image upload and storage in `/uploads` folder
✅ Chat history with context awareness
✅ AI-powered image analysis with safety filters
✅ On-demand photo generation
✅ Visual memory system

## Setup

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. **Run Server**
```bash
python main.py
```

Server will start at `http://127.0.0.1:8000`

## API Endpoints

- `POST /api/chat` - Chat with Luna
- `POST /api/analyze-image` - Upload and analyze image
- `POST /api/generate-luna` - Generate Luna's photo
- `GET /api/history/{user_id}` - Get chat history
- `GET /api/gallery/{user_id}` - Get visual memories
- `GET /api/generated-images/{user_id}` - Get generated images

## Storage

All data is stored locally:
- `luna_memory.json` - Chat history, visual memories, generated images
- `uploads/` - User uploaded images

## Safety

Built-in safety filters block inappropriate content automatically.
