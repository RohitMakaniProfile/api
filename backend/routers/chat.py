from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from core.agent import luna_agent
from core.photoengine import select_companion_photo
from database import conversations_collection
import traceback
import asyncio

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str
    message: Optional[str] = None
    imageAnalysis: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"\n💬 Chat from: {request.user_id}")
        print(f"📝 Message: {request.message}")

        # Load conversation history
        history_cursor = conversations_collection.find(
            {"user_id": request.user_id}
        ).sort("timestamp", 1).limit(50)  # Get more history

        history = list(history_cursor)
        print(f"📚 History length: {len(history)}")

        # ✅ Check if user is asking for image generation
        image_generation_keywords = [
            'image', 'generate', 'photo', 'pic', 'picture', 'draw', 'banao',
            'photo kro', 'generate kro', 'bana do', 'abb koi', 'koi photo',
            'image kro', 'pic kro', 'banao na', 'yrr koi'
        ]

        message_lower = request.message.lower() if request.message else ""
        is_asking_for_image = any(keyword in message_lower for keyword in image_generation_keywords)

        print(f"🎨 Asking for image: {is_asking_for_image}")

        if is_asking_for_image:
            print("✨ Processing image generation request...")

            # ✅ Extract ALL context from conversation
            context_messages = []

            # Add user messages from history
            for msg in history:
                if msg.get("user_message"):
                    context_messages.append(msg.get("user_message"))

            # Add current message
            if request.message:
                context_messages.append(request.message)

            # Combine ALL context
            full_context = " ".join(context_messages)
            print(f"📚 Full context: {full_context[:150]}...")

            # ✅ Generate image with FULL context
            try:
                photo_data = await select_companion_photo(
                    mood="neutral",
                    prompt=full_context,  # ✅ FULL CONVERSATION CONTEXT
                    last_activity=None
                )

                image_url = photo_data.get("url")
                detected_intent = photo_data.get("intent", "general")
                caption = photo_data.get("caption", "")

                print(f"✅ Image generated successfully!")
                print(f"   Intent: {detected_intent}")
                print(f"   Caption: {caption}")
                print(f"   URL: {image_url[:80]}...")

                # Get chat response
                response_data = await luna_agent.process_message(
                    user_id=request.user_id,
                    message=request.message,
                    image_analysis=request.imageAnalysis,
                    history=history
                )

                # ✅ Return BOTH chat response AND image
                result = {
                    **response_data,
                    "image": {
                        "imageUrl": image_url,
                        "caption": caption,
                        "intent": detected_intent
                    }
                }

                print(f"✅ Returning response with image")
                return result

            except Exception as img_error:
                print(f"⚠️ Image generation failed: {img_error}")
                traceback.print_exc()

                # Still return chat response even if image fails
                response_data = await luna_agent.process_message(
                    user_id=request.user_id,
                    message=request.message,
                    image_analysis=request.imageAnalysis,
                    history=history
                )
                return {
                    **response_data,
                    "image_error": str(img_error)
                }

        # Regular chat (no image)
        print("💬 Regular chat response only")
        response_data = await luna_agent.process_message(
            user_id=request.user_id,
            message=request.message,
            image_analysis=request.imageAnalysis,
            history=history
        )

        return response_data

    except Exception as e:
        print(f"❌ Chat Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
