import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Request
from database import visual_memory_collection

router = APIRouter()


def get_full_url(request: Request, path: str) -> str:
    if not path:
        return ""
    if path.startswith(("http://", "https://")):
        return path

    base_url = str(request.base_url).rstrip("/")
    filename = os.path.basename(path)
    return f"{base_url}/uploads/{filename}"


@router.get("/gallery/{user_id}")
async def get_user_gallery(
    request: Request,
    user_id: str,
    search: Optional[str] = Query(None),
):
    try:
        cursor = (
            visual_memory_collection
            .find({"user_id": user_id})
            .sort("timestamp", -1)
        )
        all_memories: List[Dict[str, Any]] = list(cursor)

        # search filter
        if search:
            search_lower = search.lower()
            filtered_memories: List[Dict[str, Any]] = []
            for mem in all_memories:
                desc = (mem.get("description") or "").lower()
                scene = (mem.get("scene") or "").lower()
                tags = [t.lower() for t in (mem.get("tags") or [])]

                if (
                    search_lower in desc
                    or search_lower in scene
                    or any(search_lower in t for t in tags)
                ):
                    filtered_memories.append(mem)
        else:
            filtered_memories = all_memories

        memories = filtered_memories[:50]

        formatted_memories: List[Dict[str, Any]] = []
        for mem in memories:
            raw_path = mem.get("image_url") or mem.get("image_path") or ""

            ts = mem.get("timestamp")
            # datetime ya string dono ko safe string me convert karo
            if hasattr(ts, "isoformat"):
                ts_str = ts.isoformat()
            else:
                ts_str = str(ts) if ts is not None else None

            formatted_memories.append(
                {
                    "id": str(mem.get("_id", "")),
                    "image_url": get_full_url(request, raw_path),
                    "description": mem.get("description", ""),
                    "scene": mem.get("scene", ""),
                    "objects": mem.get("objects", []),
                    "mood": mem.get("mood", "Neutral"),
                    "tags": mem.get("tags", []),
                    "timestamp": ts_str,
                }
            )

        return formatted_memories

    except Exception as e:
        print(f"❌ Gallery Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load gallery")
