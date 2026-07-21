"""
Retriever Test
"""

from app.rag.retriever.retriever import Retriever


def main():

    retriever = Retriever()

    results = retriever.retrieve(
        "What is the recommended treatment for sepsis?",
        top_k=3,
    )

    print("=" * 80)
    print("TOP RETRIEVED DOCUMENTS")
    print("=" * 80)

    for i, result in enumerate(results, start=1):

        print(f"\nResult {i}")
        print("-" * 80)

        print("Title:")
        print(result["metadata"]["title"])

        print()

        print("Organization:")
        print(result["metadata"]["organization"])

        print()

        print("Page:")
        print(result["metadata"]["page"])

        print()

        print("Distance:")
        print(result["distance"])

        print()

        print("Content:")
        print(result["content"][:600])


if __name__ == "__main__":
    main()