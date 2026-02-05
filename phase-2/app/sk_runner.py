from __future__ import annotations

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.ollama.ollama_prompt_execution_settings import (
    OllamaChatPromptExecutionSettings,
)

from app.sk_plugins.manager_tools import ManagerToolsPlugin


async def run_sk(message: str, tools: ManagerToolsPlugin) -> str:
    """
    Uses Semantic Kernel with Ollama + automatic function calling.
    The model decides when to call tools.
    """
    kernel = Kernel()

    # Ollama connector (endpoint + model)
    # Example import style used in SK Ollama examples. :contentReference[oaicite:3]{index=3}
    chat_service = OllamaChatCompletion(
        service_id="ollama",
        ai_model_id="qwen2.5:7b-instruct",
        host="http://127.0.0.1:11434",
    )
    kernel.add_service(chat_service)

    # Add our tools plugin
    kernel.add_plugin(tools, plugin_name="ManagerTools")

    # Enable auto tool calling
    settings = OllamaChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    history = ChatHistory()
    history.add_system_message(
        "You are a manager assistant. "
        "Use tools when needed: create tasks, list tasks, answer policy questions using RAG. "
        "If no tool is needed, reply normally."
    )
    history.add_user_message(message)

    # Ask the model (it can auto-call functions/tools)
    result = await chat_service.get_chat_message_content(chat_history=history, settings=settings, kernel=kernel)
    return str(result)
