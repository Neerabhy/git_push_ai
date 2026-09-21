import json
from dataclasses import dataclass, asdict


@dataclass
class Document:
    page_content: str
    metadata: dict


def load_document(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def perform_fixed_size_chunking(document, chunk_size=1000, chunk_overlap=200):

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    documents = []
    start = 0
    n = len(document)
    chunk_id = 0

    while start < n:
        end = min(start + chunk_size, n)

        chunk = document[start:end]

        metadata = {
            "chunk_id": chunk_id,
            "start_char": start,
            "end_char": end,
            "chunk_size": len(chunk),
            "overlap": chunk_overlap,
        }

        documents.append(Document(chunk, metadata))

        start += chunk_size - chunk_overlap
        chunk_id += 1

    print(f"Document split into {len(documents)} chunks")

    return documents


def save_chunks_to_json(documents, output_file="chunks.json"):

    json_data = []

    for doc in documents:
        entry = {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "preview": doc.page_content[:120]  # quick preview
        }
        json_data.append(entry)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"Chunks saved to {output_file}")


if __name__ == "__main__":

    document = load_document("book.txt")

    chunked_docs = perform_fixed_size_chunking(
        document,
        chunk_size=1000,
        chunk_overlap=200,
    )

    save_chunks_to_json(chunked_docs)
