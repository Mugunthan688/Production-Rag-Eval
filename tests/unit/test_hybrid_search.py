from src.retrieval.hybrid import reciprocal_rank_fusion
from src.db.models import ChunkORM


def test_reciprocal_rank_fusion():
    c1 = ChunkORM(id="c1", paper_id="p1", chunk_index=0, text="t1", chunking_strategy="fixed")
    c2 = ChunkORM(id="c2", paper_id="p2", chunk_index=0, text="t2", chunking_strategy="fixed")

    dense = [(c1, 0.9), (c2, 0.8)]
    sparse = [(c2, 10.0), (c1, 5.0)]

    fused = reciprocal_rank_fusion(dense, sparse, top_k=2)

    assert len(fused) == 2
    # c2 ranked #2 in dense, #1 in sparse -> higher fused RRF score than c1
    assert fused[0][0].id == "c2"
