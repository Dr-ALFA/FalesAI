"""
Orchestrator Agent
------------------
The master agent that coordinates the multi-agent workflow.
Uses OpenRouter API via LangChain's ChatOpenAI.
"""

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools.essay_tool import essay_writer_tool
from tools.image_tool import image_suggester_tool
from tools.organizer_tool import content_organizer_tool

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _build_agent() -> AgentExecutor:
    """Build the orchestrator agent with all tools."""
    llm = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=0.3,
        default_headers={"HTTP-Referer": "https://falesai.app", "X-Title": "FalesAI"},
    )

    tools = [essay_writer_tool, image_suggester_tool, content_organizer_tool]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior content production orchestrator managing a team of specialized AI agents.

Your mission is to produce a comprehensive, publication-ready document on any given topic.

You have access to three specialized tools:

1. **essay_writer_tool** — Writes a detailed, well-researched essay on the topic.
   Call this FIRST with the topic and desired word count.

2. **image_suggester_tool** — Suggests relevant images with descriptions and URLs.
   Call this SECOND with the topic.

3. **content_organizer_tool** — Takes the essay and image suggestions and produces
   a beautifully organized, polished final document.
   Call this LAST, passing the essay and image suggestions.

WORKFLOW (follow this exact order):
Step 1: Call essay_writer_tool with the topic
Step 2: Call image_suggester_tool with the topic
Step 3: Call content_organizer_tool with the essay from Step 1 and images from Step 2
Step 4: Return the final organized document from Step 3

IMPORTANT: 
- Always follow the 3-step workflow in order
- Pass the FULL output of Steps 1 and 2 to Step 3
- Return the complete final document from Step 3 as your final answer
"""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


def run_orchestrator(topic: str, word_count: int = 1500, progress_callback=None):
    """Run the full content production pipeline."""
    agent_executor = _build_agent()

    user_input = (
        f"Create a complete, publication-ready document about: {topic}. "
        f"The essay should be approximately {word_count} words. "
        f"Follow your 3-step workflow exactly."
    )

    if progress_callback:
        progress_callback("🚀 Orchestrator", "Starting the multi-agent pipeline...")

    result = agent_executor.invoke({"input": user_input})

    essay_text = ""
    image_data = ""
    steps_log = []

    for step in result.get("intermediate_steps", []):
        action, observation = step
        tool_name = action.tool
        steps_log.append({
            "tool": tool_name,
            "input": str(action.tool_input),
            "output_preview": str(observation)[:500] + "..." if len(str(observation)) > 500 else str(observation),
        })
        if tool_name == "essay_writer_tool":
            essay_text = observation
            if progress_callback:
                progress_callback("✍️ Essay Agent", "Essay written successfully!")
        elif tool_name == "image_suggester_tool":
            image_data = observation
            if progress_callback:
                progress_callback("🖼️ Image Agent", "Images curated successfully!")
        elif tool_name == "content_organizer_tool":
            if progress_callback:
                progress_callback("📐 Organizer Agent", "Content organized successfully!")

    return {
        "final_document": result.get("output", ""),
        "essay": essay_text,
        "images": image_data,
        "steps": steps_log,
    }
