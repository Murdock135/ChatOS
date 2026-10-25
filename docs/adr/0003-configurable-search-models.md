# 0003 — Configurable local search and assistant review

Date: 2026-10-24. Status: adopted.

The user requested local hybrid search with a reranker and a way for the Chief of Staff to perform relevance review, with user-selected downloadable models.

The library offers keyword and local hybrid search in one conversation list. Local search combines lexical and embedding candidates before scalar CrossEncoder reranking. Model settings and downloaded commit manifests identify the embedding cache; token limits and prompts are configurable. Public Hugging Face IDs are accepted for compatible Sentence Transformers and CrossEncoder models. Custom executable model code and pickle weights are unsupported. Downloading is an explicit action; inference loads local data.

Assistant review uses a local request packet with the query, scope, inventory and candidate excerpts. The existing assistant inspects captured sources and writes ordered results with exact message evidence. The app validates excerpts and current scope before showing reviewed results. Preparing a packet does not invoke an assistant or transmit private content.
