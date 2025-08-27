from langchain_ollama import ChatOllama

# Configura tu modelo local
def get_local_llm():
    return ChatOllama(
        model="llama3.1",
        temperature=0.1
    )
