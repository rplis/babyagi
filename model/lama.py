"""Llama Embedding Function"""
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings


class LlamaEmbeddingFunction(EmbeddingFunction):
    """Llama Embedding Function"""

    def __init__(self):
        return

    def __call__(self, texts: Documents) -> Embeddings:
        embeddings = []
        for t in texts:
            e = llm_embed.embed(t)
            embeddings.append(e)
        return embeddings
