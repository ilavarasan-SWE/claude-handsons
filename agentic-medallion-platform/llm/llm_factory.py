from llm.ollama_llm import OllamaLLM

class LLMFactory:
    """
    Creates the configured LLM implementation.
    """

    @staticmethod
    def create():
        return OllamaLLM()  # Currently, only OllamaLLM is supported.

