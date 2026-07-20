from prompts.semantic_prompt import SEMANTIC_PROMPT
from prompts.summary_prompt import SUMMARY_PROMPT

class PromptManager:

    @staticmethod
    def semantic_prompt(**kwargs):
        return SEMANTIC_PROMPT.substitute(**kwargs)

    @staticmethod
    def summary_prompt(**kwargs):
        return SUMMARY_PROMPT.substitute(**kwargs)