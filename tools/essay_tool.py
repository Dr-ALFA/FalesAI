"""
Essay Writer Tool
-----------------
Uses OpenRouter (OpenAI-compatible) via LangChain to write a comprehensive,
well-researched essay on a given topic.
"""

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
import time

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _get_llm(temperature=0.7):
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=temperature,
        default_headers={"HTTP-Referer": "https://falesai.app", "X-Title": "FalesAI"},
    )


@tool
def essay_writer_tool(topic: str, word_count: int = 1500) -> str:
    """Write a comprehensive, well-researched essay on the given topic.

    Args:
        topic: The subject to write about.
        word_count: Approximate target word count (default 1500).

    Returns:
        A fully written essay in Markdown format with sections, headings,
        and rich detail.
    """
    llm = _get_llm(temperature=0.7)

    system_prompt = """You are an expert essay writer and researcher. 
    Write a comprehensive, well-structured essay with the following requirements:
    - Use clear markdown formatting with headers (##, ###)
    - Include an engaging introduction that hooks the reader
    - Organize the body into clearly themed sections
    - Support claims with historical context, facts, and analysis
    - Include a powerful conclusion
    - Maintain an academic yet accessible tone
    - Be factual, balanced, and informative
    - Write approximately {word_count} words
    - Use sub-headings to break up content
    - Include key dates, events, and figures where relevant
    """.format(word_count=word_count)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Write a comprehensive essay about: {topic}"),
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
