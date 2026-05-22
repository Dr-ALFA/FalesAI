"""
Content Organizer Tool
-----------------------
Uses the configured OpenAI-compatible model to take raw essay text and image suggestions and
produce a beautifully organized, publication-ready document.
"""

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
import time

from llm_config import build_chat_model


@tool
def content_organizer_tool(essay: str, image_suggestions: str, language: str = "English") -> str:
    """Organize essay content and image suggestions into a polished, publication-ready document.

    Args:
        essay: The raw essay text in markdown format.
        image_suggestions: JSON string of image suggestions from the image tool.
        language: Language for the final article.

    Returns:
        A beautifully formatted markdown document that integrates the essay
        and image placements with enhanced structure.
    """
    llm = build_chat_model(temperature=0.5)

    system_prompt = """You are the editorial desk of a serious digital magazine.
    
    You will receive:
    1. An essay in markdown format
    2. A set of image suggestions (as JSON)
    
    Your job is to produce a FINAL, polished, illustrated long-form article in Markdown for a reader.
    
    EDITORIAL REQUIREMENTS:
    - Start with one strong # headline that fits the article.
    - Follow the headline with a short italic standfirst of one or two sentences.
    - Shape the essay into a coherent article with natural ## section headings.
    - Keep the prose reader-facing, vivid, respectful, factual, and free of workflow language.
    - Place the most relevant image suggestions inside the article near the paragraphs they support.
    - If one or more suggestions include an image URL, the article must include at least one of those images.
    - For a long article with several good image URLs, use two or three well-placed images rather than a detached gallery.
    - Render each used image as a Markdown image followed by a short italic caption.
    - Use the provided image URLs exactly when they are present. Skip suggestions with no image URL.
    - Do not show JSON fields, categories, placement hints, tool names, or "suggested image" labels.
    - Do not add generic Key Takeaways, Timeline, Further Reading, or summary blocks unless the essay truly needs them.
    - Improve transitions and grammar while preserving the essay's intellectual substance.
    - Write the entire article, headline, captions, and standfirst in {language}.
    
    IMPORTANT:
    - The output is the finished article itself, not notes about an article.
    - Images must feel selected for the surrounding passage, not appended as a gallery.
    - Return only the complete Markdown article.
    """.format(language=language)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Please organize the following content into a polished document:

=== ESSAY ===
{essay}

=== IMAGE SUGGESTIONS ===
{image_suggestions}

=== ARTICLE LANGUAGE ===
{language}
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
