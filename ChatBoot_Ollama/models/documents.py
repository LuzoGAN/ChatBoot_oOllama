import os
import concurrent.futures
import pandas as pd
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.vectorstores import Chroma
import ollama
from langchain_community.embeddings.ollama import OllamaEmbeddings
from utils import send_response_to_user

CHROMA_PATH = r"C:\Users\luzo.neto\OneDrive - Sicoob\Meus Arquivos"
DATA_PATH = r"C:\Users\luzo.neto\OneDrive - Sicoob\Documentos\Regulamento CNV"
EXCEL_PATH = r"C:\Users\luzo.neto\OneDrive - Sicoob\Meus Arquivos\historico_perguntas_respostas.xlsx"

PROMPT_TEMPLATE = """
Responda à pergunta como se fosse um gerente senior de uma cooperativa de crédito de forma clara e respeitosa, com base apenas no seguinte contexto:

{context}

---

Responda à pergunta como se fosse um gerente senior de uma cooperativa de crédito de forma clara e respeitosa, com base no contexto acima: {question}
"""

def get_embedding_function():
    embeddings = OllamaEmbeddings(model='nomic-embed-text:latest', show_progress=True)
    return embeddings

def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=120,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: list[Document]):
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Numeros de páginas no DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adicionandos: {len(new_chunks)} Documentos")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("Nada para Atualizar")

def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id

    return chunks

def process_documents(documents):
    chunks = split_documents(documents)
    add_to_chroma(chunks)

def main():
    documents = load_documents()
    chunk_limit = 165

    while documents:
        chunk_batch = documents[:chunk_limit]
        documents = documents[chunk_limit:]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(process_documents, chunk_batch)

def save_to_excel(question: str, answer: str):
    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)
    else:
        df = pd.DataFrame(columns=["Pergunta", "Resposta"])

    new_entry = pd.DataFrame({"Pergunta": [question], "Resposta": [answer]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)

def get_response_from_model(user_content: str, user_id: str):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_score(user_content, k=3)

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
        send_response_to_user(user_id, response_chunk)
        response_text += response_chunk

    formatted_response = f"Response: {response_text}\nSources: {sources}"
