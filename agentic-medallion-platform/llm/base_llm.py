from abc import ABC, abstractmethod

class BaseLLM(ABC):
    """
    Abstract base class for all LLM providers
    """

    @abstractmethod
    def invoke(self, prompt: str) -> str:
        """
        Execute a prompt and return the model response
        """
        pass
    