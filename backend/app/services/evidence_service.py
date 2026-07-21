"""
Evidence Service
Provides evidence sources supporting AI recommendations.
This is a placeholder until RAG integration.
"""


class EvidenceService:
    """
    Enterprise Evidence Retrieval Service.
    """

    @staticmethod
    def generate(patient_data: dict) -> list[dict]:
        """
        Returns evidence sources supporting the current recommendations.
        """

        return [
            {
                "title": "Surviving Sepsis Campaign 2024",
                "organization": "Society of Critical Care Medicine",
                "document_type": "Clinical Guideline",
                "page": 47,
                "relevance": 0.98,
                "summary": (
                    "Early recognition of sepsis, broad-spectrum antibiotics, "
                    "fluid resuscitation and lactate monitoring improve outcomes."
                ),
            },
            {
                "title": "WHO Sepsis Clinical Management",
                "organization": "World Health Organization",
                "document_type": "Clinical Guideline",
                "page": 18,
                "relevance": 0.95,
                "summary": (
                    "Patients with suspected sepsis require rapid assessment, "
                    "oxygen therapy and hemodynamic stabilization."
                ),
            },
        ]