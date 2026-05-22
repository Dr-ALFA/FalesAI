"""
Multi-agent workflow for the Palestine content studio.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool

from llm_config import build_chat_model
from tools import content_organizer_tool, essay_writer_tool, image_suggester_tool


def _agent(name: str, instruction: str, tools: Sequence[BaseTool], temperature: float) -> Any:
    return create_agent(
        model=build_chat_model(temperature),
        tools=list(tools),
        name=name.lower().replace(" ", "_"),
        system_prompt=f"""You are {name} in a multi AI agentic content system.
{instruction}

You must use the provided tool before returning your answer.
Return the useful tool result as your final answer without narrating the workflow.""",
    )


def _step(agent_name: str, executor: Any, instruction: str) -> dict[str, Any]:
    result = executor.invoke({"messages": [{"role": "user", "content": instruction}]})
    tool_messages = [message for message in result["messages"] if isinstance(message, ToolMessage)]
    tool_message = tool_messages[-1] if tool_messages else result["messages"][-1]
    tool_output = str(tool_message.content)
    return {
        "agent": agent_name,
        "tool": getattr(tool_message, "name", None) or "no_tool_called",
        "input": instruction,
        "output": tool_output,
        "output_preview": tool_output[:900],
    }


def _notify(progress_callback: Callable[[str, str], None] | None, phase: str, message: str) -> None:
    if progress_callback:
        progress_callback(phase, message)


def run_orchestrator(
    topic: str,
    word_count: int = 1200,
    num_images: int = 6,
    article_language: str = "English",
    progress_callback: Callable[[str, str], None] | None = None,
) -> dict[str, Any]:
    """Run the three specialist agents and return their artifacts."""
    essay_agent = _agent(
        "Essay Writer Agent",
        "Write a factual, clear essay for the requested topic and target length.",
        [essay_writer_tool],
        temperature=0.5,
    )
    image_agent = _agent(
        "Image Curator Agent",
        "Suggest suitable, respectful images that support the essay topic.",
        [image_suggester_tool],
        temperature=0.4,
    )
    organizer_agent = _agent(
        "Content Organizer Agent",
        "Organize the essay and image suggestions into a clear user-facing Markdown document.",
        [content_organizer_tool],
        temperature=0.3,
    )

    _notify(progress_callback, "essay_started", "وكيل كتابة المقالة يكتب النص الأساسي.")
    essay_step = _step(
        "Essay Writer Agent",
        essay_agent,
        f"Write an essay about {topic} with approximately {word_count} words in {article_language}.",
    )
    _notify(progress_callback, "essay_done", "اكتملت مسودة المقالة.")

    _notify(progress_callback, "images_started", "وكيل الصور يبحث عن صور مناسبة لفقرات المقالة.")
    image_step = _step(
        "Image Curator Agent",
        image_agent,
        f"""Suggest {num_images} suitable images for this essay about {topic}.
Choose images that support specific passages, themes, places, or cultural details in the essay.

Essay:
{essay_step["output"]}""",
    )
    _notify(progress_callback, "images_done", "اكتمل اختيار الصور المناسبة.")

    _notify(progress_callback, "organizer_started", "وكيل تنظيم المحتوى ينسق النص والصور.")
    organizer_step = _step(
        "Content Organizer Agent",
        organizer_agent,
        f"""Organize this content for the user.

Essay:
{essay_step["output"]}

Image suggestions:
{image_step["output"]}

Final article language:
{article_language}""",
    )
    _notify(progress_callback, "organizer_done", "اكتملت النسخة النهائية للمقالة.")

    return {
        "essay": essay_step["output"],
        "images": image_step["output"],
        "final_document": organizer_step["output"],
        "article_language": article_language,
        "steps": [essay_step, image_step, organizer_step],
    }
