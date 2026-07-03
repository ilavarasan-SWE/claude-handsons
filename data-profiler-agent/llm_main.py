from llm.ollama_client import get_llm

def main():

    llm = get_llm()


    prompt = input("Enter your prompt: ")

    response = llm.invoke(prompt)

    print("\n================== LLM Response ==================")
    print(response.content)

if __name__ == "__main__":
    main()