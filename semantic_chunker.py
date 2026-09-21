import re
from dataclasses import dataclass
#updated

@dataclass
class Document:
    page_content: str
    metadata: dict


def recursive_split(text, chunk_size, separators):

    if len(text) <= chunk_size:
        return [text]

    for sep in separators:

        if sep == "":
            break

        parts = text.split(sep)

        chunks = []
        current = parts[0]

        for part in parts[1:]:

            candidate = current + sep + part

            if len(candidate) <= chunk_size:
                current = candidate
            else:
                chunks.append(current.strip())
                current = part

        if current:
            chunks.append(current.strip())

        if all(len(c) <= chunk_size * 1.5 for c in chunks):

            final_chunks = []

            for chunk in chunks:

                if len(chunk) > chunk_size:
                    final_chunks.extend(
                        recursive_split(chunk, chunk_size, separators[1:])
                    )
                else:
                    final_chunks.append(chunk)

            return final_chunks


    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]


def add_overlap(chunks, overlap):

    if overlap <= 0:
        return chunks

    overlapped = []

    for i, chunk in enumerate(chunks):

        if i == 0:
            overlapped.append(chunk)
        else:
            prev = chunks[i - 1]
            overlap_text = prev[-overlap:]
            overlapped.append(overlap_text + chunk)

    return overlapped


def perform_semantic_chunking(document, chunk_size=500, chunk_overlap=100):

    separators = ["\n\n", "\n", ". ", " ", ""]

    base_chunks = recursive_split(
        document,
        chunk_size,
        separators
    )

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
        stopwords = {
            'the', 'and', 'is', 'of', 'to',
            'a', 'in', 'that', 'it', 'with',
            'as'
        }

        content_words = [
            w for w in words if w not in stopwords
        ]

        semantic_density = len(content_words) / max(1, len(words))

        metadata = {
            "chunk_id": i,
            "chunk_type": "semantic",
            "chunk_size": len(chunk),
            "section": current_section,
            "semantic_density": round(semantic_density, 2)
        }

        documents.append(
            Document(chunk, metadata)
        )

    return documents
