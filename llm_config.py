"""
Shared OpenAI-compatible model configuration.
"""

import os

from langchain_openai import ChatOpenAI


def build_chat_model(temperature: float) -> ChatOpenAI:
    """Build the model configured for the current provider."""
    return ChatOpenAI(
        model=os.getenv("AI_MODEL", os.getenv("OPENROUTER_MODEL", "gpt-oss:20b")),
        openai_api_key=os.getenv("AI_API_KEY", os.getenv("OPENROUTER_API_KEY")),
        openai_api_base=os.getenv("AI_BASE_URL", "https://ollama.com/v1"),
        temperature=temperature,
    )
