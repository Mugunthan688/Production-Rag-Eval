import argparse
import sys
from pathlib import Path

# Add project root to sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion.arxiv_client import ArxivClient


def main():
    parser = argparse.ArgumentParser(description="Fetch papers metadata from arXiv API")
    parser.add_argument("--query", type=str, default='all:"retrieval augmented generation"')
    parser.add_argument("--max-results", type=int, default=10)
    args = parser.parse_args()

    client = ArxivClient()
    papers = client.fetch_papers(search_query=args.query, max_results=args.max_results)

    print(f"Fetched {len(papers)} papers from arXiv:")
    for idx, p in enumerate(papers, 1):
        print(f"{idx}. [{p.id}] {p.title} ({p.submitted_date.strftime('%Y-%m-%d')})")
        print(f"   Authors: {', '.join(p.authors[:3])}")
        print(f"   Abstract sample: {p.abstract[:120]}...\n")


if __name__ == "__main__":
    main()
