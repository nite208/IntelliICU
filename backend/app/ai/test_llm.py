"""
Test Local LLM
"""

from app.ai.llm_service import LLMService


def main():

    llm = LLMService()

    question = """
What is sepsis?
"""

    answer = llm.generate(question)

    print("=" * 80)
    print("LLM RESPONSE")
    print("=" * 80)
    print()
    print(answer)


if __name__ == "__main__":
    main()