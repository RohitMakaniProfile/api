from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import base64
import os
import uuid
from core.vision_agent import vision_agent

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/analyze-image")
async def analyze_image(user_id: str = Form(...), file: UploadFile = File(...)):
    try:
        print(f"📸 Analyzing image for: {user_id}")
        
        # Save file
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Convert to Base64
        image_b64 = base64.b64encode(content).decode("utf-8")
        
        # Run Vision Agent
        initial_state = {
            "user_id": user_id,
            "image_base64": image_b64,
            "image_url": file_path,
            "raw_analysis_text": "",
            "parsed_analysis": {},
            "is_safe": True,
            "safety_issues": [],
            "memory_type": "unknown",
            "status": "processing"
        }
        
        result = await vision_agent.ainvoke(initial_state)
        
        analysis = result.get("parsed_analysis", {})
        
        return {
            "analysis": {
                "comment": analysis.get("comment", "Nice photo!"),
                "description": analysis.get("scene", "Image uploaded"),
                "scene": analysis.get("scene", ""),
                "objects": analysis.get("objects", []),
                "mood": analysis.get("mood", "neutral"),
                "tags": analysis.get("tags", [])
            },
            "image_url": file_path,
            "status": result.get("status", "success"),
            "is_safe": result.get("is_safe", True),
            "safety_issues": result.get("safety_issues", [])
        }
    
    except Exception as e:
        print(f"❌ Vision Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
