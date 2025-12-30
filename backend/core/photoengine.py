import os
import random
import asyncio
import urllib.parse
from google import genai

# Setup Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model_name = 'gemini-2.0-flash-exp'

# Intent keywords to extract what user actually wants
INTENT_KEYWORDS = {
    'shopping': ['clothes', 'shopping', 'market', 'bazaar', 'khareedna', 'dress', 'shirt', 'saree', 'kurti', 'kurta'],
    'wedding': ['wedding', 'marriage', 'ceremony', 'vivah', 'shaadi', 'bride', 'groom'],
    'food': ['khana', 'eat', 'restaurant', 'food', 'pizza', 'biryani', 'kheer'],
    'travel': ['travel', 'trip', 'destination', 'ghumna', 'beach', 'mountain', 'hill station'],
    'nature': ['nature', 'flower', 'garden', 'tree', 'sunset', 'sunrise'],
    'selfie': ['selfie', 'mujhe', 'myself', 'my photo', 'picture'],
}


def extract_user_intent(message: str) -> str:
    """Extract what user actually wants based on keywords"""

    message_lower = message.lower()

    # Check each intent category
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            return intent

    return 'general'


def enhance_prompt_by_intent(original_prompt: str, intent: str) -> str:
    """Enhance the prompt based on detected intent"""

    enhancement_map = {
        'shopping': "Generate a realistic, vibrant image of a clothing market or fashion store. Show colorful clothes, dresses, kurtas displayed. People shopping. Modern and stylish.",
        'wedding': "Generate a beautiful, elegant wedding ceremony image. Bride and groom in traditional attire. Festive, joyful atmosphere.",
        'food': "Generate a delicious-looking food image in a restaurant setting. Professional food photography style. Appetizing and colorful.",
        'travel': "Generate a beautiful travel destination image. Scenic, vacation-ready location. Mountains, beaches, or iconic landmarks.",
        'nature': "Generate a beautiful nature photograph. Fresh, scenic, peaceful landscape. Natural lighting.",
        'selfie': "Generate a beautiful portrait/selfie image. Professional photography quality. Attractive, well-lit, friendly expression.",
        'general': original_prompt
    }

    return enhancement_map.get(intent, original_prompt)


async def generate_smart_caption(prompt: str, mood: str, last_activity: str = None) -> str:
    """Generate context-aware caption for Luna's photo"""
    try:
        intent = extract_user_intent(prompt)

        caption_prompt = f"""
        You are Luna, an AI companion, sending a photo to your friend.
        Context: Last activity was "{last_activity or 'nothing specific'}"
        Photo intent: {intent.upper()}
        Photo request: "{prompt}"

        Write a 1-line casual Hinglish caption (max 10 words).
        Be natural, friendly, and conversational.
        NO EMOJIS.
        """

        response = client.models.generate_content(
            model=model_name,
            contents=caption_prompt
        )
        return response.text.strip().replace('"', '')
    except Exception as e:
        print(f"⚠️ Caption Error: {e}")
        return "Here you go!"


async def select_companion_photo(mood: str, prompt: str = None, last_activity: str = None) -> dict:
    """Generate or select a photo with smart caption - NOW WITH INTENT DETECTION"""

    # Backup collection (Unsplash photos) - only use if NO specific prompt
    base_url = "https://images.unsplash.com/photo-"
    collections = {
        "happy": ["1514888286974-6c03e2ca1dba", "1502920917128-1aa500764cbd"],
        "neutral": ["1509042239860-f550ce710b93", "1486312338219-ce68d2c6f44d"]
    }

    final_url = ""
    smart_caption = ""

    if prompt and len(prompt) > 5:
        # ✅ EXTRACT INTENT
        intent = extract_user_intent(prompt)

        # ✅ ENHANCE PROMPT BASED ON INTENT
        enhanced_prompt = enhance_prompt_by_intent(prompt, intent)

        # ✅ URL encode the ENHANCED prompt
        encoded_prompt = urllib.parse.quote(enhanced_prompt)

        # Generate image using Pollinations API
        seed = random.randint(1, 99999)
        final_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width=1024&height=1024&nologo=true&seed={seed}"
            "&model=flux-realism&enhance=true"
        )

        # Generate smart caption
        smart_caption = await generate_smart_caption(prompt, mood, last_activity)

        print(f"✅ Generated image for intent: {intent.upper()}")
        print(f"📸 Prompt used: {enhanced_prompt[:50]}...")

    else:
        # Fallback to Unsplash - only when no specific prompt
        selected_category = mood if mood in collections else "neutral"
        selected_id = random.choice(collections[selected_category])
        final_url = f"{base_url}{selected_id}?w=1024&q=90"
        smart_caption = "Here you go!"

    await asyncio.sleep(0.3)

    return {
        "url": final_url,
        "caption": smart_caption,
        "intent": intent if prompt and len(prompt) > 5 else "fallback"
    }
