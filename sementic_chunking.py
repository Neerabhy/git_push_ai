import json
import re
from dataclasses import dataclass


@dataclass
class Document:
    page_content: str
    metadata: dict


def load_document(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# Recursive splitter (NO overlap inside recursion)
def recursive_split(text, chunk_size, separators):

    # allow if chunk is less then chunk size as small para can have diff content and don't need other text.
    if len(text) <= chunk_size:
        return [text]

    for sep in separators:

        if sep == "":
            break

        parts = text.split(sep)

        chunks = []
        current = parts[0]

        for part in parts[1:]:

            # try merging adjacent parts instead of rebuilding prefixes
            candidate = current + sep + part

            if len(candidate) <= chunk_size:
                current = candidate
            else:
                chunks.append(current.strip())  # It removes whitespace from the beginning and end of a string.
                current = part

        if current:
            chunks.append(current.strip())

        # If splitting worked reasonably, recurse
        if all(len(c) <= chunk_size * 1.5 for c in chunks):

            final_chunks = []

            for chunk in chunks:

                # make sure that hard limit of chunk size doesn't exeed
                if len(chunk) > chunk_size:
                    final_chunks.extend(
                        recursive_split(chunk, chunk_size, separators[1:])
                    )
                else:
                    final_chunks.append(chunk)

            return final_chunks

        # else:
        # “This separator didn’t work. Try a smaller one.”

    # fallback: hard split
    # what if we don't have seprators to seprate word by word it just seprate by para or page then chunk would exeeed
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


# Overlap applied ONLY once after recursion
def add_overlap(chunks, overlap):

    if overlap <= 0:
        return chunks

    overlapped = []

    for i, chunk in enumerate(chunks):

        if i == 0:
            overlapped.append(chunk)
        else:
            # use original chunks to prevent overlap explosion
            prev = chunks[i-1]
            overlap_text = prev[-overlap:]
            overlapped.append(overlap_text + chunk)

    return overlapped


def perform_semantic_chunking(document, chunk_size=500, chunk_overlap=100):

    separators = ["\n\n", "\n", ". ", " ", ""]

    # first get clean base chunks (no overlap here)
    base_chunks = recursive_split(
        document,
        chunk_size,
        separators
    )

    # apply overlap once
    semantic_chunks = add_overlap(base_chunks, chunk_overlap)

    print(f"Document split into {len(semantic_chunks)} semantic chunks")

    section_patterns = [
        r'^#+\s+(.+)$',
        r'^.+\n[=\-]{2,}$',
        r'^[A-Z\s]+:$'
    ]

    documents = []
    current_section = "Introduction"

    for i, chunk in enumerate(semantic_chunks):

        for line in chunk.split("\n"):
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    current_section = match.group(0)

        words = re.findall(r'\b\w+\b', chunk.lower())
        stopwords = {'the','and','is','of','to','a','in','that','it','with','as','for'}
        content_words = [w for w in words if w not in stopwords]

        semantic_density = len(content_words) / max(1, len(words))

        metadata = {
            "chunk_id": i,
            "chunk_type": "semantic",
            "chunk_size": len(chunk),
            "section": current_section,
            "semantic_density": round(semantic_density, 2)
        }

        documents.append(Document(chunk, metadata))

    return documents


def save_to_json(documents, filename="semantic_chunks.json"):

    data = []

    for doc in documents:
        data.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "preview": doc.page_content[:120]
        })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Semantic chunks saved to {filename}")


if __name__ == "__main__":

    document = load_document("book.txt")

    chunked_docs = perform_semantic_chunking(
        document,
        chunk_size=500,
        chunk_overlap=100
    )

    save_to_json(chunked_docs)
