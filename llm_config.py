"""
Shared OpenAI-compatible model configuration.
"""

import os

from langchain_openai import ChatOpenAI


def _secret(name: str) -> str | None:
    """Read a Streamlit secret when the app runs on Streamlit Cloud."""
    try:
        import streamlit as st

        value = st.secrets.get(name)
    except (FileNotFoundError, RuntimeError):
        return None
    return str(value) if value else None


def _setting(name: str, default: str | None = None) -> str | None:
    return os.getenv(name) or _secret(name) or default


def has_chat_credentials() -> bool:
    """Return whether an API key is configured for the chat model."""
    return bool(_setting("AI_API_KEY") or _setting("OPENROUTER_API_KEY"))


def build_chat_model(temperature: float) -> ChatOpenAI:
    """Build the model configured for the current provider."""
    api_key = _setting("AI_API_KEY") or _setting("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing AI_API_KEY. Add it to .env locally or Streamlit Secrets when deployed."
        )

    return ChatOpenAI(
        model=_setting("AI_MODEL") or _setting("OPENROUTER_MODEL", "gpt-oss:20b"),
        openai_api_key=api_key,
        openai_api_base=_setting("AI_BASE_URL", "https://ollama.com/v1"),
        temperature=temperature,
    )
