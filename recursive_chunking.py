import json
import re
from dataclasses import dataclass


@dataclass
class Document:
    page_content: str
    metadata: dict


def load_code_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# Language-aware separators
def get_language_separators(language):

    language = language.lower()

    if language == "python":
        return ["\nclass ", "\ndef ", "\n\n", "\n", " ", ""]
    elif language == "javascript":
        return ["\nclass ", "\nfunction ", "\n\n", "\n", " ", ""]
    elif language == "java":
        return ["\nclass ", "\npublic ", "\n\n", "\n", " ", ""]
    elif language == "go":
        return ["\nfunc ", "\n\n", "\n", " ", ""]
    elif language == "rust":
        return ["\nfn ", "\nimpl ", "\n\n", "\n", " ", ""]
    else:
        return ["\n\n", "\n", " ", ""]


def recursive_split(text, chunk_size, separators):

    if len(text) <= chunk_size:
        return [text.strip()]

    if not separators:
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    sep = separators[0]

    # fallback to hard split
    if sep == "":
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

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

    # recursively refine oversized chunks
    result = []
    for chunk in chunks:
        if len(chunk) > chunk_size:
            result.extend(
                recursive_split(chunk, chunk_size, separators[1:])
            )
        else:
            result.append(chunk)

    return result



def add_overlap(chunks, overlap):

    if overlap <= 0:
        return chunks

    overlapped = []

    for i, chunk in enumerate(chunks):

        if i == 0:
            overlapped.append(chunk)
        else:
            overlap_text = chunks[i-1][-overlap:]
            overlapped.append(overlap_text + chunk)

    return overlapped


def perform_code_chunking(
    code_document,
    language="python",
    chunk_size=1000,
    chunk_overlap=0
):

    separators = get_language_separators(language)

    chunks = recursive_split(code_document, chunk_size, separators)
    chunks = add_overlap(chunks, chunk_overlap)

    print(f"Code document split into {len(chunks)} chunks")

    documents = []

    for i, chunk in enumerate(chunks):

        function_match = re.search(
            r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            chunk
        )
        class_match = re.search(
            r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            chunk
        )
        import_match = re.search(
            r'import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
            chunk
        )

        chunk_type = "code_segment"

        if function_match:
            chunk_type = "function"
            structure_name = function_match.group(1)
        elif class_match:
            chunk_type = "class"
            structure_name = class_match.group(1)
        elif import_match:
            chunk_type = "import"
            structure_name = import_match.group(1)
        else:
            structure_name = f"segment_{i}"

        metadata = {
            "chunk_id": i,
            "language": language,
            "chunk_type": chunk_type,
            "structure_name": structure_name,
            "lines": chunk.count("\n") + 1
        }

        documents.append(Document(chunk, metadata))

    return documents


def save_to_json(documents, filename="recursive_code_chunks.json"):

    data = []

    for doc in documents:
        data.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "preview": doc.page_content[:120]
        })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Code chunks saved to {filename}")


if __name__ == "__main__":

    code_document = load_code_file("recursive_chunking.py")

    chunked_docs = perform_code_chunking(
        code_document,
        language="python",
        chunk_size=1000,
        chunk_overlap=0
    )

    save_to_json(chunked_docs)
