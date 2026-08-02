from src.ingestion.arxiv_client import ArxivClient

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2312.00001v1</id>
    <published>2023-12-01T12:00:00Z</published>
    <title>Retrieval-Augmented Generation Survey</title>
    <summary>Abstract of the RAG survey paper.</summary>
    <author><name>Alice Smith</name></author>
    <category term="cs.CL"/>
  </entry>
</feed>
"""


def test_parse_feed():
    client = ArxivClient()
    papers = client.parse_feed(SAMPLE_XML)

    assert len(papers) == 1
    p = papers[0]
    assert p.id == "2312.00001"
    assert p.title == "Retrieval-Augmented Generation Survey"
    assert p.authors == ["Alice Smith"]
    assert p.categories == ["cs.CL"]
