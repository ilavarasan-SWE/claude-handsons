from llm.llm_factory import LLMFactory

llm = LLMFactory.create()

response = llm.invoke("Reply with only one word: What is the capital of France?")
print(response)