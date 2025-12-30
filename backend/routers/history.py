from fastapi import APIRouter, HTTPException
from database import conversations_collection
import traceback

router = APIRouter()

@router.get("/history/{user_id}")
async def get_conversation_history(user_id: str):
    try:
        cursor = conversations_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", 1).limit(100)
        
        history = list(cursor)
        
        formatted_history = []
        for msg in history:
            formatted_history.append({
                "role": msg.get("role"),
                "content": msg.get("content"),
                "type": msg.get("type", "text"),
                "image_url": msg.get("image_url"),
                "photo_sent": msg.get("photo_sent"),
                "timestamp": str(msg.get("timestamp"))
            })
        
        return formatted_history
    
    except Exception as e:
        print(f"❌ History Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
