"""
app/rag/document.py

Clinical document schema for the RAG knowledge base.
Provider-independent, plain Python dataclass — no ORM, no vector store.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ClinicalDocument:
    """
    Represents a single unit of clinical knowledge.

    Fields
    ------
    id          : Unique slug (e.g. "sepsis-ssc-2024-fluid")
    title       : Human-readable title
    source      : Authoring organisation (e.g. "Surviving Sepsis Campaign")
    category    : Clinical domain (e.g. "Sepsis", "AKI", "Shock", "Oxygen Therapy")
    section     : Sub-section within the guideline (e.g. "Fluid Resuscitation")
    content     : Full text of the chunk — what the LLM will read
    tags        : Free-form keyword list for lightweight keyword matching
    """

    id: str
    title: str
    source: str
    category: str
    section: str
    content: str
    tags: List[str] = field(default_factory=list)

    # Optional drug-specific fields
    generic_name: str = None
    drug_class: str = None
    indications: str = None
    contraindications: str = None
    mechanism: str = None
    dosing: str = None
    renal_adjustment: str = None
    monitoring: str = None
    adverse_effects: str = None
    interactions: str = None

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "category": self.category,
            "section": self.section,
            "content": self.content,
            "tags": self.tags,
        }
        # Add drug fields if they are set
        if self.category == "Drug":
            data.update({
                "generic_name": self.generic_name,
                "drug_class": self.drug_class,
                "indications": self.indications,
                "contraindications": self.contraindications,
                "mechanism": self.mechanism,
                "dosing": self.dosing,
                "renal_adjustment": self.renal_adjustment,
                "monitoring": self.monitoring,
                "adverse_effects": self.adverse_effects,
                "interactions": self.interactions,
            })
        return data
