"""
Test Enterprise RAG Pipeline
"""

from app.ai.clinical_assistant import ClinicalAssistant


def main():

    assistant = ClinicalAssistant()

    question = (
        "Should broad-spectrum antibiotics be started "
        "within one hour in septic shock?"
    )

    result = assistant.ask(question)

    print("=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(result["question"])

    print()

    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(result["answer"])

    print()

    print("=" * 80)
    print("SOURCES")
    print("=" * 80)

    for index, source in enumerate(result["sources"], start=1):

        print(f"\nSource {index}")

        print(
            f"Document : {source.get('title', 'Unknown')}"
        )

        print(
            f"Page     : {source.get('page', '-')}"
        )

        print(
            f"Organization : {source.get('organization', '-')}"
        )


if __name__ == "__main__":
    main()