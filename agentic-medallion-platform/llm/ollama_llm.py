"""
Ollama implementation of the BaseLLM interface.
"""

from langchain_ollama import ChatOllama

from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    TEMPERATURE,
)
from llm.base_llm import BaseLLM


class OllamaLLM(BaseLLM):
    """
    Concrete implementation of the BaseLLM interface using Ollama.
    """

    def __init__(self):
        self.llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=TEMPERATURE,
        )

    def invoke(self, prompt: str) -> str:
        """
        Execute a prompt using Ollama.

        Args:
            prompt: Prompt to send to the LLM.

        Returns:
            Model response as plain text.
        """
        response = self.llm.invoke(prompt)
        return response.content