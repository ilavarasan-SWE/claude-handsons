class LLMFactory:
    """
    Creates the configured LLM implementation.
    """

    @staticmethod
    def create():
        try:
            from llm.ollama_llm import OllamaLLM

            return OllamaLLM()
        except Exception:
            from llm.fallback_llm import FallbackLLM

            return FallbackLLM()

