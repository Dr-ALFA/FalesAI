"""
Image Suggester Tool
--------------------
Uses the configured OpenAI-compatible model to suggest relevant, meaningful images that complement
an essay topic. Returns structured image suggestions with descriptions
and search keywords.
"""

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
import json
import time

import requests

from llm_config import build_chat_model


def _commons_pages(query: str) -> list[dict]:
    response = requests.get(
        "https://commons.wikimedia.org/w/api.php",
        headers={"User-Agent": "FalesAI/1.0 (Palestine content image suggestions)"},
        params={
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrnamespace": "6",
            "gsrsearch": query,
            "gsrlimit": "4",
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": "960",
        },
        timeout=12,
    )
    response.raise_for_status()
    return list(response.json().get("query", {}).get("pages", {}).values())


def _search_commons_image(query: str, title: str = "") -> dict[str, str]:
    """Find a relevant Wikimedia Commons thumbnail for an image idea."""
    searches = [query]
    if title:
        searches.append(f"{title} {query}")
    searches.append(f"Palestine {query}")

    seen_urls = set()
    for search in searches:
        try:
            pages = _commons_pages(search)
        except requests.RequestException:
            continue
        for page in pages:
            page_title = str(page.get("title", "")).lower()
            image_info = page.get("imageinfo", [])
            if not image_info or any(term in page_title for term in ("map", "logo", "flag icon", "svg")):
                continue
            file_info = image_info[0]
            image_url = file_info.get("thumburl") or file_info.get("url", "")
            if not image_url or image_url in seen_urls:
                continue
            seen_urls.add(image_url)
            return {
                "image_url": image_url,
                "source_url": file_info.get("descriptionurl", ""),
                "commons_title": page.get("title", ""),
            }

    return {"image_url": "", "source_url": "", "commons_title": ""}


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
    llm = build_chat_model(temperature=0.6)

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
    - Real, concrete, and likely to exist as photographs or historical images in Wikimedia Commons
    - Searchable with English proper nouns, place names, landmarks, events, crafts, foods, archives, or landscapes
    - Emotionally resonant and visually compelling
    - Directly relevant to key essay sections
    - Diverse in subject matter (mix of historical, cultural, geographical, etc.)
    - Respectful and appropriate
    Avoid vague fantasy directions such as "at sunset", symbolic composites, generic suffering scenes,
    or images that would require generation rather than retrieval.
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
        img.update(_search_commons_image(keywords, img.get("title", "")))

    return json.dumps(suggestions, indent=2, ensure_ascii=False)
