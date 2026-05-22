"""
Image Suggester Tool
--------------------
Uses OpenRouter to suggest relevant, meaningful images that complement
an essay topic. Returns structured image suggestions with descriptions
and search keywords.
"""

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
import json
import time

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _get_llm(temperature=0.6):
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=temperature,
        default_headers={"HTTP-Referer": "https://falesai.app", "X-Title": "FalesAI"},
    )


def _search_unsplash_image(query: str) -> str | None:
    """Search for a free image URL using Unsplash Source (no API key needed)."""
    clean_query = query.replace(" ", ",")
    return f"https://source.unsplash.com/800x500/?{clean_query}"


@tool
def image_suggester_tool(topic: str, num_images: int = 6) -> str:
    """Suggest relevant images for an essay topic with descriptions and URLs.

    Args:
        topic: The essay topic to find images for.
        num_images: Number of images to suggest (default 6).

    Returns:
        A JSON string containing a list of image suggestions, each with
        title, description, search_keywords, category, and image_url.
    """
    llm = _get_llm(temperature=0.6)

    system_prompt = """You are an expert visual content curator. 
    For a given essay topic, suggest {n} powerful and relevant images that would 
    complement the written content.
    
    Return your response as a valid JSON array. Each object must have exactly these fields:
    - "title": short descriptive title for the image
    - "description": 2-3 sentence description of what the image should depict
    - "search_keywords": comma-separated keywords to search for this image
    - "category": one of ["Historical", "Cultural", "Geographic", "People", "Art", "Architecture", "Modern", "Nature", "Symbol"]
    - "placement_hint": which section of the essay this image fits best
    
    IMPORTANT: Return ONLY the JSON array, no markdown code fences, no extra text.
    Choose images that are:
    - Emotionally resonant and visually compelling
    - Directly relevant to key essay sections
    - Diverse in subject matter (mix of historical, cultural, geographical, etc.)
    - Respectful and appropriate
    """.format(n=num_images)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Suggest {num_images} images for an essay about: {topic}"),
    ]

    for attempt in range(3):
        try:
            response = llm.invoke(messages)
            break
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                time.sleep(30)
                continue
            raise
    raw = response.content.strip()

    # Clean up markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()

    # Parse and enrich with image URLs
    try:
        suggestions = json.loads(raw)
    except json.JSONDecodeError:
        return raw

    for img in suggestions:
        keywords = img.get("search_keywords", topic)
        img["image_url"] = _search_unsplash_image(keywords)

    return json.dumps(suggestions, indent=2, ensure_ascii=False)
