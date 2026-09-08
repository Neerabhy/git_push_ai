from dataclasses import dataclass


# Simple Document class
@dataclass
class Document:
    page_content: str
    metadata: dict


def load_document(file_path):
    """Load text file safely."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def perform_fixed_size_chunking(document, chunk_size=1000, chunk_overlap=200):

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    n = len(document)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = document[start:end]
        chunks.append(chunk)

        start += chunk_size - chunk_overlap

    print(f"Document split into {len(chunks)} chunks")

    documents = []
    for i, chunk in enumerate(chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk),
                    "chunk_type": "fixed-size",
                },
            )
        )

    return documents


def save_chunks_to_file(documents, output_file="chunks_output.txt"):
    """Optional: save chunks to inspect them."""
    with open(output_file, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(f"\n--- Chunk {doc.metadata['chunk_id']} ---\n")
            f.write(doc.page_content + "\n")


if __name__ == "__main__":

   
    document = load_document("book.txt")

    
    chunked_docs = perform_fixed_size_chunking(
        document,
        chunk_size=1000,
        chunk_overlap=200,
    )

    print("\n----- CHUNKING RESULTS -----")
    print(f"Total chunks: {len(chunked_docs)}")
    print("\nChunks saved to 'chunks_output.txt'")
