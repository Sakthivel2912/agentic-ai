# Research Brief: Retrieval-Augmented Generation Architectures

## Document Metadata

- Topic: RAG architecture for enterprise applications
- Evidence type: Research brief and implementation checklist
- Prepared for: AI Council
- Source links:
  - https://python.langchain.com/docs/concepts/retrieval/
  - https://docs.pinecone.io/guides/get-started/overview
  - https://www.sbert.net/

## Executive Summary

Retrieval-Augmented Generation (RAG) combines a language model with an external retrieval system. A typical pipeline ingests documents, splits them into chunks, creates vector embeddings, stores those vectors, retrieves relevant chunks for a question, and supplies the retrieved context to the language model.

For enterprise systems, the retrieval boundary should enforce tenant or user ownership before context is sent to an agent. Retrieval quality depends on chunking, metadata, embedding choice, query formulation, ranking, and evaluation. A vector database is not a substitute for source attribution or access control.

## Core Pipeline

1. Load a document and preserve its filename and metadata.
2. Extract text and page or section information when available.
3. Split text into bounded chunks with useful overlap.
4. Generate embeddings using a consistent embedding model.
5. Store vectors with document, user, chunk, and source metadata.
6. Embed the user question.
7. Filter retrieval by the authenticated user or tenant.
8. Retrieve a limited number of relevant chunks.
9. Provide the chunks to the model with explicit source labels.
10. Evaluate retrieval relevance and answer grounding.

## Enterprise Design Considerations

- Access control must be applied during retrieval, not only in the UI.
- Metadata should include document id, user id, filename, chunk id, and page number when available.
- Chunk size should be tested against the domain and model context window.
- Hybrid keyword and vector retrieval can help with identifiers, product names, and exact terminology.
- Reranking may improve precision when the initial candidate set is large.
- Empty retrieval results should be reported clearly; the system must not fabricate private context.
- Every generated claim should be traceable to retrieved evidence or labeled as inference.

## Evaluation Checklist

- Recall of relevant chunks
- Precision of top-k results
- Source coverage in the final answer
- Unsupported-claim rate
- Latency from query to context
- Behavior when no document is relevant
- Isolation between users or tenants

## Application Relevance

AI Council should use this flow for `enable_rag=true`. The future implementation should persist ingestion status in SQLite, index chunks in Pinecone, filter by `user_id`, and expose source metadata to the reviewer and synthesizer agents.
