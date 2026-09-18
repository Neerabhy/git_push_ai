# Project: RAG + Vector Search

This repository contains a lightweight retrieval-augmented generation (RAG) and vector search demo implemented in Python.

## Overview
- Ingest documents, create embeddings, and query a vector store to retrieve context for LLM prompts.
- Implements simple vector stores and utilities for experimentation.

## Key Files
- ingest.py — document ingestion pipeline
- embeddings.py — embedding helpers (adapter for embedding models)
- vector_store_faiss.py — FAISS-backed vector store implementation
- vector_store_brute_force.py — simple in-memory brute-force vector store
- semantic_chunker.py — text chunking utilities
- query.py — example query flow
- rag.py — orchestration for retrieval-augmented generation

## Getting Started
1. Create a virtual environment and install dependencies:

   pip install -r requirements.txt

2. Run the ingestion pipeline to build or update the vector store:

   python ingest.py

3. Query the collection:

   python query.py

## Notes
- This repo is a demo and not production hardened. Avoid using sensitive API keys in plaintext.
- Large binary artifacts and secrets are intentionally ignored.

## Development
- Tests and CI are not configured. Contributions are welcome — follow the existing code style.

