"""
Enterprise Local LLM Service (LM Studio)
"""

from openai import OpenAI


class LLMService:
    """
    Enterprise wrapper for LM Studio.
    """

    def __init__(self):

        self.client = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio",
            timeout=180,
        )

        self.model = "qwen2.5-7b-instruct"

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> str:

        print("=" * 80)
        print("CALLING LM STUDIO")
        print("=" * 80)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are IntelliICU, an AI Clinical Decision "
                        "Support Assistant. Answer ONLY using the provided "
                        "medical context. If the answer is not present in "
                        "the context, clearly state that you do not have "
                        "enough evidence."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        print("=" * 80)
        print("LM STUDIO RESPONDED")
        print("=" * 80)

        return response.choices[0].message.content.strip()