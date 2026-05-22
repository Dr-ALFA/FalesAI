"""
Content Organizer Tool
-----------------------
Uses OpenRouter to take raw essay text and image suggestions and
produce a beautifully organized, publication-ready document.
"""

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
import time

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _get_llm(temperature=0.5):
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=temperature,
        default_headers={"HTTP-Referer": "https://falesai.app", "X-Title": "FalesAI"},
    )


@tool
def content_organizer_tool(essay: str, image_suggestions: str) -> str:
    """Organize essay content and image suggestions into a polished, publication-ready document.

    Args:
        essay: The raw essay text in markdown format.
        image_suggestions: JSON string of image suggestions from the image tool.

    Returns:
        A beautifully formatted markdown document that integrates the essay
        and image placements with enhanced structure.
    """
    llm = _get_llm(temperature=0.5)

    system_prompt = """You are an expert content editor and document organizer.
    
    You will receive:
    1. An essay in markdown format
    2. A set of image suggestions (as JSON)
    
    Your job is to produce a FINAL, polished, publication-ready markdown document that:
    
    FORMAT REQUIREMENTS:
    - Starts with a compelling title using # heading
    - Has a brief abstract/summary at the top (2-3 sentences, italicized)
    - Uses clear section hierarchy (##, ###)
    - Integrates image placement markers in the appropriate sections
    - For each image, use this exact format:
      
      📷 **[Image Title]**
      *[Image Description]*
      `Category: [category] | Suggested placement: [section]`
      ![Image](IMAGE_URL)
      
    - Adds a "Key Takeaways" or "Summary Points" section with bullet points
    - Includes a "Timeline of Key Events" section if applicable
    - Adds a "Further Reading" section at the end
    - Ensures smooth transitions between sections
    - Fixes any grammar or style issues in the original essay
    
    IMPORTANT: Preserve the intellectual depth and factual accuracy of the original essay.
    Enhance the formatting and organization, do NOT remove content.
    Return the complete organized document.
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Please organize the following content into a polished document:

=== ESSAY ===
{essay}

=== IMAGE SUGGESTIONS ===
{image_suggestions}
"""),
    ]

    for attempt in range(3):
        try:
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                time.sleep(30)
                continue
            raise
