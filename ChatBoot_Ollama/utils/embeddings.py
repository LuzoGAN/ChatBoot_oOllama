from langchain_community.embeddings.ollama import OllamaEmbeddings

def get_embedding_function():
    embeddings = OllamaEmbeddings(model='nomic-embed-text:latest', show_progress=True)
    return embeddings
