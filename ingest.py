from pypdf import PdfReader
from embeddings import EmbeddingModel
from vector_store_brute_force import VectorStore
from semantic_chunker import perform_semantic_chunking

# Load PDF
reader = PdfReader("data/sample.pdf")
text = ""

for page_num, page in enumerate(reader.pages):
    extracted = page.extract_text() or ""
    text += extracted + "\n"

# Semantic chunking
documents = perform_semantic_chunking(
    text,
    chunk_size=500,
    chunk_overlap=100
)

# Extract texts + metadata
chunks = [doc.page_content for doc in documents]
metadatas = [doc.metadata for doc in documents]

# Embed
embedder = EmbeddingModel()
embeddings = embedder.embed_texts(chunks)

# Create brute-force vector store
store = VectorStore()  # no dim needed

# Add embeddings + metadata
store.add(embeddings, chunks, metadatas)

print(f"✅ Ingestion complete! Stored {len(chunks)} semantic chunks, embedding dim = {embeddings.shape[1]}")
