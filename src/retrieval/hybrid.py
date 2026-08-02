from typing import List, Tuple, Dict
from ..db.models import ChunkORM


def reciprocal_rank_fusion(
    dense_results: List[Tuple[ChunkORM, float]],
    sparse_results: List[Tuple[ChunkORM, float]],
    c: int = 60,
    top_k: int = 20,
) -> List[Tuple[ChunkORM, float]]:
    """Combines dense vector search & BM25 sparse search using Reciprocal Rank Fusion (RRF)."""
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, ChunkORM] = {}

    # Process dense results
    for rank, (chunk, score) in enumerate(dense_results):
        chunk_map[chunk.id] = chunk
        scores[chunk.id] = scores.get(chunk.id, 0.0) + (1.0 / (c + rank + 1))

    # Process sparse results
    for rank, (chunk, score) in enumerate(sparse_results):
        chunk_map[chunk.id] = chunk
        scores[chunk.id] = scores.get(chunk.id, 0.0) + (1.0 / (c + rank + 1))

    # Sort combined scores
    sorted_chunk_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

    return [(chunk_map[cid], scores[cid]) for cid in sorted_chunk_ids[:top_k]]
