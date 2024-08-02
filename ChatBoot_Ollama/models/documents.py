from langchain.prompts import ChatPromptTemplate
from models.chroma import add_to_chroma
from utils.embeddings import get_embedding_function
import ollama
from app import socketio

PROMPT_TEMPLATE = """
Responda à pergunta como se fosse um gerente senior de uma cooperativa de crédito de forma clara e respeitosa, com base apenas no seguinte contexto:

{context}

---

Responda à pergunta como se fosse um gerente senior de uma cooperativa de crédito de forma clara e respeitosa, com base no contexto acima: {question}
"""

CHROMA_PATH = r"C:\Users\luzo.neto\OneDrive - Sicoob\Meus Arquivos"

def get_response_from_model(user_content: str):
    # Preparando DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Procurando no DB.
    results = db.similarity_search_with_score(user_content, k=3)

    # Preparando o contexto.
    context_text = "\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=user_content)

    sources = [doc.metadata.get("id", None) for doc, _score in results]

    stream = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': prompt}],
        stream=True,
    )

    response_text = ""
    for chunk in stream:
        response_chunk = chunk['message']['content']
        socketio.emit('response_chunk', {'data': response_chunk})
        response_text += response_chunk

    formatted_response = f"Response: {response_text}\nSources: {sources}"
