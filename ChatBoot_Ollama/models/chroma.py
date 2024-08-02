from langchain_community.vectorstores import Chroma
from utils.embeddings import get_embedding_function

CHROMA_PATH = r"C:\Users\luzo.neto\OneDrive - Sicoob\Meus Arquivos"

def add_to_chroma(chunks):
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Numeros de páginas no DB: {len(existing_ids)}")

    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]

    if new_chunks:
        print(f"Adicionandos: {len(new_chunks)} Documentos")
        db.add_documents(new_chunks, ids=[chunk.metadata["id"] for chunk in new_chunks])
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

        chunk.metadata["id"] = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

    return chunks
