"""
Embedding Test
"""

from app.rag.embeddings.embedding_service import EmbeddingService


texts = [
    "Patient has septic shock.",
    "Early antibiotics reduce mortality.",
]

embeddings = EmbeddingService.encode(texts)

print()

print("=" * 80)

print("Embedding Shape")

print("=" * 80)

print(embeddings.shape)