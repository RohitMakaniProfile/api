import datetime
import os
import json
from typing import TypedDict, Optional, List, Dict, Any

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from database import conversations_collection, visual_memory_collection
from core.personality import LUNA_SYSTEM_PROMPT
from core.photoengine import select_companion_photo


# ---------- Agent State ----------

class AgentState(TypedDict):
    user_id: str
    user_message: str
    image_analysis: Optional[dict]
    intent: str
    mood: str
    photo_subject: Optional[str]
    context_summary: str
    chat_history: List[dict]
    final_response: str
    photo_url: Optional[str]
    last_ai_activity: Optional[str]


# ---------- LLM Setup ----------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7,
    max_retries=3,
)


# ---------- Nodes ----------

async def node_retrieve_context(state: AgentState) -> Dict[str, Any]:
    print(f"🧠 Retrieving context for {state['user_id']}")
    user_id = state["user_id"]

    try:
        history_cursor = (
            conversations_collection
            .find({"user_id": user_id})
            .sort("timestamp", 1)
            .limit(30)
        )
        history_docs = list(history_cursor)

        mem_cursor = (
            visual_memory_collection
            .find({"user_id": user_id})
            .sort("timestamp", -1)
            .limit(5)
        )
        memories = list(mem_cursor)

        context_str = ""
        if memories:
            context_str += "\n\nRecent Visual Memories:\n"
            for mem in memories:
                desc = mem.get("description", "unknown image")
                context_str += f"- {desc}\n"

        last_activity = None
        if history_docs:
            for msg in reversed(history_docs):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "").lower()
                    if any(word in content for word in ["work", "laptop", "code"]):
                        last_activity = "working on laptop"
                    elif any(word in content for word in ["eat", "food", "dinner"]):
                        last_activity = "eating"
                    break

        return {
            "context_summary": context_str,
            "chat_history": history_docs,
            "last_ai_activity": last_activity,
        }
    except Exception as e:
        print(f"❌ Context Error: {e}")
        return {
            "context_summary": "",
            "chat_history": [],
            "last_ai_activity": None,
        }


async def node_analyze_intent(state: AgentState) -> Dict[str, Any]:
    print("🔍 Analyzing intent (history-aware)")

    # default: current message ko subject maan lo
    subject = state["user_message"]

    # generic triggers: "generate an image", "now generate your image", etc.
    generic_triggers = [
        "generate an image",
        "generate your image",
        "generate image",
        "photo banao",
        "ab image banao",
        "now generate an image",
    ]

    lower_msg = state["user_message"].lower()

    if any(t in lower_msg for t in generic_triggers):
        # agar message generic hai, last assistant ka descriptive reply use karo
        last_ai = None
        for msg in reversed(state.get("chat_history", [])):
            if msg.get("role") == "assistant":
                last_ai = msg.get("content", "")
                break
        if last_ai:
            subject = last_ai

    return {
        "intent": state["intent"],        # intent process_message se aaya
        "mood": "neutral",
        "photo_subject": subject,         # yehi prompt jayega photoengine ko
    }


async def node_select_photo(state: AgentState) -> Dict[str, Any]:
    print("📸 Selecting/Generating photo")
    query = state.get("photo_subject") or state["user_message"]

    try:
        photo_data = await select_companion_photo(
            state.get("mood", "happy"),
            query,
            last_activity=state.get("last_ai_activity"),
        )

        return {
            "photo_url": photo_data["url"],
            "final_response": photo_data["caption"],
        }
    except Exception as e:
        print(f"❌ Photo Error: {e}")
        return {
            "photo_url": None,
            "final_response": "Can't send photo right now, but I'm here!",
        }


async def node_generate_reply(state: AgentState) -> Dict[str, Any]:
    print("💬 Generating chat reply")

    if state.get("final_response"):
        return {"final_response": state["final_response"]}

    try:
        full_system_prompt = LUNA_SYSTEM_PROMPT + state.get("context_summary", "")
        messages: List[Any] = [SystemMessage(content=full_system_prompt)]

        for doc in state.get("chat_history", []):
            role = doc.get("role")
            content = doc.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))

        current_content = state["user_message"]
        if state.get("image_analysis"):
            current_content += (
                "\n[User shared an image: "
                f"{state['image_analysis'].get('description', '')}]"
            )

        messages.append(HumanMessage(content=current_content))
        response = await llm.ainvoke(messages)

        return {"final_response": response.content}
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return {
            "final_response": "Having connection issues! Let me reconnect... 🌙"
        }


async def node_save_interaction(state: AgentState) -> Dict[str, Any]:
    print("💾 Saving to local storage")
    user_id = state["user_id"]
    timestamp = datetime.datetime.utcnow()

    conversations_collection.insert_one(
        {
            "user_id": user_id,
            "role": "user",
            "content": state["user_message"],
            "timestamp": timestamp,
        }
    )

    conversations_collection.insert_one(
        {
            "user_id": user_id,
            "role": "assistant",
            "content": state["final_response"],
            "photo_sent": state.get("photo_url"),
            "timestamp": timestamp,
        }
    )

    return {
        "last_ai_activity": state.get("last_ai_activity")
    }


# ---------- Graph Build ----------

workflow = StateGraph(AgentState)

workflow.add_node("retrieve", node_retrieve_context)
workflow.add_node("analyze", node_analyze_intent)
workflow.add_node("photo", node_select_photo)
workflow.add_node("chat", node_generate_reply)
workflow.add_node("save", node_save_interaction)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "analyze")


def route_intent(state: AgentState) -> str:
    return "photo" if state["intent"] == "photo" else "chat"


workflow.add_conditional_edges(
    "analyze",
    route_intent,
    {"photo": "photo", "chat": "chat"},
)
workflow.add_edge("photo", "save")
workflow.add_edge("chat", "save")
workflow.add_edge("save", END)

graph = workflow.compile()


# ---------- Wrapper ----------

class LunaAgentWrapper:
    def __init__(self, graph):
        self.graph = graph

    async def process_message(
        self,
        user_id: str,
        message: str,
        image_analysis: Optional[dict] = None,
        history: Optional[List[dict]] = None,
    ) -> Dict[str, Any]:
        user_id = user_id or "anonymous"
        message = message or ""

        lower = message.lower()
        intent = "chat"

        photo_keywords = ["photo", "image", "dikhao", "picture", "pic"]
        soft_triggers = ["generate", "accordingly", "like this", "aisa hi", "same jaisa"]

        # 1) Direct, clear photo request → always photo
        if any(w in lower for w in photo_keywords):
            intent = "photo"

        # 2) Soft “generate accordingly” type + recent visual context → photo
        elif any(t in lower for t in soft_triggers):
            recent_text = " ".join(
                (m.get("content", "").lower() for m in (history or [])[-4:])
            )
            if any(
                w in recent_text
                for w in ["photo", "image", "market", "temple", "scene", "classroom", "sunset"]
            ):
                intent = "photo"

        # warna chat hi rahega

        initial_state: AgentState = {
            "user_id": user_id,
            "user_message": message,
            "image_analysis": image_analysis,
            "chat_history": history or [],
            "intent": intent,
            "mood": "neutral",
            "photo_subject": None,
            "context_summary": "",
            "final_response": "",
            "photo_url": None,
            "last_ai_activity": None,
        }

        print("INITIAL INTENT:", intent)
        result = await self.graph.ainvoke(initial_state)
        print("Luna graph result:", result)

        return {
            "reply": result.get("final_response"),
            "photo_url": result.get("photo_url"),
        }



luna_agent = LunaAgentWrapper(graph)
