import os
import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
from database import generated_images_collection
from core.photoengine import select_companion_photo

router = APIRouter()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model_name = 'gemini-2.0-flash-exp'


class GenerationRequest(BaseModel):
    user_id: str
    prompt: str
    conversation_id: Optional[str] = None


@router.post("/generate-luna")
async def generate_luna_photo(request: GenerationRequest):
    print(f"✨ Generating photo for: {request.prompt}")

    try:
        # ✅ PASS ORIGINAL PROMPT DIRECTLY (Don't extract!)
        # This way intent detection works properly

        photo_data = await select_companion_photo(
            mood="neutral",
            prompt=request.prompt,  # ✅ Full original prompt
            last_activity=None
        )

        image_url = photo_data.get("url")
        if not image_url:
            raise ValueError("Photo generation failed")

        # Print what was detected
        detected_intent = photo_data.get("intent", "general")
        print(f"✅ Intent detected: {detected_intent}")
        print(f"📸 Image generated successfully")

        # Save to local DB
        image_doc = {
            "user_id": request.user_id,
            "conversation_id": request.conversation_id,
            "prompt": request.prompt,
            "image_url": image_url,
            "caption": photo_data.get("caption", ""),
            "intent": detected_intent,
            "timestamp": datetime.datetime.utcnow()
        }

        generated_images_collection.insert_one(image_doc)

        return {
            "imageUrl": image_url,
            "caption": photo_data.get("caption", ""),
            "intent": detected_intent,
            "status": "success"
        }

    except Exception as e:
        print(f"❌ Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generated-images/{user_id}")
async def get_generated_images(user_id: str):
    try:
        cursor = generated_images_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(50)

        images = list(cursor)

        formatted_images = []
        for img in images:
            formatted_images.append({
                "id": str(img.get("_id", "")),
                "prompt": img.get("prompt"),
                "image_url": img.get("image_url"),
                "caption": img.get("caption"),
                "intent": img.get("intent", "general"),
                "timestamp": img.get("timestamp").isoformat() if img.get("timestamp") else None
            })

        return formatted_images

    except Exception as e:
        print(f"❌ History Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load images")
