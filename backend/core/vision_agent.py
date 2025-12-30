import os
import json
import datetime
import re
from typing import TypedDict, Optional, List, Dict, Any

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from database import visual_memory_collection


# ---------- Safety filters ----------

DISALLOWED_PATTERNS = [
    # sexual / nudity
    "nudity", "nude", "naked", "nsfw", "explicit",
    "lingerie", "underwear", "bikini", "bra", "panties",
    "sensual", "seductive", "sexual",

    # violence
    "violence", "violent", "blood", "gore", "weapon", "gun", "knife",

    # illegal / drugs
    "illegal", "drug", "substance",

    # self harm
    "self-harm", "suicide", "cutting",
]


# ---------- State Definition ----------

class VisionState(TypedDict):
    user_id: str
    image_base64: str
    image_url: Optional[str]
    raw_analysis_text: str
    parsed_analysis: Dict[str, Any]
    is_safe: bool
    safety_issues: List[str]
    memory_type: str
    status: str


# ---------- Model Setup ----------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.8,
)


# ---------- Node: Analyze Image ----------

async def node_analyze_image(state: VisionState):
    print("👁️ Analyzing image with Gemini Vision")

    prompt = """
    You are Luna, a friendly AI companion.
    Analyze this image and respond in valid JSON format.

    In the 'comment' field, react naturally in casual English or Hinglish (2-3 sentences).
    Ask a question or make an observation.

    OUTPUT ONLY THIS JSON:
    {
        "comment": "your natural reaction here",
        "scene": "technical description",
        "objects": ["obj1", "obj2"],
        "mood": "mood detected",
        "tags": ["tag1", "tag2"],
        "safety_concerns": "none or describe issue"
    }
    """

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{state['image_base64']}"
                },
            },
        ]
    )

    try:
        response = await llm.ainvoke([message])
        return {"raw_analysis_text": response.content}
    except Exception as e:
        print(f"❌ Vision API Error: {e}")
        return {"raw_analysis_text": "{}", "status": "error"}


# ---------- Node: Process Safety ----------

def node_process_safety(state: VisionState):
    print("🛡️ Processing safety and parsing JSON")
    text = state.get("raw_analysis_text", "{}")

    analysis: Dict[str, Any] = {}

    try:
        # Extract JSON from markdown/fenced output
        clean_text = re.sub(r"```json\s*", "", text)
        clean_text = re.sub(r"```", "", clean_text).strip()

        json_match = re.search(r"\{.*\}", clean_text, re.DOTALL)
        if json_match:
            clean_text = json_match.group(0)

        analysis = json.loads(clean_text)
    except Exception as e:
        print(f"⚠️ JSON Parsing Failed: {e}")
        analysis = {
            "comment": "Hmm, couldn't process this image properly. Try another one?",
            "scene": "Unknown",
            "objects": [],
            "mood": "Neutral",
            "tags": [],
            "safety_concerns": "parsing_error",
        }

    issues: List[str] = []
    raw_str = str(analysis).lower()

    # 1) keyword-based safety
    for pattern in DISALLOWED_PATTERNS:
        if pattern in raw_str:
            issues.append(pattern)

    # 2) heuristic: suggestive bed pose (woman/girl lying on bed)
    scene = analysis.get("scene", "").lower()
    tags = [t.lower() for t in analysis.get("tags", [])]
    objects = [str(o).lower() for o in analysis.get("objects", [])]
    joined_meta = " ".join([scene] + tags + objects)

    if (
        "bed" in scene
        and any(w in scene for w in ["lying", "reclining", "laying"])
        and any(w in joined_meta for w in ["woman", "girl", "female", "person"])
    ):
        issues.append("suggestive_pose")

    is_safe = len(issues) == 0
    analysis["safety_score"] = 100 if is_safe else 0

    # Memory type
    mem_type = "visual"
    if any(
        x in joined_meta for x in ["person", "people", "man", "woman", "girl", "boy"]
    ):
        mem_type = "relationship"
    elif any(x in scene for x in ["location", "place", "outdoor", "mountain", "city"]):
        mem_type = "location"

    return {
        "parsed_analysis": analysis,
        "is_safe": is_safe,
        "safety_issues": issues,
        "memory_type": mem_type,
    }


# ---------- Node: Save Memory ----------

async def node_save_memory(state: VisionState):
    if state["is_safe"]:
        print("💾 Saving visual memory")
        doc = {
            "user_id": state["user_id"],
            "image_url": state.get("image_url", ""),
            "type": "visual_memory",
            "memory_type": state["memory_type"],
            "description": state["parsed_analysis"].get("scene"),
            "luna_comment": state["parsed_analysis"].get("comment"),
            "mood": state["parsed_analysis"].get("mood"),
            "objects": state["parsed_analysis"].get("objects", []),
            "tags": state["parsed_analysis"].get("tags", []),
            "safety_score": state["parsed_analysis"].get("safety_score", 100),
            "timestamp": datetime.datetime.utcnow(),
        }
        visual_memory_collection.insert_one(doc)
        return {"status": "saved"}
    else:
        return {"status": "blocked"}


# ---------- Build Graph ----------

def route_safety(state: VisionState):
    return "save" if state["is_safe"] else "end"


workflow = StateGraph(VisionState)
workflow.add_node("see", node_analyze_image)
workflow.add_node("think", node_process_safety)
workflow.add_node("save", node_save_memory)

workflow.set_entry_point("see")
workflow.add_edge("see", "think")
workflow.add_conditional_edges("think", route_safety, {"save": "save", "end": END})
workflow.add_edge("save", END)

vision_agent = workflow.compile()
