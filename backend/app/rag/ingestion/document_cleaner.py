"""
Document Cleaner
"""

import re


class DocumentCleaner:

    @staticmethod
    def clean(text: str) -> str:

        text = text.replace("\n", " ")

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()