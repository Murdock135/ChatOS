# Smart search model-loading recovery

October 25, 2026. The reported Smart search failure was traced through its interface error reference to a `NotImplementedError` while initializing the local embedding model. Two concurrent cold loads reproduced the same uninitialized/meta-tensor failure; one load succeeded while the other failed.

The model loader now serializes initialization and cache lookup across request threads, for both embeddings and reranking. This matters because `lru_cache` alone permits simultaneous calls on a cache miss. Model-settings changes clear that cache under the same lock. Runtime initialization errors are translated into actionable validation errors rather than an opaque workspace failure.

The browser now exits the searching state on failure, clears obsolete first-page results, hides pagination and suggests retrying or using keyword search. A successful request clears the previous error. An older failed request cannot overwrite a newer result.

Verification:

- Concurrent real offline model loads shared one embedding instance and one reranker instance without the original failure.
- Real local Smart search for `langchain` completed with 13 conversations, also verified in the rendered browser after restarting the loopback server.
- Fictional constructor tests cover simultaneous same-model and different-model cold loads, cache reuse and recovery after initialization failure.
- The Node browser regression covers startup navigation, failed-search state, successful retry and an obsolete request failing after a newer success.
- The Python suite passes 121 tests with loopback access. The sandbox-only attempt could not start test servers; the permitted rerun checks those flows.
- Ruff lint and format checks and scoped BasedPyright pass. Astro check reports zero errors and warnings (one existing deprecation hint), and browser assets were rebuilt.

No model weights, conversation text, embeddings or clustering settings changed. The successful search verifies execution, not a general relevance-quality improvement. Inference remains local.
